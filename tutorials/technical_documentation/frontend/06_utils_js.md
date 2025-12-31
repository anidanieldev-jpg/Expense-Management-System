# Part 6: Helpful Utilities (`js/utils.js`)

In programming, we follow the **DRY Principle** (Don't Repeat Yourself).
If you find yourself formatting currency in 5 different files, you should move that logic to a Utility file. That's exactly what `js/utils.js` is for.

## 1. Caching Data

When you open the "Expenses" list, we show the Vendor's Name (e.g., "Mama Favor"). But the expense data only has `vendorId: "VND-002"`.
To show the name, we need to look it up. We *could* fetch the vendor list from the server every single time we render a row, but that would be slow.

Instead, we **Cache** it:

```javascript
let cachedVendors = [];

const loadCache = async () => {
    cachedVendors = await API.get('vendors');
    // ...
};

export const utils = {
    init: async () => {
        await loadCache();
    },
    
    getVendorName: (id) => cachedVendors.find(v => v.id === id)?.name || 'Unknown',
}
```

When the app starts (`utils.init()`), we download the phonebook (vendors). Later, when we need a name (`getVendorName`), we just look it up in our local memory. Instant!

## 2. Formatting Currency

Money is hard to read as `5300`. It's easier as `₦ 5,300.00`.
We use the browser's built-in `toLocaleString` formatter:

```javascript
formatCurrency: (num) => '₦ ' + num.toLocaleString('en-NG', { minimumFractionDigits: 2 }),
```

## 3. ID Generation

In a real database, the database creates IDs (1, 2, 3...). Since we are faking it, we create our own random IDs:

```javascript
generateId: (prefix) => prefix + '-' + Math.floor(100000 + Math.random() * 900000),
```
This gives us IDs like `AEX-123456`.

## Key Takeaway
Utilities are the "Swiss Army Knife" of your project. They keep your main business logic clean by hiding the messy details of formatting strings and finding array items.

In **Part 7**, we'll look at `api.js` to see how we pretend to talk to a server.
