<script>
  import BaseInput from "$components/argon_template/Inputs/BaseInput.svelte";
  import { InputValidators } from "$lib/commons/utils";
  import { User } from "$lib/models/user";
  import { t } from "svelte-i18n";

  /**
   * @typedef {Object} ProfileFormProps
   * @property {User} [user]
   * @property {boolean} [readonly]
   */

  /** @type ProfileFormProps */
  let {
    /** @type User */ user = $bindable(User.empty()),
    /** @type boolean */ readonly = false,
  } = $props();

  /** @type BaseInput */
  let _firstNameInput = $state();

  /** @type string */
  const _firstNameField = $t("entity.user.firstName");

  /** @type BaseInput */
  let _lastNameInput = $state();
  /** @type string */
  const _lastNameField = $t("entity.user.lastName");

  /** @type BaseInput */
  let _emailInput = $state();

  /** @type string */
  const _emailField = $t("entity.user.email");

  /** @type string */
  const _phoneField = $t("entity.user.phone");

  // TODO: ADD IMAGE CHANGE
  // const changeProfileImage = () => Utils.logging('warn', 'Change image is not available yet.');

  /** @returns boolean */
  export const validateForm = () => {
    return ![
      _firstNameInput,
      _lastNameInput,
      _emailInput,
    ].map((el) => el.validate()).includes(false);
  };

</script>

<div class="mx-2">
  <!--  TODO: Add this when support to change image is available -->
  <!--  <div class="row col-12 mb-4 mt-3 ml-0 ml-md-3 align-items-center justify-content-center justify-content-md-start">-->
  <!--    <div class="avatar avatar-xl avatar-custom bg-secondary profile-img">-->
  <!--      {#if user.profilePictureUrl}-->
  <!--        <img alt="User profile" src={user.profilePictureUrl} />-->
  <!--      {:else}-->
  <!--        <img class="avatar-logo" src="/imgs/logos/.svg" alt="bracelet logo" />-->
  <!--      {/if}-->

  <!--      <div class="position-absolute bottom--3 btn-change-img" onclick={changeProfileImage}>-->
  <!--        <BaseButton class="media-device-icon m-0" size="sm">-->
  <!--          <i class="fas fa-camera fa-fw"></i>-->
  <!--        </BaseButton>-->
  <!--      </div>-->
  <!--      -->
  <!--    </div>-->
  <!--  </div>-->

  <div class="row">
    <div class="col-12 col-md-6">
      <BaseInput
          bind:this={_firstNameInput}
          customRequired
          label={_firstNameField}
          name={_firstNameField}
          onchange={(event) => user.firstName = event.target.value}
          placeholder={_firstNameField}
          {readonly}
          type="text"
          value={user.firstName}
      />
    </div>

    <div class="col-12 col-md-6">
      <BaseInput
          bind:this={_lastNameInput}
          customRequired
          label={_lastNameField}
          name={_lastNameField}
          onchange={(event) => user.lastName = event.target.value}
          placeholder={_lastNameField}
          {readonly}
          type="text"
          value={user.lastName}
      />
    </div>
  </div>

  <div class="row">
    <div class="col-12 col-md-6">
      <BaseInput
          autocomplete="email"
          bind:this={_emailInput}
          customRequired
          label={_emailField}
          name={_emailField}
          onchange={(event) => user.email = event.target.value}
          placeholder={_emailField}
          {readonly}
          type="email"
          validator={({value, defaultValidator}) => {
                return defaultValidator(value)
                || InputValidators.validateEmail(value, $t, { tArgs: { field: _emailField } });
              }}
          value={user.email}
      />
    </div>

    <div class="col-12 col-md-6">
      <BaseInput
          label={_phoneField}
          name={_phoneField}
          onchange={(event) => user.phone = event.target.value}
          placeholder={_phoneField}
          {readonly}
          type="text"
          value={user.phone}
      />
    </div>

  </div>
</div>

<style>
  .profile-img {
    box-shadow: 0.4rem 0.4rem 0.5rem #dad6d6f7 !important;
  }

  .btn-change-img {
    z-index: 1;
  }
</style>
