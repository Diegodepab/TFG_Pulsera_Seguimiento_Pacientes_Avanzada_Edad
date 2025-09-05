import { BaseModel } from "$lib/models/base_model";
import { OauthToken } from "$lib/models/oauth_token";

/**
 * Enum representing types to be granted.
 * @readonly
 * @enum string
 */
const GrantType = {
  PASSWORD: "password",
  REFRESH_TOKEN: "refresh_token",
};

/**
 * Enum representing a Scope type.
 * @readonly
 * @enum string
 */
const ScopeType = {
  FULL: "full",
};

class ApiFields {
  /**
   * @type string
   * @readonly
   */
  grantType = "grant_type";
  /**
   * @type string
   * @readonly
   */
  username = "username";
  /**
   * @type string
   * @readonly
   */
  password = "password";
  /**
   * @type string
   * @readonly
   */
  scope = "scope";
  /**
   * @type string
   * @readonly
   */
  clientId = "client_id";
  /**
   * @type string
   * @readonly
   */
  clientSecret = "client_secret";
  /**
   * @type string
   * @readonly
   */
  refreshToken = "refresh_token";
}

class Oauth extends BaseModel {
  /**
   * @type ApiFields
   * @readonly
   */
  static apiFields = new ApiFields();

  /** @type {GrantType} */
  grantType;

  /** @type {string|undefined} */
  username;

  /** @type {string|undefined} */
  password;

  /** @type {string|null|undefined} */
  refreshToken;

  /** @type {string|null|undefined} */
  scope;

  /** @type {string|null|undefined} */
  clientId;

  /** @type {string|null|undefined} */
  clientSecret;

  /** @type {OauthToken|undefined} */
  token;

  /**
   * Constructs an instance of Oauth.
   * @param {GrantType} grantType - The grant type.
   * @param {Object} opts - Optional parameters.
   * @param {string|undefined} [opts.username] - The username.
   * @param {string|undefined} [opts.password] - The password.
   * @param {string|null|undefined} [opts.refreshToken] - The refresh token.
   * @param {string|null|undefined} [opts.scope] - The scope.
   * @param {string|null|undefined} [opts.clientId] - The client ID.
   * @param {string|null|undefined} [opts.clientSecret] - The client secret.
   */
  constructor(grantType, opts) {
    super();
    this.grantType = grantType;
    this.username = opts?.username;
    this.password = opts?.password;
    this.refreshToken = opts?.refreshToken;
    this.scope = opts?.scope;
    this.clientId = opts?.clientId;
    this.clientSecret = opts?.clientSecret;
  }


  static empty = () => new Oauth(null);

  /**
   * This is a special case, API REST response a different Model <OauthToken>
   * Creates an OAuth instance from JSON data.
   * @param {Json} data - The JSON data.
   * @returns Promise<Oauth> - A promise that resolves to an OAuth instance.
   */
  static fromJson = async (data) => {
    const oauth = Oauth.empty();
    oauth.token = await OauthToken.fromJson(data);
    return oauth;
  };

  /**
   * Transforms JSON data into an instance of a specified type.
   * @template T - The type of the instance to transform to.
   * @param {Json} data - The JSON data to transform.
   * @returns Promise<Oauth> - The transformed instance.
   */
  static transformer = async (data) => await Oauth.fromJson(data);

  /**
   * Converts the OAuth instance to a dictionary representation.
   * @param {toDictModel} [opts] - Optional parameters.
   * @returns Json - The dictionary representation of the OAuth instance.
   */
  toDict = (opts) => {
    /** @type Json */
    const dict = {};

    dict[Oauth.apiFields.grantType] = this.grantType;
    [
      [ Oauth.apiFields.username, this.username ],
      [ Oauth.apiFields.password, this.password ],
      [ Oauth.apiFields.refreshToken, this.refreshToken ],
      [ Oauth.apiFields.scope, this.scope ],
      [ Oauth.apiFields.clientId, this.clientId ],
      [ Oauth.apiFields.clientSecret, this.clientSecret ],
    ].forEach(([ first, second ]) => {
      if (second !== undefined && (second !== null || !opts?.ignoreNullValues)) {
        dict[first] = second;
      }
    });

    return dict;
  };
}

export { Oauth, GrantType, ScopeType };
