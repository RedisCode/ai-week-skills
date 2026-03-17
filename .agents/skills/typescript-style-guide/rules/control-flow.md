---
description: >-
  Rules for control flow statements, switch cases, equality checks, iteration,
  and spread operators in TypeScript.
metadata:
  tags: [control flow, switch, for-of, equality, iteration]
---

---
description: >-
  Rules for control flow statements, switch cases, equality checks,
  iteration, and spread operators in TypeScript.
metadata:
  tags: [control flow, switch, equality, for-of, iteration]
---

# Control Flow

## Control flow statements & blocks

Control flow statements spanning multiple lines always use blocks for the
containing code.

```ts
// Good
for (let i = 0; i < x; i++) {
    doSomethingWith(i);
    andSomeMore();
}
if (x) {
    doSomethingWithALongMethodName(x);
}
```

```ts
// Bad
if (x) x.doFoo();
for (let i = 0; i < x; i++) doSomethingWithALongMethodName(i);
```

The exception is that `if` statements fitting on one line may elide the block.

```ts
// Good
if (x) x.doFoo();
```

## Switch Statements

All `switch` statements must contain a `default` statement group, even if it
contains no code.

```ts
// Good
switch (x) {
    case Y:
        doSomethingElse();
        break;
    default:
    // nothing to do.
}
```

Non-empty statement groups (`case ...`) may not fall through (enforced by the
compiler):

```ts
// Bad
switch (x) {
    case X:
        doSomething();
    // fall through — not allowed!
    case Y:
    // ...
}
```

Empty statement groups are allowed to fall through:

```ts
// Good
switch (x) {
    case X:
    case Y:
        doSomething();
        break;
    default: // nothing to do.
}
```

## Equality Checks

Always use triple equals (`===`) and not equals (`!==`). The double equality
operators cause error prone type coercions that are hard to understand and
slower to implement for JavaScript VMs. See also the
[JavaScript equality table](https://dorey.github.io/JavaScript-Equality-Table/).

```ts
// Bad
if (foo == 'bar' || baz != bam) {
    // Hard to understand behaviour due to type coercion.
}
```

```ts
// Good
if (foo === 'bar' || baz !== bam) {
    // All good here.
}
```

**Exception**: Comparisons to the literal `null` value may use the `==` and `!=`
operators to cover both `null` and `undefined` values.

```ts
// Good
if (foo == null) {
    // Will trigger when foo is null or undefined.
}
```

## Iterating objects

Iterating objects with `for (... in ...)` is error prone. It will include
enumerable properties from the prototype chain.

Do not use unfiltered `for (... in ...)` statements:

```ts
// Bad
for (const x in someObj) {
    // x could come from some parent prototype!
}
```

Either filter values explicitly with an `if` statement, or use
`for (... of Object.keys(...))`.

```ts
// Good
for (const x in someObj) {
    if (!someObj.hasOwnProperty(x)) continue;
    // now x was definitely defined on someObj
}
for (const x of Object.keys(someObj)) {
    // note: for _of_!
}
for (const [key, value] of Object.entries(someObj)) {
    // note: for _of_!
}
```

## Iterating containers

Do not use `for (... in ...)` to iterate over arrays. It will counterintuitively
give the array's indices (as strings!), not values:

```ts
// Bad
for (const x in someArray) {
    // x is the index!
}
```

Use `for (... of someArr)` or vanilla `for` loops with indices to iterate over
arrays.

```ts
// Good
for (const x of someArr) {
    // x is a value of someArr.
}

for (let i = 0; i < someArr.length; i++) {
    // Explicitly count if the index is needed, otherwise use the for/of form.
    const x = someArr[i];
    // ...
}
for (const [i, x] of someArr.entries()) {
    // Alternative version of the above.
}
```

Do not use `Array.prototype.forEach`, `Set.prototype.forEach`, and
`Map.prototype.forEach`. They make code harder to debug and defeat some useful
compiler checks (e.g. reachability).

```ts
// Bad
someArr.forEach((item, index) => {
    someFn(item, index);
});
```

> Why? Consider this code:
>
> ```ts
> let x: string | null = 'abc';
> myArray.forEach(() => {
>     x.charAt(0);
> });
> ```
>
> You can recognize that this code is fine: `x` isn't null and it doesn't
> change before it is accessed. But the compiler cannot know that this
> `.forEach()` call doesn't hang on to the closure that was passed in and call
> it at some later point, maybe after `x` was set to null, so it flags this
> code as an error. The equivalent for-of loop is fine.

## Using the spread operator

Using the spread operator `[...foo]; {...bar}` is a convenient shorthand for
copying arrays and objects. When using the spread operator on objects, later
values replace earlier values at the same key.

```ts
// Good
const foo = {
    num: 1,
};

const foo2 = {
    ...foo,
    num: 5,
};

const foo3 = {
    num: 5,
    ...foo,
};

foo2.num === 5;
foo3.num === 1;
```

When using the spread operator, the value being spread must match what is being
created. That is, when creating an object, only objects may be used with the
spread operator; when creating an array, only spread iterables. Primitives,
including `null` and `undefined`, may never be spread.

```ts
// Bad
const foo = { num: 7 };
const bar = { num: 5, ...(shouldUseFoo && foo) }; // might be undefined

// Creates {0: 'a', 1: 'b', 2: 'c'} but has no length
const fooStrings = ['a', 'b', 'c'];
const ids = { ...fooStrings };
```

```ts
// Good
const foo = shouldUseFoo ? { num: 7 } : {};
const bar = { num: 5, ...foo };
const fooStrings = ['a', 'b', 'c'];
const ids = [...fooStrings, 'd', 'e'];
```
