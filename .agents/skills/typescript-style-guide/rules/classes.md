---
description: >-
  Rules for TypeScript class declarations including visibility, constructors,
  properties, and member ordering.
metadata:
  tags: [classes, visibility, constructors, properties, readonly]
---

---
description: >-
  Rules for TypeScript class visibility, constructors, properties, and
  member declarations.
metadata:
  tags: [classes, visibility, constructors, readonly, properties]
---

# Classes

## Visibility

Restricting visibility of properties, methods, and entire types helps with
keeping code decoupled.

- Limit symbol visibility as much as possible.
- Consider converting private methods to non-exported functions within the
  same file but outside of any class, and moving private properties into a
  separate, non-exported class.
- TypeScript symbols are public by default. Never use the `public` modifier
  except when declaring non-readonly public parameter properties (in
  constructors).

```ts
// Bad
class Foo {
    public bar = new Bar(); // public modifier not needed

    constructor(public readonly baz: Baz) {} // readonly implies it's a property which defaults to public
}
```

```ts
// Good
class Foo {
    bar = new Bar();

    constructor(public baz: Baz) {} // public modifier allowed for non-readonly
}
```

## Constructors

Constructor calls must use parentheses, even when no arguments are passed:

```ts
// Bad
const x = new Foo;
```

```ts
// Good
const x = new Foo();
```

It is unnecessary to provide an empty constructor or one that simply delegates
into its parent class because ES2015 provides a default class constructor if one
is not specified. However constructors with parameter properties, modifiers or
parameter decorators should not be omitted even if the body of the constructor
is empty.

```ts
// Bad
class UnnecessaryConstructor {
    constructor() {}
}
```

```ts
// Bad
class UnnecessaryConstructorOverride extends Base {
    constructor(value: number) {
        super(value);
    }
}
```

```ts
// Good
class DefaultConstructor {}

class ParameterProperties {
    constructor(private myService) {}
}

class ParameterDecorators {
    constructor(@SideEffectDecorator myService) {}
}

class NoInstantiation {
    private constructor() {}
}
```

## No `#private` fields

Do not use private fields (also known as private identifiers):

```ts
// Bad
class Clazz {
    #ident = 1;
}
```

Instead, use TypeScript's visibility annotations:

```ts
// Good
class Clazz {
    private ident = 1;
}
```

> Why? Private identifiers cause substantial emit size and performance
> regressions when down-leveled by TypeScript, and are unsupported before
> ES2015. They do not offer substantial benefits when static type checking is
> used to enforce visibility.

## Use `readonly`

Mark properties that are never reassigned outside of the constructor with the
`readonly` modifier (these need not be deeply immutable).

## Parameter properties

Rather than plumbing an obvious initializer through to a class member, use a
TypeScript
[parameter property](https://www.typescriptlang.org/docs/handbook/classes.html#parameter-properties).

```ts
// Bad
class Foo {
    private readonly barService: BarService;

    constructor(barService: BarService) {
        this.barService = barService;
    }
}
```

```ts
// Good
class Foo {
    constructor(private readonly barService: BarService) {}
}
```

If the parameter property needs documentation,
[use an `@param` JSDoc tag](comments-and-documentation.md#parameter-property-comments).

## Field initializers

If a class member is not a parameter, initialize it where it's declared, which
sometimes lets you drop the constructor entirely.

```ts
// Bad
class Foo {
    private readonly userList: string[];
    constructor() {
        this.userList = [];
    }
}
```

```ts
// Good
class Foo {
    private readonly userList: string[] = [];
}
```

## Properties used outside of class lexical scope

Properties used from outside the lexical scope of their containing class, such
as an Angular controller's properties used from a template, must not use
`private` visibility, as they are used outside of the lexical scope of their
containing class.

Use `public` or `protected` visibility as appropriate for your framework.

## Getters and Setters (Accessors)

Getters and setters for class members may be used. The getter method must be a
[pure function](https://en.wikipedia.org/wiki/Pure_function) (i.e., result is
consistent and has no side effects). They are also useful as a means of
restricting the visibility of internal or verbose implementation details.

```ts
// Good
class Foo {
    constructor(private readonly someService: SomeService) {}

    get someMember(): string {
        return this.someService.someVariable;
    }

    set someMember(newValue: string) {
        this.someService.someVariable = newValue;
    }
}
```

If an accessor is used to hide a class property, the hidden property may be
prefixed or suffixed with any whole word, like `internal` or `wrapped`. When
using these private properties, access the value through the accessor whenever
possible. At least one accessor for a property must be non-trivial: do not
define "pass-through" accessors only for the purpose of hiding a property.
Instead, make the property public (or consider making it `readonly` rather than
just defining a getter with no setter).

```ts
// Good — non-trivial logic in the accessors
class Foo {
    private wrappedBar = '';
    get bar() {
        return this.wrappedBar || 'bar';
    }

    set bar(wrapped: string) {
        this.wrappedBar = wrapped.trim();
    }
}
```

```ts
// Bad — neither accessor has logic, so just make bar public.
class Bar {
    private barInternal = '';
    get bar() {
        return this.barInternal;
    }

    set bar(value: string) {
        this.barInternal = value;
    }
}
```

## Member property declarations

Interface and class declarations must use the `;` character to separate
individual member declarations:

```ts
// Good
interface Foo {
    memberA: string;
    memberB: number;
}
```

Interfaces specifically must not use the `,` character to separate fields, for
symmetry with class declarations:

```ts
// Bad
interface Foo {
    memberA: string,
    memberB: number,
}
```

Inline object type declarations must use the comma as a separator:

```ts
// Good
type SomeTypeAlias = {
    memberA: string;
    memberB: number;
};

let someProperty: { memberC: string; memberD: number };
```
