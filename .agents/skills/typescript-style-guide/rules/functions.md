---
description: >-
  Rules for function declarations, arrow functions, expression bodies, and
  proper use of 'this' in TypeScript.
metadata:
  tags: [functions, arrow functions, declarations, callbacks]
---

---
description: >-
  Rules for function declarations, arrow functions, expression bodies,
  and use of this in TypeScript.
metadata:
  tags: [functions, arrow functions, declarations, callbacks]
---

# Functions

## Function Declarations

Use `function foo() { ... }` to declare named functions, including functions in
nested scopes, e.g. within another function.

Use function declarations instead of assigning a function expression into a
local variable (~~`const x = function() {...};`~~). TypeScript already disallows
rebinding functions, so preventing overwriting a function declaration by using
`const` is unnecessary.

Exception: Use arrow functions assigned to variables instead of function
declarations if the function accesses the outer scope's `this`.

```ts
// Good
function foo() { ... }
```

```ts
// Bad
// Given the above declaration, this won't compile:
foo = () => 3;  // ERROR: Invalid left-hand side of assignment expression.

// So declarations like this are unnecessary.
const foo = function() { ... }
```

Top level arrow functions _may_ be used to explicitly declare that a function
implements an interface.

```ts
// Good
interface SearchFunction {
  (source: string, subString: string): boolean;
}

const fooSearch: SearchFunction = (source, subString) => { ... };
```

## Use arrow functions in expressions

Always use arrow functions instead of pre-ES6 function expressions defined with
the `function` keyword.

```ts
// Good
bar(() => {
    this.doSomething();
});
```

```ts
// Bad
bar(function() { ... })
```

Function expressions (defined with the `function` keyword) may only be used if
code has to dynamically rebind the `this` pointer, but code _should not_ rebind
the `this` pointer in general. Code in regular functions (as opposed to arrow
functions and methods) _should not_ access `this`.

## Expression bodies vs block bodies

Use arrow functions with expressions or blocks as their body as appropriate.

```ts
// Good
function someFunction() {
    // Block arrow function bodies, i.e. bodies with => { }, are fine:
    const receipts = books.map((b: Book) => {
        const receipt = payMoney(b.price);
        recordTransaction(receipt);
        return receipt;
    });

    // Expression bodies are fine, too, if the return value is used:
    const longThings = myValues
        .filter((v) => v.length > 1000)
        .map((v) => String(v));

    function payMoney(amount: number) {
        // function declarations are fine, but don't access `this` in them.
    }
}
```

Only use an expression body if the return value of the function is actually
used.

```ts
// Bad — use a block ({ ... }) if the return value of the function is not used.
myPromise.then((v) => console.log(v));
```

```ts
// Good — return value is unused, use a block body.
myPromise.then((v) => {
    console.log(v);
});
// Good — code may use blocks for readability.
const transformed = [1, 2, 3].map((v) => {
    const intermediate = someComplicatedExpr(v);
    const more = acrossManyLines(intermediate);
    return worthWrapping(more);
});
```

## Rebinding `this`

Function expressions must not use `this` unless they specifically exist to
rebind the `this` pointer. Rebinding `this` can in most cases be avoided by
using arrow functions or explicit parameters.

```ts
// Bad
function clickHandler() {
    // What's `this` in this context?
    this.textContent = 'Hello';
}
// The `this` pointer reference is implicitly set to document.body.
document.body.onclick = clickHandler;
```

```ts
// Good — explicitly reference the object from an arrow function.
document.body.onclick = () => {
    document.body.textContent = 'hello';
};
// Alternatively: take an explicit parameter
const setTextFn = (e: HTMLElement) => {
    e.textContent = 'hello';
};
document.body.onclick = setTextFn.bind(null, document.body);
```

## Arrow functions as properties

Classes usually _should not_ contain properties initialized to arrow functions.
Arrow function properties require the calling function to understand that the
callee's `this` is already bound, which increases confusion about what `this`
is, and call sites and references using such handlers look broken (i.e. require
non-local knowledge to determine that they are correct). Code _should_ always
use arrow functions to call instance methods
(`const handler = (x) => { this.listener(x); };`), and _should not_ obtain or
pass references to instance methods
(~~`const handler = this.listener; handler(x);`~~).

> Note: in some specific situations, e.g. when binding functions in a template,
> arrow functions as properties are useful and create much more readable code.
> Use judgement with this rule. Also, see the
> [Event Handlers](#event-handlers) section below.

```ts
// Bad — `this` is not preserved in the callback.
class DelayHandler {
    constructor() {
        setTimeout(this.patienceTracker, 5000);
    }
    private patienceTracker() {
        this.waitedPatiently = true;
    }
}
```

```ts
// Bad — arrow functions usually should not be properties.
class DelayHandler {
    constructor() {
        // This code looks like it forgot to bind `this`.
        setTimeout(this.patienceTracker, 5000);
    }
    private patienceTracker = () => {
        this.waitedPatiently = true;
    };
}
```

```ts
// Good — explicitly manage `this` at call time.
class DelayHandler {
    constructor() {
        setTimeout(() => {
            this.patienceTracker();
        }, 5000);
    }
    private patienceTracker() {
        this.waitedPatiently = true;
    }
}
```

## Event Handlers

Event handlers _may_ use arrow functions when there is no need to uninstall the
handler (for example, if the event is emitted by the class itself). If the
handler must be uninstalled, arrow function properties are the right approach,
because they automatically capture `this` and provide a stable reference to
uninstall.

```ts
// Good — event handlers may be anonymous functions or arrow function properties.
class Component {
    onAttached() {
        // The event is emitted by this class, no need to uninstall.
        this.addEventListener('click', () => {
            this.listener();
        });
        // this.listener is a stable reference, we can uninstall it later.
        window.addEventListener('onbeforeunload', this.listener);
    }
    onDetached() {
        window.removeEventListener('onbeforeunload', this.listener);
    }
    // An arrow function stored in a property is bound to `this` automatically.
    private listener = () => {
        confirm('Do you want to exit the page?');
    };
}
```

Do not use `bind` in the expression that installs an event handler, because it
creates a temporary reference that can't be uninstalled.

```ts
// Bad — binding listeners creates a temporary reference that prevents uninstalling.
class Component {
    onAttached() {
        window.addEventListener('onbeforeunload', this.listener.bind(this));
    }
    onDetached() {
        // This bind creates a different reference, so this line does nothing.
        window.removeEventListener('onbeforeunload', this.listener.bind(this));
    }
    private listener() {
        confirm('Do you want to exit the page?');
    }
}
```
