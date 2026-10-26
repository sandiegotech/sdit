# SDIT Account Service — the Card

Phase 1 of the unified SDIT login. Passwordless sign-in (email code) and cloud
sync of student work, on AWS — pinned to a US region, no third-party identity
provider, no tracking. One DynamoDB table, one Lambda, one HTTP API.

## What it does

- **Subscribe** — anyone can join The Daily with just an email (`subscriber`).
- **Sign in** — an emailed 6-digit code promotes them to `visitor` and issues a
  signed session. No passwords, nothing to store, nothing to leak.
- **Sync** — saved lesson responses follow the person across browsers and devices.

The belt series (`subscriber → visitor → student → fellow → professor`) is one
field on one record; `tester` is a flag, not a rank. Phase 1 issues `subscriber`
and `visitor` only — higher ranks are reserved names, granted later.

## Architecture

| Piece | Service |
|-------|---------|
| Compute | AWS Lambda (Node.js 20, arm64) |
| Data | DynamoDB single table `sdit-account` (on-demand, TTL on `ttl`) |
| API | API Gateway HTTP API (CORS) |
| Email | SES (`SendEmail`) |
| Session | self-signed JWT (HS256) — no Cognito, no Auth0 |

The AWS SDK v3 ships inside the Lambda runtime, so there are **no npm
dependencies** to install — the deploy is just the source.

## Routes

| Method | Path | Auth | Body / query | Returns |
|--------|------|------|--------------|---------|
| POST | `/subscribe` | — | `{ email }` | `{ ok }` |
| POST | `/auth/request` | — | `{ email }` | `{ ok }` |
| POST | `/auth/verify` | — | `{ email, code }` | `{ token, profile }` + session cookie |
| POST | `/auth/signout` | — | — | `{ ok }`, expires the cookie |
| GET | `/me` | session | — | `{ profile }` |
| GET | `/progress` | session | — | `{ lessons }` |
| GET | `/work` | session | `?lesson=<path>` | `{ responses }` |
| PUT | `/work` | session | `{ lesson, heading, content }` | `{ ok }` |
| GET | `/work/all` | session | — | `{ responses: [{ lesson, heading, content, updatedAt }] }` |
| POST | `/work/upload` | session | `{ course, name, type }` | `{ key, url, kind, max }` — a signed link to PUT one file |
| POST | `/work/upload/complete` | session | `{ key }` | `{ file }` — checked against its kind's size limit |
| POST | `/work/file-urls` | session | `{ keys }` | `{ urls: { key: url } }` — signed read links, one hour |
| POST | `/work/file/delete` | session | `{ key }` | `{ ok }` |
| GET | `/enrollments` | session | — | `{ courses }` |
| POST | `/enroll` | session | `{ course }` | `{ ok }` |
| POST | `/unenroll` | session | `{ course }` | `{ ok }` |

`profile` is `{ email, role, tester }`.

### The files behind the made things

Photos, films, decks, essays and recordings attached to a course's highlight
live in a private S3 bucket (`WorkBucket`, `<stack>-work`), never in DynamoDB.
The browser uploads straight to the bucket over a link the function signs
(`src/lib/files.mjs`); the record in the learner's work keeps only the keys.
Keys are `u/<hash of email>/<course>/<id>-<name>`, so a key carries no address.
Publishing an edition copies its files to `p/<handle>/<edition>/` and rewrites
the snapshot to site paths (`/work/p/...`), which the site's distribution
serves through its own origin access; the bucket policy allows it to read
`p/*` and nothing else. Unpublishing deletes the copies. Limits per file:
images 20 MB, PDF 40 MB, audio 60 MB, video 300 MB, text 1 MB.

### How the session travels

Two carriers are accepted, cookie first:

1. **`sdit_session` cookie** — `Secure; HttpOnly; SameSite=Lax`. This is the one
   browsers use, and it works because the site and this API share an origin
   behind CloudFront (`/api/*`). `HttpOnly` keeps it out of reach of page
   scripts, so an XSS bug cannot steal sessions the way it could when the token
   lived in `localStorage`.
2. **`Authorization: Bearer <token>`** — the fallback. Local development
   (`serve.py` on :3001) calls this API cross-origin, where a `SameSite` cookie
   is not sent.

`Lax` rather than `Strict` is deliberate: `Strict` withholds the cookie on
cross-site navigation, so a student following a lesson link out of The Daily
would arrive logged out. `Lax` still blocks the cross-site POST that CSRF
relies on.

Signing out is a request rather than a local delete — the page cannot clear a
cookie it is not permitted to read.

## Deploy

Prerequisites: an AWS account, the [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html),
and credentials configured (`aws configure`).

### First deploy only

```sh
cd account

# Pin the region to keep data in the US (this is the Cloudflare/Hong-Kong fix).
sam build
sam deploy --guided \
  --region us-west-2 \
  --parameter-overrides \
    SessionSecret="$(openssl rand -hex 32)" \
    MailFrom="" \
    AllowOrigin="https://learn.sandiegotech.org,http://localhost:3001"
```

The stack prints **`ApiUrl`** on success.

### Every deploy after that

> **Do not re-run the command above.** `openssl rand` mints a *new*
> `SessionSecret` each time, and that secret both signs sessions and hashes
> pending sign-in codes — rotating it signs out every student and invalidates
> every code in flight.

Redeploy reusing the parameters already on the stack. `SessionSecret` is
`NoEcho`, so CloudFormation can carry it forward without anyone reading it:

```sh
sam build
sam package \
  --s3-bucket aws-sam-cli-managed-default-samclisourcebucket-fjpqboao7kti \
  --region us-west-2 \
  --output-template-file /tmp/packaged.yaml

aws cloudformation update-stack \
  --stack-name sdit-account \
  --region us-west-2 \
  --template-body file:///tmp/packaged.yaml \
  --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
  --parameters \
    ParameterKey=SessionSecret,UsePreviousValue=true \
    ParameterKey=MailFrom,UsePreviousValue=true \
    ParameterKey=AllowOrigin,UsePreviousValue=true

aws cloudformation wait stack-update-complete \
  --stack-name sdit-account --region us-west-2
```

`CAPABILITY_AUTO_EXPAND` is required because this is a SAM template; without it
the call fails. Note that `wait` returns immediately if the stack is already
`UPDATE_COMPLETE`, so a failed `update-stack` followed by a successful `wait`
does **not** mean the deploy landed — check `LastUpdatedTime` moved.

To deliberately rotate the secret (which does sign everyone out), pass
`ParameterKey=SessionSecret,ParameterValue="$(openssl rand -hex 32)"` instead.

### Wire it to the site

Set the printed URL in [`../partials/header.html`](../partials/header.html):

```js
window.SDIT_ACCOUNT_API = "https://abc123.execute-api.us-west-2.amazonaws.com";
```

Until that is set, the site behaves exactly as before (localStorage only) and no
sign-in UI appears — so this can ship dark and be switched on when ready.

### Turn on real emails

While `MailFrom` is blank, sign-in codes are written to the function's
CloudWatch logs instead of emailed (good for first testing). To send for real:

1. Verify a domain or address in **SES** (same region), and move the account out
   of the SES sandbox so it can email anyone.
2. Redeploy with `MailFrom="no-reply@sandiegotech.org"`.

## Notes / next phases

- **Session storage.** The web client keeps the token in `localStorage` and
  sends it as a bearer header — simplest and CORS-friendly across subdomains.
  Phase 2 can move to an httpOnly cookie scoped to `.sandiegotech.org` once the
  API lives on that domain.
- **Passkeys & Sign in with Apple** slot in as additional `/auth/*` routes that
  end the same way: `signIn(email)` + `signSession(...)`.
- **AI is out of scope** here by design — bring-your-own-key lives elsewhere and
  is never the line between Visitor and Student.
