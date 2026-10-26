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
  throw new Error('unstubbed command');
}

export class DynamoDBClient { constructor() {} }
export const DynamoDBDocumentClient = { from: () => ({ send: async (c) => send(c) }) };
export class SESClient { async send(c) { return send(c); } }
