import type { ParamMatcher } from '@sveltejs/kit';

export const match = ((param) => {
  return /^\d+$|^any$/.test(param);
}) satisfies ParamMatcher;
