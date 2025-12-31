# Part 5: The Router Engine (`js/router.js`)

In traditional websites, "Routing" is handled by the server. You ask for `/about.html`, and the server sends it. In our SPA, we do this in the browser using `js/router.js`.

## The "Registry" Pattern

You'll notice something unique at the top of our router:

```javascript
registry: {},

register: (view, controller) => {
    router.registry[view] = controller;
},
```

**Why do we do this?**
This is how we solved the **Circular Dependency** bug.
- If `router.js` imported `controllers.js`...
- And `controllers.js` imported `router.js` (to refresh the page after delete)...
- ...loops would happen, causing crashes.

By using a **Registry**, the router doesn't know *what* controllers exist until `index.js` introduces them. It's a "blind" system effectively decoupled from the specific logic of the views.

## The `navigate` Function

When you click "Vendors", this happens:

1.  **Update State**: `store.currentView = view;`
2.  **Update UI**:
    - Highlight the correct sidebar link (`ui.setActiveNav`).
    - Change the page title ("Manage Vendors").
    - Update the "New" button text ("Add Vendor").
3.  **Load Data**:
    ```javascript
    await router.registry[view].list();
    ```
    It looks up the registered controller for "vendors" and calls its `list()` method. This is where the actual HTML generation happens.

## Handling Edits

The router also handles the "Edit" action:

```javascript
openEdit: (id) => {
    router.registry[store.currentView].form(id);
}
```

It asks the *current* controller to open its form with the specific ID. This keeps the Router code generic—it doesn't care if you are editing a Vendor or an Expense; it just delegates to the expert (the Controller).

In **Part 6**, we'll look at the silent heroes of the app: the helper functions in `js/utils.js`.
