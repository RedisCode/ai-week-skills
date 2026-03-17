---
description: >-
  Rules for JSDoc comments, line comments, and documentation practices in
  TypeScript code.
metadata:
  tags: [comments, documentation, JSDoc, encoding]
---

---
description: >-
  Rules for JSDoc, line comments, file encoding, and documentation of
  TypeScript exports.
metadata:
  tags: [comments, documentation, JSDoc, encoding]
---

# Comments & Documentation

## File encoding: UTF-8

For non-ASCII characters, use the actual Unicode character (e.g. `∞`). For
non-printable characters, the equivalent hex or Unicode escapes (e.g. `\u221e`)
can be used along with an explanatory comment.

```ts
// Good — perfectly clear, even without a comment.
const units = 'μs';

// Good — use escapes for non-printable characters.
const output = '\ufeff' + content; // byte order mark
```

```ts
// Bad — hard to read and prone to mistakes, even with the comment.
const units = '\u03bcs'; // Greek letter mu, 's'

// Bad — the reader has no idea what this is.
const output = '\ufeff' + content;
```

## Source code formatting

Source code formatting can be completely automated. Humans should not waste time
arguing about comma placement in code reviews. Use your project's formatter
(e.g. Prettier, dprint). In rare situations where the formatter produces
problematic output, disable it for a specific section with an inline directive.

## JSDoc vs comments

There are two types of comments, JSDoc (`/** ... */`) and non-JSDoc ordinary
comments (`// ...` or `/* ... */`).

- Use `/** JSDoc */` comments for documentation, i.e. comments a user of the
  code should read.
- Use `// line comments` for implementation comments, i.e. comments that only
  concern the implementation of the code itself.

JSDoc comments are understood by tools (such as editors and documentation
generators), while ordinary comments are only for other humans.

## Document all top-level exports of modules

Use `/** JSDoc */` comments to communicate information to the users of your
code. Avoid merely restating the property or parameter name. You _should_ also
document all properties and methods (exported/public or not) whose purpose is
not immediately obvious from their name, as judged by your reviewer.

## Omit comments that are redundant with TypeScript

For example, do not declare types in `@param` or `@return` blocks, do not write
`@implements`, `@enum`, `@private` etc. on code that uses the `implements`,
`enum`, `private` etc. keywords.

## Do not use `@override`

Do not use `@override` in TypeScript source code.

`@override` is not enforced by the compiler, which is surprising and leads to
annotations and implementation going out of sync. Including it purely for
documentation purposes is confusing.

## Make comments that actually add information

For non-exported symbols, sometimes the name and type of the function or
parameter is enough. Code will _usually_ benefit from more documentation than
just variable names though!

- Avoid comments that just restate the parameter name and type, e.g.

    ```ts
    // Bad
    /** @param fooBarService The Bar service for the Foo application. */
    ```

- Because of this rule, `@param` and `@return` lines are only required when
  they add information, and may otherwise be omitted.

    ```ts
    // Good
    /**
     * POSTs the request to start coffee brewing.
     * @param amountLitres The amount to brew. Must fit the pot size!
     */
    brew(amountLitres: number, logger: Logger) {
      // ...
    }
    ```

## Parameter property comments

A parameter property is when a class declares a field and a constructor
parameter in a single declaration, by marking a parameter in the constructor.
E.g. `constructor(private readonly foo: Foo)`, declares that the class has a
`foo` field.

To document these fields, use JSDoc's `@param` annotation. Editors display the
description on constructor calls and property accesses.

```ts
/** This class demonstrates how parameter properties are documented. */
class ParamProps {
    /**
     * @param percolator The percolator used for brewing.
     * @param beans The beans to brew.
     */
    constructor(
        private readonly percolator: Percolator,
        private readonly beans: CoffeeBean[],
    ) {}
}
```

```ts
/** This class demonstrates how ordinary fields are documented. */
class OrdinaryClass {
    /** The bean that will be used in the next call to brew(). */
    nextBean: CoffeeBean;

    constructor(initialBean: CoffeeBean) {
        this.nextBean = initialBean;
    }
}
```

## Comments when calling a function

If needed, document parameters at call sites inline using block comments. Also
consider named parameters using object literals and destructuring.

```ts
// Inline block comments for parameters that'd be hard to understand:
new Percolator().brew(/* amountLitres= */ 5);
// Also consider using named arguments and destructuring parameters (in brew's declaration):
new Percolator().brew({ amountLitres: 5 });
```

```ts
/** An ancient {@link CoffeeBrewer} */
export class Percolator implements CoffeeBrewer {
    /**
     * Brews coffee.
     * @param amountLitres The amount to brew. Must fit the pot size!
     */
    brew(amountLitres: number) {
        // This implementation creates terrible coffee, but whatever.
        // TODO(b/12345): Improve percolator brewing.
    }
}
```

## Place documentation prior to decorators

When a class, method, or property have both decorators like `@Component` and
JSDoc, write the JSDoc before the decorator.

```ts
// Bad — do not write JSDoc between the Decorator and the decorated statement.
@Component({
    selector: 'foo',
    template: 'bar',
})
/** Component that prints "bar". */
export class FooComponent {}
```

```ts
// Good — write the JSDoc block before the Decorator.
/** Component that prints "bar". */
@Component({
    selector: 'foo',
    template: 'bar',
})
export class FooComponent {}
```
