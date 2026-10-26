// In-memory stand-ins for the parts of the AWS SDK the account service uses.
// The real SDK is provided by the Lambda runtime and is not installed locally,
// so tests resolve '@aws-sdk/*' here (see hooks.mjs). One shared table.

export const table = new Map();          // `${pk}|${sk}` -> item
const k = (key) => `${key.pk}|${key.sk}`;

class Command { constructor(input) { this.input = input; } }
export class GetCommand extends Command {}
export class PutCommand extends Command {}
export class UpdateCommand extends Command {}
export class QueryCommand extends Command {}
export class DeleteCommand extends Command {}
export class SendEmailCommand extends Command {}
export class TransactWriteCommand extends Command {}
export class PutObjectCommand extends Command {}
export class GetObjectCommand extends Command {}
export class HeadObjectCommand extends Command {}
export class CopyObjectCommand extends Command {}
export class DeleteObjectCommand extends Command {}
export class ListObjectsV2Command extends Command {}
export class DeleteObjectsCommand extends Command {}

// The work bucket: key -> { ContentType, ContentLength }. Tests put objects
// here directly, standing in for the browser's upload over the signed link.
export const bucket = new Map();

export const sent = [];                  // emails "sent"
export let pageSize = 1000;              // shrink to exercise pagination
export function setPageSize(n) { pageSize = n; }

function send(cmd) {
  const i = cmd.input;
  if (cmd instanceof GetCommand) return { Item: table.get(k(i.Key)) };
  if (cmd instanceof PutCommand) { table.set(k(i.Item), { ...i.Item }); return {}; }
  if (cmd instanceof DeleteCommand) { table.delete(k(i.Key)); return {}; }
  if (cmd instanceof UpdateCommand) {
    const cur = table.get(k(i.Key)) || { ...i.Key };
    const v = i.ExpressionAttributeValues || {};
    if (/attempts = if_not_exists/.test(i.UpdateExpression)) cur.attempts = (cur.attempts || 0) + 1;
    if (/#r = :role/.test(i.UpdateExpression)) { cur.role = v[':role']; cur.updatedAt = v[':u']; }
    table.set(k(i.Key), cur);
    return {};
  }
  if (cmd instanceof QueryCommand) {
    const p = i.ExpressionAttributeValues[':p'], s = i.ExpressionAttributeValues[':s'];
    const all = [...table.values()].filter((it) => it.pk === p && it.sk.startsWith(s))
      .sort((a, b) => (a.sk < b.sk ? -1 : 1));
    const start = i.ExclusiveStartKey ? all.findIndex((it) => it.sk === i.ExclusiveStartKey.sk) + 1 : 0;
    const page = all.slice(start, start + pageSize);
    const more = start + pageSize < all.length;
    return { Items: page, LastEvaluatedKey: more ? { pk: p, sk: page[page.length - 1].sk } : undefined };
  }
  if (cmd instanceof TransactWriteCommand) {
    // All or nothing: check every condition first, then apply.
    for (const t of i.TransactItems) {
      if (t.Put && t.Put.ConditionExpression === 'attribute_not_exists(pk)' && table.has(k(t.Put.Item))) {
        const e = new Error('cancelled'); e.name = 'TransactionCanceledException'; throw e;
      }
    }
    for (const t of i.TransactItems) {
      if (t.Put) table.set(k(t.Put.Item), { ...t.Put.Item });
      if (t.Delete) table.delete(k(t.Delete.Key));
    }
    return {};
  }
  if (cmd instanceof SendEmailCommand) { sent.push(i); return {}; }
  if (cmd instanceof HeadObjectCommand) {
    const o = bucket.get(i.Key);
    if (!o) { const e = new Error('NotFound'); e.name = 'NotFound'; throw e; }
    return { ...o };
  }
  if (cmd instanceof DeleteObjectCommand) { bucket.delete(i.Key); return {}; }
  if (cmd instanceof CopyObjectCommand) {
    const src = decodeURIComponent(i.CopySource.replace(/^\/[^/]+\//, ''));
    const o = bucket.get(src);
    if (!o) { const e = new Error('NoSuchKey'); e.name = 'NoSuchKey'; throw e; }
    bucket.set(i.Key, { ...o, CacheControl: i.CacheControl });
    return {};
  }
  if (cmd instanceof ListObjectsV2Command) {
    return { Contents: [...bucket.keys()].filter((key) => key.startsWith(i.Prefix)).map((Key) => ({ Key })), IsTruncated: false };
  }
  if (cmd instanceof DeleteObjectsCommand) { for (const o of i.Delete.Objects) bucket.delete(o.Key); return {}; }
  throw new Error('unstubbed command');
}

export class DynamoDBClient { constructor() {} }
export const DynamoDBDocumentClient = { from: () => ({ send: async (c) => send(c) }) };
export class SESClient { async send(c) { return send(c); } }
export class S3Client { async send(c) { return send(c); } }
// A "signed" link: the key is in the query so a test can see what it points at.
export async function getSignedUrl(_client, cmd, opts) {
  const verb = cmd instanceof PutObjectCommand ? 'put' : 'get';
  return `https://work.test/${cmd.input.Key}?verb=${verb}&expires=${opts.expiresIn}`;
}
