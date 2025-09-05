import { browser } from "$app/environment";
import { goto } from "$app/navigation";
import { PagesCache } from "$lib/models/cache/pages_cache";
import { User } from "$lib/models/user";
import { writable } from "svelte/store";

/** @type Writable<User> */
const userLogged = writable(User.empty());

/** @type Writable<PagesCache> */
const pagesCache = writable(new PagesCache());

/** @returns NavigatorHistory */
const initNavigatorHistory = () => {
  const saveHistory = () => {
    if (browser) window.sessionStorage.setItem("navigatorHistory", JSON.stringify(history));
    set(history);
  };

  /** @type Array<string> */
  const history = browser ? JSON.parse(window.sessionStorage.getItem("navigatorHistory") ?? "[]") : [];
  const { subscribe, set } = writable(history);

  /**
   * Navigates back and updates the history.
   * @param {string} defaultPath - The default path to navigate to if history is empty.
   * @returns Promise<void> - A promise that resolves once navigation is complete.
   */
  const __goBack = async (defaultPath) => {
    history?.pop();
    /** @type string */
    const goPath = history?.pop() ?? defaultPath;

    saveHistory();
    await goto(goPath);
  };

  return {
    subscribe,
    /**
     * Returns the URL at the specified index in the history.
     * @param {number} i - The index of the URL to retrieve.
     * @returns string - The URL at the specified index.
     */
    at: (i) => history.at(i),
    /**
     * Pushes a new URL to the history and returns the path.
     * @param {URL} url - The URL to push to the history.
     * @returns string - The path of the pushed URL.
     */
    push: (url) => {
      const path = url.href.replace(url.origin, "");
      history.push(path);
      saveHistory();
      return path;
    },
    reset: () => {
      history.splice(0);
      saveHistory();
    },
    /**
     * Navigates back in history and saves the updated history.
     * @param {string} defaultPath - The default path to navigate to if history is empty.
     * @returns Promise<void> - A promise that resolves once navigation is complete.
     */
    goBack: async (defaultPath) => {
      history?.pop();
      const goPath = history?.pop() ?? defaultPath;
      await goto(goPath);
      saveHistory();
    },
    /**
     * Removes the last item from the history and returns it.
     * @returns string - The removed item from the history.
     */
    pop: () => {
      const current = history?.pop();
      saveHistory();
      return current;
    },
    /**
     * Checks if the given URL is the current path in the history.
     * @param {URL} url - The URL to compare with the current path.
     * @returns boolean - True if the URL matches the current path, false otherwise.
     */
    isCurrentPath: (url) => {
      return navigatorHistory.at(-1) === url.href.replace(url.origin, "");
    },
    /**
     * Checks if the given URL is the previous path in the history.
     * @param {URL} url - The URL to compare with the previous path.
     * @returns boolean - True if the URL matches the previous path, false otherwise.
     */
    isPrevPath: (url) => {
      return navigatorHistory.at(-2) === url.href.replace(url.origin, "");
    },
    /**
     * Removes all paths matching the given pattern from the history and navigates back to the default path.
     * @param {string} defaultPath - The default path to navigate to if history is empty.
     * @param {RegExp} pattern - The regular expression pattern to match against the paths to remove.
     * @returns Promise<void> - A promise that resolves once navigation is complete.
     */
    removePatternAndGoBack: async (defaultPath, pattern) => {
      let index = 0;
      while (index < history.length - 1) {
        const value = history.at(index);
        if (!value.match(pattern)) {
          index++;
        } else {
          history.splice(index, 1);
        }
      }
      await __goBack(defaultPath);
    },
  };
};

/** @type {NavigatorHistory} */
const navigatorHistory = initNavigatorHistory();

export { userLogged, pagesCache, navigatorHistory };
