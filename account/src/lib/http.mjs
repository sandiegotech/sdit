/**
 * HTTP helpers for the API-Gateway HTTP API (payload format v2).
 *
 * CORS is handled here in the function (not by API Gateway) so the allow-list
 * is owned in one place: the request Origin is echoed back only if it is in
 * ALLOW_ORIGIN. Auth is by bearer token, so credentials are not used.
 */

const ALLOW = (process.env.ALLOW_ORIGIN || '*').split(',').map((s) => s.trim());

export function corsHeaders(event) {
  const headers = event.headers || {};
  const origin = headers.origin || headers.Origin || '';
  const allowed = ALLOW.includes('*') ? '*' : (ALLOW.includes(origin) ? origin : ALLOW[0]);
  return {
    'access-control-allow-origin': allowed,
    'access-control-allow-headers': 'content-type,authorization',
    'access-control-allow-methods': 'GET,POST,PUT,OPTIONS',
    'vary': 'Origin',
  };
}

export function json(statusCode, body) {
  return {
    statusCode,
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  };
}

export const ok = (body) => json(200, body);
export const bad = (message) => json(400, { error: message });
export const unauthorized = (message = 'Not signed in') => json(401, { error: message });
export const notFound = () => json(404, { error: 'Not found' });

export function parseBody(event) {
  if (!event.body) return {};
  const raw = event.isBase64Encoded
    ? Buffer.from(event.body, 'base64').toString('utf8')
    : event.body;
  try {
    return JSON.parse(raw);
  } catch {
    return {};
  }
}
