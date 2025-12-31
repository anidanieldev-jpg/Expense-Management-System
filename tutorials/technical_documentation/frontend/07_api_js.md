# Part 7: Mocking the Backend (`js/api.js`)

In a real job, you often have to build the Frontend before the Backend is ready. How do you do that?
You **Mock** it.

`js/api.js` is a "Fake Server". Use this technique to impress interviewers or clients with a working demo even if you don't have a database yet.

## 1. The Fake Database

We use a simple JavaScript object to store our data:

```javascript
const MOCK_DATA = {
    vendors: [ ... ],
    wallets: [ ... ],
    expenses: [ ... ],
    payments: []
};
```
When you reload the page, this resets. In a real app, this would be a MongoDB or SQL database running on a server.

## 2. Simulating Reality (Latency)

Local JavaScript runs instantly (0ms). Real internet requests take time (200ms - 2000ms).
If you build your app assuming 0ms, it will feel "janky" when you connect it to the real internet.

We create a fake delay helper:
```javascript
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
```

And we use it in every function:
```javascript
get: async (collection) => {
    await delay(200); // Wait 0.2 seconds
    return [...MOCK_DATA[collection]];
},
```
This forces our app to handle "waiting" states properly (using `async/await`), ensuring we are ready for the real world.

## 3. The API Interface (CRUD)

We export an object `API` with standard methods:
- **C**reate: `API.create(collection, data)`
- **R**ead: `API.get(collection)` or `API.getById(...)`
- **U**pdate: `API.update(...)`
- **D**elete: `API.delete(...)`

## The Beauty of Abstraction

This file is an **Abstraction Layer**.
The rest of our app (Controllers) has *no idea* this is fake. They just call `API.get('vendors')`.
Tomorrow, if we build a real Python backend, we only have to rewrite this **one file** to use `fetch()` instead of `MOCK_DATA`. The rest of the app won't even notice.

In **Part 8**, we'll dive into the heavy lifter: `js/ui.js`.
