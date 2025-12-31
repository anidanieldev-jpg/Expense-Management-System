# Part 3: The Entry Point (`js/index.js`)

Scripts need a captain. In our app, that captain is `js/index.js`. It runs immediately when the page loads, and its job is to set everything up before the user starts clicking around.

Let's look at the crucial steps it performs inside `document.addEventListener('DOMContentLoaded', ...)`:

## 1. Imports: Gathering the Team

```javascript
import { store } from './store.js';
import { utils } from './utils.js';
import { router } from './router.js';
import { Controllers } from './controllers.js';
```
We import all the different modules we need. This is standard ES6 Module syntax.

## 2. Initialization & Registration

```javascript
await utils.init(); // Load mocked data (vendors, wallets) into cache

// Register Controllers
router.register('expenses', Controllers.expenses);
// ... others
```
**Why Register?**  
This was a key fix we made during debugging! Originally, `router.js` tried to import `Controllers` directly, but `Controllers` imported `router`. This loop (Circular Dependency) crashed the app.
**The Solution**: We broke the loop. Now, the `router` starts empty. The `index.js` captain introduces them: *"Hey Router, here are the Controllers you can use."*

## 3. Global Event Listeners (The "Magic" Part)

You might expect us to find every single "Delete" button and add an event listener to it.
**NO!** That is slow and buggy. If we add a new row later, it wouldn't have a listener.

Instead, we use **Event Delegation**:

```javascript
const tableContainer = document.getElementById('table-container');
tableContainer.addEventListener('click', (e) => {
    const row = e.target.closest('tr'); // Did we click inside a row?
    const btn = e.target.closest('button'); // Did we click a button?

    if (btn) {
        // Handle Edit/Delete
    } else if (row) {
        // Handle Row Click (Show Details)
    }
});
```
We listen on the **Container**. When you click *anything* inside the table, the event bubbles up to the container. We then check *what* you clicked (`e.target`).
- **Benefit**: It works for 10 rows or 10,000 rows. It works even for rows we haven't created yet!

## 4. Liftoff 🚀

```javascript
router.navigate('expenses');
```
Finally, we tell the router to show the default page. The application is now alive!

In **Part 4**, we'll discuss `store.js` and how we keep track of what the user is looking at.
