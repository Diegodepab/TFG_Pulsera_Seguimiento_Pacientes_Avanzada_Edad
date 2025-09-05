from ..controllers.base_ctrl import braceletBaseCtrl
from ..models.patients import Patient
from ..models.patient_pathologies import PatientPathology

from ..models.query_builder import JoinMeta
from ..models.base_model import database_manager
import sqlalchemy as sa
from sqlalchemy import Column

from ..models.query_builder import QueryBuilder

from typing import Optional, Dict, Union, Any, OrderedDict, Sequence, Tuple, Mapping, List


class PatientPathologyCtrl(braceletBaseCtrl):
    Model       = PatientPathology
    OwnerColumn = Patient.Table.c.owner_user_id

    # noinspection PyDefaultArgument
    @classmethod
    async def _apply_fts_sort_builder(
            cls,
            builder    : QueryBuilder = None,
            fts        : str = "",
            fields_map : Dict[Union[str, Column], Any] = {},
            sort_map   : OrderedDict = {}
    ):
        if not builder:
            builder = QueryBuilder(cls.Model)

        user_t = cls.Model.Table
        # This expression is the same used for the trigram gist index
        col_expr = user_t.c.email \
            .concat(' ') \
            .concat(user_t.c.first_name) \
            .concat(' ') \
            .concat(user_t.c.first_name) \
            .concat(' ') \
            .concat(user_t.c.last_name) \
            .concat(
            sa.func.coalesce(
                sa.literal(' ').concat(user_t.c.phone),
                sa.literal('')
            )
        )

        # We use to filter both % and %>, the later being word similarity, this is needed to find small search texts
        # the full column is too big to search in all the text with only a keyword, you don't pass the threshold
        fts_query = sa.select([
            *user_t.c,
            sa.cast(
                col_expr.op('<->')(fts),
                sa.Numeric(5, 4)
            ).label('match_distance')
        ]).select_from(
            user_t
        ).where(
            sa.or_(
                col_expr % fts,
                col_expr.op('%>')(fts)

            )
        ).alias('fts')

        builder = builder.add_join(
            JoinMeta(
                table    = fts_query,
                onclause = JoinMeta.OnClause(
                    left  = cls.Model.Table.c.id,
                    right = fts_query.c.id
                )
            )
        )

        builder = cls.apply_special_sort(
            builder    = builder,
            column     = fts_query.c.match_distance,
            sort_order = 'asc',
            fields_map = fields_map,
            sort_map   = sort_map
        )

        return builder

    # noinspection PyDefaultArgument
    @classmethod
    async def search(
            cls,
            builder            : QueryBuilder                             = None,
            fields_map         : Dict[Union[str, Column], Any]            = {},
            embed_map          : Dict[str, Union[bool, Dict]]             = {},
            sort_map           : Union[OrderedDict, Dict]                 = {},
            reverse_query_sort : bool                                     = False,
            reverse_records    : bool                                     = False,
            limit              : Optional[int]                            = None,
            offset             : Optional[int]                            = None,
            where_conds        : Sequence[Tuple[str, Mapping]]            = (),
            extra_args         : Dict[str, Any]                           = {},
            dynamic_rel_context : Dict[ str, Dict[str, Union[str, int]] ] = {}
    ) -> Tuple[List[PatientPathology], bool]:
        patient_id   = extra_args.get('patient_id')
        pathology_id = extra_args.get('pathology_id')

        if patient_id is not None:
            if builder is None:
                builder = QueryBuilder(cls.Model)

            builder = builder.where(
                cls.Model.Table.c.patient_id == patient_id
            )

        if pathology_id is not None:
            if builder is None:
                builder = QueryBuilder(cls.Model)

            builder = builder.where(
                cls.Model.Table.c.pathology_id == pathology_id
            )

        return await super().search(
            builder             = builder,
            fields_map          = fields_map,
            embed_map           = embed_map,
            sort_map            = sort_map,
            reverse_query_sort  = reverse_query_sort,
            reverse_records     = reverse_records,
            limit               = limit,
            offset              = offset,
            where_conds         = where_conds,
            extra_args          = extra_args,
            dynamic_rel_context = dynamic_rel_context
        )

    @classmethod
    async def link_patient_pathologies(
            cls,
            patient_id  : int,
            pathologies : List[PatientPathology]
    ):
        coros = []

        linked: List[PatientPathology] = []

        tx = await database_manager.get_db_conn().transaction()

        options = {
            'extra_args': {
                'patient_id': patient_id
            }
        }

        # get all the patient's pathologies
        prev_patient_pathologies = await PatientPathologyCtrl.search(
            **options
        )

        # id of the presets to be ignored in the for to create PatientPathology
        ignore_operation = []
        update_operation = []

        prev_patient_pathologies, _ = prev_patient_pathologies
        try:
            # Check if I should delete the ones that were initially selected
            for patient_pathology in prev_patient_pathologies:
                ignore_operation.append(patient_pathology.pathology_id)
                # Check if I should delete the ones that were initially there
                is_still_selected = next((obj for obj in pathologies if obj.id == patient_pathology.pathology_id),
                                         None)

                if is_still_selected is None:  # It is no longer selected, delete it
                    await PatientPathologyCtrl.delete(patient_pathology.id)
                else:
                    update_operation.append(patient_pathology)

            # Select all others
            for pathology in pathologies:
                # Check if they are the ones that were initially selected to do nothing,
                # it is already done in the previous for
                prev_selected_initial = next(
                    (obj for obj in update_operation if obj.pathology_id == pathology.id),
                    None
                )

                if prev_selected_initial is not None:
                    prev_selected_initial.detection_date = pathology.detection_date
                    coros.append(PatientPathologyCtrl.update(
                        prev_selected_initial.id,
                        prev_selected_initial
                    ))
                else:
                    new_link_patient_pathology = PatientPathology(
                        patient_id     = patient_id,
                        pathology_id   = pathology.id,
                        detection_date = pathology.detection_date
                    )

                    coros.append(PatientPathologyCtrl.create(
                        new_link_patient_pathology, with_transaction=False
                    ))

            for coro in coros:
                linked.append(await coro)
        except Exception as e:
            await tx.rollback()
            raise e

        await tx.commit()

        return linked
