---
description: >-
  Rules for ES6 module imports, import paths, namespace usage, and import
  type declarations in TypeScript.
metadata:
  tags: [modules, imports, namespaces, import type, ES6]
---

---
description: >-
  Rules for ES6 import paths, module vs destructuring imports, and
  avoiding namespace and require in TypeScript.
metadata:
  tags: [modules, imports, ES6, namespace, require]
---

# Modules & Imports

## Import Paths

TypeScript code must use paths to import other TypeScript code. Paths may be
relative, i.e. starting with `.` or `..`, or rooted at the base directory, e.g.
`root/path/to/file`.

Code _should_ use relative imports (`./foo`) rather than absolute imports
`path/to/foo` when referring to files within the same (logical) project.

Consider limiting the number of parent steps (`../../../`) as those can make
module and path structures hard to understand.

```ts
// Good
import { Symbol1 } from 'path/from/root';
import { Symbol2 } from '../parent/file';
import { Symbol3 } from './sibling';
```

## Namespaces vs Modules

TypeScript supports two methods to organize code: _namespaces_ and _modules_,
but namespaces are disallowed. Code must use TypeScript _modules_ (which are
[ECMAScript 6 modules](http://exploringjs.com/es6/ch_modules.html)). That is,
your code _must_ refer to code in other files using imports and exports of the
form `import {foo} from 'bar';`

Your code must not use the `namespace Foo { ... }` construct. `namespace`s may
only be used when required to interface with external, third party code. To
semantically namespace your code, use separate files.

Code must not use `require` (as in `import x = require('...');`) for imports.
Use ES6 module syntax.

```ts
// Bad — do not use namespaces:
namespace Rocket {
  function launch() { ... }
}

// Bad — do not use <reference>
/// <reference path="..."/>

// Bad — do not use require()
import x = require('mydep');
```

## Import variants

There are four variants of import statements in ES6 and TypeScript:

| Import type   | Example                          | Use for                                                                           |
| ------------- | -------------------------------- | --------------------------------------------------------------------------------- |
| module        | `import * as foo from '...'`     | TypeScript imports                                                                |
| destructuring | `import { SomeThing } from ...`  | TypeScript imports                                                                |
| default       | `import SomeThing from '...'`    | Only for other external code that requires them                                   |
| side-effect   | `import '...';`                  | Only to import libraries for their side-effects on load (such as custom elements) |

```ts
// Good — choose between two options as appropriate (see below).
import * as ng from '@angular/core';
import { Foo } from './foo';

// Only when needed: default imports.
import Button from 'Button';

// Sometimes needed to import libraries for their side effects:
import 'jasmine';
```

## Module versus destructuring imports

Both module and destructuring imports have advantages depending on the
situation.

Module imports give a name to the entire module and each symbol reference
mentions the module, which can make code more readable and gives autocompletion
on all symbols in a module. They also require less import churn (all symbols are
available), fewer name collisions, and allow terser names in the module that's
imported. Module imports are particularly useful when using many different
symbols from large APIs.

Destructuring imports give local names for each imported symbol. They allow
terser code when using the imported symbol, which is particularly useful for
very commonly used symbols, such as Jasmine's `describe` and `it`.

```ts
// Bad — overlong import statement of needlessly namespaced names.
import {TableViewItem, TableViewHeader, TableViewRow, TableViewModel,
  TableViewRenderer} from './tableview';
let item: TableViewItem = ...;
```

```ts
// Good — use the module for namespacing.
import * as tableview from './tableview';
let item: tableview.Item = ...;
```

```ts
// Good — give local names for these common functions.
import {describe, it, expect} from './testing';

describe('foo', () => {
  it('bar', () => {
    expect(...);
    expect(...);
  });
});
```

## Renaming imports

Code _should_ fix name collisions by using a module import or renaming the
exports themselves. Code _may_ rename imports
(`import {SomeThing as SomeOtherThing}`) if needed.

Three examples where renaming can be helpful:

1. If it's necessary to avoid collisions with other imported symbols.
2. If the imported symbol name is generated.
3. If importing symbols whose names are unclear by themselves, renaming can
   improve code clarity. For example, when using RxJS the `from` function
   might be more readable when renamed to `observableFrom`.

## `import type` / `export type`

Use `import type` and `export type` when importing or exporting only types. This
makes the intent explicit and aligns with TypeScript's `verbatimModuleSyntax`
compiler option, which requires type-only imports for types.

```ts
// Good
import type { Foo } from './foo';
export type { Bar } from './bar';
```

Note: this does not apply to exporting type definitions, i.e.
`export type Foo = ...;`.

TypeScript tooling automatically distinguishes symbols used as types vs symbols
used as values and only generates runtime loads for the latter.
