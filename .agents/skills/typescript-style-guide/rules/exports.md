---
description: >-
  Rules for named exports, API surface minimization, and module organization
  in TypeScript.
metadata:
  tags: [exports, named exports, API surface, modules]
---

---
description: >-
  Rules for named exports, API surface minimization, and module
  organization in TypeScript.
metadata:
  tags: [exports, named exports, API surface, modules]
---

# Exports

## Named exports

Use named exports in all code:

```ts
// Good
export class Foo { ... }
```

Do not use default exports. This ensures that all imports follow a uniform
pattern.

```ts
// Bad
export default class Foo { ... }
```

> Why? Default exports provide no canonical name, which makes central
> maintenance difficult with relatively little benefit to code owners,
> including potentially decreased readability:
>
> ```ts
> import Foo from './bar'; // Legal.
> import Bar from './bar'; // Also legal.
> ```
>
> Named exports have the benefit of erroring when import statements try to
> import something that hasn't been declared. Additionally, default exports
> encourage people to put everything into one big object to namespace it all
> together, which is unnecessary when file scope already provides namespacing.

## Export visibility

TypeScript does not support restricting the visibility for exported symbols.
Only export symbols that are used outside of the module. Generally minimize the
exported API surface of modules.

## Mutable Exports

Regardless of technical support, mutable exports can create hard to understand
and debug code, in particular with re-exports across multiple modules. One way
to paraphrase this style point is that `export let` is not allowed.

```ts
// Bad
export let foo = 3;
// In pure ES6, foo is mutable and importers will observe the value change after a second.
// In TS, if foo is re-exported by a second file, importers will not see the value change.
window.setTimeout(() => {
    foo = 4;
}, 1000 /* ms */);
```

If one needs to support externally accessible and mutable bindings, they should
instead use explicit getter functions.

```ts
// Good
let foo = 3;
window.setTimeout(() => {
    foo = 4;
}, 1000 /* ms */);
// Use an explicit getter to access the mutable export.
export function getFoo() {
    return foo;
}
```

For the common pattern of conditionally exporting either of two values, first do
the conditional check, then the export. Make sure that all exports are final
after the module's body has executed.

```ts
// Good
function pickApi() {
    if (useOtherApi()) return OtherApi;
    return RegularApi;
}
export const SomeApi = pickApi();
```

## Container Classes

Do not create container classes with static methods or properties for the sake
of namespacing.

```ts
// Bad
export class Container {
    static FOO = 1;
    static bar() {
        return 1;
    }
}
```

Instead, export individual constants and functions:

```ts
// Good
export const FOO = 1;
export function bar() {
    return 1;
}
```

## Organize By Feature

Organize packages by feature, not by type. For example, an online shop _should_
have packages named `products`, `checkout`, `backend`, not ~~`views`, `models`,
`controllers`~~.
