# Architecture

## Platform summary

The source application is an internal marketing operations platform, not a consumer app. Its architecture is optimized for authenticated employees using a growing set of focused tools:

- marketing and campaign tools
- pipeline generation and outbound tools
- reporting and operator utilities
- brand and content tools

The important pattern is not the exact feature list. It is the shared container:

- one Next.js app
- one authentication boundary
- one common navigation system
- many independent tools with their own routes, APIs, and helper modules

## Core stack

- Next.js App Router
- React 19
- TypeScript
- Tailwind CSS 4
- shadcn/ui-style component primitives
- Auth.js v5 with Okta
- Neon Postgres for durable data and token vault records
- Redis for cache, shared settings, and coordination
- Vercel hosting and analytics

## How Basecamp is organized

The app behaves like an internal tool hub.

- Home page introduces Basecamp and shows role-based cards.
- Each role page exposes a curated subset of tools.
- Navigation dropdowns expose tools grouped into role-specific sections.
- Tool metadata is centralized in `lib/tools.ts`.
- Runtime overrides and custom ordering come from Redis-backed settings.

This means new features should usually be shaped as tools inside a hub, not as free-floating pages.

## Role model

The visible role buckets in the source app are:

- `marketers`
- `pipeline-generators`
- `operators`

If you are designing a new tool, decide first which role owns it. This affects placement, naming, copy, and whether the feature needs admin-only capabilities.

## Common feature shapes

### 1. Simple utility

Use this for deterministic inputs and outputs with limited persistence.

Examples from the source shape:

- name generators
- ID converters
- chunkers
- template-driven page/task creation

Recommended structure:

- one tool page
- one or more client components
- one or two route handlers
- small helper module under `lib/<feature>`

### 2. Integration-backed workflow

Use this when the tool reads or writes to SaaS platforms.

Examples in the source app:

- Asana task creation and calendar sync
- Salesforce-backed campaign or account workflows
- Outreach bulk operations
- Sanity page creation

Recommended structure:

- tool page
- integration gating
- server route handlers
- provider-specific helper modules
- token-vault-backed auth to external services

### 3. Run-oriented or operational workflow

Use this when work is multi-step, asynchronous, resumable, or reviewable later.

Examples in the source app:

- campaign runs
- lead agent runs
- import-list-cleaner histories

Recommended structure:

- tool page for new work
- run list page if users need history
- run detail page if users revisit output
- durable database records for each run

## Storage boundaries

Use the same mental model as the source app:

- Postgres for durable business records, users, run history, and encrypted token metadata
- Redis for app settings, feature flags, health-check caches, ordering overrides, and short-lived coordination state
- environment variables for platform secrets and provider credentials

If data must survive redeploys and support user history, it belongs in Postgres.
If data is operational, cached, or globally configurable, Redis is a better fit.

## Server-first design rule

The source app consistently keeps sensitive work on the server. Follow that pattern:

- API handlers verify the session again, even though middleware already protects routes.
- Provider tokens are resolved server-side.
- External API calls usually originate from route handlers or server-side helper code.
- Client components orchestrate UX, not secret handling.

## Tool design checklist

Before proposing implementation, answer these:

- Which role owns this tool?
- Is it a simple utility, integration workflow, or run-based workflow?
- Which systems does it touch?
- Does it need durable records?
- Does it need integration gating?
- Does it need admin-only views or actions?
- Does it need a recent-runs/history surface?
- Does it need audit logging, webhook handlers, or cron support?

## Recommended default deliverable

When someone asks for a Basecamp-bound app without the source repo, produce:

- a route tree
- a component tree
- a list of server helpers
- a list of route handlers
- a storage plan
- a secrets/integrations plan
- a role placement plan

That level of specificity is the closest substitute for direct codebase access.
