import { QueryFields, QueryLogicOperations, QueryParamsQ } from "$lib/services/utils/query_utils";

class QueryEncoder {
  /**
   * Codifica una consulta en una cadena de consulta URL.
   * @param {Object} opts - Opciones para la codificación de la consulta.
   * @param {Map<QueryFields, unknown>} opts.params - Parámetros de la consulta.
   * @param {string} [opts.path] - Ruta opcional para la consulta.
   * @returns string - La cadena de consulta URL codificada.
   */
  static encodeQuery = (opts) => {
    /** @type string */
    let query = "";
    /** @param {string} args */
    const addQueryArgs = (args) => query !== "" ? `${ query }&${ args }` : args;

    if (opts.params.has(QueryFields.Q)) {
      query = addQueryArgs(QueryEncoder._encodeArgsQuery("q", opts.params.get(QueryFields.Q)));
    }

    if (opts.params.has(QueryFields.Q_EXTRA)) {
      query = addQueryArgs(
        opts.params.get(QueryFields.Q_EXTRA)
          .map((qExtra) => QueryEncoder._encodeArgsQuery(`q.${ qExtra.embed }`, qExtra.queryElements))
          .join("&"),
      );
    }

    if (opts.params.has(QueryFields.EMBED)) {
      /** @type string */
      const embedArgs = `embed=${ QueryEncoder._encodeEmbed(opts.params.get(QueryFields.EMBED)) }`;
      query = addQueryArgs(embedArgs);
    }

    if (opts.params.has(QueryFields.FIELDS)) {
      /** @type string */
      const embedArgs = `fields=${ QueryEncoder._encodeFields(opts.params.get(QueryFields.FIELDS)) }`;
      query = addQueryArgs(embedArgs);
    }

    if (opts.params.has(QueryFields.SORT)) {
      /** @type string */
      const sortArgs = `sort_by=${ opts.params.get(QueryFields.SORT)
        .map((sort) => `${ sort.field }:${ sort.sort }`)
        .join(",") }`;
      query = addQueryArgs(sortArgs);
    }

    if (opts.params.has(QueryFields.LIMIT)) {
      /** @type string */
      const limitArgs = `limit=${ opts.params.get(QueryFields.LIMIT) }`;
      query = addQueryArgs(limitArgs);
    }

    if (opts.params.has(QueryFields.RAW)) {
      /** @type string */
      const rawArgs = opts.params.get(QueryFields.RAW)
        .map((raw) => `${ raw.field }=${ raw.value }`)
        .join("&");
      query = addQueryArgs(rawArgs);
    }

    if (opts.params.has(QueryFields.PLAIN)) {
      /** @type import("$lib/services/utils/query_utils").QueryParamsPlain */
      const plainParam = opts.params.get(QueryFields.PLAIN);
      query = plainParam.ignoreOthers ? plainParam.filters : addQueryArgs(plainParam.filters);
    }

    return opts.path != null ? `${ opts.path }${ query != "" ? `?${ query }` : "" }` : query;
  };

  /**
   * Encode Q params to the output used on the query
   * @param {string} arg - Q param field name
   * @param {(QueryParamsQ|QueryLogicOperations)[]} value - Q param field values
   * @returns string - encode Q params
   */
  static _encodeArgsQuery = (arg, value) => {
    let previousTerm;

    return `${ arg }=${ value
      .map((q) => {
        /** @type string */
        let qTerm;
        if ([ QueryLogicOperations.AND, QueryLogicOperations.OR ].some((op) => op === q)) {
          qTerm = q.toString();
        } else {
          /** @type string */
          const qTermValue = `${ q.field }.${ q.operation }:${ QueryEncoder._encodeValue(q.value) }`;
          qTerm = previousTerm != null && previousTerm instanceof QueryParamsQ ? `AND ${ qTermValue }` : qTermValue;
        }

        previousTerm = q;

        return qTerm;
      })
      .join(" ") }`;
  };

  /**
   * Encodes a value to a string representation.
   * @param {unknown} value - The value to encode.
   * @returns string - The encoded value as a string.
   */
  static _encodeValue = (value) => {
    if (typeof value === "number") {
      return value.toString();
    }

    if (value instanceof Array) {
      return `'${ value.join(",") }'`;
    }

    return `'${ value }'`;
  };

  /**
   * Encodes an embed object to a string representation.
   * @param {import("$lib/services/utils/query_utils").QueryParamsEmbed} embed - The embed object to encode.
   * @returns string - The encoded embed as a string.
   */
  static _encodeEmbed = (embed) => {
    return embed.embeds
      .map((e) => {
        if (typeof e === "string") return e;
        return `${ e.parent }(${ QueryEncoder._encodeEmbed(e) })`;
      })
      .join(",");
  };

  /**
   * Encodes fields to a string representation.
   * @param {import("$lib/services/utils/query_utils").QueryParamsFields} embed - The fields object to encode.
   * @returns string - The encoded fields as a string.
   */
  static _encodeFields = (embed) => {
    return embed.fields
      .map((e) => {
        if (typeof e === "string") return e;
        return `${ e.embed }(${ QueryEncoder._encodeFields(e) })`;
      })
      .join(",");
  };
}

export { QueryEncoder };
