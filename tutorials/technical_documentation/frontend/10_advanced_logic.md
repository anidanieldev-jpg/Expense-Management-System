# Part 10: Advanced Logic - Payments & Wallets

Welcome to the final chapter! We saved the hardest for last.
The **Payments** screen is complex because it ties everything together:
1.  **Vendors**: Who are we paying?
2.  **Expenses**: Which bills are we paying off?
3.  **Wallets**: Where is the money coming from?

## 1. The Dynamic Form

Unlike the simple "Name/Address" form for Vendors, the Payment form interacts with the user in real-time.

### Step A: Dynamic Filtering
When the user selects a Vendor from the dropdown:
```javascript
document.getElementById('pay-vendor-select').onchange = async (e) => {
    const vendorId = e.target.value;
    // 1. Fetch all expenses
    // 2. Filter for interactions matching this Vendor AND Status != 'Paid'
    const bills = expenses.filter(x => x.vendorId === vendorId && x.status !== 'Paid');
    // 3. Render the "Unpaid Expenses" list on the right side
};
```
This is **Event-Driven UI**. The state of the form changes based on user input before they even click "Save".

### Step B: The "Allocation" Logic
We introduced two ways to handle payments:
1.  **Manual Entry**: You can type amounts directly into each bill's input field.
2.  **Auto-Allocation**: We added a **"Payment Amount"** field and a **"Pay Full Amount"** checkbox.

**How Auto-Allocation Works**:
If the user types `₦ 5,000` into the main input, our code loops through the list of bills and fills them one by one until the money runs out:
```javascript
amtInput.addEventListener('input', (e) => {
    let remaining = parseFloat(e.target.value) || 0;
    
    document.querySelectorAll('.alloc-input').forEach(inp => {
        const debt = parseFloat(inp.getAttribute('max'));
        // Take whichever is smaller: the remaining cash or the debt size
        const taking = Math.min(remaining, debt);
        inp.value = taking;
        remaining -= taking;
    });
});
```

**"Pay Full Amount" Checkbox**:
When checked, we simply loop through all inputs and set them to their maximum value (`max` attribute), effectively marking everything as fully paid.

## 2. The Pseudo-Transaction

When you click "Record Payment", we have to do three things at once. In a real database, this is called a **Transaction** (All or Nothing).
Since we are mocking it, we do it sequentially:

```javascript
// 1. Create the Payment Record
await API.create('payments', { ... });

// 2. Deduct from Wallet
const wallet = await API.getById('wallets', walletId);
await API.update('wallets', walletId, { balance: wallet.balance - total });

// 3. Update Status of Every Expense Paid
for (let alloc of allocations) {
    const exp = await API.getById('expenses', alloc.id);
    let newBal = exp.balance - alloc.amount;
    
    // logic: If balance is 0, status is 'Paid', else 'Partial'
    await API.update('expenses', alloc.id, { 
        balance: newBal, 
        status: newBal === 0 ? 'Paid' : 'Partial' 
    });
}
```

This ensures that if you pay ₦5,000 towards an invoice of ₦5,000, that invoice automatically turns green ("Paid") and your Wallet balance decreases by ₦5,000.

## Conclusion

Congratulations! You have toured the entire codebase of a functional Single Page Application.
You've learned about:
- **`index.html`**: The static shell.
- **`router.js`**: navigating without reloading.
- **`api.js`**: mocking backend data.
- **`ui.js`**: manipulating the DOM.
- **`controllers.js`**: the heavy lifting of business logic.

You are now ready to extend this app or build your own from scratch! 🚀
