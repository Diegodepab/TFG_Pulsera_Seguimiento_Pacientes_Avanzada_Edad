/**
 * @typedef {import("$lib/models/base_model").BaseModel} BaseModel
 */

class ApiFields {
  /**
   * @type string
   * @readonly
   */
  items = "items";
  /**
   * @type string
   * @readonly
   */
  first = "first";
  /**
   * @type string
   * @readonly
   */
  next = "next";
  /**
   * @type string
   * @readonly
   */
  previous = "previous";
}

/**
 * Represents the search results returned from an API call.
 * @template {BaseModel | BaseDC} T - The type of items in the search results.
 */
class SearchResults {
  /**
   *  @type ApiFields
   * @readonly
   */
  static apiFields = new ApiFields();

  /** @type {T[]} */
  items;
  /** @type string */
  first;
  /** @type string */
  next;
  /** @type string */
  previous;

  /**
   * Creates an instance of SearchResults.
   * @param {T[]} items - The items in the search results.
   * @param {string} first - The link to the first page of search results.
   * @param {string} next - The link to the next page of search results.
   * @param {string} previous - The link to the previous page of search results.
   */
  constructor(items, first, next, previous) {
    this.items = items;
    this.first = first;
    this.next = next;
    this.previous = previous;
  }

  /**
   * Creates a SearchResults instance from JSON data.
   * @template {BaseModel | BaseDC} T - The type of items in the search results, extending BaseModel or BaseDC.
   * @param {Json} data - The JSON data representing the search results.
   * @param {ModelTransformer} transformer - The transformer function to convert JSON objects to model objects.
   * @returns Promise<SearchResults<T>> - A promise that resolves to a SearchResults instance.
   */
  static fromJson = async (
    data,
    transformer,
  ) => {
    return new SearchResults(
      await Promise.all(data[SearchResults.apiFields.items].map((item) => transformer(item))),
      data[SearchResults.apiFields.first],
      data[SearchResults.apiFields.next],
      data[SearchResults.apiFields.previous],
    );
  };

  /**
   * Creates an empty SearchResults instance.
   * @template {BaseModel | BaseDC} T - The type of items in the search results, extending BaseModel or BaseDC.
   * @returns SearchResults<T> - An empty SearchResults instance.
   */
  static empty = () => new SearchResults(null, null, null, null);
}

export { SearchResults };
