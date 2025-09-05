/**
 * @typedef {Object} ChartObject
 * @property {string[]} labels - The labels for the chart data.
 * @property {ChartDataSet[]} datasets - The datasets for the chart.
 */

/**
 * @typedef {Object} ChartDataSet
 * @property {string} label - The label for the group.
 * @property {boolean} fill - Whether to fill the area under the line.
 * @property {number} lineTension - The tension of the line.
 * @property {string} borderColor - The color of the line.
 * @property {string} pointBorderColor - The color of the data points.
 * @property {number} pointBorderWidth - The width of the data point border.
 * @property {number} pointRadius - The radius of the data points.
 * @property {number} pointHitRadius - The hit radius of the data points.
 * @property {Array<number>} data - The data values for the group.
 */

/**
 * Object representing navigator history functions.
 * @typedef {Object} NavigatorHistory
 * @property {() => string} pop - Function to pop a URL from history.
 * @property {(defaultPath: string) => Promise<void>} goBack - Function to go back in history.
 * @property {(i: number) => string} at - Function to get the URL at a specific index in history.
 * @property {(defaultPath: string, pattern: RegExp) => Promise<void>} removePatternAndGoBack - Function to remove URLs
 *   matching a pattern from history and go back.
 * @property {(run: Subscriber<Array<string>>, invalidate?: Invalidator<Array<string>>) => Unsubscriber} subscribe -
 *   Function to subscribe to changes in history.
 * @property {() => void} reset - Function to reset history.
 * @property {(url: URL) => boolean} isCurrentPath - Function to check if a URL is the current path.
 * @property {(url: URL) => boolean} isPrevPath - Function to check if a URL is the previous path.
 * @property {(url: URL) => string} push - Function to push a URL to history.
 */

/**
 * toDict.
 * @typedef {Object} toDictModel
 * @property {boolean} [ignoreEmbeds] - Whether to ignore embedded objects.
 * @property {boolean} [ignoreNullValues] - Whether to ignore null values.
 */

/**
 * Represents the result of a SweetAlert.
 * @typedef {Object} SweetAlertResult
 * @property {boolean} isConfirmed - Indicates whether the dialog was confirmed.
 * @property {boolean} isDenied - Indicates whether the dialog was denied.
 * @property {boolean} isDismissed - Indicates whether the dialog was dismissed.
 * @property {?} value - The value returned from the dialog.
 * @property {Record<string, ?>} [additionalProps] - Additional properties included in the result.
 */

/**
 * Function called when a svelte component is mounted.
 * @callback OnMount
 * @returns void
 */

/**
 * Type for every event param
 * @callback EventCallback
 * @param {CustomEvent} event
 * @returns void
 */

/**
 * Type for every event param in an async function
 * @callback EventCallbackAsync
 * @param {CustomEvent} event
 * @returns Promise<void>
 */

/**
 * Studies a function to be called when the component is destroyed.
 * @callback onDestroy - The function to be called when the component is destroyed.
 * @returns void
 */

// Types from exception_actions
/**
 * Type representing arguments for displaying a message in an exception action.
 * @typedef {Object} ExceptionActionShowMessageArgs
 * @property {string} [title] - The title of the message.
 * @property {string} [content] - The content of the message.
 * @property {string} [icon] - The icon for the message.
 * @property {string} [confirmButton] - The text for the confirmation button.
 * @property {string} [cancelButton] - The text for the cancel button.
 */

/**
 * Type representing a function for showing a message in an exception action.
 * @typedef {Function} ExceptionActionShowMessageFunction
 * @param {ExceptionActionShowMessageArgs} args - The arguments for showing the message.
 * @returns Promise<void> - A promise indicating the completion of showing the message.
 */

/**
 * Type representing a function for managing an exception in an exception action.
 * @typedef {Function} ExceptionOnManageFunction
 * @returns Promise<void> - A promise indicating the completion of managing the exception.
 */

// Types from exception
/**
 * Represents an exception with UI context information.
 * @typedef {Object} UiCtxException
 * @property {number} code - The code associated with the exception.
 * @property {string} [message] - Optional message describing the exception.
 */

/**
 * Represents an exception with API context information.
 * @typedef {Object} ApiCtxException
 * @property {number} [code] - Optional code associated with the exception.
 * @property {string} [type] - Optional type of exception.
 * @property {string} [message] - Optional message describing the exception.
 * @property {string[]} [loc] - Optional location information.
 * @property {Record<string, ?>} [extra] - Additional arbitrary data associated with the exception.
 */

// Types from dropzone_upload_file_utils
/**
 * Represents a Blob file.
 * @typedef {Object} BlobFile
 * @property {number} id - The ID of the file.
 * @property {string} name - The name of the file.
 * @property {string} url - The URL of the file.
 * @property {string} displayUrl - The display URL of the file.
 * @property {string=} deleteUrl - The delete URL of the file (optional).
 * @property {boolean=} original - Indicates if the file is original (optional).
 * @property {DropzoneFileType=} type - The type of the file (optional).
 */

/**
 * Represents data about upload progress.
 * @typedef {Object} UploadProgressData
 * @property {boolean|undefined} uploading - Indicates if uploading is in progress.
 * @property {number} progress - The progress of the upload (percentage).
 */

// Types from global_types
/**
 * Represents a JSON value.
 * @typedef {string | number | boolean | null | Json[] | { [key: string]: Json }} Json
 */

/**
 * Represents the context for notifications.
 * @typedef {Object} NotificationContext
 * @property {?} subscribe - The subscription context.
 * @property {(notification: ?) => void} addNotification - Function to add a notification.
 * @property {(notificationId: string) => void} removeNotification - Function to remove a notification by ID.
 * @property {() => void} clearNotifications - Function to clear all notifications.
 */

/**
 * @typedef {Object} NotificationArgs
 * @property {string} id - Unique identifier
 * @property {("top-right"|string)} [position='top-right'] - Position
 * @property {("top right"|string)} [notifyClassNames='top right'] - CSS classes
 * @property {number} removeAfter - Time in ms to auto-remove
 * @property {string} [type] - Notification type
 * @property {string} [icon] - Icon to display
 * @property {string} [text] - Text content
 * @property {OptionalMethod} [onclick] - Click handler
 */

/**
 * Represents a function to create a model from JSON data.
 * @typedef {(data: Json) => BaseModel | BaseDC} ModelFromJson
 */

/**
 * Represents a function to transform JSON data into a model.
 // * @typedef {<T extends BaseModel | BaseDC>(data: Json) => T} ModelTransformer
 * @typedef {(data: Json) => (BaseModel|BaseDC|Json|Promise<BaseModel|BaseDC|Json>)} ModelTransformer
 */

// Types from ui_utils

/**
 * Base type representing duration for videos or records.
 * @typedef {Object} BaseDuration
 * @property {number} hours - The number of hours.
 * @property {number} minutes - The number of minutes.
 * @property {number} seconds - The number of seconds.
 */

/**
 * @template [ReturnType=void]
 * @template {any[]} [Params=[]]
 * @typedef {(function(...): ReturnType)|null|undefined} OptionalMethod
 */

