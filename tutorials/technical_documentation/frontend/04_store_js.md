# Part 4: Managing State (`js/store.js`)

In any application, "State" refers to the data that changes over time.
- *Which page am I on?*
- *Which item did I just click?*
- *Is the user logged in?*

If we scatter this info across 10 different files, we get "Spaghetti Code". Instead, we use a central **Store**.

## The Code

Open `js/store.js`. You'll see it's surprisingly simple:

```javascript
export const store = {
    currentView: 'expenses', // Default start page
    selectedId: null,        // Which row is currently active?

    // Simple helper to update state
    setState(key, value) {
        this[key] = value;
    }
};
```

## Why is this special?

In JavaScript Modules, when you `export const store = { ... }`, that object is created **once**.
No matter how many files imply `import { store } from './store.js'`, they all get the **exact same object**.

This is called the **Singleton Pattern**.

### Example Usage

1.  **Router**: When you click a menu link, the router says:
    ```javascript
    store.currentView = 'vendors';
    ```
2.  **UI**: When you click a row in the table, the UI might check:
    ```javascript
    console.log(store.currentView); // Output: 'vendors'
    ```

Because they share the same `store` object, they stay in sync perfectly without needing to pass variables back and forth complexly.

## Is this "Redux"?

No. Redux (used with React) is much more complex. This is a "Poor Man's Store"—perfect for small-to-medium vanilla JS apps. It gives us a single source of truth without the boilerplate code of a full state management library.

In **Part 5**, we'll see how the `Router` uses this state to switch pages.
