# Part 8: Rendering the UI (`js/ui.js`)

This is where the app comes alive visually. `ui.js` is responsible for taking raw data (JSON) and turning it into HTML that the user can see.

## 1. Template Literals: The Modern Way

In the old days, we used to do this:
```javascript
var html = '<div>' + name + '</div>'; // Messy
```
Now, we use **Template Literals** (backticks \` \`):
```javascript
let html = `
    <div class="user-card">
        <h3>${user.name}</h3>
        <p>${user.email}</p>
    </div>
`;
```
This serves as our "Templating Engine". We don't need external libraries like Handlebars or Pug. JavaScript can do it natively now.

## 2. Rendering Tables (`renderTable`)

This function is a workhorse. It takes `columns` (headers) and `rows` (data) and builds a table dynamically.

### Key logic:
1.  **Map Headers**: Loop through columns to create `<th>` tags.
2.  **Map Rows**: Loop through rows to create `<tr>` tags.
3.  **Action Buttons**: It automatically adds the "Edit" and "Delete" buttons to the end of every row.

*Crucial Detail*: We add `data-id="${row.id}"` to the row. This is how `index.js` knows which item you clicked later!

## 3. The Detail Panel (`openDetail`)

This function handles the sliding drawer on the right.

```javascript
openDetail: (subtitle, title, contentHtml, onEdit) => {
    // 1. Fill Text
    document.getElementById('detail-title').innerText = title;
    
    // 2. Set Content
    document.getElementById('detail-content').innerHTML = contentHtml;
    
    // 3. Handle the Edit Button (The Callback Pattern)
    const editBtn = document.getElementById('detail-edit-btn');
    if (onEdit) {
        editBtn.onclick = onEdit;
        // ... show button
    }
}
```

### The Callback Fix
Notice `onEdit`. This used to be an ID, which required importing the router here. That caused a crash (Circular Dependency).
By changing it to `onEdit` (a function function), `ui.js` becomes **dumb**. It doesn't know *what* happens when you click Edit; it just receives a function and executes it. This makes the code much safer and cleaner.

In **Part 9**, we enter the brain of the operation: the **Controllers**.
