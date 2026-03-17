# Integration And Security

## Baseline security model

Basecamp is an authenticated internal system with defense in depth.

- Middleware protects nearly all app routes.
- API handlers verify the session again before doing work.
- Admin capabilities are explicitly allowlisted.
- OAuth tokens are stored in an encrypted token vault.
- Webhooks and cron endpoints are excluded from user auth and protected separately.

If you design a new Basecamp-bound tool, start from this posture unless the user explicitly wants a simpler prototype.

## Auth pattern

The source app uses Auth.js with Okta as the identity provider and JWT sessions.

Carry these forward:

- SSO-first sign-in
- authenticated internal routes by default
- session user includes stable identity fields such as the Okta subject and email
- per-handler `401` responses when session checks fail

Do not rely on middleware alone for sensitive routes.

## OAuth integration pattern

Several tools require per-user connections to providers such as:

- Salesforce
- Google
- Asana
- Outreach
- Glean
- Goldcast

The source pattern is:

1. user authorizes the integration
2. tokens are stored server-side in an encrypted vault
3. tool pages query a shared integrations endpoint
4. required integrations are gated in the UI before the workflow begins
5. server helpers refresh or probe tokens as needed

This pattern is preferable to embedding provider-specific auth logic inside each feature page.

## Token vault model

The source app uses envelope encryption:

- plaintext token encrypted with AES-256-GCM
- per-token DEK wrapped with RSA-OAEP
- encrypted artifacts stored in Postgres
- RSA keys kept in environment variables, not in the database

You do not need to reproduce the exact crypto implementation for every mockup, but you should preserve these design principles:

- no plaintext tokens in the database
- no tokens in client state beyond the current request
- no provider secrets committed to source
- server-side refresh and storage only

## Settings and cache

The source app uses Redis for app-wide settings and health-check caching.

Good Redis use cases in Basecamp-style apps:

- feature flags
- tool visibility
- role-based ordering
- integration health cache
- short-lived coordination state

Bad Redis use cases:

- sole storage for durable run history
- replacing a token vault
- storing secrets without an explicit security model

## Handler design

A good Basecamp-style route handler usually:

- checks auth immediately
- validates request payloads
- delegates business logic to `lib/`
- talks to external providers from the server
- stores or updates durable records
- returns structured JSON errors

If the feature is expensive, asynchronous, or operationally meaningful, also decide:

- should this action create a run record?
- should it log an audit event?
- should it be rate-limited?
- should only admins be able to invoke it?

## Admin model

The source app uses an email allowlist for admin access. The exact implementation can vary, but the pattern matters:

- normal users only see or mutate their own data
- admins may access global views or trigger broader actions
- admin entry points are visible but scoped

Use admin-only actions sparingly and clearly.

## Webhooks and cron

The source app has public machine-to-machine endpoints for:

- Slack events
- Marketo or similar webhooks
- Okta event hooks
- Vercel audit and log drains
- scheduled cleanup and sync jobs

These should not use user-session auth. Protect them with one of:

- bearer secrets
- HMAC signatures
- provider-specific verification

Also keep them outside the normal middleware matcher if they must be callable by external services.

## Environment model

A Basecamp-style tool often needs env vars from a few groups:

- SSO: Okta and Auth.js secrets
- database: Postgres connection
- token vault: encryption key material
- shared callback origin for OAuth
- provider credentials: Salesforce, Asana, Google, Outreach, Glean, Sanity, Slack
- app infrastructure: Redis, cron secret, logging secrets, audit secrets
- AI services: OpenAI or gateway credentials

When proposing a new tool, list only the env vars that tool actually needs. Do not dump every possible secret unless the user asked for a full platform setup.

## Anti-patterns to reject

- browser-side calls to privileged provider APIs
- plaintext refresh tokens in a table
- exposing tools before checking required integrations
- mixing webhook auth with user auth
- storing all state in one place because it is convenient
- building a public-facing onboarding flow when the app is internal-only

## Security checklist for a new tool

- page protected by SSO
- API handlers re-check auth
- role and admin expectations defined
- provider access remains server-side
- integration prerequisites surfaced in the UI
- durable vs cached data split is explicit
- background endpoints have machine auth
- errors avoid leaking secrets or raw provider payloads
