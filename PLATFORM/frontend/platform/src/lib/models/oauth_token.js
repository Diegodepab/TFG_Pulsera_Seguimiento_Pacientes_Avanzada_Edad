import { BaseModel } from "$lib/models/base_model";
import atob from "atob";

/**
 * Represents the data contained in a JSON Web Token (JWT).
 * @typedef {Object} JWTData
 * @property {number} sub - The subject of the JWT.
 * @property {string} iss - The issuer of the JWT.
 * @property {number} exp - The expiration time of the JWT.
 * @property {string} [role] - The role associated with the JWT.
 * @property {Record<string, unknown>} - Additional custom claims in the JWT.
 */

class ApiFields {
  /**
   * @type string
   * @readonly
   */
  accessToken = "access_token";
  /**
   * @type string
   * @readonly
   */
  refreshToken = "refresh_token";
  /**
   * @type string
   * @readonly
   */
  tokenType = "token_type";
  /**
   * @type string
   * @readonly
   */
  expiresIn = "expires_in";
}

class OauthToken extends BaseModel {
  /**
   * @type ApiFields
   * @readonly
   */
  static apiFields = new ApiFields();

  /** @type string */
  accessToken;

  /** @type string */
  refreshToken;

  /** @type string */
  tokenType;

  /** @type number */
  expiresIn;

  /** @type {JWTData|undefined} @private */
  _data;

  /**
   * Constructs an OauthToken instance.
   * @param {string} accessToken - The access token.
   * @param {string} refreshToken - The refresh token.
   * @param {string} tokenType - The token type.
   * @param {number} expiresIn - The expiration time of the token (in seconds).
   */
  constructor(accessToken, refreshToken, tokenType, expiresIn) {
    super();
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    this.tokenType = tokenType;
    this.expiresIn = expiresIn;
    this._data = this.getData();
  }

  /** @returns number */
  get userId() {
    return this._data?.sub;
  }

  /** @returns string */
  get userRole() {
    return this._data?.role;
  }

  /** @returns number */
  get tokenExpirationDate() {
    return this._data?.exp;
  }

  /**
   * Creates an OauthToken instance from JSON data.
   * @param {Json} data - The JSON data representing the OAuth token.
   * @returns Promise<OauthToken> - A promise that resolves to an OauthToken instance.
   */
  static fromJson = async (data) => {
    if (Object.keys(data).length === 0) return null;

    return new OauthToken(
      data[OauthToken.apiFields.accessToken],
      data[OauthToken.apiFields.refreshToken],
      data[OauthToken.apiFields.tokenType],
      data[OauthToken.apiFields.expiresIn],
    );
  };

  /**
   * Transforms JSON data into an instance of a specified type.
   * @template T - The type of the instance to transform to.
   * @param {Json} data - The JSON data to transform.
   * @returns Promise<OauthToken> - The transformed instance.
   */
  static transformer = async (data) => await OauthToken.fromJson(data);

  /** @returns Json */
  toDict = (_) => {
    /** @type Json */
    const dict = {};

    dict[OauthToken.apiFields.accessToken] = this.accessToken;
    dict[OauthToken.apiFields.refreshToken] = this.refreshToken;
    dict[OauthToken.apiFields.tokenType] = this.tokenType;
    dict[OauthToken.apiFields.expiresIn] = this.expiresIn;

    return dict;
  };

  /** @returns JWTData */
  getData = () => {
    /** @type string */
    const base64Url = this.accessToken.split(".").at(1);
    /** @type string */
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    /** @type string */
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join(""),
    );

    return JSON.parse(jsonPayload);
  };

  /** @returns Json */
  getHeader = () => {
    return { Authorization: `Bearer ${ this.accessToken }` };
  };
}

export { OauthToken };
