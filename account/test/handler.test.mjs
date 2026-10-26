// Run: node --import ./account/test/hooks.mjs --test account/test/
import { test, before } from 'node:test';
import assert from 'node:assert/strict';

process.env.TABLE_NAME = 'test';
process.env.WORK_BUCKET = 'work-test';
process.env.SESSION_SECRET = 'test-secret';
process.env.MAIL_FROM = '';
process.env.ALLOW_ORIGIN = 'https://learn.sandiegotech.org';

let handler, stub;
before(async () => {
  ({ handler } = await import('../src/index.mjs'));
  stub = await import('./aws-stub.mjs');
});

function ev(method, path, { body, cookies, token, query } = {}) {
  return {
    rawPath: path,
    requestContext: { http: { method } },
    headers: { origin: 'https://learn.sandiegotech.org', ...(token ? { authorization: `Bearer ${token}` } : {}) },
    cookies,
    queryStringParameters: query,
    body: body ? JSON.stringify(body) : undefined,
  };
}

async function signIn(email) {
  const logs = [];
  const orig = console.log;
  console.log = (m) => logs.push(String(m));
  try {
    const r = await handler(ev('POST', '/auth/request', { body: { email } }));
    assert.equal(r.statusCode, 200);
  } finally { console.log = orig; }
  const code = logs.join('\n').match(/sign-in code for .+: (\d{6})/)[1];
  return handler(ev('POST', '/auth/verify', { body: { email, code } }));
}

const cookieOf = (r) => r.cookies.find((c) => c.startsWith('sdit_session=')).split(';')[0];

test('verify sets an HttpOnly, Secure, Lax session cookie and still returns the token', async () => {
  const r = await signIn('a@example.com');
  assert.equal(r.statusCode, 200);
  const set = r.cookies.find((c) => c.startsWith('sdit_session='));
  assert.match(set, /HttpOnly/);
  assert.match(set, /Secure/);
  assert.match(set, /SameSite=Lax/);
  assert.ok(JSON.parse(r.body).token);
});

test('the cookie authenticates, and so does the bearer token', async () => {
  const r = await signIn('b@example.com');
  const me1 = await handler(ev('GET', '/me', { cookies: [cookieOf(r)] }));
  assert.equal(me1.statusCode, 200);
  const me2 = await handler(ev('GET', '/me', { token: JSON.parse(r.body).token }));
  assert.equal(me2.statusCode, 200);
  const none = await handler(ev('GET', '/me'));
  assert.equal(none.statusCode, 401);
  const forged = await handler(ev('GET', '/me', { cookies: ['sdit_session=a.b.c'] }));
  assert.equal(forged.statusCode, 401);
});

test('signout expires the cookie', async () => {
  const r = await handler(ev('POST', '/auth/signout'));
  assert.equal(r.statusCode, 200);
  assert.match(r.cookies[0], /^sdit_session=; .*Max-Age=0/);
});

test('/work/all returns every answer, across pages, and only the caller\'s', async () => {
  const r = await signIn('c@example.com');
  const cookies = [cookieOf(r)];
  const answers = [
    ['/begin', 'commitment', '2027-01-04'],
    ['/begin', 'education', 'Seeing clearly.'],
    ['/courses/HUM-101/day-01', 'answer', 'My phone.'],
    ['/gates/semester-1', 'education', 'Making things that last.'],
  ];
  for (const [lesson, heading, content] of answers) {
    const p = await handler(ev('PUT', '/work', { cookies, body: { lesson, heading, content } }));
    assert.equal(p.statusCode, 200);
  }
  const other = await signIn('d@example.com');
  await handler(ev('PUT', '/work', { cookies: [cookieOf(other)], body: { lesson: '/begin', heading: 'education', content: 'not yours' } }));

  stub.setPageSize(2);                       // force pagination
  const all = await handler(ev('GET', '/work/all', { cookies }));
  stub.setPageSize(1000);
  assert.equal(all.statusCode, 200);
  const got = JSON.parse(all.body).responses;
  assert.equal(got.length, 4);
  assert.deepEqual(got.map((x) => x.content).sort(), answers.map((a) => a[2]).sort());
  assert.ok(got.every((x) => x.updatedAt));

  const anon = await handler(ev('GET', '/work/all'));
  assert.equal(anon.statusCode, 401);
});

test('a wrong code is refused and counted; the right one still works', async () => {
  const email = 'e@example.com';
  const logs = []; const orig = console.log; console.log = (m) => logs.push(String(m));
  try { await handler(ev('POST', '/auth/request', { body: { email } })); } finally { console.log = orig; }
  const code = logs.join('\n').match(/: (\d{6})/)[1];
  const wrong = String((Number(code) + 1) % 1000000).padStart(6, '0');
  const bad = await handler(ev('POST', '/auth/verify', { body: { email, code: wrong } }));
  assert.equal(bad.statusCode, 400);
  const good = await handler(ev('POST', '/auth/verify', { body: { email, code } }));
  assert.equal(good.statusCode, 200);
});

// ── Public portfolios ───────────────────────────────────────────────────────

const snap = (text) => ({ name: 'Ana', answers: [{ lesson: '/begin', heading: 'education', content: text, at: '2027-01-04T10:00:00Z' }] });

test('publishing claims a handle, and the public read shows only what was published', async () => {
  const r = await signIn('p1@example.com');
  const cookies = [cookieOf(r)];
  // A private answer that was never published must not appear.
  await handler(ev('PUT', '/work', { cookies, body: { lesson: '/begin', heading: 'believe', content: 'private' } }));
  const pub = await handler(ev('PUT', '/portfolio', { cookies, body: { handle: 'ana-r', edition: 'short', snapshot: snap('Seeing clearly.') } }));
  assert.equal(pub.statusCode, 200);
  const read = await handler(ev('GET', '/portfolio/ana-r'));
  assert.equal(read.statusCode, 200);
  const body = JSON.parse(read.body);
  assert.deepEqual(Object.keys(body.editions), ['short']);
  assert.equal(body.editions.short.snapshot.answers[0].content, 'Seeing clearly.');
  assert.ok(!read.body.includes('p1@example.com'), 'the public read never carries the email');
  assert.ok(!read.body.includes('private'), 'unpublished answers never appear');
  const mine = JSON.parse((await handler(ev('GET', '/portfolio/mine', { cookies }))).body);
  assert.equal(mine.handle, 'ana-r');
  assert.deepEqual(mine.published.map((p) => p.edition), ['short']);
});

test('a handle belongs to one learner; reserved and malformed handles are refused', async () => {
  const other = await signIn('p2@example.com');
  const cookies = [cookieOf(other)];
  const taken = await handler(ev('PUT', '/portfolio', { cookies, body: { handle: 'ana-r', edition: 'short', snapshot: snap('x') } }));
  assert.equal(taken.statusCode, 409);
  for (const h of ['api', 'ab', 'Has Space', '-dash', 'double--dash']) {
    const r = await handler(ev('PUT', '/portfolio', { cookies, body: { handle: h, edition: 'short', snapshot: snap('x') } }));
    assert.equal(r.statusCode, 400, h);
  }
  const anon = await handler(ev('PUT', '/portfolio', { body: { handle: 'ghost', edition: 'short', snapshot: snap('x') } }));
  assert.equal(anon.statusCode, 401);
});

test('unpublishing takes an edition down; a handle with nothing published is not found', async () => {
  const r = await signIn('p1@example.com');
  const cookies = [cookieOf(r)];
  const down = await handler(ev('POST', '/portfolio/unpublish', { cookies, body: { edition: 'short' } }));
  assert.equal(down.statusCode, 200);
  assert.equal((await handler(ev('GET', '/portfolio/ana-r'))).statusCode, 404);
  assert.equal((await handler(ev('GET', '/portfolio/nobody-here'))).statusCode, 404);
});

test('an oversized snapshot is refused', async () => {
  const r = await signIn('p3@example.com');
  const big = { name: '', answers: [{ lesson: '/x', heading: 'answer', content: 'x'.repeat(320 * 1024) }] };
  const res = await handler(ev('PUT', '/portfolio', { cookies: [cookieOf(r)], body: { handle: 'big-one', edition: 'expanded', snapshot: big } }));
  assert.equal(res.statusCode, 400);
});

// ── Files behind the made things ─────────────────────────────────────────────

test('an upload is a signed put link under the learner\'s own prefix, checked once it lands', async () => {
  const r = await signIn('f1@example.com');
  const cookies = [cookieOf(r)];
  const no = await handler(ev('POST', '/work/upload', { cookies, body: { course: 'ART-310', name: 'tide.exe', type: 'application/x-msdownload' } }));
  assert.equal(no.statusCode, 400);
  const link = JSON.parse((await handler(ev('POST', '/work/upload', { cookies, body: { course: 'ART-310', name: 'Tide Clock (1).JPG', type: 'image/jpeg' } }))).body);
  assert.match(link.key, /^u\/[0-9a-f]{20}\/ART-310\/[0-9a-f]{12}-Tide-Clock-1.JPG$/);
  assert.ok(!link.key.includes('f1@'), 'the key never carries the email');
  assert.match(link.url, /verb=put/);
  assert.equal(link.kind, 'image');

  // Nothing arrived yet.
  const early = await handler(ev('POST', '/work/upload/complete', { cookies, body: { key: link.key } }));
  assert.equal(early.statusCode, 400);
  // Too big for its kind: deleted and refused.
  stub.bucket.set(link.key, { ContentType: 'image/jpeg', ContentLength: 21 * 1024 * 1024 });
  const big = await handler(ev('POST', '/work/upload/complete', { cookies, body: { key: link.key } }));
  assert.equal(big.statusCode, 400);
  assert.ok(!stub.bucket.has(link.key));
  // Accepted.
  stub.bucket.set(link.key, { ContentType: 'image/jpeg', ContentLength: 240000 });
  const done = JSON.parse((await handler(ev('POST', '/work/upload/complete', { cookies, body: { key: link.key } }))).body);
  assert.deepEqual(done.file, { key: link.key, name: 'Tide-Clock-1.JPG', type: 'image/jpeg', size: 240000, kind: 'image' });

  // Only the owner can read or delete it.
  const other = await signIn('f2@example.com');
  const theirs = JSON.parse((await handler(ev('POST', '/work/file-urls', { cookies: [cookieOf(other)], body: { keys: [link.key] } }))).body);
  assert.deepEqual(theirs.urls, {});
  const mine = JSON.parse((await handler(ev('POST', '/work/file-urls', { cookies, body: { keys: [link.key] } }))).body);
  assert.match(mine.urls[link.key], /verb=get/);
  assert.equal((await handler(ev('POST', '/work/file/delete', { cookies: [cookieOf(other)], body: { key: link.key } }))).statusCode, 400);
  assert.equal((await handler(ev('POST', '/work/file/delete', { cookies, body: { key: link.key } }))).statusCode, 200);
  assert.ok(!stub.bucket.has(link.key));
});

test('publishing copies the files behind the made things to the public prefix; unpublishing removes them', async () => {
  const r = await signIn('f3@example.com');
  const cookies = [cookieOf(r)];
  const link = JSON.parse((await handler(ev('POST', '/work/upload', { cookies, body: { course: 'CAP-402', name: 'deck.pdf', type: 'application/pdf' } }))).body);
  stub.bucket.set(link.key, { ContentType: 'application/pdf', ContentLength: 5000 });
  const stranger = 'u/0000000000000000dead/CAP-402/abcdefabcdef-secret.pdf';
  stub.bucket.set(stranger, { ContentType: 'application/pdf', ContentLength: 10 });
  const rec = { title: 'Cheap Eyes', form: 'build', words: 'x', files: [
    { key: link.key, name: 'deck.pdf', type: 'application/pdf', size: 5000, kind: 'pdf' },
    { key: stranger, name: 'secret.pdf', type: 'application/pdf', size: 10, kind: 'pdf' },
  ] };
  const snapshot = { name: 'F', answers: [{ lesson: '/courses/CAP-402/made', heading: 'made-thing', content: JSON.stringify(rec), at: '2030-05-01' }] };
  const pub = await handler(ev('PUT', '/portfolio', { cookies, body: { handle: 'f-three', edition: 'short', snapshot } }));
  assert.equal(pub.statusCode, 200);
  const base = link.key.split('/').pop();
  assert.ok(stub.bucket.has(`p/f-three/short/${base}`), 'copied to the public prefix');
  const shown = JSON.parse(JSON.parse((await handler(ev('GET', '/portfolio/f-three'))).body).editions.short.snapshot.answers[0].content);
  assert.deepEqual(shown.files.map((f) => f.url), [`/work/p/f-three/short/${base}`]);
  assert.ok(!JSON.stringify(shown).includes('u/'), 'no private key leaks into the public snapshot');
  assert.ok(!JSON.stringify(shown).includes('secret'), 'a file the learner does not own is left out');
  const down = await handler(ev('POST', '/portfolio/unpublish', { cookies, body: { edition: 'short' } }));
  assert.equal(down.statusCode, 200);
  assert.ok(!stub.bucket.has(`p/f-three/short/${base}`), 'the public copy is gone');
  assert.ok(stub.bucket.has(link.key), 'the learner\'s own file stays');
});
