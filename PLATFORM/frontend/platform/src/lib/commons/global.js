class _Global {

  /**
   * @private
   * @type string
   */
  _apiVersion;

  /**
   * @private
   * @type string
   */
  _wsPath;

  /**
   * @private
   * @type URL
   */
  _host;

  /** @returns URL */
  get host() {
    return this._host;
  }

  /**
   * @private
   * @type string
   */
  _apiUrl;

  /** @returns string */
  get apiUrl() {
    return this._apiUrl;
  }

  /**
   * @private
   * @type string
   */
  _sentryDSN;

  /** @returns string */
  get sentryDSN() {
    return this._sentryDSN;
  }

  /**
   * @private
   * @type string
   */
  _wsUrl;

  /** @returns string */
  get wsUrl() {
    return this._wsUrl;
  }

  /**
   * @private
   * @type string
   */
  _wsOrigin;

  /** @returns string */
  get wsOrigin() {
    return this._wsOrigin;
  }

  /**
   * @private
   * @type string
   */
  _signalingWsPrePath;

  /** @returns string */
  get signalingWsPrePath() {
    return this._signalingWsPrePath;
  }

  /**
   * @private
   * @type {NotificationContext}
   */
  _notificationContext;

  /** @returns NotificationContext */
  get notificationContext() {
    return this._notificationContext;
  }

  /** @param {NotificationContext} value */
  set notificationContext(value) {
    this._notificationContext = value;
  }

  /**
   * Initializes global configuration settings.
   * @param {Object} opts - Options for initialization.
   * @param {URL} opts.host - The host URL.
   * @param {string} opts.apiVersion - The API version.
   * @param {string} opts.wsPath - The WebSocket path.
   * @param {string} [opts.signalingWsPrePath] - The signaling WebSocket pre-path (optional).
   * @param {string} [opts.apiPort] - The API port (optional).
   * @param {string} [opts.sentryDSN] - The Sentry DSN (optional).
   * @returns void
   */
  init(opts) {
    this._host = opts.host;

    let apiOrigin = `${ opts.host.protocol }//${ opts.host.hostname }`;
    opts.apiPort ??= opts.host.port;

    if (opts.apiPort != null) apiOrigin += `:${ opts.apiPort }`;

    this._apiVersion = opts.apiVersion;
    this._apiUrl = `${ apiOrigin }${ this._apiVersion }`;

    this._wsPath = opts.wsPath;
    this._wsOrigin = apiOrigin.replace("http", "ws");
    this._wsUrl = `${ this._wsOrigin }${ this._apiVersion }${ this._wsPath }`;

    this._signalingWsPrePath = opts.signalingWsPrePath;

    this._sentryDSN = opts.sentryDSN ?? "https://ea55f3d4524e495bbf9b1d44cd906dbb@o435580.ingest.sentry.io/6106466";
  }
}

export const Global = new _Global();
