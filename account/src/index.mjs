/**
 * SDIT account service — request router.
 *
 * Routes (all JSON):
 *   POST /subscribe      { email }            → join The Daily (role: subscriber)
 *   POST /auth/request   { email }            → email a one-time sign-in code
 *   POST /auth/verify    { email, code }      → { token, profile }
 *   GET  /me                                  → { profile }            (Bearer)
 *   GET  /work?lesson=<path>                  → { responses }          (Bearer)
 *   PUT  /work           { lesson, heading, content }                  (Bearer)
 */

import { ok, bad, unauthorized, notFound, json, parseBody, corsHeaders } from './lib/http.mjs';
import { signSession, verifySession, bearer, newCode, hashCode } from './lib/auth.mjs';
import { sendCode } from './lib/email.mjs';
import * as db from './lib/db.mjs';

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const MAX_ATTEMPTS = 5;

export async function handler(event) {
  const method = event.requestContext?.http?.method || 'GET';
  const path = (event.rawPath || '/').replace(/\/+$/, '') || '/';
  const cors = corsHeaders(event);

  // Preflight — answer here; the catch-all ANY route sends OPTIONS to us.
  if (method === 'OPTIONS') return { statusCode: 204, headers: cors, body: '' };

  let response;
  try {
    response = await route(method, path, event);
  } catch (err) {
    console.error(err);
    response = json(500, { error: 'Server error' });
  }
  response.headers = { ...(response.headers || {}), ...cors };
  return response;
}

function route(method, path, event) {
  if (method === 'POST' && path === '/subscribe') return subscribe(event);
  if (method === 'POST' && path === '/auth/request') return authRequest(event);
  if (method === 'POST' && path === '/auth/verify') return authVerify(event);
  if (method === 'GET' && path === '/me') return me(event);
  if (method === 'GET' && path === '/progress') return getProgress(event);
  if (method === 'GET' && path === '/work') return getWork(event);
  if (method === 'PUT' && path === '/work') return putWork(event);
  return notFound();
}

// ── Handlers ─────────────────────────────────────────────────────────────────

async function subscribe(event) {
  const { email } = parseBody(event);
  if (!email || !EMAIL_RE.test(email)) return bad('A valid email is required');
  await db.ensureSubscriber(email);
  return ok({ ok: true });
}

async function authRequest(event) {
  const { email } = parseBody(event);
  if (!email || !EMAIL_RE.test(email)) return bad('A valid email is required');
  const code = newCode();
  await db.putCode(email, hashCode(code, email));
  await sendCode(email, code);
  // Always succeed — never reveal whether an address is on file.
  return ok({ ok: true });
}

async function authVerify(event) {
  const { email, code } = parseBody(event);
  if (!email || !code) return bad('Email and code are required');

  const record = await db.getCode(email);
  if (!record) return bad('That code has expired — request a new one');
  if ((record.attempts || 0) >= MAX_ATTEMPTS) {
    await db.deleteCode(email);
    return bad('Too many attempts — request a new code');
  }
  if (record.codeHash !== hashCode(code, email)) {
    await db.bumpCodeAttempts(email);
    return bad('That code is incorrect');
  }

  await db.deleteCode(email);
  const profile = await db.signIn(email);
  const token = signSession({ sub: profile.email, role: profile.role });
  return ok({ token, profile: publicProfile(profile) });
}

async function me(event) {
  const session = sessionFrom(event);
  if (!session) return unauthorized();
  const profile = await db.getProfile(session.sub);
  if (!profile) return unauthorized();
  return ok({ profile: publicProfile(profile) });
}

async function getProgress(event) {
  const session = sessionFrom(event);
  if (!session) return unauthorized();
  return ok({ lessons: await db.listProgress(session.sub) });
}

async function getWork(event) {
  const session = sessionFrom(event);
  if (!session) return unauthorized();
  const lesson = (event.queryStringParameters || {}).lesson;
  if (!lesson) return bad('lesson is required');
  return ok({ responses: await db.loadWork(session.sub, lesson) });
}

async function putWork(event) {
  const session = sessionFrom(event);
  if (!session) return unauthorized();
  const { lesson, heading, content } = parseBody(event);
  if (!lesson || !heading) return bad('lesson and heading are required');
  await db.saveWork(session.sub, lesson, heading, content ?? '');
  return ok({ ok: true });
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function sessionFrom(event) {
  return verifySession(bearer(event));
}

function publicProfile(p) {
  return { email: p.email, role: p.role, tester: !!p.tester };
}
