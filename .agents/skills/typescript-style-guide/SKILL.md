---
name: typescript-style-guide
description: >-
  Use when writing or reviewing TypeScript code.
license: See LICENSE in repository root
metadata:
  author: redis
  version: "1.0"
  category: discipline
  triggers: TypeScript, TS, naming, imports, types, style, code review
---

# TypeScript Style Guide

Rules and best practices for writing TypeScript. Each section links to
a detailed rule file with full code examples.

## When to Use This Skill

- Writing new TypeScript code
- Reviewing TypeScript pull requests
- Refactoring existing TypeScript code
- Setting up a new TypeScript project

## Syntax

### [Identifiers](rules/identifiers.md)

| Style            | Category                                                           |
| ---------------- | ------------------------------------------------------------------ |
| `UpperCamelCase` | class / interface / type / enum / decorator / type parameters      |
| `lowerCamelCase` | variable / parameter / function / method / property / module alias |
| `CONSTANT_CASE`  | global constant values, including enum values                      |

Key rules:

- Treat abbreviations as whole words: `loadHttpUrl`, not ~~`loadHTTPURL`~~
- Do not use `_` as a prefix or suffix
- Do not use `#private` fields; use TypeScript's `private` keyword
- React components must be `UpperCamelCase`
- Do not decorate names with type info (no `IMyInterface`, no `opt_` prefix)
- Names must be descriptive and clear to new readers

### [Comments & Documentation](rules/comments-and-documentation.md)

- Use `/** JSDoc */` for documentation (user-facing)
- Use `// line comments` for implementation notes
- Document all top-level exports
- Omit comments redundant with TypeScript types (no `@param` types, no `@implements`)
- Do not use `@override`
- Place JSDoc before decorators, not between decorator and declaration
- Make comments add information; don't just restate parameter names
- Use UTF-8 encoding; use actual Unicode characters for non-ASCII

## Language Rules

### [Classes](rules/classes.md)

- Limit symbol visibility as much as possible
- Never use the `public` modifier except for non-readonly public parameter properties
- Always use parentheses in constructor calls: `new Foo()`, not `new Foo`
- Don't write empty constructors or constructors that just call `super()`
- Use `readonly` for properties never reassigned outside the constructor
- Use parameter properties instead of manual assignment
- Initialize fields where they're declared when possible
- Use semicolons (not commas) in interface/class member declarations

### [Functions](rules/functions.md)

- Use `function foo() {}` declarations for named functions
- Use arrow functions in expressions (callbacks, etc.)
- Only use expression body (`=>` without braces) when the return value is used
- Do not use `this` in regular functions; use arrow functions or explicit params
- Prefer wrapping instance method calls in arrow functions over arrow function properties

### [Variables & Primitives](rules/variables-and-primitives.md)

- Always use `const` or `let`, never `var`
- Use `const` by default; `let` only when reassignment is needed
- Always use `new Error()` (not bare `Error()`) for exceptions
- Do not instantiate wrapper classes (`new String()`, `new Boolean()`, `new Number()`)
- Do not use `Array()` constructor; use bracket notation or `Array.from()`
- Use `Number()` for parsing; always check for `NaN`
- Do not use unary `+` or `parseInt`/`parseFloat` (except for non-base-10)
- Do not rely on Automatic Semicolon Insertion; always use semicolons
- Always use `enum`, not `const enum`
- No `debugger` statements in production code
- Do not define new decorators; only use framework-provided ones

### [Control Flow](rules/control-flow.md)

- Multi-line control flow must use blocks `{ }`
- All `switch` statements must have a `default` case
- Always use `===` and `!==` (exception: `== null` to check both null/undefined)
- Use `for...of` or `Object.keys()`/`Object.entries()` instead of `for...in`
- Do not use `.forEach()`; use `for...of` loops
- Only spread matching types (objects into objects, iterables into arrays)

### [Type Safety](rules/type-safety.md)

- Do not use `@ts-ignore`
- Prefer runtime checks (`instanceof`, truthiness) over type assertions
- When assertions are necessary, use `as` syntax (not angle brackets)
- Use type annotations (`: Foo`) on object literals, not assertions (`as Foo`)
- Do not mix quoted and dotted property access

## Source Organization

### [Modules & Imports](rules/modules-and-imports.md)

- Use relative imports (`./foo`) within the same project
- Do not use `namespace`; use ES6 modules
- Do not use `require()`; use ES6 `import`
- Use `import type` / `export type` for type-only imports/exports

| Import type   | Example                          | Use for                                          |
| ------------- | -------------------------------- | ------------------------------------------------ |
| module        | `import * as foo from '...'`     | Large APIs where namespacing improves readability |
| destructuring | `import { Foo } from '...'`     | Commonly used symbols                            |
| default       | `import Foo from '...'`         | Only for external code that requires it           |
| side-effect   | `import '...'`                  | Libraries loaded for side effects only            |

### [Exports](rules/exports.md)

- Use named exports; do not use default exports
- Minimize the exported API surface
- Do not use `export let` (mutable exports)
- Do not create container classes with only static members; export functions/constants directly
- Organize packages by feature, not by type

## Type System

### [Type System Rules](rules/type-system.md)

- Rely on inference for trivially inferred types (`string`, `number`, `boolean`, `new` expressions)
- Add annotations when they improve readability or catch refactoring bugs
- Return type annotations are optional but can improve documentation
- Use optional fields/params (`?`) rather than `| undefined`
- Do not include `| null` or `| undefined` in type aliases
- Use `interface` for object shapes; `type` for unions, tuples, primitives
- Use `T[]` for simple types; `Array<T>` for complex types (unions, objects)
- Avoid `any`; prefer specific types, `unknown`, or documented suppression
- Use `Record<K, V>` or `Map`/`Set` over plain objects as associative arrays
- Never use wrapper types (`String`, `Boolean`, `Number`, `Object`)
- Avoid return-type-only generics
- Prefer simple types over complex mapped/conditional types when possible

## Consistency

For any style question not covered here, follow the conventions already in the
file, then the directory, then the project.
