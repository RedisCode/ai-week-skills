---
name: agent-coding-guide
description: >-
  Use when the user asks for a code change, new feature, bug fix, refactor, or
  to start or scaffold a new project.
license: See LICENSE in repository root
metadata:
  author: redis
  version: "1.0"
  category: discipline
  triggers: code change, new feature, bug fix, refactor, new project, scaffold, project setup, template, starter, tests
---

# Agent Coding Guide

Follow this workflow for every coding prompt. Do not skip steps.

## Project-Start Branch

If the prompt is about starting or scaffolding a project, first read
[`references/project-starting.md`](references/project-starting.md). Use that
guide to choose the template, establish the initial structure, and set up
dependencies. Then continue with the workflow below for planning, implementation,
and verification.

## Phase 1: Understand

1. **Read the prompt carefully.** Identify what is being asked — new feature, bug fix, refactor, etc.
2. **Ask clarifying questions** before writing any code if the requirements are ambiguous. Don't guess at business logic.
3. **Search the codebase** for existing patterns, conventions, and related code. Read every file you plan to change *before* changing it.

## Phase 2: Plan

Before writing any code, produce a **file-by-file plan** and share it with the user.

The plan should list:

- **Each file** that will be created or modified
- **What changes** will be made in that file and why
- **The order** you will work through the files

Structure the plan like this:

```
Plan:
1. `src/components/users/user.test.ts` — Add failing test for <feature>
2. `src/components/users/controller.ts` — Implement <feature> to make the test pass
3. `src/components/users/router.ts` — Wire up the new endpoint
...
```

Test files always come first in the plan. If the user disagrees with the plan, revise it before proceeding.

## Phase 3: Red/Green TDD

Follow the red/green TDD cycle for every meaningful change:

### Step 1: Run existing tests (baseline)

Run the project's test suite *before* making any changes. This establishes a green baseline and reveals any pre-existing failures you need to be aware of.

```
# Example
npm test          # JS/TS
pytest             # Python
go test ./...      # Go
cargo test         # Rust
dotnet test        # C#
```

If tests fail before you've changed anything, notify the user and decide how to proceed.

### Step 2: Red — write a failing test

Write a test that describes the desired behavior. Run it and confirm it **fails**. If it passes immediately, the test is not adding value — reconsider what you're testing.

### Step 3: Green — write the minimum code to pass

Implement only enough production code to make the failing test pass. Do not add behavior that is not covered by a test.

### Step 4: Refactor

With tests green, improve the code's structure. Re-run tests after refactoring to confirm nothing broke.

### Step 5: Repeat

Continue the red/green cycle for each piece of behavior in your plan.

## Phase 4: Verify

1. **Run the full test suite** one final time to confirm everything passes.
2. **Review your own diff** — check for leftover debug code, commented-out lines, and unnecessary changes.
3. **Summarize what you did** to the user, noting any deviations from the plan.

## Rules

- **Never edit a file you haven't read first.** Always read the current contents before making changes.
- **Never skip tests.** If the project has no test infrastructure, set it up before writing feature code.
- **Keep changes minimal.** Only touch files that are necessary for the task. Don't refactor unrelated code unless asked.
- **Follow existing conventions.** Match the naming, formatting, and architectural patterns already in the codebase. If a language-specific style skill exists (e.g. `typescript-style-guide`), follow it.

## Rationalization Table

**Violating the letter of these rules is violating the spirit of the rules.**

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. A test takes 30 seconds to write. |
| "I'll add tests after" | Tests that pass immediately prove nothing about intent. Tests-first define *what should happen*; tests-after confirm *what already happened*. |
| "The task is small, no plan needed" | Small tasks still touch multiple files. A one-line plan takes 10 seconds and prevents wasted work. |
| "I already know what to change" | Reading the file first catches stale assumptions. ALWAYS read before editing. |
| "I'll just refactor this unrelated code while I'm here" | Out-of-scope changes introduce risk. Only touch what the task requires. |
| "The user seems in a hurry" | Skipping steps costs more time when bugs surface later. The process IS the shortcut. |

## Red Flags — STOP and Correct Course

If you catch yourself doing any of these, stop immediately:

- Writing implementation code before a failing test exists
- Editing a file you haven't read yet
- Starting to code without sharing a plan
- Thinking "this is different because..."
- Skipping the baseline test run

**All of these mean**: go back to the phase you skipped. Do not continue forward.

## Edge Cases

1. **No test framework exists** — Set up a minimal test runner appropriate for the language before proceeding with TDD. Confirm the choice with the user.
2. **The task is a new project or scaffold** — Start with [`references/project-starting.md`](references/project-starting.md). Greenfield work still requires a plan. Apply TDD once runnable code and test infrastructure exist.
3. **The task is purely config/docs** — TDD does not apply. Still read before editing and present a plan.
4. **Existing tests are broken** — Report the failures to the user before making changes. Don't silently fix unrelated tests unless asked.
5. **Large task with many files** — Break the plan into phases. Confirm each phase with the user before moving to the next.
