import { Utils } from "$lib/commons/utils";
import { Oauth } from "$lib/models/oauth";
import { OauthToken } from "$lib/models/oauth_token";
import { ExceptionFetch } from "$lib/services/fetch/exception_fetch";
import { Fetch } from "$lib/services/fetch/fetch";
import { QueryEncoder } from "$lib/services/utils/query_encoder";
import { QueryFields, QueryParamsRaw } from "$lib/services/utils/query_utils";

class OauthFetch extends Fetch {
  /** @type string */
  path = "/oauth";
  /** @type string */
  entity = "oauth";
  /** @type ModelTransformer */
  transformer = Oauth.transformer;

  constructor() {
    super();
  }

  /**
   * Retrieves an OAuth token using the provided data.
   * @param {Json} data - The data used to obtain the OAuth token.
   * @returns Promise<OauthToken> - A promise that resolves to the retrieved OAuth token.
   */
  getToken = async (data) => {
    return await this.post(Utils.jsonToFormUrlEncoded(data), {
      customPath: `${ this.path }/token`,
      transformer: OauthToken.transformer,
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  };

  /**
   * Checks the validity of an OAuth token.
   * @param {string} token - The OAuth token to check.
   * @returns Promise<boolean> - A promise that resolves to a boolean indicating the validity of the token.
   */
  checkToken = async (token) => {
    /** @type {Map<QueryFields, *>} */
    const params = new Map();

    params.set(QueryFields.RAW, [
      new QueryParamsRaw({
        field: "token",
        value: token.trim(),
      }),
    ]);

    return await this.tokenRequest("check", params, "token");
  };

  /**
   * Revokes an OAuth token.
   * @param {string} token - The OAuth token to revoke.
   * @returns Promise<boolean> - A promise that resolves to a boolean indicating the success of the revocation.
   */
  revokeToken = async (token) => {
    return (await this.post({ token }, { customPath: `${ this.path }/revoke` }));
  };

  /**
   * @private
   * Makes a token request to the OAuth server.
   * @param {string} extraPath - Additional path for the token request.
   * @param {Map<QueryFields, unknown>} params - Parameters for the token request.
   * @param {string} entity - The entity associated with the token request.
   * @returns Promise<boolean> - A promise that resolves to a boolean indicating the success of the token request.
   * @throws ExceptionFetch - If the request fails.
   */
  tokenRequest = async (extraPath, params, entity) => {
    /** @type string */
    let _path = `${ this.host }${ this.path }/${ extraPath }`;
    _path = QueryEncoder.encodeQuery({ params, path: _path });

    /** @type Response */
    const response = await fetch(_path, { method: "GET" });

    if (response.status === 204) return true;
    throw await ExceptionFetch.fromResponse(response, { entity });
  };
}

export { OauthFetch };
