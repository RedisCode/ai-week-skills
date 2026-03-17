---
description: >-
  Rules for type assertions, ts-ignore usage, runtime checks, and safe type
  narrowing in TypeScript.
metadata:
  tags: [type safety, assertions, ts-ignore, type narrowing, instanceof]
---

---
description: >-
  Rules for type assertions, ts-ignore, runtime checks, and safe
  property access in TypeScript.
metadata:
  tags: [type safety, assertions, ts-ignore, runtime checks]
---

# Type Safety

## `@ts-ignore`

Do not use `@ts-ignore`. It superficially seems to be an easy way to "fix" a
compiler error, but in practice, a specific compiler error is often caused by a
larger problem that can be fixed more directly.

For example, if you are using `@ts-ignore` to suppress a type error, then it's
hard to predict what types the surrounding code will end up seeing. For many
type errors, the advice in [how to best use `any`](type-system.md#any-type) is
useful.

## Type and Non-nullability Assertions

Type assertions (`x as SomeType`) and non-nullability assertions (`y!`) are
unsafe. Both only silence the TypeScript compiler, but do not insert any runtime
checks to match these assertions, so they can cause your program to crash at
runtime.

Because of this, you _should not_ use type and non-nullability assertions
without an obvious or explicit reason for doing so.

Instead of the following:

```ts
// Bad
(x as Foo).foo();

y!.bar();
```

When you want to assert a type or non-nullability the best answer is to
explicitly write a runtime check that performs that check.

```ts
// Good
// assuming Foo is a class.
if (x instanceof Foo) {
    x.foo();
}

if (y) {
    y.bar();
}
```

Sometimes due to some local property of your code you can be sure that the
assertion form is safe. In those situations, you _should_ add clarification to
explain why you are ok with the unsafe behavior:

```ts
// Good — with justification
// x is a Foo, because ...
(x as Foo).foo();

// y cannot be null, because ...
y!.bar();
```

If the reasoning behind a type or non-nullability assertion is obvious, the
comments may not be necessary. For example, generated proto code is always
nullable, but perhaps it is well-known in the context of the code that certain
fields are always provided by the backend. Use your judgement.

## Type Assertions Syntax

Type assertions must use the `as` syntax (as opposed to the angle brackets
syntax). This enforces parentheses around the assertion when accessing a member.

```ts
// Bad
const x = (<Foo>z).length;
const y = <Foo>z.length;
```

```ts
// Good
const x = (z as Foo).length;
```

## Type Assertions and Object Literals

Use type annotations (`: Foo`) instead of type assertions (`as Foo`) to specify
the type of an object literal. This allows detecting refactoring bugs when the
fields of an interface change over time.

```ts
// Bad
interface Foo {
    bar: number;
    baz?: string; // was "bam", but later renamed to "baz".
}

const foo = {
    bar: 123,
    bam: 'abc', // no error!
} as Foo;

function func() {
    return {
        bar: 123,
        bam: 'abc', // no error!
    } as Foo;
}
```

```ts
// Good
interface Foo {
    bar: number;
    baz?: string;
}

const foo: Foo = {
    bar: 123,
    bam: 'abc', // complains about "bam" not being defined on Foo.
};

function func(): Foo {
    return {
        bar: 123,
        bam: 'abc', // complains about "bam" not being defined on Foo.
    };
}
```

## Property access consistency

Code must not mix quoted property access with dotted property access:

```ts
// Bad — code must use either non-quoted or quoted access for any property
// consistently across the entire application:
console.log(x['someField']);
console.log(x.someField);
```

```ts
// Good — declaring an interface
declare interface ServerInfoJson {
    appVersion: string;
    user: UserJson;
}
const data = JSON.parse(serverResponse) as ServerInfoJson;
console.log(data.appVersion); // Type safe & renaming safe!
```

## Module object imports

When importing a module object, directly access properties on the module object
rather than passing it around. This ensures that modules can be analyzed and
optimized. Treating module imports as namespaces is fine.

```ts
// Good
import { method1, method2 } from 'utils';
class A {
    readonly utils = { method1, method2 };
}
```

```ts
// Bad
import * as utils from 'utils';
class A {
    readonly utils = utils;
}
```
