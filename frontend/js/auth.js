function decodeTokenPayload(token) {
  const parts = token.split(".");
  if (parts.length !== 3) throw new Error("JWT không hợp lệ");

  const base64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
  const padded = base64.padEnd(Math.ceil(base64.length / 4) * 4, "=");
  const bytes = Uint8Array.from(atob(padded), (character) => character.charCodeAt(0));
  return JSON.parse(new TextDecoder().decode(bytes));
}

function getTokenRoles(payload) {
  const realmRoles = payload.realm_access && payload.realm_access.roles;
  const claim = payload.roles ?? payload.role ?? realmRoles;
  const roles = Array.isArray(claim) ? claim : [claim];
  return new Set(roles
    .filter((role) => typeof role === "string")
    .map((role) => role.trim().toLowerCase())
    .filter(Boolean));
}

function getAuthSession() {
  const token = localStorage.getItem(CONFIG.AUTH_TOKEN_KEY);
  if (!token) return { status: "anonymous", token: null, payload: null };

  try {
    const payload = decodeTokenPayload(token);
    const expiresAt = payload.exp === undefined ? null : Number(payload.exp);
    if (expiresAt !== null && (!Number.isFinite(expiresAt) || expiresAt <= Date.now() / 1000)) {
      localStorage.removeItem(CONFIG.AUTH_TOKEN_KEY);
      return { status: "expired", token: null, payload: null };
    }
    return { status: "authenticated", token, payload };
  } catch {
    localStorage.removeItem(CONFIG.AUTH_TOKEN_KEY);
    return { status: "invalid", token: null, payload: null };
  }
}

function hasAnyRole(allowedRoles, payload) {
  const user = payload || getAuthSession().payload;
  if (!user) return false;
  const roles = getTokenRoles(user);
  return allowedRoles.some((role) => roles.has(role.toLowerCase()));
}

function requireAnyRole(allowedRoles) {
  const session = getAuthSession();
  if (session.status !== "authenticated" || !hasAnyRole(allowedRoles, session.payload)) {
    const reason = session.status === "authenticated" ? "forbidden" : session.status;
    const root = document.body.dataset.root || "./";
    window.location.replace(`${root}index.html?auth=${encodeURIComponent(reason)}`);
    return false;
  }
  return true;
}

const AUTH = {
  getSession: getAuthSession,
  hasAnyRole,
  requireAnyRole,
  setToken(token) {
    if (typeof token !== "string" || !token) {
      throw new Error("Backend không trả về access token hợp lệ.");
    }
    localStorage.setItem(CONFIG.AUTH_TOKEN_KEY, token);
    const session = getAuthSession();
    if (session.status !== "authenticated") {
      localStorage.removeItem(CONFIG.AUTH_TOKEN_KEY);
      throw new Error("Access token không hợp lệ hoặc đã hết hạn.");
    }
    return session;
  },
  logout() {
    localStorage.removeItem(CONFIG.AUTH_TOKEN_KEY);
    const root = document.body.dataset.root || "./";
    window.location.replace(`${root}index.html`);
  },
};
