// Deployment-time configuration for the static Web Console.
// Manual overrides win first; otherwise we auto-switch between local and Demo API bases.
const LOCAL_API_BASE = "http://127.0.0.1:8000";
const DEMO_API_BASE = "https://your-cloudflare-api.trycloudflare.com";
const runtimeRoot = typeof window !== "undefined" ? window : globalThis;

function isLocalHostname(hostname) {
  return hostname === "localhost" || hostname === "127.0.0.1";
}

const runtimeHostname = runtimeRoot.location ? runtimeRoot.location.hostname : "";
const manualApiBase =
  typeof runtimeRoot.PERSONAOS_API_BASE === "string" && runtimeRoot.PERSONAOS_API_BASE.trim()
    ? runtimeRoot.PERSONAOS_API_BASE.trim()
    : "";
const autoApiBase = isLocalHostname(runtimeHostname) ? LOCAL_API_BASE : DEMO_API_BASE;
const resolvedApiBase = manualApiBase || autoApiBase;

runtimeRoot.PERSONAOS_CONFIG = Object.assign({}, runtimeRoot.PERSONAOS_CONFIG || {}, {
  apiBase: resolvedApiBase,
  localApiBase: LOCAL_API_BASE,
  demoApiBase: DEMO_API_BASE,
  apiBaseSource: manualApiBase ? "manual" : isLocalHostname(runtimeHostname) ? "auto-local" : "auto-demo",
});
