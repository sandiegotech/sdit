/**
 * Files behind the made things: photos, a film, a deck, an essay, a recording.
 *
 * One private S3 bucket (WORK_BUCKET), two prefixes:
 *
 *   u/<uid>/<course>/<id>-<name>      the learner's own files. uid is a hash of
 *                                     the email, so a key never carries it.
 *                                     Read and written only through links
 *                                     signed here, each good for minutes.
 *   p/<handle>/<edition>/<id>-<name>  copies made when an edition is published.
 *                                     CloudFront serves this prefix, and only
 *                                     this prefix, at /work/p/... on the site.
 *
 * The browser talks to the bucket directly with the signed links; this
 * function never carries file bytes. Nothing is written into the learner's
 * record here: the page keeps the list of files inside the made-thing record,
 * and this module only hands out keys, links, and copies.
 */

import { createHash, randomBytes } from 'node:crypto';
import {
  S3Client, PutObjectCommand, GetObjectCommand, HeadObjectCommand, CopyObjectCommand,
  DeleteObjectCommand, ListObjectsV2Command, DeleteObjectsCommand,
} from '@aws-sdk/client-s3';

const BUCKET = process.env.WORK_BUCKET || '';
const s3 = new S3Client({});

export const enabled = () => !!BUCKET;

const MB = 1024 * 1024;
// kind → [accepted content types (prefix match on "/"), size limit]
export const KINDS = {
  image: { types: ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/heic', 'image/svg+xml'], max: 20 * MB },
  video: { types: ['video/mp4', 'video/quicktime', 'video/webm'], max: 300 * MB },
  audio: { types: ['audio/mpeg', 'audio/mp4', 'audio/x-m4a', 'audio/wav', 'audio/x-wav', 'audio/ogg', 'audio/aac'], max: 60 * MB },
  pdf: { types: ['application/pdf'], max: 40 * MB },
  text: { types: ['text/plain', 'text/markdown'], max: 1 * MB },
};

export function kindOf(type) {
  const t = String(type || '').toLowerCase().split(';')[0].trim();
  for (const [kind, spec] of Object.entries(KINDS)) if (spec.types.includes(t)) return kind;
  return null;
}

export const uidOf = (email) => createHash('sha256').update(String(email).trim().toLowerCase()).digest('hex').slice(0, 20);
const userPrefix = (email) => `u/${uidOf(email)}/`;
const editionPrefix = (handle, edition) => `p/${handle}/${edition}/`;

/** A file name safe in a key and a URL: letters, digits, dot, dash, underscore. */
export function safeName(name) {
  const base = String(name || 'file').split(/[\\/]/).pop();
  const dot = base.lastIndexOf('.');
  const stem = dot > 0 ? base.slice(0, dot) : base, ext = dot > 0 ? base.slice(dot + 1) : '';
  const clean = (t) => t.normalize('NFKD').replace(/[^\w.-]+/g, '-').replace(/-+/g, '-').replace(/^[-.]+|[-.]+$/g, '');
  const head = (clean(stem) || 'file').slice(0, 70);
  return ext ? `${head}.${clean(ext).slice(0, 8)}` : head;
}

export function ownsKey(email, key) {
  return typeof key === 'string' && key.startsWith(userPrefix(email)) && !key.includes('..');
}

/** Where a new file will live, and a link that lets the browser put it there. */
export async function uploadLink(email, course, name, type) {
  const kind = kindOf(type);
  if (!kind) return null;
  const id = randomBytes(6).toString('hex');
  const key = `${userPrefix(email)}${course}/${id}-${safeName(name)}`;
  const { getSignedUrl } = await import('@aws-sdk/s3-request-presigner');
  const url = await getSignedUrl(s3, new PutObjectCommand({ Bucket: BUCKET, Key: key, ContentType: type }), { expiresIn: 900 });
  return { key, url, kind, max: KINDS[kind].max };
}

/**
 * After the browser has uploaded: look at what landed. Anything over its
 * kind's limit, or of a type not accepted, is deleted and refused — the signed
 * link could not enforce size, so this is where the limit lives.
 */
export async function complete(email, key) {
  if (!ownsKey(email, key)) return { error: 'Not your file' };
  let head;
  try {
    head = await s3.send(new HeadObjectCommand({ Bucket: BUCKET, Key: key }));
  } catch {
    return { error: 'The upload did not arrive' };
  }
  const kind = kindOf(head.ContentType);
  const size = Number(head.ContentLength || 0);
  if (!kind || size > KINDS[kind].max) {
    await s3.send(new DeleteObjectCommand({ Bucket: BUCKET, Key: key }));
    return { error: kind ? `Too large: the limit for ${kind} files is ${Math.round(KINDS[kind].max / MB)} MB` : 'That kind of file is not accepted' };
  }
  const name = key.split('/').pop().replace(/^[0-9a-f]{12}-/, '');
  return { file: { key, name, type: head.ContentType, size, kind } };
}

/** Links to read the learner's own files, good for an hour. */
export async function viewLinks(email, keys) {
  const { getSignedUrl } = await import('@aws-sdk/s3-request-presigner');
  const out = {};
  for (const key of [...new Set(keys)].slice(0, 200)) {
    if (!ownsKey(email, key)) continue;
    out[key] = await getSignedUrl(s3, new GetObjectCommand({ Bucket: BUCKET, Key: key }), { expiresIn: 3600 });
  }
  return out;
}

export async function remove(email, key) {
  if (!ownsKey(email, key)) return false;
  await s3.send(new DeleteObjectCommand({ Bucket: BUCKET, Key: key }));
  return true;
}

// ── Publishing ───────────────────────────────────────────────────────────────

/** Every file entry inside the made-thing records of a snapshot. */
function fileEntries(snapshot) {
  const out = [];
  for (const a of snapshot.answers || []) {
    if (a.heading !== 'made-thing') continue;
    let rec;
    try { rec = JSON.parse(a.content); } catch { continue; }
    if (!rec || !Array.isArray(rec.files)) continue;
    out.push({ answer: a, rec });
  }
  return out;
}

async function listPrefix(prefix) {
  const keys = [];
  let token;
  do {
    const r = await s3.send(new ListObjectsV2Command({ Bucket: BUCKET, Prefix: prefix, ContinuationToken: token }));
    for (const o of r.Contents || []) keys.push(o.Key);
    token = r.IsTruncated ? r.NextContinuationToken : undefined;
  } while (token);
  return keys;
}

async function deleteKeys(keys) {
  for (let i = 0; i < keys.length; i += 1000) {
    const batch = keys.slice(i, i + 1000).map((Key) => ({ Key }));
    if (batch.length) await s3.send(new DeleteObjectsCommand({ Bucket: BUCKET, Delete: { Objects: batch, Quiet: true } }));
  }
}

/**
 * Make the edition's files public: copy each one the learner owns to the
 * edition's public prefix and rewrite the record to point at the site path.
 * Returns the snapshot to store. Files already copied under the same name are
 * kept; anything no longer referenced is removed, so an unpublished photo
 * really goes away.
 */
export async function publish(email, handle, edition, snapshot) {
  const entries = fileEntries(snapshot);
  const prefix = editionPrefix(handle, edition);
  const existing = new Set(enabled() ? await listPrefix(prefix) : []);
  const wanted = new Set();
  for (const { answer, rec } of entries) {
    const files = [];
    for (const f of rec.files.slice(0, 24)) {
      if (!f || !ownsKey(email, f.key)) continue;
      const base = f.key.split('/').pop();
      const target = prefix + base;
      wanted.add(target);
      if (!existing.has(target)) {
        try {
          await s3.send(new CopyObjectCommand({
            Bucket: BUCKET, Key: target, CopySource: `/${BUCKET}/${encodeURIComponent(f.key).replace(/%2F/g, '/')}`,
            MetadataDirective: 'REPLACE', ContentType: f.type || undefined,
            CacheControl: 'public, max-age=31536000, immutable',
          }));
        } catch {
          continue;   // the source is gone; leave it out rather than publish a broken link
        }
      }
      files.push({ url: `/work/${target}`, name: f.name, type: f.type, size: f.size, kind: f.kind });
    }
    answer.content = JSON.stringify({ ...rec, files });
  }
  const stale = [...existing].filter((key) => !wanted.has(key));
  if (stale.length) await deleteKeys(stale);
  return snapshot;
}

export async function unpublish(handle, edition) {
  if (!enabled()) return;
  await deleteKeys(await listPrefix(editionPrefix(handle, edition)));
}
