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

/** Six-digit numeric sign-in code. */
export function newCode() {
  return String(crypto.randomInt(0, 1000000)).padStart(6, '0');
}

/** Codes are never stored in the clear — only this keyed hash is. */
export function hashCode(code, email) {
  return crypto.createHmac('sha256', SECRET).update(`${email.toLowerCase()}:${code}`).digest('hex');
}
