---
description: >-
  Rules for variable declarations, const/let usage, error handling, enums,
  and primitive type usage in TypeScript.
metadata:
  tags: [variables, const, let, enums, primitives, errors]
---

---
description: >-
  Rules for variable declarations, const/let usage, error construction,
  enums, and primitive type handling in TypeScript.
metadata:
  tags: [variables, const, let, enum, primitives, errors]
---

# Variables & Primitives

## Variables

Always use `const` or `let` to declare variables. Use `const` by default, unless
a variable needs to be reassigned. Never use `var`.

```ts
// Good
const foo = otherValue; // Use if "foo" never changes.
let bar = someValue; // Use if "bar" is ever assigned into later on.
```

`const` and `let` are block scoped, like variables in most other languages.
`var` in JavaScript is function scoped, which can cause difficult to understand
bugs. Don't use it.

```ts
// Bad
var foo = someValue; // Don't use — var scoping is complex and causes bugs.
```

Variables must not be used before their declaration.

## Exceptions

Always use `new Error()` when instantiating exceptions, instead of just calling
`Error()`. Both forms create a new `Error` instance, but using `new` is more
consistent with how other objects are instantiated.

```ts
// Good
throw new Error('Foo is not a valid bar.');
```

```ts
// Bad
throw Error('Foo is not a valid bar.');
```

## Primitive Types & Wrapper Classes

TypeScript code must not instantiate the wrapper classes for the primitive types
`String`, `Boolean`, and `Number`. Wrapper classes have surprising behaviour,
such as `new Boolean(false)` evaluating to `true`.

```ts
// Bad
const s = new String('hello');
const b = new Boolean(false);
const n = new Number(5);
```

```ts
// Good
const s = 'hello';
const b = false;
const n = 5;
```

## Array constructor

TypeScript code must not use the `Array()` constructor, with or without `new`.
It has confusing and contradictory usage:

```ts
// Bad
const a = new Array(2); // [undefined, undefined]
const b = new Array(2, 3); // [2, 3];
```

Instead, always use bracket notation to initialize arrays, or `from` to
initialize an `Array` with a certain size:

```ts
// Good
const a = [2];
const b = [2, 3];

// Equivalent to Array(2):
const c = [];
c.length = 2;

// [0, 0, 0, 0, 0]
Array.from<number>({ length: 5 }).fill(0);
```

## Type coercion

TypeScript code may use the `String()` and `Boolean()` (note: no `new`!)
functions, string template literals, or `!!` to coerce types.

```ts
// Good
const bool = Boolean(false);
const str = String(aNumber);
const bool2 = !!str;
const str2 = `result: ${bool2}`;
```

Using string concatenation to cast to string is discouraged, as we check that
operands to the plus operator are of matching types.

Code must use `Number()` to parse numeric values, and _must_ check its return
for `NaN` values explicitly, unless failing to parse is impossible from context.

Note: `Number('')`, `Number(' ')`, and `Number('\t')` would return `0` instead
of `NaN`. `Number('Infinity')` and `Number('-Infinity')` would return `Infinity`
and `-Infinity` respectively. These cases may require special handling.

```ts
// Good
const aNumber = Number('123');
if (isNaN(aNumber)) throw new Error(...);  // Handle NaN if the string might not contain a number
assertFinite(aNumber, ...);                // Optional: if NaN cannot happen because it was validated before.
```

Code must not use unary plus (`+`) to coerce strings to numbers. Parsing numbers
can fail, has surprising corner cases, and can be a code smell (parsing at the
wrong layer). A unary plus is too easy to miss in code reviews given this.

```ts
// Bad
const x = +y;
```

Code must also not use `parseInt` or `parseFloat` to parse numbers, except for
non-base-10 strings (see below). Both of those functions ignore trailing
characters in the string, which can shadow error conditions (e.g. parsing
`12 dwarves` as `12`).

```ts
// Bad
const n = parseInt(someString, 10); // Error prone,
const f = parseFloat(someString); // regardless of passing a radix.
```

Code that must parse using a radix _must_ check that its input is a number
before calling into `parseInt`;

```ts
// Good
if (!/^[a-fA-F0-9]+$/.test(someString)) throw new Error(...);
// Needed to parse hexadecimal.
const n = parseInt(someString, 16);  // Only allowed for radix != 10
```

Use `Number()` followed by `Math.floor` or `Math.trunc` (where available) to
parse integer numbers:

```ts
// Good
let f = Number(someString);
if (isNaN(f)) handleError();
f = Math.floor(f);
```

Do not use explicit boolean coercions in conditional clauses that have implicit
boolean coercion. Those are the conditions in an `if`, `for` and `while`
statements.

```ts
// Bad
const foo: MyInterface|null = ...;
if (!!foo) {...}
while (!!foo) {...}
```

```ts
// Good
const foo: MyInterface|null = ...;
if (foo) {...}
while (foo) {...}
```

Code may use explicit comparisons:

```ts
// Good
// Explicitly comparing > 0 is OK:
if (arr.length > 0) {...}
// so is relying on boolean coercion:
if (arr.length) {...}
```

## Automatic Semicolon Insertion

Do not rely on Automatic Semicolon Insertion (ASI). Explicitly terminate all
statements using a semicolon. This prevents bugs due to incorrect semicolon
insertions and ensures compatibility with tools with limited ASI support.

## Debugger statements

Debugger statements must not be included in production code.

```ts
// Bad
function debugMe() {
    debugger;
}
```

## Enums

Always use `enum` and not `const enum`. TypeScript enums already cannot be
mutated; `const enum` is a separate language feature related to optimization
that makes the enum invisible to JavaScript users of the module.

## Decorators

Decorators are syntax with an `@` prefix, like `@MyDecorator`.

Do not define new decorators. Only use the decorators defined by frameworks
(e.g. Angular, NestJS, TypeORM, etc.).

When using decorators, the decorator must immediately precede the symbol it
decorates, with no empty lines between:

```ts
/** JSDoc comments go before decorators */
@Component({...})  // Note: no empty line after the decorator.
class MyComp {
  @Input() myField: string;  // Decorators on fields may be on the same line...

  @Input()
  myOtherField: string;  // ... or wrap.
}
```
