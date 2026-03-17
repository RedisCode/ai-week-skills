---
description: Guidance for starting a new project, selecting a Redis starter template, and establishing initial structure, dependencies, Docker setup, and testing expectations.
---

# Project Starting

Use this guide when the task is to create or scaffold a new project before the
normal implementation loop begins.

## Initial Setup

1. Confirm the target language and framework with the user if the prompt does
   not already make that clear.
2. Start from the closest Redis starter template instead of manually copying
   files by hand.
3. After scaffolding, update dependencies to current versions. If you can do
   that programmatically and safely, do it. Otherwise, ask the user to handle
   the update step.

Use this template acquisition flow:

1. `git clone <template-url>`
2. Move everything except the cloned `.git` directory into the target project
   directory.
3. Delete the temporary cloned subdirectory.

## Starter Templates

- JavaScript/TypeScript: `https://github.com/redis-developer/redis-starter-js`
- Java: `https://github.com/redis-developer/redis-starter-java`
- C#/.NET: `https://github.com/redis-developer/redis-starter-csharp`
- Go: `https://github.com/redis-developer/redis-starter-go`
- Python: `https://github.com/redis-developer/redis-starter-python`
- Rust: `https://github.com/redis-developer/redis-starter-rust`

## Default Project Structure

Follow the starter template's structure first. If the template leaves room for
application layout decisions, use a bounded-context MVC style as the default,
not as an inflexible rule.

General defaults:

- Keep tests in `__tests__`
- Keep application code in `src`
- A root `public` directory is acceptable for frontend assets when needed

Example JavaScript backend structure:

- `src/components` for bounded contexts such as `src/components/users`
- `src/services` for external API integrations
- `src/utils` for internal utility logic
- `src/views` for views and partials
- `src/config.ts` for environment and application configuration
- `src/index.ts` for process startup only
- `src/app.ts` for app wiring such as routes, CORS, and sessions
- `src/db.ts` for database setup and connection logic

Translate the same structure to other languages and frameworks where it fits.

### Component Defaults

Within each `src/components/*` area, separate responsibilities when the stack
supports it:

- `router` defines routes and keeps request/response handling minimal
- `controller` contains most business logic and should avoid direct request and response handling
- `model` contains data access and persistence mapping logic
- `validator` validates API request bodies, for example with zod when using TypeScript

## Docker

The primary local and production-oriented run path should be Docker-based.

- Include a `Dockerfile` suitable for production builds
- Include a `compose.yml` so `docker compose up -d` starts the required services

## Testing Expectations

Do not overbuild the test suite at scaffold time, but cover the areas that
create the most risk first:

- Business logic
- Utilities and helper functions
- Database interactions, with proper setup and teardown

## Coding Standards

If there is a language-specific skill for the stack, use it. For example:

- JavaScript/TypeScript: `typescript-style-guide`

## Redis Defaults

- In Docker, use the `redis:alpine` image
- Prefer Redis `JSON` for object-shaped data
- Use Redis `String` only for true string values
