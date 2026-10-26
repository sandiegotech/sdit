/**
 * DynamoDB access. One table, keyed by (pk, sk):
 *
 *   USER#<email> / PROFILE              → the Card: email, role, tester, daily
 *   USER#<email> / WORK#<lesson>#<head> → one saved response
 *   AUTH#<email> / CODE                 → pending sign-in code (TTL-expired)
 *   USER#<email> / HANDLE               → the learner's public handle
 *   USER#<email> / PUBLISHED#<edition>  → a published Portfolio snapshot
 *   HANDLE#<handle> / OWNER             → who holds a handle (uniqueness)
 *
 * The belt series lives in one field, `role`:
 *   subscriber → visitor → student → fellow → professor
 * `tester` is a flag, not a rank.
 *
 * The AWS SDK v3 is provided by the Node 24 Lambda runtime, so it needs no
 * bundling and the deploy stays dependency-free.
 */

import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import {
  DynamoDBDocumentClient,
  GetCommand,
  PutCommand,
  UpdateCommand,
  QueryCommand,
  DeleteCommand,
  TransactWriteCommand,
} from '@aws-sdk/lib-dynamodb';

const TABLE = process.env.TABLE_NAME;
const doc = DynamoDBDocumentClient.from(new DynamoDBClient({}));

const norm = (email) => String(email).trim().toLowerCase();
const userPk = (email) => `USER#${norm(email)}`;
const authPk = (email) => `AUTH#${norm(email)}`;
const now = () => new Date().toISOString();

// ── Profile (the Card) ───────────────────────────────────────────────────────

export async function getProfile(email) {
  const r = await doc.send(new GetCommand({
    TableName: TABLE,
    Key: { pk: userPk(email), sk: 'PROFILE' },
  }));
  return r.Item || null;
}

/** The Daily signup: create as `subscriber` if new; never touch an existing Card. */
export async function ensureSubscriber(email) {
  const existing = await getProfile(email);
  if (existing) return existing;
  const item = {
    pk: userPk(email), sk: 'PROFILE',
    email: norm(email), role: 'subscriber', tester: false, daily: true,
    createdAt: now(), updatedAt: now(),
  };
  await doc.send(new PutCommand({ TableName: TABLE, Item: item }));
  return item;
}

/**
 * Sign-in: create as `visitor` if new, promote `subscriber` → `visitor`,
 * and never downgrade a higher rank (student/fellow/professor).
 */
export async function signIn(email) {
  const existing = await getProfile(email);
  const ts = now();
  if (!existing) {
    const item = {
      pk: userPk(email), sk: 'PROFILE',
      email: norm(email), role: 'visitor', tester: false, daily: true,
      createdAt: ts, updatedAt: ts,
    };
    await doc.send(new PutCommand({ TableName: TABLE, Item: item }));
    return item;
  }
  const role = (!existing.role || existing.role === 'subscriber') ? 'visitor' : existing.role;
  await doc.send(new UpdateCommand({
    TableName: TABLE,
    Key: { pk: userPk(email), sk: 'PROFILE' },
    UpdateExpression: 'SET #r = :role, updatedAt = :u',
    ExpressionAttributeNames: { '#r': 'role' },
    ExpressionAttributeValues: { ':role': role, ':u': ts },
  }));
  return { ...existing, role, updatedAt: ts };
}

// ── Sign-in codes ────────────────────────────────────────────────────────────

export async function putCode(email, codeHash, ttlSeconds = 600) {
  await doc.send(new PutCommand({
    TableName: TABLE,
    Item: {
      pk: authPk(email), sk: 'CODE',
      codeHash, attempts: 0,
      ttl: Math.floor(Date.now() / 1000) + ttlSeconds,
    },
  }));
}

export async function getCode(email) {
  const r = await doc.send(new GetCommand({
    TableName: TABLE,
    Key: { pk: authPk(email), sk: 'CODE' },
  }));
  return r.Item || null;
}

export async function bumpCodeAttempts(email) {
  await doc.send(new UpdateCommand({
    TableName: TABLE,
    Key: { pk: authPk(email), sk: 'CODE' },
    UpdateExpression: 'SET attempts = if_not_exists(attempts, :z) + :one',
    ExpressionAttributeValues: { ':z': 0, ':one': 1 },
  }));
}

export async function deleteCode(email) {
  await doc.send(new DeleteCommand({
    TableName: TABLE,
    Key: { pk: authPk(email), sk: 'CODE' },
  }));
}

// ── Student work ─────────────────────────────────────────────────────────────
// One item per response keeps concurrent saves conflict-free; the lesson is
// reassembled with a begins_with query.

const workSk = (lesson, heading) => `WORK#${lesson}#${heading}`;
const workPrefix = (lesson) => `WORK#${lesson}#`;

export async function saveWork(email, lesson, heading, content) {
  await doc.send(new PutCommand({
    TableName: TABLE,
    Item: {
      pk: userPk(email), sk: workSk(lesson, heading),
      lesson, heading, content, updatedAt: now(),
    },
  }));
}

export async function loadWork(email, lesson) {
  const r = await doc.send(new QueryCommand({
    TableName: TABLE,
    KeyConditionExpression: 'pk = :p AND begins_with(sk, :s)',
    ExpressionAttributeValues: { ':p': userPk(email), ':s': workPrefix(lesson) },
  }));
  const responses = {}, updatedAt = {};
  for (const item of r.Items || []) { responses[item.heading] = item.content; updatedAt[item.heading] = item.updatedAt || null; }
  return { responses, updatedAt };
}

/**
 * Progress across all lessons: the distinct lessons the user has saved work in,
 * each with the most recent update. Powers the signed-in course-mode header.
 */
export async function listProgress(email) {
  const r = await doc.send(new QueryCommand({
    TableName: TABLE,
    KeyConditionExpression: 'pk = :p AND begins_with(sk, :s)',
    ExpressionAttributeValues: { ':p': userPk(email), ':s': 'WORK#' },
    ProjectionExpression: 'lesson, updatedAt',
  }));
  const latest = {};
  for (const item of r.Items || []) {
    if (!item.lesson) continue;
    if (!latest[item.lesson] || item.updatedAt > latest[item.lesson]) {
      latest[item.lesson] = item.updatedAt;
    }
  }
  return Object.keys(latest).map((lesson) => ({ lesson, updatedAt: latest[lesson] }));
}

/**
 * Every answer the learner has written, for the Notebook and the Portfolio.
 * Paginated: four years of answers can pass DynamoDB's 1 MB page.
 */
export async function listAllWork(email) {
  const items = [];
  let ExclusiveStartKey;
  do {
    const r = await doc.send(new QueryCommand({
      TableName: TABLE,
      KeyConditionExpression: 'pk = :p AND begins_with(sk, :s)',
      ExpressionAttributeValues: { ':p': userPk(email), ':s': 'WORK#' },
      ProjectionExpression: 'lesson, heading, content, updatedAt',
      ExclusiveStartKey,
    }));
    for (const it of r.Items || []) {
      if (it.lesson && it.heading) {
        items.push({ lesson: it.lesson, heading: it.heading, content: it.content ?? '', updatedAt: it.updatedAt || null });
      }
    }
    ExclusiveStartKey = r.LastEvaluatedKey;
  } while (ExclusiveStartKey);
  return items;
}

// ── Enrollments ──────────────────────────────────────────────────────────────
// USER#<email> / ENROLL#<courseId> — the courses a person has added to "My Courses".

const enrollSk = (courseId) => `ENROLL#${courseId}`;

export async function enroll(email, courseId) {
  await doc.send(new PutCommand({
    TableName: TABLE,
    Item: { pk: userPk(email), sk: enrollSk(courseId), courseId, enrolledAt: now() },
  }));
}

export async function unenroll(email, courseId) {
  await doc.send(new DeleteCommand({
    TableName: TABLE,
    Key: { pk: userPk(email), sk: enrollSk(courseId) },
  }));
}

export async function listEnrollments(email) {
  const r = await doc.send(new QueryCommand({
    TableName: TABLE,
    KeyConditionExpression: 'pk = :p AND begins_with(sk, :s)',
    ExpressionAttributeValues: { ':p': userPk(email), ':s': 'ENROLL#' },
    ProjectionExpression: 'courseId, enrolledAt',
  }));
  return (r.Items || []).map((i) => ({ courseId: i.courseId, enrolledAt: i.enrolledAt }));
}


// ── Public portfolios ────────────────────────────────────────────────────────
// Opt-in, per edition. Publishing stores a snapshot of exactly what the
// learner chose to show; nothing written afterward is public until they
// publish again. A handle is claimed once and is unique.

const handlePk = (h) => `HANDLE#${h}`;

export async function getHandle(email) {
  const r = await doc.send(new GetCommand({ TableName: TABLE, Key: { pk: userPk(email), sk: 'HANDLE' } }));
  return r.Item ? r.Item.handle : null;
}

export async function handleOwner(handle) {
  const r = await doc.send(new GetCommand({ TableName: TABLE, Key: { pk: handlePk(handle), sk: 'OWNER' } }));
  return r.Item ? r.Item.email : null;
}

/** Claim a handle for this learner. Returns false if someone else holds it. */
export async function claimHandle(email, handle) {
  const owner = await handleOwner(handle);
  if (owner && owner !== norm(email)) return false;
  if (owner === norm(email)) return true;
  const previous = await getHandle(email);
  const items = [
    { Put: { TableName: TABLE, Item: { pk: handlePk(handle), sk: 'OWNER', email: norm(email), createdAt: now() },
             ConditionExpression: 'attribute_not_exists(pk)' } },
    { Put: { TableName: TABLE, Item: { pk: userPk(email), sk: 'HANDLE', handle, updatedAt: now() } } },
  ];
  if (previous && previous !== handle) {
    items.push({ Delete: { TableName: TABLE, Key: { pk: handlePk(previous), sk: 'OWNER' } } });
  }
  try {
    await doc.send(new TransactWriteCommand({ TransactItems: items }));
    return true;
  } catch (err) {
    if (err && (err.name === 'TransactionCanceledException' || err.name === 'ConditionalCheckFailedException')) return false;
    throw err;
  }
}

export async function publishEdition(email, edition, snapshot) {
  await doc.send(new PutCommand({
    TableName: TABLE,
    Item: { pk: userPk(email), sk: `PUBLISHED#${edition}`, edition, snapshot, publishedAt: now() },
  }));
}

export async function unpublishEdition(email, edition) {
  await doc.send(new DeleteCommand({ TableName: TABLE, Key: { pk: userPk(email), sk: `PUBLISHED#${edition}` } }));
}

export async function listPublished(email) {
  const r = await doc.send(new QueryCommand({
    TableName: TABLE,
    KeyConditionExpression: 'pk = :p AND begins_with(sk, :s)',
    ExpressionAttributeValues: { ':p': userPk(email), ':s': 'PUBLISHED#' },
  }));
  return (r.Items || []).map((i) => ({ edition: i.edition, snapshot: i.snapshot, publishedAt: i.publishedAt }));
}
