import { ExceptionActionLevel } from "$lib/exceptions/exception_action";
import Hashids from "hashids";
import moment from "moment";
import { v4 as uuidv4, v5 as uuidv5 } from "uuid";

/**
 * @typedef {import("@sentry/browser").SeverityLevel} SeverityLevel
 * @typedef {import("hashids/cjs/util").NumberLike} NumberLike
 */

/**
 * @typedef {Object} ValueUnit
 * @property {number} value - The numeric value
 * @property string [unit] - The unit of measurement
 */

class Debounce {
  /**
   * The delay in milliseconds for to debounce.
   * @type number
   * @readonly
   * @private
   */
  delay;

  /**
   * The timer for to debounce.
   * @type {ReturnType<typeof setTimeout>}
   * @private
   */
  timer;

  /**
   * Creates an instance of Debounce.
   * @param {number} delay - The delay in milliseconds for to debounce.
   */
  constructor(delay) {
    this.delay = delay;
  }

  /**
   * Debounce a callback function.
   * @param {(...args: unknown[]) => void} callback - The callback function to debounce.
   * @returns void
   */
  debounce(callback) {
    clearTimeout(this.timer);
    this.timer = setTimeout(callback, this.delay);
  }

  /**
   * Cancels the debounced timer.
   * @returns void
   */
  cancel() {
    clearTimeout(this.timer);
  };
}

/**
 * Utility class providing common helper functions for full-screen
 * @abstract
 */
class FullScreenUtils {
  /**
   * Indicates if the fullscreen it is supported by the device
   * @return boolean
   */
  static isSupported = () => {
    return "fullscreenEnabled" in document
      || "mozFullScreenEnabled" in document
      || "webkitFullscreenEnabled" in document
      || "msFullscreenEnabled" in document;
  };

  /**
   * Indicates if exists some element using fullscreen
   * @returns boolean
   */
  static isSomethingInFullScreen = () => {
    return ("fullscreenElement" in document && document.fullscreenElement)
      || ("mozFullScreenElement" in document && document.mozFullScreenElement)
      || ("webkitFullscreenElement" in document && document.webkitFullscreenElement)
      || ("msFullscreenElement" in document && document.msFullscreenElement);
  };

  /**
   * Request fullscreen in the given element.
   * @param {HTMLElement} [element = document]
   * @returns Promise<boolean>
   */
  static async setFullScreen({ element } = {}) {
    if (!this.isSupported()) return false;

    const el = element ?? document.documentElement;

    try {
      if ("requestFullscreen" in el) await el.requestFullscreen();
      else if ("webkitRequestFullscreen" in el) el.webkitRequestFullscreen();
      else if ("msRequestFullscreen" in el) el.msRequestFullscreen();
      else return false;

    } catch (e) {
      console.warn("Could not request fullscreen", e);
      return false;
    }

    return true;
  };

  /**
   * Remove fullscreen for a given element.
   * @returns Promise<void>
   */
  static exitFullScreen = async () => {
    if (!this.isSomethingInFullScreen()) return;

    // TODO. Search which is the 'exitFullScreen' prop from 'moz' (if exists)
    if ("exitFullscreen" in document) {
      await document.exitFullscreen();
    } else if ("webkitExitFullscreen" in document) {
      await document.webkitExitFullscreen();
    } else if ("msExitFullscreen" in document) {
      await document.msExitFullscreen();
    }
  };
}

/**
 * Enum representing comparison operators for dates.
 * @readonly
 * @enum string
 */
const DateComparison = {
  EQ: "eq",
  LT: "lt",
  LEQ: "leg",
  GT: "gt",
  GEQ: "get",
  BTW: "btw",
};

const HASHIDS_SALT = "Cry Chicken";

/**
 * Utility class providing various helper functions.
 * @abstract
 */
class Utils {
  static deepCopy = (arg) => JSON.parse(JSON.stringify(arg ?? {}));

  /**
   * Logs messages to the console based on the specified log level.
   * @param {"log" | "info" | "warn" | "error"} level - The log level.
   * @param {...unknown} params - The parameters to log.
   * @returns void
   */
  static logging = (level, ...params) => {
    if (level === "error") return console.error(...params);
    if (window["__PLATFORM_DEV_MODE"]) return console[level](...params);
  };

  /**
   * Encodes numbers or strings into a hashid.
   * @param {NumberLike[] | string[] | string} numbers - The numbers or strings to encode.
   * @returns string - The encoded hashid.
   */
  static hashIdEncode = (numbers) => {
    const hashids = new Hashids(HASHIDS_SALT);
    return hashids.encode(numbers);
  };

  /**
   * Decodes a hashid into numbers.
   * @param {string} hash - The hashid to decode.
   * @returns NumberLike[] - The decoded numbers.
   */
  static hashIdDecode = (hash) => {
    const hashids = new Hashids(HASHIDS_SALT);
    return hashids.decode(hash);
  };

  /**
   * Converts a JSON object to a URL-encoded form string.
   * @param {Json} data - The JSON object to convert.
   * @returns string - The URL-encoded form string.
   */
  static jsonToFormUrlEncoded = (data) => {
    return Object.entries(data)
      .map(([ key, value ]) => `${ encodeURIComponent(key) }=${ encodeURIComponent(value.toString()) }`)
      ?.join("&");
  };

  /**
   * Checks if an object is empty or null.
   * @param {any} obj - The object to check.
   * @returns boolean - True if the object is empty or null, otherwise false.
   */
  static isEmptyOrNullObject = (obj) => {
    return Object.keys(obj ?? {}).length === 0;
  };

  /**
   * Converts an empty string to null.
   * @param {string} value - The string value to convert.
   * @returns string - The input value if not empty, otherwise null.
   */
    // BaseInput bind values with '' per default, so optional fields always are sent as '' and not null
  static emptyToNull = (value) => {
    return value === "" ? null : value;
  };

  /**
   * Converts an ExceptionActionLevel to a SeverityLevel compatible with Sentry.
   * @param {ExceptionActionLevel} level - The ExceptionActionLevel to convert.
   * @returns SeverityLevel - The converted SeverityLevel.
   */
  static exceptionLevelToSentrySeverity = (level) => {
    switch (level) {
      case ExceptionActionLevel.DEBUG:
        return "debug";

      case ExceptionActionLevel.INFO:
        return "info";

      case ExceptionActionLevel.WARNING:
        return "warning";

      case ExceptionActionLevel.FATAL:
        return "fatal";

      case ExceptionActionLevel.ERROR:
        return "error";
    }
  };
}

/**
 * Utility class providing common helper functions
 * @abstract
 */
/** @abstract */
class DateUtils {
  /**
   * Converts a Moment to a UTC ISO string or null
   * @param {moment.Moment|null} value - Moment to convert
   * @return {string|null} UTC ISO string or null
   */
  static utcTimestampOrNull(value) {
    // null-safety ? into dates matches null as undefined, so some dates as 'disableTs' are not sent correctly
    return value === null ? null : value?.utc()?.toISOString(true);
  };

  /**
   * Converts a boolean value to a Moment object
   * @param {boolean} value - Boolean value to convert
   * @return {moment.Moment|null} Current moment if true, null if false
   */
  static booleanToMoment(value) {
    return value ? moment() : null;
  };

  /**
   * Converts a value to a Moment object
   * @param {moment.MomentInput} [value] - Value to convert
   * @return {moment.Moment|null} Moment object or null if value is falsy
   */
  static momentOrNull(value) {
    return value ? moment(value) : null;
  };

  /**
   * Compares two moment objects based on a comparison operator
   * @param {moment.Moment|null} date1 - First date
   * @param {moment.Moment|null} date2 - Second date
   * @param {DateComparison} comparison - Comparison type
   * @param {Object} [opts] - Comparison options
   * @param {moment.unitOfTime.StartOf|undefined} [opts.granularity] - Limit granularity to compare
   * @return {boolean} Result of the comparison
   */
  static compare(date1, date2, comparison, opts) {
    const granularity = opts?.granularity;
    switch (comparison) {
      case DateComparison.EQ:
        return date1?.isSame(date2, granularity);

      case DateComparison.LT:
        return date1?.isBefore(date2, granularity);

      case DateComparison.LEQ:
        return date1?.isSameOrBefore(date2, granularity);

      case DateComparison.GT:
        return date1?.isAfter(date2, granularity);

      case DateComparison.GEQ:
        return date1?.isSameOrAfter(date2, granularity);

      case DateComparison.BTW:
        return moment().isBetween(date1, date2, granularity);

      default:
        return false;
    }
  };

  /**
   * Format moment object to a date string
   * @param {moment.MomentInput} value - Value to convert
   * @param {Object} [opts] - Value to convert
   * @param {string} [opts.format="DD-MM-YYYY"] - Formatter format. Defaults to "DD-MM-YYYY"
   * @return {string | null} - formatted date
   */
  static toDate(value, { format } = {}) {
    if (!value) return null;

    // The better format for this is "LL", but 'moment' cannot determine the browser locale correctly.
    // For this reason, the default format is 'DD-MM-YYYY'
    return value.format(format ?? "DD-MM-YYYY");
  };

  /**
   * Format moment object to a time string
   * @param {moment.MomentInput} value - Value to convert
   * @param {Object} [opts] - Value to convert
   * @param {string} [opts.format="HH:mm:ss"] - Formatter format. Defaults to "HH:mm:ss", which give time in
   * 24h format.
   * @param {string} [opts.locale] - Locale to format the time. If it's not provided, use the 'svelte-i18n' own locale.
   * @return {string|null} - formatted time
   */
  static toTime(value, { format, locale } = {}) {
    if (!value) return null;
    return value.format(format ?? "HH:mm:ss");
  };
}

class RegExpUtils {
  /** Regex for HTML class names */
  static htmlClassRegExp = RegExp(/^[a-zA-Z\d-]+$/);
  /** Regex for validating HTML elements IDs */
  static idHTMLElementRegExp = RegExp(/^[a-zA-Z]{1}[a-zA-Z\d]*$/);
  /** Regex for validating email addresses */
  static emailRegExp = RegExp(
    /^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/,
  );

  /**
   * @param {*} value
   * @param {RegExp} regExp
   * @return boolean
   */
  static isValid(value, regExp) {
    if (!value) return false;
    return !!value.match(regExp);
  };
}

/**
 * Validation utilities for form inputs
 * @abstract
 */
class InputValidators {
  /**
   * Validates if a value is empty or not
   * @param {string} value - value to validate
   * @returns boolean - Whether the value is empty or not
   */
  static isEmpty(value) {
    return value == null || (typeof value != "number" && (value.length ?? Object.keys(value).length) === 0);
  };

  /**
   * Validates that a value is not empty
   * @param {*} value - Value to check
   * @param {Function} t - Translation function
   * @param {Object} tArgs - Translation arguments
   * @return {string|undefined} Error message or undefined if valid
   */
  static validateRequired(value, t, tArgs) {
    if (!InputValidators.isEmpty(value)) return;
    return t("common.form.field.required", tArgs);
  };

  /**
   * Validates if a value is a valid date
   * @param {string} value - value to validate
   * @returns boolean - Whether the value is a valid date or not
   */
  static isDate(value) {
    if (!value) return false;
    return moment(value)?.isValid() ?? false;
  };

  /**
   * Validates that a date is valid
   * @param {*} value - Value to check
   * @param {Function} t - Translation function
   * @param {Object} [tArgs] - Translation arguments
   * @return {string|undefined} Error message or undefined if valid
   */
  static validateDate(value, t, { tArgs } = {}) {
    if (!value) return;
    if (InputValidators.isDate(value)) return;

    if (!tArgs) return t("common.form.field.bad-format.base");
    return t("common.form.field.bad-format.specific", { values: { ...tArgs } });
  };

  /**
   * Validates if the date is not later than today.
   * @param {moment.Moment} value - Value to check
   * @param {*} t - The translation function.
   * @param {Object} [opts] - Optional parameters.
   * @param {boolean} [opts.strict=false] - Whether to perform strict comparison. Defaults to false.
   * @param {string} [opts.granularity="d"] - unit of time to compare. Default "d" - "day"
   * @return {string|undefined} - A message indicating if the date is not valid because it is older than today.
   */
  static validateNotFutureDate(value, t, { strict, granularity } = {}) {
    if (!value) return;
    strict ??= false;
    granularity ??= "d";
    if (!DateUtils.compare(value, moment(), strict ? DateComparison.GEQ : DateComparison.GT, { granularity })) return;

    return t("common.form.date-not-future");
  };

  /**
   * Validates if the interval between two moments is valid.
   * @param {moment.Moment} start - The start moment of the interval.
   * @param {moment.Moment} end - The end moment of the interval.
   * @param {*} t - The translation function.
   * @param {*} tArgs - Arguments for the translation function.
   * @param {Object} [opts] - Optional parameters.
   * @param {boolean} [opts.strict] - Whether to perform strict comparison.
   * @param {string} [opts.granularity="m"] - unit of time to compare. Default "m" - "minute"
   * @return {string|undefined} - A message indicating an invalid interval if the interval is not valid, otherwise null.
   */
  static validIntervalDate(start, end, t, tArgs, opts) {
    if (!start || !end) return;
    if (DateUtils.compare(start, end, opts?.strict ? DateComparison.GEQ : DateComparison.GT, {
      granularity: opts?.granularity ?? "m",
    })) {
      return t("common.form.finish-before-start", tArgs);
    }
  };

  /**
   * Validates if a value is a valid email address
   * @param {string} value - value to validate
   * @returns boolean - Whether the value is a valid email address or not
   */
  static isEmail(value) {
    return RegExpUtils.isValid(value, RegExpUtils.emailRegExp);
  };

  /**
   * Validates an email address
   * @param {string} value - Email to validate
   * @param {Function} t - Translation function
   * @param {Object} [tArgs] - Translation arguments
   * @return {string|undefined} Error message or undefined if valid
   */
  static validateEmail(value, t, { tArgs } = {}) {
    if (InputValidators.isEmail(value)) return;

    if (!tArgs) return t("common.form.field.bad-format.base");
    return t("common.form.field.bad-format.specific", { values: { ...tArgs } });
  };

  /**
   * Validates if a value is a valid URL
   * @param {string} value - value to validate
   * @returns boolean - Whether the value is a valid URL or not
   */
  static isURL(value) {
    try {
      new URL(value);
      return true;
    } catch (e) {
      return false;
    }
  };

  /**
   * Validates a URL
   * @param {string} value - URL to validate
   * @param {Function} t - Translation function
   * @param {Object} tArgs - Translation arguments
   * @return {string|undefined} - Error message or undefined if valid
   */
  static validateURL(value, t, tArgs) {
    try {
      new URL(value);
    } catch (e) {
      return t("component.form.url", tArgs);
    }
  };
}

/** @abstract */
class Transformations {
  static decimalUnitRegExp = RegExp(/^(?<value>\d+(.\d+)?)(?<unit>([a-zA-Z]+|%))?$/);

  /**
   * Parses a value with optional unit information.
   * @param {*} value - The value to parse.
   * @param {Object} [opts] - Optional parameters.
   * @param {number} [opts.dftValue] - Default value if parsing fails.
   * @param {string} [opts.dftUnit] - Default unit if parsing fails.
   * @returns {{value: number, unit: string}} - An object containing the parsed value and unit.
   */
  static valuePerUnit(value, opts) {
    /** @type RegExpMatchArray */
    const match = value.match(Transformations.decimalUnitRegExp);

    return {
      value: Number(match?.groups?.value ?? opts?.dftValue ?? "0"),
      unit: match?.groups?.unit ?? opts?.dftUnit,
    };
  };
}

/** @abstract */
class UniqueUser {
  /**
   * UUID namespace for unique user identifiers
   * @type string
   * @constant
   * @private
   */
  static __UNQ_U_SPACE = "925f92da-0e80-11ed-861d-0242ac120002";

  /**
   * Generates a unique identifier based on user alias, room ID, and event ID.
   * @param {Object} opts - Options for generating the unique identifier.
   * @param {string} opts.userAlias - The user alias.
   * @param {number} opts.roomId - The room ID.
   * @param {string} [opts.eventId] - The event ID (optional).
   * @returns string - The generated unique identifier.
   */
  static getId(opts) {
    const baseValue = `${ opts.userAlias }-${ opts.eventId ? opts.eventId : opts.roomId }`;
    const key = `__unq_u${ uuidv5(baseValue, this.__UNQ_U_SPACE) }`;

    const decodedCookie = decodeURIComponent(document.cookie);
    /** @type string */
    const ca = decodedCookie.split(";").find((ca) => ca.includes(key));

    /** @type string */
    const uniqueID = (ca != null ? ca.split(`${ key }=`)?.at(1) : null) || uuidv4();

    const cExpire = moment().add(2, "hours");
    document.cookie = `${ key }=${ uniqueID }; expires=${ cExpire }; path=/;`;

    return uniqueID;
  };
}

export {
  Utils,
  Debounce,
  InputValidators,
  Transformations,
  UniqueUser,
  DateComparison,
  DateUtils,
  FullScreenUtils,
};
