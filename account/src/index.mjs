/**
 * SDIT account service — request router.
 *
 * Routes (all JSON):
 *   POST /subscribe      { email }            → join The Daily (role: subscriber)
 *   POST /auth/request   { email }            → email a one-time sign-in code
 *   POST /auth/verify    { email, code }      → { token, profile } + session cookie
 *   POST /auth/signout                        → clears the session cookie
 *   GET  /me                                  → { profile }            (Bearer)
 *   GET  /work?lesson=<path>                  → { responses }          (Bearer)
 *   PUT  /work           { lesson, heading, content }                  (Bearer)
 *   GET  /work/all                            → { responses: [{lesson, heading, content, updatedAt}] }
 *   POST /work/upload    { course, name, type }  → { key, url, kind, max }   a signed link to put one file
 *   POST /work/upload/complete { key }          → { file }                 after the put: checked and accepted
 *   POST /work/file-urls { keys }               → { urls: {key: url} }     signed links to read own files
 *   POST /work/file/delete { key }              → { ok }
 *   GET  /portfolio/mine                      → { handle, published: [edition] }        (session)
 *   PUT  /portfolio      { handle, edition, snapshot }  → publish one edition          (session)
 *   POST /portfolio/unpublish { edition }                → take one edition down       (session)
 *   GET  /portfolio/<handle>                  → { handle, editions: {edition: {snapshot, publishedAt}} }  (public)
 *   GET  /enrollments                         → { courses: [id] }      (Bearer)
 *   POST /enroll         { course }                                    (Bearer)
 *   POST /unenroll       { course }                                    (Bearer)
 */

import { ok, bad, unauthorized, notFound, json, parseBody, corsHeaders } from './lib/http.mjs';
import {
  signSession, verifySession, bearer, newCode, hashCode,
  sessionCookie, sessionCookieHeader, clearSessionCookieHeader,
} from './lib/auth.mjs';
import { sendCode } from './lib/email.mjs';
import * as db from './lib/db.mjs';
import * as files from './lib/files.mjs';

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const COURSE_RE = /^[A-Z]+-\d+$/;
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
  if (method === 'POST' && path === '/auth/signout') return authSignout();
  if (method === 'GET' && path === '/me') return me(event);
  if (method === 'GET' && path === '/progress') return getProgress(event);
  if (method === 'GET' && path === '/work/all') return getAllWork(event);
  if (method === 'POST' && path === '/work/upload') return postUpload(event);
  if (method === 'POST' && path === '/work/upload/complete') return postUploadComplete(event);
  if (method === 'POST' && path === '/work/file-urls') return postFileUrls(event);
  if (method === 'POST' && path === '/work/file/delete') return postFileDelete(event);
  if (method === 'GET' && path === '/work') return getWork(event);
  if (method === 'PUT' && path === '/work') return putWork(event);
  if (method === 'GET' && path === '/portfolio/mine') return getMyPortfolio(event);
  if (method === 'PUT' && path === '/portfolio') return putPortfolio(event);
  if (method === 'POST' && path === '/portfolio/unpublish') return postUnpublish(event);
  if (method === 'GET' && path.startsWith('/portfolio/')) return getPublicPortfolio(path.slice('/portfolio/'.length));
  if (method === 'GET' && path === '/enrollments') return getEnrollments(event);
  if (method === 'POST' && path === '/enroll') return postEnroll(event);
  if (method === 'POST' && path === '/unenroll') return postUnenroll(event);
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
  // The token stays in the body for now so existing clients keep working; the
  // cookie is what the browser will actually use once the site is same-origin.
  // Drop the body copy only after nothing reads it.
  return ok({ token, profile: publicProfile(profile) }, [sessionCookieHeader(token)]);
}

/**
 * Signing out has to happen server-side now: the session cookie is HttpOnly,
 * so the page cannot delete it — only a Set-Cookie from here can.
 */
async function authSignout() {
  return ok({ ok: true }, [clearSessionCookieHeader()]);
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

/** Everything the learner has written: the Notebook's and Portfolio's source. */
async function getAllWork(event) {
  const session = sessionFrom(event);
  if (!session) return unauthorized();
  return ok({ responses: await db.listAllWork(session.sub) });
}

async function putWork(event) {
  const session = sessionFrom(event);
  if (!session) return unauthorized();
  const { lesson, heading, content } = parseBody(event);
  if (!lesson || !heading) return bad('lesson and heading are required');
  await db.saveWork(session.sub, lesson, heading, content ?? '');
  return ok({ ok: true });
}

// ── Files behind the made things ─────────────────────────────────────────────

async function postUpload(event) {
  const session = sessionFrom(event);
  if (!session) return unauthorized();
  if (!files.enabled()) return json(503, { error: 'File uploads are not switched on yet' });
  const { course, name, type } = parseBody(event);
  if (!course || !COURSE_RE.test(course)) return bad('A valid course id is required');
  if (!name || !type) return bad('name and type are required');
  const link = await files.uploadLink(session.sub, course, name, type);
  if (!link) return bad('That kind of file is not accepted: photos, video, audio, PDF, or plain text');
  return ok(link);
}

async function postUploadComplete(event) {
  const session = sessionFrom(event);
  if (!session) return unauthorized();
  const { key } = parseBody(event);
  if (!key) return bad('key is required');
  const r = await files.complete(session.sub, key);
  if (r.error) return bad(r.error);
  return ok(r);
}

async function postFileUrls(event) {
  const session = sessionFrom(event);
  if (!session) return unauthorized();
  const { keys } = parseBody(event);
  if (!Array.isArray(keys)) return bad('keys is required');
  return ok({ urls: await files.viewLinks(session.sub, keys) });
}

async function postFileDelete(event) {
  const session = sessionFrom(event);
  if (!session) return unauthorized();
  const { key } = parseBody(event);
  if (!key) return bad('key is required');
  if (!(await files.remove(session.sub, key))) return bad('Not your file');
  return ok({ ok: true });
}

async function getEnrollments(event) {
  const session = sessionFrom(event);
  if (!session) return unauthorized();
  const rows = await db.listEnrollments(session.sub);
  return ok({ courses: rows.map((r) => r.courseId) });
}

async function postEnroll(event) {
  const session = sessionFrom(event);
  if (!session) return unauthorized();
  const { course } = parseBody(event);
  if (!course || !COURSE_RE.test(course)) return bad('A valid course id is required');
  await db.enroll(session.sub, course);
  return ok({ ok: true });
}

async function postUnenroll(event) {
  const session = sessionFrom(event);
  if (!session) return unauthorized();
  const { course } = parseBody(event);
  if (!course) return bad('course is required');
  await db.unenroll(session.sub, course);
  return ok({ ok: true });
}

// ── Public portfolios ────────────────────────────────────────────────────────

const HANDLE_RE = /^[a-z0-9](?:[a-z0-9-]{1,28})[a-z0-9]$/;
const RESERVED = new Set(['api', 'admin', 'view', 'mine', 'demo', 'sample', 'new', 'edit', 'index', 'sdit', 'institute',
  'portfolio', 'notebook', 'begin', 'gates', 'courses', 'curriculum', 'assets', 'help', 'about', 'support']);
const EDITION_RE = /^(short|expanded|volume-[1-8])$/;
const MAX_SNAPSHOT = 300 * 1024;   // DynamoDB items stop at 400 KB

async function getMyPortfolio(event) {
  const session = sessionFrom(event);
  if (!session) return unauthorized();
  const [handle, published] = await Promise.all([db.getHandle(session.sub), db.listPublished(session.sub)]);
  return ok({ handle, published: published.map((p) => ({ edition: p.edition, publishedAt: p.publishedAt })) });
}

async function putPortfolio(event) {
  const session = sessionFrom(event);
  if (!session) return unauthorized();
  const { handle, edition, snapshot } = parseBody(event);
  const h = String(handle || '').trim().toLowerCase();
  if (!HANDLE_RE.test(h) || h.includes('--')) return bad('A handle is 3 to 30 lowercase letters, digits, or single dashes');
  if (RESERVED.has(h)) return bad('That handle is reserved');
  if (!EDITION_RE.test(String(edition || ''))) return bad('Unknown edition');
  if (!snapshot || typeof snapshot !== 'object' || !Array.isArray(snapshot.answers)) return bad('A snapshot is required');
  if (JSON.stringify(snapshot).length > MAX_SNAPSHOT) return bad('That edition is too large to publish; publish a single volume instead');
  if (!(await db.claimHandle(session.sub, h))) return json(409, { error: 'That handle is taken' });
  // The files behind the made things are copied to the public prefix and the
  // snapshot rewritten to point at them, so the page never needs a signed link.
  await db.publishEdition(session.sub, edition, await files.publish(session.sub, h, edition, snapshot));
  return ok({ ok: true, handle: h, edition });
}

async function postUnpublish(event) {
  const session = sessionFrom(event);
  if (!session) return unauthorized();
  const { edition } = parseBody(event);
  if (!EDITION_RE.test(String(edition || ''))) return bad('Unknown edition');
  await db.unpublishEdition(session.sub, edition);
  const handle = await db.getHandle(session.sub);
  if (handle) await files.unpublish(handle, edition);
  return ok({ ok: true });
}

/** Public: only what the learner chose to publish, and never their email. */
async function getPublicPortfolio(raw) {
  const h = decodeURIComponent(raw || '').toLowerCase();
  if (!HANDLE_RE.test(h)) return notFound();
  const owner = await db.handleOwner(h);
  if (!owner) return notFound();
  const published = await db.listPublished(owner);
  if (!published.length) return notFound();
  const editions = {};
  for (const p of published) editions[p.edition] = { snapshot: p.snapshot, publishedAt: p.publishedAt };
  return ok({ handle: h, editions });
}

// ── Helpers ──────────────────────────────────────────────────────────────────

/**
 * Cookie first, bearer token second. Both are accepted during the migration off
 * localStorage: the browser sends the cookie once the site is served through
 * CloudFront, while local development and any not-yet-updated client keep
 * working over the Authorization header.
 */
function sessionFrom(event) {
  return verifySession(sessionCookie(event) || bearer(event));
}

function publicProfile(p) {
  return { email: p.email, role: p.role, tester: !!p.tester };
}
