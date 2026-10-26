/**
 * Sessions and one-time codes.
 *
 * Sessions are self-signed JWTs (HS256) — no third-party identity provider,
 * no vendor lock-in. The same secret signs sessions and hashes sign-in codes.
 * Implemented on node:crypto so the deploy ships with zero npm dependencies.
 */

import crypto from 'node:crypto';

const SECRET = process.env.SESSION_SECRET || 'dev-secret-change-me';
const THIRTY_DAYS = 60 * 60 * 24 * 30;

const b64url = (input) => Buffer.from(input).toString('base64url');
const b64urlJson = (obj) => b64url(JSON.stringify(obj));

export function signSession(payload, ttlSeconds = THIRTY_DAYS) {
  const now = Math.floor(Date.now() / 1000);
  const header = b64urlJson({ alg: 'HS256', typ: 'JWT' });
  const body = b64urlJson({ ...payload, iat: now, exp: now + ttlSeconds });
  const data = `${header}.${body}`;
  const sig = crypto.createHmac('sha256', SECRET).update(data).digest('base64url');
  return `${data}.${sig}`;
}

export function verifySession(token) {
  if (!token) return null;
  const parts = token.split('.');
  if (parts.length !== 3) return null;
  const data = `${parts[0]}.${parts[1]}`;
  const expected = crypto.createHmac('sha256', SECRET).update(data).digest('base64url');
  const got = Buffer.from(parts[2]);
  const want = Buffer.from(expected);
  if (got.length !== want.length || !crypto.timingSafeEqual(got, want)) return null;
  let body;
  try {
    body = JSON.parse(Buffer.from(parts[1], 'base64url').toString('utf8'));
  } catch {
    return null;
  }
  if (body.exp && Math.floor(Date.now() / 1000) > body.exp) return null;
  return body;
}

export function bearer(event) {
  const headers = event.headers || {};
  const header = headers.authorization || headers.Authorization || '';
  return header.startsWith('Bearer ') ? header.slice(7) : null;
}

// ── Session cookie ───────────────────────────────────────────────────────────
//
// The cookie is the preferred carrier now that the site and this API share an
// origin behind CloudFront: HttpOnly means a script cannot read the session, so
// an XSS bug on the site can no longer walk off with every signed-in student's
// credentials the way a localStorage token could.
//
// bearer() stays as a fallback — local development (serve.py on :3001) still
// calls this API cross-origin, where a SameSite cookie is not sent.

export const SESSION_COOKIE = 'sdit_session';

/** Read the session cookie. HTTP API v2 hands cookies over as name=value strings. */
export function sessionCookie(event) {
  for (const c of event.cookies || []) {
    const eq = c.indexOf('=');
    if (eq > 0 && c.slice(0, eq).trim() === SESSION_COOKIE) return c.slice(eq + 1).trim();
  }
  return null;
}

/**
 * SameSite=Lax, not Strict. Strict withholds the cookie on cross-site
 * navigation, so a student clicking a lesson link in The Daily would land on
 * the site logged out and have to reload. Lax still blocks the cross-site POST
 * that CSRF depends on.
 */
export function sessionCookieHeader(token, maxAgeSeconds = THIRTY_DAYS) {
  return `${SESSION_COOKIE}=${token}; Path=/; Secure; HttpOnly; SameSite=Lax; Max-Age=${maxAgeSeconds}`;
}

/** Expire it. JavaScript cannot clear a cookie it is not allowed to read. */
export function clearSessionCookieHeader() {
  return `${SESSION_COOKIE}=; Path=/; Secure; HttpOnly; SameSite=Lax; Max-Age=0`;
}

/** Six-digit numeric sign-in code. */
export function newCode() {
  return String(crypto.randomInt(0, 1000000)).padStart(6, '0');
}

/** Codes are never stored in the clear — only this keyed hash is. */
export function hashCode(code, email) {
  return crypto.createHmac('sha256', SECRET).update(`${email.toLowerCase()}:${code}`).digest('hex');
}
