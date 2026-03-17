---
description: >-
  Rules for type inference, annotations, interfaces vs type aliases, generics,
  and avoiding any in TypeScript.
metadata:
  tags: [type system, inference, interfaces, generics, any, unknown]
---

---
description: >-
  Rules for type inference, annotations, interfaces vs type aliases,
  generics, and avoiding any in TypeScript.
metadata:
  tags: [type system, inference, interfaces, generics, any, unknown]
---

# Type System

## Type Inference

Code may rely on type inference as implemented by the TypeScript compiler for
all type expressions (variables, fields, return types, etc).

```ts
// Good
const x = 15; // Type inferred.
```

Leave out type annotations for trivially inferred types: variables or parameters
initialized to a `string`, `number`, `boolean`, `RegExp` literal or `new`
expression.

```ts
// Bad
const x: boolean = true; // 'boolean' here does not aid readability
```

```ts
// Bad
const x: Set<string> = new Set(); // 'Set' is trivially inferred from the initialization
```

```ts
// Good
const x = new Set<string>();
```

For more complex expressions, type annotations can help with readability of the
program. Whether an annotation is required is decided by the code reviewer.

### Return types

Whether to include return type annotations for functions and methods is up to
the code author. Reviewers _may_ ask for annotations to clarify complex return
types that are hard to understand. Projects _may_ have a local policy to always
require return types, but this is not a general TypeScript style requirement.

There are two benefits to explicitly typing out the implicit return values of
functions and methods:

- More precise documentation to benefit readers of the code.
- Surface potential type errors faster in the future if there are code changes
  that change the return type of the function.

## Null vs Undefined

TypeScript supports `null` and `undefined` types. Nullable types can be
constructed as a union type (`string|null`); similarly with `undefined`. There
is no special syntax for unions of `null` and `undefined`.

TypeScript code can use either `undefined` or `null` to denote absence of a
value, there is no general guidance to prefer one over the other. Many
JavaScript APIs use `undefined` (e.g. `Map.get`), while many DOM APIs use
`null` (e.g. `Element.getAttribute`), so the appropriate absent value depends
on the context.

### Nullable/undefined type aliases

Type aliases _must not_ include `|null` or `|undefined` in a union type.
Nullable aliases typically indicate that null values are being passed around
through too many layers of an application, and this clouds the source of the
original issue that resulted in `null`. They also make it unclear when specific
values on a class or interface might be absent.

Instead, code _must_ only add `|null` or `|undefined` when the alias is actually
used. Code _should_ deal with null values close to where they arise.

```ts
// Bad
type CoffeeResponse = Latte|Americano|undefined;

class CoffeeService {
  getLatte(): CoffeeResponse { ... };
}
```

```ts
// Better
type CoffeeResponse = Latte|Americano;

class CoffeeService {
  getLatte(): CoffeeResponse|undefined { ... };
}
```

```ts
// Best
type CoffeeResponse = Latte | Americano;

class CoffeeService {
    getLatte(): CoffeeResponse {
        return assert(fetchResponse(), 'Coffee maker is broken, file a ticket');
    }
}
```

### Optionals vs `|undefined` type

TypeScript supports a special construct for optional parameters and fields,
using `?`:

```ts
interface CoffeeOrder {
  sugarCubes: number;
  milk?: Whole|LowFat|HalfHalf;
}

function pourCoffee(volume?: Milliliter) { ... }
```

Optional parameters implicitly include `|undefined` in their type. However, they
are different in that they can be left out when constructing a value or calling
a method. For example, `{sugarCubes: 1}` is a valid `CoffeeOrder` because `milk`
is optional.

Use optional fields (on interfaces or classes) and parameters rather than a
`|undefined` type.

For classes preferably avoid this pattern altogether and initialize as many
fields as possible.

```ts
// Good
class MyClass {
    field = '';
}
```

## Structural Types vs Nominal Types

TypeScript's type system is structural, not nominal. That is, a value matches a
type if it has at least all the properties the type requires and the properties'
types match, recursively.

Use structural typing where appropriate in your code. Outside of test code, use
interfaces to define structural types, not classes. In test code it can be
useful to have mock implementations structurally match the code under test
without introducing an extra interface.

When providing a structural-based implementation, explicitly include the type at
the declaration of the symbol (this allows more precise type checking and error
reporting).

```ts
// Good
const foo: Foo = {
    a: 123,
    b: 'abc',
};
```

```ts
// Bad
const badFoo = {
    a: 123,
    b: 'abc',
};
```

> Why? The "badFoo" object above relies on type inference. Additional fields
> could be added to "badFoo" and the type is inferred based on the object
> itself. When passing a "badFoo" to a function that takes a "Foo", the error
> will be at the function call site, rather than at the object declaration
> site.

## Interfaces vs Type Aliases

TypeScript supports
[type aliases](https://www.typescriptlang.org/docs/handbook/advanced-types.html#type-aliases)
for naming a type expression. This can be used to name primitives, unions,
tuples, and any other types.

However, when declaring types for objects, use interfaces instead of a type
alias for the object literal expression.

```ts
// Good
interface User {
    firstName: string;
    lastName: string;
}
```

```ts
// Bad
type User = {
    firstName: string;
    lastName: string;
};
```

> Why? These forms are nearly equivalent, so under the principle of just
> choosing one out of two forms to prevent variation, we should choose one.
> Additionally, there are
> [interesting technical reasons to prefer interface](https://ncjamieson.com/prefer-interfaces/).

## `Array<T>` Type

For simple types (containing just alphanumeric characters and dot), use the
syntax sugar for arrays, `T[]`, rather than the longer form `Array<T>`.

For anything more complex, use the longer form `Array<T>`.

This also applies for `readonly T[]` vs `ReadonlyArray<T>`.

```ts
// Good
const a: string[];
const b: readonly string[];
const c: ns.MyObj[];
const d: Array<string | number>;
const e: ReadonlyArray<string | number>;
```

```ts
// Bad
const f: Array<string>; // the syntax sugar is shorter
const g: ReadonlyArray<string>;
const h: { n: number; s: string }[]; // the braces/parens make it harder to read
const i: (string | number)[];
const j: readonly (string | number)[];
```

## Indexable (`{[key: string]: number}`) Type

In JavaScript, it's common to use an object as an associative array (aka "map",
"hash", or "dict"):

```ts
const fileSizes: { [fileName: string]: number } = {};
fileSizes['readme.txt'] = 541;
```

In TypeScript, provide a meaningful label for the key. (The label only exists
for documentation; it's unused otherwise.)

```ts
// Bad
const users: {[key: string]: number} = ...;
```

```ts
// Good
const users: {[userName: string]: number} = ...;
```

> Rather than using one of these, consider using the ES6 `Map` and `Set` types
> instead. JavaScript objects have
> [surprising undesirable behaviors](http://2ality.com/2012/01/objects-as-maps.html)
> and the ES6 types more explicitly convey your intent. Also, `Map`s can be
> keyed by—and `Set`s can contain—types other than `string`.

TypeScript's builtin `Record<Keys, ValueType>` type allows constructing types
with a defined set of keys. This is distinct from associative arrays in that the
keys are statically known.

## Mapped & Conditional Types

TypeScript's
[mapped types](https://www.typescriptlang.org/docs/handbook/advanced-types.html#mapped-types)
and
[conditional types](https://www.typescriptlang.org/docs/handbook/advanced-types.html#conditional-types)
allow specifying new types based on other types. TypeScript's standard library
includes several type operators based on these (`Record`, `Partial`, `Readonly`
etc).

These type system features allow succinctly specifying types and constructing
powerful yet type safe abstractions. They come with a number of drawbacks
though:

- Compared to explicitly specifying properties and type relations (e.g. using
  interfaces and extension), type operators require the reader to mentally
  evaluate the type expression. This can make programs substantially harder to
  read.
- Mapped & conditional types' evaluation model, in particular when combined
  with type inference, is underspecified, not always well understood, and
  often subject to change in TypeScript compiler versions.
- Some language tooling does not work well with these type system features.
  E.g. your IDE's find references (and thus rename property refactoring) will
  not find properties in a `Pick<T, Keys>` type.

The style recommendation is:

- Always use the simplest type construct that can possibly express your code.
- A little bit of repetition or verbosity is often much cheaper than the long
  term cost of complex type expressions.
- Mapped & conditional types may be used, subject to these considerations.

For example, TypeScript's builtin `Pick<T, Keys>` type allows creating a new
type by subsetting another type `T`, but simple interface extension can often be
easier to understand.

```ts
interface User {
    shoeSize: number;
    favoriteIcecream: string;
    favoriteChocolate: string;
}

// FoodPreferences has favoriteIcecream and favoriteChocolate, but not shoeSize.
type FoodPreferences = Pick<User, 'favoriteIcecream' | 'favoriteChocolate'>;
```

This is equivalent to spelling out the properties on `FoodPreferences`:

```ts
interface FoodPreferences {
    favoriteIcecream: string;
    favoriteChocolate: string;
}
```

To reduce duplication, `User` could extend `FoodPreferences`, or (possibly
better) nest a field for food preferences:

```ts
// Good
interface FoodPreferences {
    /* as above */
}
interface User extends FoodPreferences {
    shoeSize: number;
}
```

## `any` Type

TypeScript's `any` type is a super and subtype of all other types, and allows
dereferencing all properties. As such, `any` is dangerous — it can mask severe
programming errors, and its use undermines the value of having static types in
the first place.

**Consider _not_ using `any`.** In circumstances where you want to use `any`,
consider one of:

- [Provide a more specific type](#providing-a-more-specific-type)
- [Use `unknown`](#using-unknown-over-any)
- [Suppress the lint warning and document why](#suppressing-any-lint-warnings)

### Providing a more specific type

Use interfaces, an inline object type, or a type alias:

```ts
// Good
// Use declared interfaces to represent server-side JSON.
declare interface MyUserJson {
    name: string;
    email: string;
}

// Use type aliases for types that are repetitive to write.
type MyType = number | string;

// Or use inline object types for complex returns.
function getTwoThings(): { something: number; other: string } {
    // ...
    return { something, other };
}

// Use a generic type, where otherwise a library would say `any` to represent
// they don't care what type the user is operating on (but note "Return type
// only generics" below).
function nicestElement<T>(items: T[]): T {
    // Find the nicest element in items.
}
```

### Using `unknown` over `any`

The `any` type allows assignment into any other type and dereferencing any
property off it. Often this behaviour is not necessary or desirable, and code
just needs to express that a type is unknown. Use the built-in type `unknown` in
that situation — it expresses the concept and is much safer as it does not allow
dereferencing arbitrary properties.

```ts
// Good
// Can assign any value (including null or undefined) into this but cannot
// use it without narrowing the type or casting.
const val: unknown = value;
```

```ts
// Bad
const danger: any = value; /* result of an arbitrary expression */
danger.whoops(); // This access is completely unchecked!
```

To safely use `unknown` values, narrow the type using a
[type guard](https://www.typescriptlang.org/docs/handbook/advanced-types.html#type-guards-and-differentiating-types).

### Suppressing `any` lint warnings

Sometimes using `any` is legitimate, for example in tests to construct a mock
object. In such cases, add a comment that suppresses the lint warning, and
document why it is legitimate.

```ts
// Good
// This test only needs a partial implementation of BookService, and if
// we overlooked something the test will fail in an obvious way.
// This is an intentionally unsafe partial mock
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const mockBookService = {
    get() {
        return mockBook;
    },
} as any as BookService;
// Shopping cart is not used in this test
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const component = new MyComponent(
    mockBookService,
    /* unused ShoppingCart */ null as any,
);
```

## Tuple Types

If you are tempted to create a Pair type, instead use a tuple type:

```ts
// Bad
interface Pair {
  first: string;
  second: string;
}
function splitInHalf(input: string): Pair {
  ...
  return {first: x, second: y};
}
```

```ts
// Good
function splitInHalf(input: string): [string, string] {
  ...
  return [x, y];
}

// Use it like:
const [leftHalf, rightHalf] = splitInHalf('my string');
```

However, often it's clearer to provide meaningful names for the properties.

If declaring an `interface` is too heavyweight, you can use an inline object
literal type:

```ts
// Good
function splitHostPort(address: string): {host: string, port: number} {
  ...
}

// Use it like:
const address = splitHostPort(userAddress);
use(address.port);

// You can also get tuple-like behavior using destructuring:
const {host, port} = splitHostPort(userAddress);
```

## Wrapper types

There are a few types related to JavaScript primitives that should never be
used:

- `String`, `Boolean`, and `Number` have slightly different meaning from the
  corresponding primitive types `string`, `boolean`, and `number`. Always use
  the lowercase version.
- `Object` has similarities to both `{}` and `object`, but is slightly looser.
  Use `{}` for a type that include everything except `null` and `undefined`,
  or lowercase `object` to further exclude the other primitive types (the
  three mentioned above, plus `symbol` and `bigint`).

Further, never invoke the wrapper types as constructors (with `new`).

## Return type only generics

Avoid creating APIs that have return type only generics. When working with
existing APIs that have return type only generics always explicitly specify the
generics.
