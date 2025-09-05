<script>
  import Notification from "$components/argon_template/NotificationPlugin/Notification.svelte";
  import { getNotificationsContext } from "svelte-notifications";
  import { slide } from "svelte/transition";

  const { removeNotification } = getNotificationsContext();

  /**
   * @typedef {Object} CustomNotificationProps
   * @property {NotificationArgs} [notification]
   */

  /** @type CustomNotificationProps */
  let {
    /** @type NotificationArgs */ notification = {},
  } = $props();

  /**
   * @param {string} id - ID from notification to remove
   * @return void
   */
  const remove = (id) => removeNotification(id);
</script>

<div class="top-right-notifications" class:icon={!!notification.icon} transition:slide>
  <Notification
      dataNotify
      dismissible
      icon={notification.icon ?? ''}
      id={notification.id}
      notifyClassNames={notification.notifyClassNames}
      onclick={notification.onclick}
      onremove={() => remove(notification.id)}
      type={notification.type ?? "info"}>
    <span>{notification.text}</span>
  </Notification>
</div>

<style>
  .top-right-notifications.icon {
    min-height: 75px !important;
  }
</style>
 