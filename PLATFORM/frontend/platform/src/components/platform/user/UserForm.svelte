<script>
  import BaseInput from "$components/argon_template/Inputs/BaseInput.svelte";
  import BaseSelect from "$components/platform/commons/BaseSelect.svelte";
  import { InputValidators } from "$lib/commons/utils";
  import { UserController } from "$lib/controllers/user_controller";
  import { BaseSelectListDC } from "$lib/models/data_containers/base_select_list_dc";
  import { User, UserStatusType } from "$lib/models/user";
  import { onMount } from "svelte";
  import { t } from "svelte-i18n";

  /**
   * @typedef {Object} UserFormProps
   * @property {User} [user]
   * @property {boolean} [readonly]
   */

  /** @type UserFormProps */
  let {
    user = $bindable(User.empty()),
    readonly = false,
  } = $props();

  /** @type boolean */
  let disabledFields = $state();

  /** @type boolean */
  let loading = $state(true);

  /** @type {UserController} */
  const userCtl = new UserController();

  /** @type BaseInput */
  let _userFirstNameInput = $state();

  /** @type string */
  const _userFirstNameField = $t("entity.user.firstName");

  /** @type BaseInput */
  let _userLastNameInput = $state();

  /** @type string */
  const _userLastNameField = $t("entity.user.lastName");

  /** @type BaseInput */
  let _userEmailInput = $state();

  /** @type string */
  const _userEmailField = $t("entity.user.email");

  /** @type BaseSelect */
  let _userRoleSelect = $state();

  /** @type string */
  const _userRoleField = $t("entity.user.roleName");

  /** @type BaseSelect */
  let _userStatusSelect = $state();

  /** @type string */
  const _userStatusField = $t("common.label.status");

  /** @type string */
  const _userPhoneField = $t("entity.user.phone");

  /** @type string */
  const _selectNoOptionsMessage = $t("component.select.no-options");

  // ROLE VARS
  /** @type BaseSelectListDC */
  let selectedRole = $state();

  /** @type BaseSelectListDC[] */
  let userRoles = $state([]);

  /** @type boolean */
  let enableRoleChange = $derived(!!user?.id && ![ UserStatusType.PENDING ].includes(user?.statusName));

  /**
   * @param {BaseSelectListDC} value
   * @return string
   */
  const getRoleLabel = (value) => $t(`entity.user.roleType.${ value }`);

  /** @type EventCallback */
  const onSelectRole = (event) => {
    const roleSelected = event && event.detail && event.detail.value !== undefined
      ? event.detail.value
      : (event.value !== undefined ? event.value : event);
    user.roleName = roleSelected;
  };

  /** @return void */
  const onClearRole = () => {
    user.roleName = null;
  };

  /** @param {BaseSelectListDC} value
   * @return string
   */
  const getStatusLabel = (value) => $t(`entity.user.statusType.${ value }`);

  /** @type EventCallback */
  const onSelectStatus = (event) => {
    const statusNameSelected = event && event.detail && event.detail.value !== undefined
      ? event.detail.value
      : (event.value !== undefined ? event.value : event);
    user.statusName = statusNameSelected;
  };

  /** @param {UserStatusType} status
   * @return BaseSelectListDC[]
   */
  const statusAvailableOptions = (status) => {
    switch (status) {
      case UserStatusType.ACTIVE:
        return [
          new BaseSelectListDC({ value: UserStatusType.INACTIVE }),
        ];

      case UserStatusType.INACTIVE:
        return user.approvalTocTs
          ? [ new BaseSelectListDC({ value: UserStatusType.ACTIVE }) ]
          : [ new BaseSelectListDC({ value: UserStatusType.INACTIVE }) ];
      default:
        return [
          new BaseSelectListDC({ value: UserStatusType.ACTIVE }),
          new BaseSelectListDC({ value: UserStatusType.INACTIVE }),
        ];
    }
  };

  /** @type {Object.<boolean, boolean>} */
  let disabledEl = { owner: true, organization: true };

  /** @param {BaseSelectListDC} role
   * @param {boolean} isDisabled
   * @return void
   */
  const disabledElFilters = (
    role,
    isDisabled,
  ) => {
    if (isDisabled) {
      disabledEl = { owner: true, organization: true };

    }
  };


  /** @type OnMount */
  onMount(async () => {
    userRoles = await userCtl.getUserRoles();
    loading = false;
  });

  /** @return boolean */
  export const validateForm = () => {
    const validators = [
      _userFirstNameInput,
      _userLastNameInput,
      _userEmailInput,
      _userRoleSelect,
      _userStatusSelect,
    ];

    return !validators.map((el) => el.validate()).includes(false);
  };
  $effect(() => {
    disabledFields = loading || readonly;
  });
  $effect(() => {
    selectedRole = user.roleName ? new BaseSelectListDC({ value: user.roleName }) : null;
  });
  $effect(() => {
    disabledElFilters(selectedRole, disabledFields);
  });
</script>

<div class="mx-2">
  {#if !loading}
    <div class="row d-block">
      <BaseInput
          bind:this={_userFirstNameInput}
          type="text"
          name={_userFirstNameField}
          label={_userFirstNameField}
          placeholder={_userFirstNameField}
          value={user.firstName}
          onchange={(event) => user.firstName = event.target.value}
          customRequired
          readonly={disabledFields}
      />

      <BaseInput
          bind:this={_userLastNameInput}
          type="text"
          name={_userLastNameField}
          label={_userLastNameField}
          placeholder={_userLastNameField}
          value={user.lastName}
          onchange={(event) => user.lastName = event.target.value}
          customRequired
          readonly={disabledFields}
      />

      <BaseInput
          bind:this={_userEmailInput}
          type="email"
          name={_userEmailField}
          label={_userEmailField}
          placeholder={_userEmailField}
          autocomplete="email"
          value={user.email}
          onchange={(event) => user.email = event.target.value}
          validator={({value, defaultValidator}) => {
                return defaultValidator(value)
                  || InputValidators.validateEmail(value, $t, { tArgs: { field: _userEmailField } });
              }}
          customRequired
          readonly={disabledFields}
      />

      <BaseInput
          type="text"
          name={_userPhoneField}
          label={_userPhoneField}
          placeholder={_userPhoneField}
          value={user.phone}
          onchange={(event) => user.phone = event.target.value}
          readonly={disabledFields}
      />

      <div class="col-12 px-0 mb-4">
        <BaseSelect
            bind:this={_userRoleSelect}
            selectClasses="form-control"
            customRequired
            searchable={false}
            items={userRoles}
            label={_userRoleField}
            name={_userRoleField}
            disabled={disabledFields}
            value={selectedRole}
            itemId="value"
            itemLabel="value"
            onchange={onSelectRole}
            onclear={onClearRole}
            placeholder={_userRoleField}
        >
          {#snippet itemSnippet({ value })}
            <span>{getRoleLabel(value)}</span>
          {/snippet}
          {#snippet selectionSnippet({ value })}
            <span>{getRoleLabel(value)}</span>
          {/snippet}
        </BaseSelect>
      </div>

      <div class="col-12 px-0 mb-4">
        <BaseSelect
            customRequired
            bind:this={_userStatusSelect}
            selectClasses="form-control"
            placeholder={_userStatusField}
            label={_userStatusField}
            name={_userStatusField}
            disabled={disabledFields || !enableRoleChange}
            searchable={false}
            items={statusAvailableOptions(user?.statusName)}
            value={new BaseSelectListDC({ value: user?.statusName })}
            itemId="value"
            itemLabel="value"
            onchange={onSelectStatus}
        >
          {#snippet itemSnippet({ value })}
            <span>{getStatusLabel(value)}</span>
          {/snippet}
          {#snippet selectionSnippet({ value })}
            <span>{getStatusLabel(value)}</span>
          {/snippet}
        </BaseSelect>
      </div>
    </div>
  {/if}
</div>