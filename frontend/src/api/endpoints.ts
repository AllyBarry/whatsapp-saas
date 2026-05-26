/**
 * API barrel — switches between the real backend and the mock layer based on
 * the `VITE_DEMO_MODE` build-time flag. Page components keep importing from
 * `@/api/endpoints` regardless of which mode the bundle was built for.
 *
 * Vite statically replaces `import.meta.env.VITE_DEMO_MODE` at build time, so
 * the unused side is tree-shaken out — neither bundle ships dead code from the
 * other.
 */
import * as real from "./real";
import * as mock from "./mock";

export const isDemoMode = import.meta.env.VITE_DEMO_MODE === "true";

const impl = isDemoMode ? mock : real;

export const authApi = impl.authApi;
export const tenantApi = impl.tenantApi;
export const credentialApi = impl.credentialApi;
export const numberApi = impl.numberApi;
export const templateApi = impl.templateApi;
export const messageApi = impl.messageApi;
export const conversationApi = impl.conversationApi;

// Exposed for the "Reset demo data" affordance in the demo banner.
export const resetDemoState = mock.resetDemoState;
