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
| POST | `/auth/verify` | — | `{ email, code }` | `{ token, profile }` |
| GET | `/me` | Bearer | — | `{ profile }` |
| GET | `/work` | Bearer | `?lesson=<path>` | `{ responses }` |
| PUT | `/work` | Bearer | `{ lesson, heading, content }` | `{ ok }` |

`profile` is `{ email, role, tester }`. The browser sends the session as
`Authorization: Bearer <token>`.

## Deploy

Prerequisites: an AWS account, the [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html),
and credentials configured (`aws configure`).

```sh
cd account

# Pin the region to keep data in the US (this is the Cloudflare/Hong-Kong fix).
sam build
sam deploy --guided \
  --region us-west-1 \
  --parameter-overrides \
    SessionSecret="$(openssl rand -hex 32)" \
    MailFrom="" \
    AllowOrigin="https://learn.sandiegotech.org,http://localhost:3001"
```

`--guided` saves your answers to `samconfig.toml`; later deploys are just
`sam deploy`. The stack prints **`ApiUrl`** on success.

### Wire it to the site

Set the printed URL in [`../partials/header.html`](../partials/header.html):

```js
window.SDIT_ACCOUNT_API = "https://abc123.execute-api.us-west-1.amazonaws.com";
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
