/**
 * Business Logic Controllers
 * Contains the specific logic for Expenses, Vendors, Wallets, and Payments.
 */
import { API } from './api.js?v=5';
import { utils } from './utils.js';
import { ui } from './ui.js?v=4';
import { router } from './router.js';

export const Controllers = {
    // --- EXPENSES MODULE ---
    expenses: {
        list: async () => {
            const data = await API.get('expenses');
            const rows = data.map(e => ({
                id: e.id,
                cells: [
                    `<span class="font-mono text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">${e.id}</span>`,
                    `<span class="font-medium text-gray-900">${utils.getVendorName(e.vendorId)}</span>`,
                    e.date,
                    utils.formatCurrency(e.total),
                    `<span class="font-bold text-gray-700">${utils.formatCurrency(e.balance)}</span>`,
                    `<span class="px-2.5 py-0.5 text-xs font-semibold rounded-full ${utils.getStatusClass(e.status)}">${e.status}</span>`
                ]
            }));
            ui.renderTable(['ID', 'Vendor', 'Date', 'Total', 'Balance', 'Status'], rows);
        },
        detail: async (id) => {
            const e = await API.getById('expenses', id);
            if (!e) return;
            const html = `
                <div class="grid grid-cols-2 gap-y-4 text-sm mb-6">
                    <div class="text-gray-500">Expense ID</div><div class="font-mono text-right text-gray-700">${e.id}</div>
                    <div class="text-gray-500">Date Incurred</div><div class="font-medium text-right">${e.date}</div>
                    <div class="text-gray-500">Vendor</div><div class="font-medium text-right text-blue-600">${utils.getVendorName(e.vendorId)}</div>
                    <div class="text-gray-500">Category</div><div class="font-medium text-right bg-gray-100 inline-block px-2 rounded justify-self-end">${e.category}</div>
                </div>
                <div class="bg-gray-50 rounded-lg p-4 border border-gray-100 mb-6">
                    <h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Description</h4>
                    <p class="text-sm text-gray-700 leading-relaxed">${e.description || 'No description provided.'}</p>
                </div>
                <div class="space-y-3 pt-4 border-t border-gray-100">
                    <div class="flex justify-between items-center"><span class="text-gray-600">Total Amount</span><span class="text-lg font-bold text-gray-900">${utils.formatCurrency(e.total)}</span></div>
                    <div class="flex justify-between items-center"><span class="text-gray-600">Balance Due</span><span class="text-lg font-bold text-red-600">${utils.formatCurrency(e.balance)}</span></div>
                    <div class="flex justify-end pt-2"><span class="px-3 py-1 text-xs font-semibold rounded-full ${utils.getStatusClass(e.status)}">${e.status}</span></div>
                </div>`;
            ui.openDetail('EXPENSE', `Invoice #${e.id}`, html,
                () => router.openEdit(id),
                () => ui.confirmDelete(id, (delId) => Controllers.expenses.delete(delId))
            );
        },
        form: async (id = null) => {
            const isEdit = !!id;
            const data = id ? await API.getById('expenses', id) : { vendorId: '', date: utils.today(), total: '', category: '', description: '' };
            const vendors = await API.get('vendors');

            const html = `
                <div class="grid grid-cols-1 gap-6">
                    <div>
                        <label class="block text-sm font-semibold text-gray-700 mb-1">Vendor</label>
                        <select id="inp-vendor" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border bg-white">
                            <option value="">Select Vendor</option>
                            ${vendors.map(v => `<option value="${v.id}" ${v.id === data.vendorId ? 'selected' : ''}>${v.name}</option>`).join('')}
                        </select>
                    </div>
                    <div class="grid grid-cols-2 gap-6">
                        <div><label class="block text-sm font-semibold text-gray-700 mb-1">Date</label><input type="date" id="inp-date" value="${data.date}" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"></div>
                        <div><label class="block text-sm font-semibold text-gray-700 mb-1">Amount (₦)</label><input type="number" id="inp-amount" value="${data.total}" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"></div>
                    </div>
                    <div>
                        <label class="block text-sm font-semibold text-gray-700 mb-1">Category</label>
                        <select id="inp-category" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border bg-white">
                            <option value="Poultry" ${data.category === 'Poultry' ? 'selected' : ''}>Poultry</option>
                            <option value="Logistics" ${data.category === 'Logistics' ? 'selected' : ''}>Logistics</option>
                            <option value="Feed" ${data.category === 'Feed' ? 'selected' : ''}>Feed</option>
                            <option value="Utilities" ${data.category === 'Utilities' ? 'selected' : ''}>Utilities</option>
                            <option value="Other" ${data.category === 'Other' ? 'selected' : ''}>Other</option>
                        </select>
                    </div>
                    <div><label class="block text-sm font-semibold text-gray-700 mb-1">Description</label><textarea id="inp-desc" rows="4" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border">${data.description || ''}</textarea></div>
                </div>`;

            ui.openForm(isEdit ? 'Edit Expense' : 'New Expense', html, async () => {
                const amt = parseFloat(document.getElementById('inp-amount').value);
                if (!amt) return alert('Please enter a valid amount');
                const payload = {
                    id: isEdit ? id : utils.generateId('AEX'),
                    vendorId: document.getElementById('inp-vendor').value,
                    date: document.getElementById('inp-date').value,
                    total: amt,
                    balance: amt, // Simple update logic
                    status: 'Unpaid',
                    category: document.getElementById('inp-category').value,
                    description: document.getElementById('inp-desc').value
                };
                isEdit ? await API.update('expenses', id, payload) : await API.create('expenses', payload);
                ui.closeForm();
                router.navigate('expenses');
            });
        },
        delete: async (id) => {
            await API.delete('expenses', id);
            router.navigate('expenses'); // Refresh
        }
    },

    // --- VENDORS MODULE ---
    vendors: {
        list: async () => {
            const vendors = await API.get('vendors');
            const expenses = await API.get('expenses');

            const rows = vendors.map(v => {
                const debt = expenses
                    .filter(e => e.vendorId === v.id && e.status !== 'Paid')
                    .reduce((sum, e) => sum + e.balance, 0);
                return {
                    id: v.id,
                    cells: [
                        `<span class="font-mono text-xs text-gray-500">${v.id}</span>`,
                        `<span class="font-semibold text-gray-900">${v.name}</span>`,
                        v.address,
                        `<span class="font-bold ${debt > 0 ? 'text-red-600' : 'text-green-600'}">${utils.formatCurrency(debt)}</span>`
                    ]
                };
            });
            ui.renderTable(['ID', 'Name', 'Address', 'Balance Due'], rows);
        },
        detail: async (id) => {
            const v = await API.getById('vendors', id);
            const expenses = await API.get('expenses');
            const unpaidExpenses = expenses.filter(e => e.vendorId === v.id && e.status !== 'Paid');
            const debt = unpaidExpenses.reduce((sum, e) => sum + e.balance, 0);

            const html = `
                <div class="text-center mb-8 pt-4">
                    <div class="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 text-3xl font-bold mx-auto mb-4 border-4 border-white shadow-md">${v.name.charAt(0)}</div>
                    <h3 class="text-xl font-bold text-gray-900">${v.name}</h3>
                    <p class="text-sm text-gray-500 font-mono mt-1">${v.id}</p>
                </div>
                <div class="space-y-6">
                    <div class="grid grid-cols-1 gap-4">
                        <div class="bg-gray-50 p-3 rounded border border-gray-100"><label class="text-xs text-gray-400 uppercase tracking-wide font-bold">Address</label><p class="text-sm font-medium text-gray-700 mt-1">${v.address}</p></div>
                        <div class="bg-gray-50 p-3 rounded border border-gray-100"><label class="text-xs text-gray-400 uppercase tracking-wide font-bold">Phone</label><p class="text-sm font-medium text-gray-700 mt-1">${v.phone}</p></div>
                    </div>
                    <div class="bg-red-50 p-5 rounded-xl border border-red-100 text-center"><label class="text-xs text-red-600 uppercase font-bold tracking-wide">Total Outstanding Debt</label><p class="text-3xl font-bold text-red-700 mt-2">${utils.formatCurrency(debt)}</p></div>
                    <div>
                        <h4 class="text-sm font-bold text-gray-700 mb-3 border-b pb-2">Unpaid Invoices</h4>
                        ${unpaidExpenses.length === 0 ? '<p class="text-xs text-gray-400 italic">No unpaid invoices.</p>' :
                    `<ul class="space-y-2">${unpaidExpenses.map(e => `<li class="flex justify-between text-xs p-2 bg-white border rounded hover:bg-gray-50"><span>${e.date} (${e.id})</span><span class="font-bold text-red-600">${utils.formatCurrency(e.balance)}</span></li>`).join('')}</ul>`
                }
                    </div>
                </div>`;
            ui.openDetail('VENDOR PROFILE', v.name, html,
                () => router.openEdit(id),
                () => ui.confirmDelete(id, (delId) => Controllers.vendors.delete(delId))
            );
        },
        form: async (id = null) => {
            const isEdit = !!id;
            const data = id ? await API.getById('vendors', id) : { name: '', address: '', phone: '' };
            const html = `
                <div class="space-y-6">
                    <div><label class="block text-sm font-semibold text-gray-700 mb-1">Vendor Name</label><input type="text" id="inp-v-name" value="${data.name}" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"></div>
                    <div><label class="block text-sm font-semibold text-gray-700 mb-1">Address</label><input type="text" id="inp-v-addr" value="${data.address}" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"></div>
                    <div><label class="block text-sm font-semibold text-gray-700 mb-1">Phone</label><input type="text" id="inp-v-phone" value="${data.phone}" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"></div>
                </div>`;

            ui.openForm(id ? 'Edit Vendor' : 'New Vendor', html, async () => {
                const payload = {
                    id: id || utils.generateId('VND'),
                    name: document.getElementById('inp-v-name').value,
                    address: document.getElementById('inp-v-addr').value,
                    phone: document.getElementById('inp-v-phone').value
                };
                isEdit ? await API.update('vendors', id, payload) : await API.create('vendors', payload);
                await utils.refreshCache();
                ui.closeForm();
                router.navigate('vendors');
            });
        },
        delete: async (id) => {
            await API.delete('vendors', id);
            await utils.refreshCache();
            router.navigate('vendors');
        }
    },

    // --- WALLETS MODULE ---
    wallets: {
        list: async () => {
            const data = await API.get('wallets');
            const rows = data.map(w => ({
                id: w.id,
                cells: [
                    `<span class="font-mono text-xs text-gray-500">${w.id}</span>`,
                    `<span class="font-semibold text-gray-900">${w.name}</span>`,
                    w.currency,
                    `<span class="font-bold text-blue-700">${utils.formatCurrency(w.balance)}</span>`
                ]
            }));
            ui.renderTable(['ID', 'Wallet Name', 'Currency', 'Current Balance'], rows);
        },
        detail: async (id) => {
            const w = await API.getById('wallets', id);
            const payments = await API.get('payments');
            const deposits = await API.get('deposits');

            const walletPayments = payments.filter(p => p.walletId === id).map(p => ({
                ...p, type: 'payment',
                label: `To: ${utils.getVendorName(p.vendorId)}`,
                sign: '-', color: 'text-red-600'
            }));

            const walletDeposits = deposits.filter(d => d.walletId === id).map(d => ({
                ...d, type: 'deposit',
                label: `From: ${d.vendorId ? utils.getVendorName(d.vendorId) : d.source}`,
                sign: '+', color: 'text-green-600'
            }));

            const history = [...walletPayments, ...walletDeposits].sort((a, b) => new Date(b.date) - new Date(a.date));

            const html = `
                <div class="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl p-6 text-white mb-8 shadow-lg relative overflow-hidden">
                    <div class="absolute top-0 right-0 -mt-2 -mr-2 w-16 h-16 bg-white opacity-10 rounded-full"></div>
                    <p class="text-blue-100 text-sm mb-1 font-medium tracking-wide uppercase">Available Balance</p>
                    <p class="text-3xl font-bold">${utils.formatCurrency(w.balance)}</p>
                    <p class="text-xs text-blue-200 mt-4 font-mono">${w.id}</p>
                </div>
                <div>
                    <h4 class="font-bold text-gray-700 mb-4 text-sm uppercase tracking-wide border-b pb-2 flex items-center"><i data-lucide="history" class="w-4 h-4 mr-2"></i> Transaction History</h4>
                    <div class="space-y-3">
                        ${history.length === 0 ? '<p class="text-sm text-gray-400 italic">No transactions recorded yet.</p>' :
                    history.map(h => `
                        <div class="flex items-center justify-between p-3 bg-white border border-gray-100 rounded-lg shadow-sm hover:bg-gray-50 transition-colors">
                            <div class="flex items-center">
                                <div class="w-8 h-8 rounded-full ${h.type === 'deposit' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'} flex items-center justify-center mr-3">
                                    <i data-lucide="${h.type === 'deposit' ? 'arrow-down-left' : 'arrow-up-right'}" class="w-4 h-4"></i>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500">${h.date}</p>
                                    <p class="text-sm font-medium text-gray-800">${h.label}</p>
                                </div>
                            </div>
                            <span class="${h.color} font-bold text-sm">${h.sign}${utils.formatCurrency(h.amount)}</span>
                        </div>`).join('')}
                    </div>
                </div>`;
            ui.openDetail('WALLET', w.name, html,
                () => router.openEdit(id),
                () => ui.confirmDelete(id, (delId) => Controllers.wallets.delete(delId))
            );
        },
        form: async (id = null) => {
            const data = id ? await API.getById('wallets', id) : { name: '', balance: 0 };
            const html = `
                <div class="space-y-6">
                    <div><label class="block text-sm font-semibold text-gray-700 mb-1">Wallet Name</label><input type="text" id="inp-w-name" value="${data.name}" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"></div>
                    <div><label class="block text-sm font-semibold text-gray-700 mb-1">Opening Balance</label><input type="number" id="inp-w-bal" value="${data.balance}" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"></div>
                </div>`;
            ui.openForm(id ? 'Edit Wallet' : 'New Wallet', html, async () => {
                const payload = {
                    id: id || utils.generateId('WLT'),
                    name: document.getElementById('inp-w-name').value,
                    balance: parseFloat(document.getElementById('inp-w-bal').value),
                    currency: 'NGN'
                };
                id ? await API.update('wallets', id, payload) : await API.create('wallets', payload);
                await utils.refreshCache();
                ui.closeForm();
                router.navigate('wallets');
            });
        },
        delete: async (id) => {
            await API.delete('wallets', id);
            await utils.refreshCache();
            router.navigate('wallets');
        }
    },

    // --- PAYMENTS MODULE (Complex) ---
    payments: {
        list: async () => {
            const data = await API.get('payments');
            const rows = data.map(p => ({
                id: p.id,
                cells: [
                    `<span class="font-mono text-xs">${p.id}</span>`,
                    p.date,
                    `<span class="font-medium text-blue-600">${utils.getVendorName(p.vendorId)}</span>`,
                    utils.getWalletName(p.walletId),
                    `<span class="font-bold text-gray-800">${utils.formatCurrency(p.amount)}</span>`
                ]
            }));
            ui.renderTable(['ID', 'Date', 'Recipient Vendor', 'Source Wallet', 'Amount Paid'], rows);
        },
        detail: async (id) => {
            const p = await API.getById('payments', id);

            // Safety: p.refs might be a JSON string from Sheets or missing
            let refs = [];
            try {
                refs = typeof p.refs === 'string' ? JSON.parse(p.refs) : (p.refs || []);
            } catch (e) {
                console.warn("Failed to parse payment refs:", p.refs);
                refs = [];
            }

            const html = `
                <div class="space-y-5 text-sm">
                    <div class="flex justify-between border-b border-gray-100 pb-2"><span class="text-gray-500">Payment Date</span><span class="font-medium">${p.date}</span></div>
                    <div class="flex justify-between border-b border-gray-100 pb-2"><span class="text-gray-500">Recipient Vendor</span><span class="font-medium text-blue-600">${utils.getVendorName(p.vendorId)}</span></div>
                    <div class="flex justify-between border-b border-gray-100 pb-2"><span class="text-gray-500">Source Wallet</span><span class="font-medium">${utils.getWalletName(p.walletId)}</span></div>
                    <div class="flex justify-between bg-blue-50 p-4 rounded-lg mt-4"><span class="text-blue-800 font-bold uppercase text-xs tracking-wider pt-1">Total Paid</span><span class="font-bold text-2xl text-blue-800">${utils.formatCurrency(p.amount)}</span></div>
                    <div class="bg-gray-50 p-4 rounded-lg border border-gray-100">
                        <p class="text-xs font-bold text-gray-400 mb-3 uppercase tracking-wider">Applied to Expenses</p>
                        ${refs.length > 0 ? refs.map(ref => `
                            <div class="flex justify-between text-xs mb-2 items-center">
                                <span class="font-mono bg-white border px-1 rounded text-gray-600">${ref}</span>
                                <span class="text-green-600 font-medium bg-green-50 px-2 py-0.5 rounded-full">Paid</span>
                            </div>`).join('') : '<p class="text-xs text-gray-400 italic">No allocations found.</p>'}
                    </div>
                </div>`;
            ui.openDetail('PAYMENT RECEIPT', p.id, html,
                null,
                () => ui.confirmDelete(id, (delId) => Controllers.payments.delete(delId))
            );
        },
        delete: async (id) => {
            await API.delete('payments', id);
            router.navigate('payments');
        },
        form: async () => {
            const vendors = await API.get('vendors');
            const wallets = await API.get('wallets');

            const html = `
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 h-full">
                    <div class="lg:col-span-1 space-y-6">
                        
                        <!-- NEW: Transfer Type Toggle -->
                        <div class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
                            <span class="text-sm font-bold text-gray-700 uppercase tracking-wide">Transfer Type</span>
                            <div class="flex bg-gray-100 rounded-lg p-1">
                                <button id="type-payment-btn" class="px-3 py-1.5 text-xs font-bold rounded-md bg-white text-blue-700 shadow-sm transition-all">Out (Pay)</button>
                                <button id="type-deposit-btn" class="px-3 py-1.5 text-xs font-bold rounded-md text-gray-500 hover:text-gray-700 transition-all">In (Receive)</button>
                            </div>
                            <input type="hidden" id="txn-type" value="payment">
                        </div>

                        <div class="bg-blue-50 p-6 rounded-xl border border-blue-100 shadow-sm transition-colors" id="vendor-panel">
                            <label class="block text-sm font-bold text-blue-900 mb-3 uppercase tracking-wide" id="lbl-vendor">Target Vendor</label>
                            <select id="pay-vendor-select" class="w-full border-gray-300 rounded-lg shadow-sm p-3 border focus:ring-2 focus:ring-blue-500 bg-white">
                                <option value="">-- Choose Vendor --</option>
                                ${vendors.map(v => `<option value="${v.id}">${v.name}</option>`).join('')}
                            </select>
                        </div>
                        <div class="p-6 rounded-xl border border-gray-200 bg-white transition-colors" id="wallet-panel">
                            <label class="block text-sm font-bold text-gray-700 mb-3 uppercase tracking-wide" id="lbl-wallet">Source Wallet</label>
                            <select id="pay-wallet-select" class="w-full border-gray-300 rounded-lg shadow-sm p-3 border focus:ring-2 focus:ring-gray-500 bg-white">
                                ${wallets.map(w => `<option value="${w.id}">${w.name} (${utils.formatCurrency(w.balance)})</option>`).join('')}
                            </select>
                        </div>
                        
                        <div class="p-6 rounded-xl border border-gray-200 bg-white shadow-sm">
                            <label class="block text-sm font-bold text-gray-700 mb-3 uppercase tracking-wide">Amount</label>
                            <div class="flex items-center mb-3" id="full-pay-wrapper">
                                <input type="checkbox" id="pay-full-chk" class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500">
                                <label for="pay-full-chk" class="ml-2 text-sm text-gray-700 font-medium">Pay Full Amount</label>
                            </div>
                            <div class="relative">
                                <span class="absolute left-3 top-2 text-gray-500 font-bold">₦</span>
                                <input type="number" id="pay-amount-input" class="pl-8 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border font-bold" placeholder="0.00">
                            </div>
                        </div>
                        <div class="bg-gray-800 text-white p-6 rounded-xl text-center shadow-lg" id="total-display-panel">
                            <span class="text-xs text-gray-400 uppercase tracking-wide font-bold">Total Allocated</span>
                            <div id="pay-total-display" class="text-4xl font-bold mt-2">₦ 0.00</div>
                        </div>
                    </div>
                    <div class="lg:col-span-2 border border-gray-200 rounded-xl overflow-hidden flex flex-col bg-white shadow-sm" id="unpaid-bills-panel">
                        <div class="bg-gray-50 px-6 py-4 border-b border-gray-200 text-sm font-bold text-gray-600 flex justify-between items-center">
                            <span>Unpaid Expenses</span><span class="text-xs font-normal text-gray-400">Enter amounts in the 'Payment' column</span>
                        </div>
                        <div id="pay-bills-container" class="flex-1 overflow-y-auto p-0 bg-white min-h-[300px]">
                            <div class="flex flex-col items-center justify-center h-full text-gray-400"><i data-lucide="arrow-left-circle" class="w-12 h-12 mb-3 opacity-20"></i><p>Select a vendor on the left to start.</p></div>
                        </div>
                    </div>
                    <!-- Empty State for Deposit Mode (replaces bills panel) -->
                    <div id="deposit-info-panel" class="hidden lg:col-span-2 flex items-center justify-center bg-gray-50 rounded-xl border border-dashed border-gray-300 text-gray-400 p-10 text-center">
                        <div>
                            <i data-lucide="download-cloud" class="w-16 h-16 mx-auto mb-4 opacity-50"></i>
                            <h3 class="text-lg font-bold text-gray-600">Receiving Funds</h3>
                            <p class="max-w-xs mx-auto mt-2 text-sm">Funds will be added to the selected wallet immediately. Vendor debt balance will NOT be affected.</p>
                        </div>
                    </div>
                </div>`;

            ui.openForm('Record Transfer', html, async () => {
                const type = document.getElementById('txn-type').value;
                const vendorId = document.getElementById('pay-vendor-select').value;
                const walletId = document.getElementById('pay-wallet-select').value;
                const amountInput = parseFloat(document.getElementById('pay-amount-input').value) || 0;

                if (!vendorId) return alert('Please select a vendor.');

                let payload = {};

                if (type === 'payment') {
                    // PAYMENT LOGIC
                    let total = 0;
                    const allocations = [];
                    document.querySelectorAll('.alloc-input').forEach(inp => {
                        const val = parseFloat(inp.value) || 0;
                        if (val > 0) { total += val; allocations.push({ id: inp.dataset.id, amount: val }); }
                    });
                    if (total === 0) return alert("Please allocate an amount.");
                    const wallet = await API.getById('wallets', walletId);
                    if (wallet.balance < total) return alert(`Insufficient funds. Need ${utils.formatCurrency(total)}.`);

                    payload = {
                        type: 'payment',
                        vendorId, walletId, amount: total,
                        allocations
                    };
                } else {
                    // DEPOSIT LOGIC
                    if (amountInput <= 0) return alert("Please enter a valid amount.");
                    payload = {
                        type: 'deposit',
                        vendorId, walletId, amount: amountInput
                    };
                }

                await API.create('payments', payload);
                await utils.refreshCache();
                ui.closeForm();
                router.navigate('payments');
            });

            // --- Dynamic Form Logic ---
            const toggleType = (type) => {
                const isPay = type === 'payment';
                document.getElementById('txn-type').value = type;

                // Toggle Button Styles
                const payBtn = document.getElementById('type-payment-btn');
                const depBtn = document.getElementById('type-deposit-btn');

                if (isPay) {
                    payBtn.className = "px-3 py-1.5 text-xs font-bold rounded-md bg-white text-blue-700 shadow-sm transition-all";
                    depBtn.className = "px-3 py-1.5 text-xs font-bold rounded-md text-gray-500 hover:text-gray-700 transition-all";

                    // Show Payment UI
                    document.getElementById('unpaid-bills-panel').classList.remove('hidden');
                    document.getElementById('deposit-info-panel').classList.add('hidden');
                    document.getElementById('full-pay-wrapper').classList.remove('hidden');
                    document.getElementById('total-display-panel').classList.remove('hidden');
                    document.getElementById('pay-amount-input').disabled = false; // logic will handle

                    // Update Labels
                    document.getElementById('lbl-vendor').innerText = "Target Vendor";
                    document.getElementById('lbl-wallet').innerText = "Source Wallet";
                    document.getElementById('vendor-panel').className = "bg-blue-50 p-6 rounded-xl border border-blue-100 shadow-sm transition-colors";
                } else {
                    depBtn.className = "px-3 py-1.5 text-xs font-bold rounded-md bg-green-100 text-green-700 shadow-sm transition-all";
                    payBtn.className = "px-3 py-1.5 text-xs font-bold rounded-md text-gray-500 hover:text-gray-700 transition-all";

                    // Show Deposit UI
                    document.getElementById('unpaid-bills-panel').classList.add('hidden');
                    document.getElementById('deposit-info-panel').classList.remove('hidden');
                    document.getElementById('full-pay-wrapper').classList.add('hidden');
                    document.getElementById('total-display-panel').classList.add('hidden');
                    document.getElementById('pay-amount-input').disabled = false;
                    document.getElementById('pay-amount-input').value = '';

                    // Update Labels
                    document.getElementById('lbl-vendor').innerText = "Source Vendor";
                    document.getElementById('lbl-wallet').innerText = "Target Wallet";
                    document.getElementById('vendor-panel').className = "bg-green-50 p-6 rounded-xl border border-green-100 shadow-sm transition-colors";
                    document.getElementById('wallet-panel').className = "bg-green-50 p-6 rounded-xl border border-green-100 shadow-sm transition-colors";
                }
            };

            document.getElementById('type-payment-btn').onclick = () => toggleType('payment');
            document.getElementById('type-deposit-btn').onclick = () => toggleType('deposit');


            document.getElementById('pay-vendor-select').onchange = async (e) => {
                const vendorId = e.target.value;
                // Only run expense fetching if in payment mode
                if (document.getElementById('txn-type').value === 'deposit') return;

                const container = document.getElementById('pay-bills-container');
                // ... (existing logic reset) ...
                document.getElementById('pay-amount-input').value = '';
                document.getElementById('pay-amount-input').disabled = false;
                document.getElementById('pay-full-chk').checked = false;
                document.getElementById('pay-total-display').innerText = utils.formatCurrency(0);

                if (!vendorId) return;

                const expenses = await API.get('expenses');
                const bills = expenses.filter(x => x.vendorId === vendorId && x.status !== 'Paid');

                if (bills.length === 0) {
                    container.innerHTML = '<div class="p-10 text-center text-green-600">No outstanding bills.</div>';
                    return;
                }

                let tHtml = `<table class="min-w-full divide-y divide-gray-200 text-sm"><tbody class="divide-y divide-gray-200">`;
                bills.forEach(b => {
                    tHtml += `<tr>
                        <td class="px-6 py-4 text-gray-500">${b.date}</td>
                        <td class="px-6 py-4"><div class="font-medium text-gray-900">${b.category}</div><div class="text-xs text-gray-400 font-mono">${b.id}</div></td>
                        <td class="px-6 py-4 text-right text-red-600 font-bold">${utils.formatCurrency(b.balance)}</td>
                        <td class="px-6 py-4"><input type="number" data-id="${b.id}" max="${b.balance}" class="alloc-input w-full border-gray-300 rounded-md shadow-sm p-2 border text-right font-mono font-bold" placeholder="0.00"></td>
                    </tr>`;
                });
                tHtml += `</tbody></table>`;
                container.innerHTML = tHtml;

                // Re-bind listeners for inputs (using same loop as before)
                const updateTotalDisplay = () => {
                    let tot = 0;
                    document.querySelectorAll('.alloc-input').forEach(i => {
                        let v = parseFloat(i.value) || 0;
                        const m = parseFloat(i.getAttribute('max'));
                        if (v > m) { v = m; i.value = m; }
                        tot += v;
                    });
                    document.getElementById('pay-total-display').innerText = utils.formatCurrency(tot);
                };

                document.querySelectorAll('.alloc-input').forEach(inp => {
                    inp.addEventListener('input', updateTotalDisplay);
                });

                // Re-bind global amount logic
                const amtInput = document.getElementById('pay-amount-input');
                const fullChk = document.getElementById('pay-full-chk');

                fullChk.addEventListener('change', (e) => {
                    const inputs = document.querySelectorAll('.alloc-input');
                    if (e.target.checked) {
                        let gt = 0;
                        inputs.forEach(i => {
                            const m = parseFloat(i.getAttribute('max'));
                            i.value = m; gt += m;
                        });
                        amtInput.value = gt; amtInput.disabled = true;
                    } else {
                        inputs.forEach(i => i.value = '');
                        amtInput.value = ''; amtInput.disabled = false;
                    }
                    updateTotalDisplay();
                });

                amtInput.addEventListener('input', (e) => {
                    if (fullChk.checked) return;
                    const val = parseFloat(e.target.value) || 0;
                    let rem = val;
                    document.querySelectorAll('.alloc-input').forEach(i => {
                        const m = parseFloat(i.getAttribute('max'));
                        if (rem > 0) {
                            const t = Math.min(rem, m);
                            i.value = t; rem -= t;
                        } else { i.value = ''; }
                    });
                    updateTotalDisplay();
                });
            };
        }
    },

    settings: {
        list: async () => {
            ui.setPageTitle('Sync Settings');
            ui.hideMainAction();

            // Initial placeholder
            ui.renderView(`
                <div class="flex items-center justify-center p-20">
                    <div class="text-center">
                        <i data-lucide="loader" class="w-10 h-10 animate-spin text-blue-600 mx-auto mb-4"></i>
                        <p class="text-gray-500 font-medium">Checking sync status...</p>
                    </div>
                </div>
            `);

            try {
                const status = await API.req('sync/status');
                const diff = await API.req('sync/diff');

                ui.renderView(`
                    <div class="p-8 max-w-3xl mx-auto space-y-8 animate-fade-in">
                        <!-- Diff Overview -->
                        <div class="grid grid-cols-1 gap-6">
                            <div class="bg-blue-50 rounded-xl p-6 border border-blue-100 shadow-sm relative overflow-hidden">
                                <i data-lucide="arrow-up-circle" class="absolute -right-4 -bottom-4 w-24 h-24 text-blue-100/50"></i>
                                <p class="text-xs font-bold text-blue-600 uppercase tracking-wider mb-1">Pending Changes (To Push)</p>
                                <p class="text-4xl font-bold text-blue-900">${diff.pending_push}</p>
                            </div>
                        </div>

                        <!-- Main Status Card -->
                        <div class="bg-white rounded-2xl border border-gray-200 shadow-xl overflow-hidden">
                            <div class="px-8 py-5 border-b border-gray-100 bg-gray-50/50 flex justify-between items-center">
                                <div class="flex items-center">
                                    <div class="w-2 h-2 rounded-full bg-green-500 mr-3 animate-pulse"></div>
                                    <h3 class="font-bold text-gray-800">Connection: Active</h3>
                                </div>
                                <span class="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded-full uppercase tracking-widest">
                                    ${status.last_sync.status}
                                </span>
                            </div>
                            
                            <div class="p-8">
                                <h4 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-6 pb-2 border-b">Resource Breakdown</h4>
                                <div class="space-y-4">
                                    ${Object.entries(diff.details).map(([name, counts]) => `
                                        <div class="flex items-center justify-between p-4 rounded-xl hover:bg-gray-50 transition-colors border border-transparent hover:border-gray-100">
                                            <div class="flex items-center">
                                                <div class="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center mr-4">
                                                    <i data-lucide="${name === 'Expenses' ? 'receipt' : name === 'Wallets' ? 'wallet' : 'database'}" class="w-5 h-5 text-gray-500"></i>
                                                </div>
                                                <span class="font-bold text-gray-700">${name}</span>
                                            </div>
                                            <div class="flex space-x-7">
                                                <div class="text-right">
                                                    <p class="text-[10px] font-bold text-gray-400 uppercase">Pending</p>
                                                    <p class="font-bold ${counts.push > 0 ? 'text-blue-600' : 'text-gray-300'}">${counts.push}</p>
                                                </div>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>

                            <div class="px-8 py-6 border-t border-gray-100 bg-gray-50/50 flex items-center justify-between">
                                <div class="text-xs text-gray-500">
                                    Last Sync: <b>${status.last_sync.time ? new Date(status.last_sync.time).toLocaleString() : 'Never'}</b>
                                </div>
                                <button id="btn-sync-now" class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl text-md font-bold flex items-center transition-all shadow-lg shadow-blue-200 active:scale-95 disabled:opacity-50">
                                    <i data-lucide="upload-cloud" class="w-5 h-5 mr-3"></i> Push to Cloud
                                </button>
                            </div>
                        </div>

                        <!-- Footer Actions -->
                        <div class="flex space-x-4 items-end">
                            <div class="flex-1 bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                                <label class="block text-xs font-bold text-gray-400 uppercase mb-3">Sync Frequency (Seconds)</label>
                                <div class="flex space-x-2">
                                    <input type="number" id="input-frequency" value="${status.settings.sync_frequency}" class="w-32 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                    <button id="btn-save-settings" class="bg-gray-800 hover:bg-black text-white px-4 py-2 rounded-lg text-sm font-bold transition-all">Save</button>
                                </div>
                            </div>
                            <div class="flex-shrink-0">
                                <button id="btn-force-pull" class="text-gray-400 hover:text-red-500 px-4 py-2 text-xs font-medium transition-colors">
                                    <i data-lucide="alert-triangle" class="w-3 h-3 inline-block mr-1"></i> Hard Reset Local Data
                                </button>
                            </div>
                        </div>
                    </div>
                `);

                // Wire up events
                document.getElementById('btn-sync-now').onclick = async () => {
                    const btn = document.getElementById('btn-sync-now');
                    const originalHtml = btn.innerHTML;
                    btn.disabled = true;
                    btn.innerHTML = '<i data-lucide="loader" class="w-4 h-4 mr-2 animate-spin"></i> Pushing...';
                    ui.renderIcons();

                    try {
                        const res = await API.req('sync/force', 'POST');
                        btn.innerHTML = '<i data-lucide="check" class="w-4 h-4 mr-2"></i> Push Started';
                        btn.classList.replace('bg-blue-600', 'bg-green-600');
                        ui.renderIcons();

                        // Wait 3 seconds then refresh the status view
                        setTimeout(() => {
                            Controllers.settings.list();
                        }, 3000);
                    } catch (e) {
                        btn.disabled = false;
                        btn.innerHTML = originalHtml;
                        ui.renderIcons();
                        alert('Failed to start sync: ' + e.message);
                    }
                };

                document.getElementById('btn-save-settings').onclick = async () => {
                    const freq = parseInt(document.getElementById('input-frequency').value);
                    await API.req('sync/settings', 'POST', { sync_frequency: freq });
                    alert('Settings updated!');
                    Controllers.settings.list();
                };

                document.getElementById('btn-force-pull').onclick = async () => {
                    if (confirm('DANGER: This will delete all local changes and pull everything from Google Sheets. Continue?')) {
                        await API.req('sync/pull', 'POST');
                        location.reload();
                    }
                };

                ui.renderIcons();

            } catch (err) {
                ui.renderView(`
                    <div class="p-20 text-center">
                        <div class="w-20 h-20 bg-red-50 text-red-500 rounded-full flex items-center justify-center mx-auto mb-6">
                            <i data-lucide="cloud-off" class="w-10 h-10"></i>
                        </div>
                        <h3 class="text-xl font-bold text-gray-800 mb-2">Connection Failed</h3>
                        <p class="text-gray-500 mb-8 max-w-sm mx-auto">Could not reach the sync server. Please check your network and Google Sheets configuration.</p>
                        <button onclick="router.navigate('settings')" class="bg-gray-800 text-white px-6 py-2 rounded-lg font-bold">Retry Connection</button>
                    </div>
                `);
                ui.renderIcons();
            }
        }
    }
};
