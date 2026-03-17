---
name: basecamp-internal-apps
description: Use when designing, scaffolding, extending, or reviewing internal marketing applications, tools, or workflows that are intended to live inside Basecamp or be merged into the Basecamp platform, especially when the builder does not have access to the original Basecamp codebase and needs concrete guidance on architecture, routing, UI conventions, auth, integrations, storage, and delivery standards.
---

# Basecamp Internal Apps

This skill captures the recurring patterns from the `marketing_basecamp` application so you can design Basecamp-compatible tools without direct repo access.

## What to assume by default

- The target platform is a Next.js App Router application deployed on Vercel.
- The implementation language is TypeScript with React 19.
- Styling uses Tailwind CSS plus shadcn/ui-style primitives.
- Authentication is mandatory and usually handled with Auth.js plus Okta SSO.
- Sensitive work happens server-side in route handlers or server components.
- Internal tools are grouped by role, exposed through navigation, and often depend on external SaaS integrations.
- Redis is used for cache, shared app settings, and lightweight coordination.
- Postgres is used for durable records and encrypted token storage.

## Read these references selectively

- For overall platform shape, tool categories, storage boundaries, and app-planning heuristics, read [references/architecture.md](references/architecture.md).
- For route naming, page shells, navigation registration, and UI behavior, read [references/ui-and-routing.md](references/ui-and-routing.md).
- For auth, OAuth, token vault, settings, webhooks, and operational safeguards, read [references/integration-security.md](references/integration-security.md).

## Standard workflow

1. Define the tool in product terms first.
   Capture the target user role, core job to be done, inputs, outputs, systems touched, whether work is synchronous or long-running, and what data is sensitive.

2. Choose the simplest Basecamp shape that fits.
   Prefer a small utility tool if the task is deterministic.
   Use an integration-backed workflow if the app must read or write to Salesforce, Asana, Google, Outreach, Sanity, Slack, or similar systems.
   Use a run-based model if the work can take time, must be resumed later, or needs an audit trail.

3. Default to Basecamp's security posture.
   Protect every page with SSO.
   Re-check auth inside every API handler.
   Keep access tokens, refresh tokens, and provider credentials off the client.
   If third-party OAuth is required, store tokens in an encrypted vault pattern rather than plain database fields.

4. Design the route tree before writing code.
   A typical feature includes:
   - `app/tools/<slug>/page.tsx`
   - optional `app/tools/<slug>/layout.tsx`
   - `components/<feature>/...`
   - `lib/<feature>/...`
   - `app/api/<feature>/.../route.ts`
   Add run pages or admin pages only if the feature truly needs them.

5. Keep the page route thin.
   Tool pages in Basecamp usually provide the shell, heading, icon, short description, and one feature component. Put provider calls, data transforms, and validation in `lib/` or server handlers.

6. Gate integrations explicitly.
   If the tool depends on Salesforce, Asana, Google, Outreach, Glean, or another provider, block usage until the required connections are present and healthy. Do not let the user get halfway through the flow before revealing missing OAuth dependencies.

7. Register the tool for discovery.
   New tools are not "done" until they are added to the correct role bucket, named clearly, given a short description, assigned an icon, and wired into navigation or role landing pages.

8. Define operational behavior.
   Decide which state belongs in Redis, which belongs in Postgres, what must be logged, which failures should surface to the user, and whether admins need broader visibility or override capabilities.

9. Deliver merge-ready output.
   When asked to propose or scaffold a tool, include:
   - the route tree
   - the env vars and integrations required
   - the storage plan
   - the auth and RBAC expectations
   - the API contracts
   - the user-facing states: empty, loading, success, error, disconnected integration

## Output expectations when using this skill

When you design a new Basecamp-bound application, return a concrete implementation plan, not generic app advice. Prefer this structure:

- One-paragraph summary of the tool and who it serves.
- Proposed route tree.
- Required integrations and secrets.
- Data model or persisted records.
- API handler list with request and response shape.
- UI states and gating behavior.
- Risks, missing assumptions, and the easiest first slice to build.

## Rules worth enforcing

- Do not invent a public, anonymous product model. Basecamp is an authenticated internal operations platform.
- Do not put provider secrets, OAuth tokens, or long-lived credentials in client components.
- Do not call external APIs directly from the browser when the server can broker the request.
- Do not skip role placement and navigation registration.
- Do not collapse durable data, cached state, and secrets into one storage system.
- Do not propose visual styles that ignore the existing dark brand system unless the user explicitly wants a departure.

## When a user wants actual code

If the user asks to scaffold a feature, implement a Basecamp-style slice directly:

- create the route shell under `app/tools/<slug>`
- create feature components under `components/`
- create server helpers under `lib/`
- create authenticated handlers under `app/api/`
- add the tool definition to the appropriate registry
- include only the minimal required env vars and integration plumbing for the requested slice

If the user asks for planning only, stay at the design level but remain specific enough that another engineer could implement the feature without the original repo.
