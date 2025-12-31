# Part 9: Business Logic - Expenses & Vendors (`js/controllers.js`)

The `Controllers` object is the brain of our application. All business logic lives here.
It is organized into modules: `expenses`, `vendors`, `wallets`, `payments`.

Each module follows a strict **"Interface"**—meaning they all look the same. They all have 4 methods:
1.  `list()`
2.  `detail(id)`
3.  `form(id)`
4.  `delete(id)`

This consistency allows our `Router` to switch between them easily.

## 1. The `list()` Method

**Goal**: Fetch data and tell UI to draw a table.

```javascript
list: async () => {
    // 1. Get Data
    const data = await API.get('expenses');

    // 2. Format Data for Table
    const rows = data.map(e => ({
        id: e.id,
        cells: [
            e.date,
            utils.getVendorName(e.vendorId), // Lookup Name
            utils.formatCurrency(e.total)    // Format $
        ]
    }));

    // 3. Render
    ui.renderTable(['Date', 'Vendor', 'Total'], rows);
}
```
Notice how it combines `API` (raw data), `utils` (formatting), and `ui` (drawing). The Controller is the conductor of the orchestra.

## 2. The `detail(id)` Method

**Goal**: Show the sliding panel with full info.

It fetches the specific item (`API.getById`) and builds a custom HTML string using Template Literals.

**Calculated Fields**:
For Vendors, we do some math on the fly:
```javascript
const expenses = await API.get('expenses');
const debt = expenses
    .filter(e => e.vendorId === v.id && e.status !== 'Paid')
    .reduce((sum, e) => sum + e.balance, 0);
```
We calculate "Total Debt" right here. We don't store "Debt" in the database; we calculate it whenever we need to see it. This ensures it's always accurate.

## 3. The `form(id)` Method

**Goal**: Handle both "New" and "Edit" modes.

- **New Mode**: `id` is null. We show an empty form.
- **Edit Mode**: `id` exists. We fetch data and pre-fill the inputs.

**Saving**:
Inside the form, we define what happens when you click "Save":
```javascript
ui.openForm(title, html, async () => {
    // 1. Read Inputs
    const payload = { ... };
    
    // 2. Save (Create or Update)
    isEdit ? await API.update(...) : await API.create(...);
    
    // 3. Go back to list
    router.navigate('expenses');
});
```

In **Part 10**, the final chapter, we will look at the most complex part of our app: **Payments Logic**.
