from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.

revision = '3f3cf07179db'
down_revision = None
branch_labels = None
depends_on    = None


def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')
    op.execute('CREATE EXTENSION IF NOT EXISTS unaccent;')
    op.execute(f"""
            CREATE OR REPLACE FUNCTION public.unaccent_text(text)
              RETURNS text AS
            $BODY$
            SELECT public.unaccent($1);
            $BODY$
            LANGUAGE sql IMMUTABLE
              COST 1;
            """)

    op.create_table(
        'user_status',
        sa.Column('name', sa.VARCHAR(64), primary_key=True),
        sa.Column('create_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        comment="Defines the visibility for the user"
    )

    op.create_table(
        'user_role',
        sa.Column('name', sa.VARCHAR(64), primary_key=True),
        sa.Column('create_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        comment="Defines the types of permissions for the user"
    )

    op.create_table(
        'user_account',
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('email', sa.VARCHAR(255), nullable=False, unique=True),
        sa.Column('password', sa.VARCHAR(255), nullable=False),
        sa.Column(
            'user_role_name',
            sa.VARCHAR(64),
            sa.ForeignKey('user_role.name', onupdate='CASCADE'),
            nullable = False,
            index    = True
        ),
        sa.Column(
            'user_status_name',
            sa.VARCHAR(64),
            sa.ForeignKey('user_status.name', onupdate='CASCADE'),
            nullable = False,
            index    = True,
            server_default = sa.text("'pending'")
        ),
        sa.Column('first_name', sa.VARCHAR(255), nullable=False),
        sa.Column('last_name', sa.VARCHAR(255), nullable=False),
        sa.Column('phone', sa.VARCHAR(64)),
        sa.Column('approval_toc_ts', sa.TIMESTAMP()),
        sa.Column('blocked_ts', sa.TIMESTAMP()),
        sa.Column('create_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Index(
            'user_account_fts_gist_idx',
            sa.text(
                "public.unaccent_text("
                "(email || ' ' || first_name || ' ' ||  last_name || COALESCE(' ' ||  phone, ''))"
                ") gist_trgm_ops"
            ),
            postgresql_using = 'gist'
        ),
        comment="People could login into the platform"
    )

    op.create_table(
        'instrument',
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.VARCHAR(255), nullable=False),
        sa.Column('filename', sa.VARCHAR(512), nullable=False),
        sa.Column('model', sa.VARCHAR(255), nullable=False),
        sa.Column('url', sa.TEXT(), nullable=False, index=True),
        sa.Column('create_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'))
    )

    op.create_table(
        'pathology',
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.VARCHAR(255), nullable=False),
        sa.Column('create_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'))
    )

    op.create_table(
        'gender_type',
        sa.Column('name', sa.VARCHAR(64), primary_key=True),
        sa.Column('create_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        comment="Defines the type of gender"
    )

    op.create_table(
        'patient',
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('code', sa.VARCHAR(255), nullable=False, unique=True),
        sa.Column(
            'gender',
            sa.VARCHAR(64),
            sa.ForeignKey('gender_type.name', onupdate='CASCADE'),
            nullable       = False,
            index          = True
        ),
        sa.Column('weight', sa.INTEGER(), nullable=False),
        sa.Column('birth_date', sa.DATE(), nullable=False),
        sa.Column(
            'owner_user_id',
            sa.INTEGER(),
            sa.ForeignKey('user_account.id', onupdate='CASCADE'),
            nullable  = False
        ),
        sa.Column(
            'patient_user_id',
            sa.INTEGER(),
            sa.ForeignKey('user_account.id', onupdate='CASCADE'),
            nullable  = True,
            index     = True
        ),
        sa.Column('create_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'))
    )

    op.create_table(
        'patient_pathology',
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column(
            'patient_id',
            sa.INTEGER(),
            sa.ForeignKey('patient.id', ondelete='CASCADE'),
            nullable = False,
            index    = True
        ),
        sa.Column(
            'pathology_id',
            sa.INTEGER(),
            sa.ForeignKey('pathology.id', ondelete='CASCADE'),
            nullable = False,
            index    = True
        ),
        sa.Column('detection_date', sa.DATE(), nullable=False),
        sa.Column(
            'create_ts',
            sa.TIMESTAMP(),
            nullable       = False,
            server_default = sa.text('now()'),
            index          = True
        ),
        sa.Column(
            'update_ts',
            sa.TIMESTAMP(),
            nullable       = False,
            server_default = sa.text('now()')
        )
    )

    op.create_table(
        'patient_model',
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column(
            'patient_id',
            sa.INTEGER(),
            sa.ForeignKey('patient.id', onupdate='CASCADE', ondelete='CASCADE'),
            nullable = False,
            index    = True
        ),
        sa.Column('name', sa.VARCHAR(512), nullable=False, index=True),
        sa.Column('filename', sa.VARCHAR(512), nullable=False),
        sa.Column('url', sa.TEXT(), nullable=False, index=True),
        sa.Column('create_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        comment="Model from the patients"
    )

    op.create_table(
        'entity',
        sa.Column('name', sa.VARCHAR(255), primary_key=True),
        sa.Column('create_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        comment="Entities on the platform"
    )

    op.create_table(
        'permission_grant',
        sa.Column('name', sa.VARCHAR(255), primary_key=True),
        sa.Column('create_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        comment="Types of permission that could be granted on the platform"
    )

    op.create_table(
        'permission',
        sa.Column(
            'user_role_name',
            sa.VARCHAR(255),
            sa.ForeignKey('user_role.name', onupdate='CASCADE', ondelete='CASCADE'),
            nullable    = False,
            primary_key = True
        ),
        sa.Column(
            'entity_name',
            sa.VARCHAR(255),
            sa.ForeignKey('entity.name', onupdate='CASCADE', ondelete='CASCADE'),
            nullable    = False,
            index       = True,
            primary_key = True
        ),
        sa.Column(
            'read',
            sa.VARCHAR(255),
            sa.ForeignKey('permission_grant.name', onupdate='CASCADE'),
            nullable = False,
            index    = True
        ),
        sa.Column(
            'write',
            sa.VARCHAR(255),
            sa.ForeignKey('permission_grant.name', onupdate='CASCADE'),
            nullable = False,
            index    = True
        ),
        sa.Column(
            'delete',
            sa.VARCHAR(255),
            sa.ForeignKey('permission_grant.name', onupdate='CASCADE'),
            nullable = False,
            index    = True
        ),
        sa.Column(
            'ui_visibility',
            sa.BOOLEAN,
            nullable       = False,
            server_default = sa.text('TRUE')
        ),
        sa.Column('create_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        comment="Permissions which defines the actions that could be done in an entity"
    )
        
    # ── New tables for telemedicine platform ──────────────────────────────────────
    op.create_table(
        'study',
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('patient_id', sa.INTEGER(), sa.ForeignKey('patient.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('step_count', sa.INTEGER(), nullable=False, comment="Cumulative steps for this study"),
        sa.Column('bpm', sa.INTEGER(), nullable=False, comment="Beats per minute"),
        sa.Column('spo2', sa.INTEGER(), nullable=True, comment="Oxygen saturation %"),
        sa.Column('ts', sa.TIMESTAMP(), nullable=False, comment="Timestamp of the measurement"),
        sa.Column('create_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        comment="Bracelet-collected signals per upload/day"
    )

    op.create_table(
        'alarm',
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('patient_id', sa.INTEGER(), sa.ForeignKey('patient.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('alarm_type', sa.VARCHAR(64), nullable=False, comment="'fall_detected', 'strange_bpm', 'button_alarm', etc."),
        sa.Column('ts', sa.TIMESTAMP(), nullable=False, comment="Time when alarm was raised"),
        sa.Column('is_urgent', sa.BOOLEAN(), nullable=False, server_default=sa.text('FALSE'), comment="True if urgent"),
        sa.Column('create_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        comment="Patient alarms from wearable or manual trigger"
    )

    op.create_table(
        'chat',
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('user1_id', sa.INTEGER(), sa.ForeignKey('user_account.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user2_id', sa.INTEGER(), sa.ForeignKey('user_account.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('administration', sa.BOOLEAN(), nullable=False, default=False, index=True),
        sa.Column('create_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('user1_id', 'user2_id', name='uq_chat_users'),
        comment="1-to-1 chats between two users"
    )

    op.create_table(
        'message',
        sa.Column('id', sa.INTEGER(), primary_key=True, autoincrement=True),
        sa.Column('chat_id', sa.INTEGER(), sa.ForeignKey('chat.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('sender_id', sa.INTEGER(), sa.ForeignKey('user_account.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('content', sa.TEXT(), nullable=False, comment="Message body"),
        sa.Column('ts', sa.TIMESTAMP(), nullable=False, comment="Time when message was sent"),
        sa.Column('create_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('update_ts', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        comment="Chat messages"
    )



    op.execute("""
        CREATE OR REPLACE FUNCTION trigger_fn_update_ts_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.update_ts = now(); 
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    for tbl_name in (
        'user_status',
        'user_role',
        'user_account',
        'instrument',
        'pathology',
        'gender_type',
        'patient',
        'patient_pathology',
        'patient_model',
        'entity',
        'permission_grant',
        'permission',
        'study', 
        'alarm', 
        'chat', 
        'message'
    ):
        op.execute(f'''
        CREATE TRIGGER {tbl_name}_update_ts_trigger BEFORE UPDATE
        ON "{tbl_name}" FOR EACH ROW EXECUTE PROCEDURE 
        trigger_fn_update_ts_column();
        ''')


def downgrade():
    for tbl_name in (
        'message',
        'alarm', 
        'chat', 
        'study', 
        'permission',
        'permission_grant',
        'entity',
        'patient_model',
        'patient_pathology',
        'patient',
        'gender_type',
        'pathology',
        'instrument',
        'user_account',
        'user_role',
        'user_status'
    ):
        op.drop_table(tbl_name)

    op.execute('DROP FUNCTION IF EXISTS trigger_fn_update_ts_column()')
