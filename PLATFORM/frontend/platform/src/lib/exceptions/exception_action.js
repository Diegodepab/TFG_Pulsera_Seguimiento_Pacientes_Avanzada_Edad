/**
 * Enum representing the level of an exception action.
 * @readonly
 * @enum {number}
 */
const ExceptionActionLevel = {
  FATAL: 0,
  ERROR: 1,
  WARNING: 2,
  INFO: 3,
  DEBUG: 4,
};

class ExceptionAction {

  /** @type {Error} */
  error;
  /** @type string */
  messageTitle;
  /** @type string */
  messageContent;
  /** @type boolean */
  report;
  /** @type {ExceptionActionLevel} */
  level;
  /** @type {ExceptionActionShowMessageFunction | undefined} */
  showMessage;
  /** @type {ExceptionActionShowMessageArgs | undefined} */
  showMessageKArgs;
  /** @type {() => Promise<void>|undefined} */
  onManage;

  /**
   * Creates an instance of ExceptionAction.
   * @param {Error} error - The error object.
   * @param {string} messageTitle - The title of the message.
   * @param {string} messageContent - The content of the message.
   * @param {Object} [opts={}] - Options for the exception action.
   * @param {boolean} [opts.report=true] - Indicates if the exception should be reported.
   * @param {ExceptionActionLevel} [opts.level=ExceptionActionLevel.ERROR] - The level of the exception action.
   * @param {ExceptionActionShowMessageFunction} [opts.showMessage] - Function for showing a message.
   * @param {ExceptionActionShowMessageArgs} [opts.showMessageKArgs] - Arguments for showing the message.
   * @param {ExceptionOnManageFunction} [opts.onManage] - Function for managing the exception.
   */
  constructor(error, messageTitle, messageContent, opts = {}) {
    this.error = error;
    this.messageTitle = messageTitle;
    this.messageContent = messageContent;
    this.report = opts.report ?? true;
    this.level = opts.level ?? ExceptionActionLevel.ERROR;
    this.showMessage = opts.showMessage;
    this.showMessageKArgs = opts.showMessageKArgs;
    this.onManage = opts.onManage;
  }
}

export { ExceptionAction, ExceptionActionLevel };
