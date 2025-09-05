/**
 *  Fields supported on API REST queries
 *  @type {QueryFields.Q} query to apply to model's attributes on API REST endpoint, its take a list
 *  of @type {QueryParamsQ} objects. This field is parsed and sent to the endpoint as an url
 *  parameter, i.e.: ?q=attribute.COM_OP:value where COM_OP is a value of [QueryComparativeOperations]
 */

/**
 * Enum representing query fields.
 * @readonly
 * @enum string
 */
const QueryFields = {
  Q: "Q",
  Q_EXTRA: "Q_EXTRA",
  EMBED: "EMBED",
  FIELDS: "FIELDS",
  SORT: "SORT",
  LIMIT: "LIMIT",
  RAW: "RAW",
  PLAIN: "PLAIN",
};

/**
 * Enum representing comparative operations in queries.
 * @readonly
 * @enum string
 */
const QueryComparativeOperations = {
  EQ: "EQ",
  NE: "NE",
  GT: "GT",
  GE: "GE",
  LT: "LT",
  LE: "LE",
  IN: "IN",
  NIN: "NIN",
  BEG: "BEG",
  CON: "CON",
  END: "END",
};

/**
 * Enum representing logical operations in queries.
 * @readonly
 * @enum string
 */
const QueryLogicOperations = {
  AND: "AND",
  OR: "OR",
};


/**
 * Enum representing sorting orders in queries.
 * @readonly
 * @enum string
 */
const QuerySortOrder = {
  ASC: "ASC",
  DESC: "DESC",
};


class QueryParamsSort {
  /**
   * Creates an instance of QueryParamsSort.
   * @param {Object} opts - Options for sorting.
   * @param {string} opts.field - The field to sort by.
   * @param {QuerySortOrder} [opts.sort=ASC] - The sorting order.
   */
  constructor(opts) {
    this.field = opts.field;
    this.sort = opts.sort ?? QuerySortOrder.ASC;
  }
}

class QueryParamsFields {
  /**
   * Creates an instance of QueryParamsFields.
   * @param {Object} opts - Options for fields.
   * @param {string} [opts.embed] - The embedded field.
   * @param {(string | QueryParamsFields)[]} opts.fields - The fields to include.
   */
  constructor(opts) {
    this.embed = opts.embed;
    this.fields = opts.fields;
  }
}


class QueryParamsRaw {
  /**
   * Creates an instance of QueryParamsRaw.
   * @param {Object} opts - Options for raw query parameters.
   * @param {string} opts.field - The field name.
   * @param {string} opts.value - The raw value.
   */
  constructor(opts) {
    this.field = opts.field;
    this.value = opts.value;
  }
}

class QueryParamsQExtra {
  /**
   * Creates an instance of QueryParamsQExtra.
   * @param {Object} opts - Options for extra query parameters.
   * @param {string} opts.embed - The embedded field.
   * @param {QueryParamsQ[]} opts.queryElements - The query elements.
   */
  constructor(opts) {
    this.embed = opts.embed;
    this.queryElements = opts.queryElements;
  }
}

class QueryParamsEmbed {
  /**
   * Creates an instance of QueryParamsEmbed.
   * @param {Object} opts - Options for embed query parameters.
   * @param {string} [opts.parent] - The parent field.
   * @param {(string | QueryParamsEmbed)[]} opts.embeds - The embedded fields.
   */
  constructor(opts) {
    this.embeds = opts.embeds;
    this.parent = opts.parent;
  }
}

class QueryParamsPlain {
  /**
   * Creates an instance of QueryParamsPlain.
   * @param {Object} opts - Options for plain query parameters.
   * @param {string} opts.filters - The filters.
   * @param {boolean} opts.ignoreOthers - Whether to ignore other parameters.
   */
  constructor(opts) {
    this.filters = opts.filters;
    this.ignoreOthers = opts.ignoreOthers;
  }
}

class QueryParamsQ {

  /**
   * Creates an instance of QueryParamsQ.
   * @param {Object} opts - Options for query parameters.
   * @param {string} opts.field - The field name.
   * @param {QueryComparativeOperations} opts.operation - The comparative operation.
   * @param {unknown} opts.value - The value.
   */
  constructor(opts) {
    this.field = opts.field;
    this.operation = opts.operation;
    this.value = opts.value;
  }
}

export {
  QueryParamsSort,
  QueryParamsFields,
  QueryParamsRaw,
  QueryParamsQExtra,
  QueryParamsEmbed,
  QueryParamsPlain,
  QueryParamsQ,
  QueryFields,
  QueryComparativeOperations,
  QueryLogicOperations,
  QuerySortOrder,
};
