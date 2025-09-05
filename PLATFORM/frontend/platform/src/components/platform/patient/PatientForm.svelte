<script>
  import BaseInput from "$components/argon_template/Inputs/BaseInput.svelte";
  import BaseDateInput from "$components/platform/commons/BaseDateInput.svelte";
  import BaseSelect from "$components/platform/commons/BaseSelect.svelte";
  import { SessionManager } from "$lib/commons/session_manager";
  import { Debounce, InputValidators } from "$lib/commons/utils";
  import { PatientController } from "$lib/controllers/patient_controller";
  import { UserController } from "$lib/controllers/user_controller";
  import { BaseSelectListDC } from "$lib/models/data_containers/base_select_list_dc";
  import { UserListDC } from "$lib/models/data_containers/user_list_dc";
  import { Patient } from "$lib/models/patient";
  import { User, UserRoleType } from "$lib/models/user";
  import {
    QueryComparativeOperations,
    QueryFields,
    QueryParamsQ,
    QueryParamsRaw,
    QueryParamsSort,
  } from "$lib/services/utils/query_utils";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";

  /**
   * @typedef {Object} PatientFormProps
   * @property {Patient} [patient] -
   * @property {boolean} [readonly] - .
   * @property {boolean} [loading] -
   */

  /** @type PatientFormProps */
  let {
    /** @type Patient */ patient = $bindable(Patient.undef()),
    /** @type boolean */ readonly = false,
    /** @type boolean */ loading = true,
  } = $props();

  $effect(() => {
    patient = patient;
  });

  /** @type boolean */
  let ownerUserElFocused = $state(false);

  /** @type boolean */
  let prevOwnerUserElFocused = undefined;

  /** @type PatientController */
  const patientCtl = new PatientController();

  /** @type {BaseInput} */
  let _patientCodeInput = $state();

  /** @type string */
  const _patientCodeField = $t("entity.patient.code");

  const getSuggestedOwner = (ownerId) => {
    return suggestedOwnerUsers.find((owner) => owner.id === ownerId);
  };

  /** @type string */
  let ownerUserFilterText = $state();

  /** @type BaseSelect */
  let _patientGenderSelect = $state();
  /** @type string */
  const _patientGenderField = $t("entity.patient.gender");

  /** @type BaseInput */
  let _patientWeightInput = $state();

  /** @type string */
  const _patientWeightField = $t("entity.patient.weight");

  /** @type BaseInput */
  let _patientBirthDateInput = $state();

  /** @type string */
  const _patientBirthDateField = $t("entity.patient.birth-date");

  /** @type BaseSelect */
  let _patientOwnerUserSelect = $state();

  /** @type string */
  const _patientOwnerUserField = $t("entity.patient.ownerFullName");

  // GENDER VARS
  /** @type BaseSelectListDC */
  let selectedGender = $derived(patient.gender ? new BaseSelectListDC({ value: patient.gender }) : null);

  /** @type BaseSelectListDC[] */
  let genderTypes = $state([]);

  // OWNER USER VARS
  /** @type UserListDC */
  let selectedOwnerUser = $state();

  /** @type UserListDC[] */
  let suggestedOwnerUsers = $state([]);
  const _searchSuggestedOwnerUsersAbortCtl = new Debounce(1);

  /** @type boolean */
  const disabledFields = $derived(loading || readonly);

  /** @param {BaseSelectListDC} value
   * @return string
   */
  const getGenderTypeLabel = (value) => $t(`entity.patient.genderType.${ value }`);

  // Gender user select method
  const onSelectGenderType = (event) => {
    const genderData = event?.detail ?? event;
    patient.gender = genderData?.value;
  };

  // Owner user select method
  const onSelectOwnerUser = (event) => {
    const userData = event?.detail ?? event;
    selectedOwnerUser = new UserListDC(userData);
    patient.ownerUserId = selectedOwnerUser.id;
  };

  /**
   * @param {string|null} filterText - text for filter search
   * @param {number} [limit] - limit the query
   **/
  const searchSuggestedOwnerUsers = async (filterText, limit) => {
    /** @type {Map<QueryFields, unknown>} */
    const params = new Map();
    params.set(QueryFields.LIMIT, limit ?? 500);

    params.set(QueryFields.Q, [
      new QueryParamsQ({
        field: User.apiFields.roleName,
        operation: QueryComparativeOperations.EQ,
        value: UserRoleType.USER,
      }),
    ]);

    if ((filterText?.trim()?.length ?? 0) > 0) {
      params.set(QueryFields.RAW, [ new QueryParamsRaw({ field: "fts", value: filterText }) ]);
    } else {
      params.set(QueryFields.SORT, [ new QueryParamsSort({ field: User.apiFields.email }) ]);
    }

    return (await ((new UserController())).search({
      params,
      transformer: async (data) => (await User.fromJson(data)).toDC(UserListDC),
    })).items;
  };

  /** @type OnMount */
  onMount(async () => {
    genderTypes = await patientCtl.getGenderTypes();
    loading = false;
  });

  /** @returns boolean */
  export const validateForm = () => {
    const validators = [
      _patientCodeInput,
      _patientWeightInput,
      _patientBirthDateInput,
      _patientGenderSelect,
      _patientOwnerUserSelect,
    ].filter(Boolean); // Remove undefined/null references

    return !validators.map((el) => el?.validate?.()).includes(false);
  };

  $effect(() => {
    if (patient.ownerUserId !== prevOwnerUserElFocused) {
      prevOwnerUserElFocused = patient.ownerUserId;

      const _owner = getSuggestedOwner(patient.ownerUserId);

      if (_owner) {
        selectedOwnerUser = _owner;
      } else {
        _searchSuggestedOwnerUsersAbortCtl.debounce(async () => {
          suggestedOwnerUsers = await searchSuggestedOwnerUsers(null, 100);
          selectedOwnerUser = getSuggestedOwner(patient.ownerUserId);
        });
      }
    }
  });

</script>

<div class="mx-2">
  {#if !loading}
    <div class="row d-block">
      <div class="row">
        <div class="col-12 col-md-6">
          <BaseInput
              bind:this={_patientCodeInput}
              type="text"
              name={_patientCodeField}
              label={_patientCodeField}
              placeholder={_patientCodeField}
              value={patient.code}
              onchange={(event) => patient.code = event.target.value}
              customRequired
              readonly={disabledFields}
          />
        </div>

        <div class="col-12 col-md-6">
          <BaseDateInput
              labelClasses="select-patient-form"
              bind:this={_patientBirthDateInput}
              type="date"
              name={_patientBirthDateField}
              label={_patientBirthDateField}
              placeholder={_patientBirthDateField}
              value={patient.birthDate}
              onchange={(value) => patient.birthDate = value}
              customRequired
              readonly={disabledFields}
              validator={({ value, defaultValidator }) => {
              return defaultValidator(patient.birthDate) ?? InputValidators.validateNotFutureDate(patient.birthDate, $t);
            }}
          />
        </div>
      </div>
      <div class="row">
        <div class="col-12 col-md-6 mb-4 ">
          <BaseSelect
              labelClasses="select-patient-form"
              bind:this={_patientGenderSelect}
              selectClasses="form-control"
              customRequired
              searchable={false}
              items={genderTypes}
              label={_patientGenderField}
              name={_patientGenderField}
              placeholder={_patientGenderField}
              disabled={disabledFields}
              value={selectedGender}
              onchange={onSelectGenderType}
              itemId="value"
              itemLabel="value"
          >
            {#snippet itemSnippet({ value })}
              <div class="d-flex flex-column">
                <span class="font-weight-bold pb-1">{getGenderTypeLabel(value)}</span>
              </div>
            {/snippet}

            {#snippet selectionSnippet({ value })}
              <span>{getGenderTypeLabel(value)}</span>
            {/snippet}
          </BaseSelect>
        </div>

        <div class="col-12 col-md-6">
          <BaseInput
              bind:this={_patientWeightInput}
              type="number"
              name={_patientWeightField}
              label={_patientWeightField}
              placeholder={_patientWeightField}
              value={patient.weight}
              onchange={(event) => patient.weight = event.target.value}
              customRequired
              readonly={disabledFields}
          />
        </div>
      </div>


      {#if SessionManager.userRole() === UserRoleType.ADMIN}
        <div class="col-12 px-0 mb-4">
          <BaseSelect
              bind:this={_patientOwnerUserSelect}
              bind:filterText={ownerUserFilterText}
              bind:focused={ownerUserElFocused}
              selectClasses="form-control"
              customRequired
              items={suggestedOwnerUsers}
              loadOptions={searchSuggestedOwnerUsers}
              label={_patientOwnerUserField}
              name={_patientOwnerUserField}
              placeholder={_patientOwnerUserField}
              disabled={disabledFields}
              value={selectedOwnerUser}
              itemId="id"
              itemLabel="fullName"
              onchange={onSelectOwnerUser}
          />
        </div>
      {/if}

    </div>
  {/if}
</div>