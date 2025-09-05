/** @abstract */
class GeneralActions {
  /**
   * @param {HTMLElement} node - DOM node which receives the element.
   * @return {{ destroy(): void }} - An object with a destroy method to remove the event listener.
   * TODO. Check this works as expected.
   */
  static outClick = (node) => {
    const handleClick = (event) => {
      if (node && !node.contains(event.target) && !event.defaultPrevented) {
        node.dispatchEvent(new CustomEvent("outclick", node));
      }
    };

    document.addEventListener("click", handleClick, true);

    return {
      destroy() {
        document.removeEventListener("click", handleClick, true);
      },
    };
  };

  /**
   * @param {HTMLElement} node - DOM node which receives the element.
   * @return {{ destroy(): void }} - An object with a destroy method to remove the event listener.
   */
  static toggleDropdownMenu = (node) => {
    /** @type {(event: Event) => void} */
    const handleClick = (event) => {
      if (node && !node.contains(event.target)) {
        node.dispatchEvent(new CustomEvent("outclick", node));
      }
    };

    document.addEventListener("click", handleClick, true);

    return {
      destroy() {
        document.removeEventListener("click", handleClick, true);
      },
    };
  };

  /**
   * Adds an event listener to handle clicks outside the modal.
   * @param {HTMLElement} node - DOM node which receives the element.
   * @param {Record<string, *>} [opts] - Options for handling clicks outside the modal.
   * @param {boolean} [opts.ignore] - If true, ignore the click event.
   * @return {{ destroy(): void }} - An object with a destroy method to remove the event listener.
   */
  static outModalClick = (node, opts) => {
    /** @type {(event: Event) => void} */
    const handleClick = (event) => {
      if (node && !node.querySelector(".modal-content")?.contains(event.target) && !event.defaultPrevented) {
        node.dispatchEvent(new CustomEvent("outclick", node));
      }
    };

    /** @type {(event: KeyboardEvent) => void} */
    const handleKeyDown = (event) => {
      if (event.code === "Escape") {
        node.dispatchEvent(new CustomEvent("keydown-esc", node));
      }
    };

    if (!opts?.ignore) {
      document.addEventListener("click", handleClick, true);
      document.addEventListener("keydown", handleKeyDown, true);
    }

    return {
      destroy() {
        if (!opts?.ignore) {
          document.removeEventListener("click", handleClick, true);
          document.removeEventListener("keydown", handleKeyDown, true);
        }
      },
    };
  };
}

export { GeneralActions };