---
description: >-
  Naming rules for TypeScript identifiers including classes, variables,
  functions, and constants.
metadata:
  tags: [naming, identifiers, camelCase, conventions]
---

---
description: >-
  Naming rules for TypeScript identifiers including classes, variables,
  functions, and constants.
metadata:
  tags: [naming, identifiers, camelCase, conventions]
---

# Identifiers

Identifiers must use only ASCII letters, digits, underscores (for constants and
structured test method names), and the `$` sign. Thus each valid identifier name
is matched by the regular expression `[$\w]+`.

| Style            | Category                                                           |
| ---------------- | ------------------------------------------------------------------ |
| `UpperCamelCase` | class / interface / type / enum / decorator / type parameters      |
| `lowerCamelCase` | variable / parameter / function / method / property / module alias |
| `CONSTANT_CASE`  | global constant values, including enum values                      |
| `#ident`         | private identifiers are never used.                                |

- **Abbreviations**: Treat abbreviations like acronyms in names as whole words,
  i.e. use `loadHttpUrl`, not ~~`loadHTTPURL`~~, unless required by a platform
  name (e.g. `XMLHttpRequest`).

- **Dollar sign**: Identifiers _should not_ generally use `$`, except when
  aligning with naming conventions for third party frameworks.
  See [naming style](#naming-style) for more on using `$` with `Observable`
  values.

- **Type parameters**: Type parameters, like in `Array<T>`, may use a single
  upper case character (`T`) or `UpperCamelCase`.

- **Test names**: Test method names in xUnit-style test frameworks may be
  structured with `_` separators, e.g. `testX_whenY_doesZ()`.

- **`_` prefix/suffix**: Identifiers must not use `_` as a prefix or suffix.

    This also means that `_` must not be used as an identifier by itself (e.g.
    to indicate a parameter is unused).

> Tip: If you only need some of the elements from an array (or TypeScript
> tuple), you can insert extra commas in a destructuring statement to ignore
> in-between elements:
>
> ```ts
> const [a, , b] = [1, 5, 10]; // a <- 1, b <- 10
> ```

- **Imports**: Module namespace imports are `lowerCamelCase` while files are
  `snake_case`, which means that imports correctly will not match in casing
  style, such as

    ```ts
    import * as fooBar from './foo_bar';
    ```

- **Constants**: `CONSTANT_CASE` indicates that a value is _intended_ to not
  be changed, and may be used for values that can technically be modified
  (i.e. values that are not deeply frozen) to indicate to users that they must
  not be modified.

    ```ts
    const UNIT_SUFFIXES = {
        milliseconds: 'ms',
        seconds: 's',
    };
    ```

    A constant can also be a `static readonly` property of a class.

    ```ts
    class Foo {
        private static readonly MY_SPECIAL_NUMBER = 5;

        bar() {
            return 2 * Foo.MY_SPECIAL_NUMBER;
        }
    }
    ```

    If a value can be instantiated more than once over the lifetime of the
    program, or if users mutate it in any way, it must use `lowerCamelCase`.

    If a value is an arrow function that implements an interface, then it can be
    declared `lowerCamelCase`.

- **React Components**: When required by JSX, components must be
  `UpperCamelCase` no matter how the component is implemented (e.g. function,
  ES6 class, `React.createClass`).

    ```ts
    // Good
    function GoLink(props: GoLinkProps) {
      return <a href={...}>...</a>;
    }

    class MyDialog extends React.Component<MyDialogProps, MyDialogState> {
      ...
    }
    ```

    ```ts
    // Bad — lowercased functions cannot be used as JSX elements because the
    // transpiler cannot distinguish them from HTML tags.
    function goLink(props: GoLinkProps) {
      return <a href={...}>...</a>;
    }
    ```

## Aliases

When creating a local-scope alias of an existing symbol, use the format of the
existing identifier. The local alias must match the existing naming and format
of the source. For variables use `const` for your local aliases, and for class
fields use the `readonly` attribute.

```ts
const { Foo } = SomeType;
const CAPACITY = 5;

class Teapot {
    readonly BrewStateEnum = BrewStateEnum;
    readonly CAPACITY = CAPACITY;
}
```

## Naming style

TypeScript expresses information in types, so names _should not_ be decorated
with information that is included in the type.

Some concrete examples of this rule:

- Do not use trailing or leading underscores for private properties or methods.
- Do not use the `opt_` prefix for optional parameters.
- Do not mark interfaces specially (~~`IMyInterface`~~ or
  ~~`MyFooInterface`~~) unless it's idiomatic in its environment. When
  introducing an interface for a class, give it a name that expresses why the
  interface exists in the first place (e.g. `class TodoItem` and
  `interface TodoItemStorage` if the interface expresses the format used for
  storage/serialization in JSON).
- Suffixing `Observable`s with `$` is a common external convention and can
  help resolve confusion regarding observable values vs concrete values.
  Judgement on whether this is a useful convention is left up to individual
  teams, but _should_ be consistent within projects.

## Descriptive names

Names _must_ be descriptive and clear to a new reader. Do not use abbreviations
that are ambiguous or unfamiliar to readers outside your project, and do not
abbreviate by deleting letters within a word.

- **Exception**: Variables that are in scope for 10 lines or fewer, including
  arguments that are _not_ part of an exported API, _may_ use short (e.g.
  single letter) variable names.
