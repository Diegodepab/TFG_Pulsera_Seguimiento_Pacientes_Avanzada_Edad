import adapter from "@sveltejs/adapter-static";

/** @type {import("@sveltejs/kit").Config} */
const config = {
  kit: {
    adapter: adapter({
      fallback: "index.html",
    }),
    alias: {
      "$components": "src/components/*",
      // "$type": "src/type.js",
    },
  },
};

export default config;
