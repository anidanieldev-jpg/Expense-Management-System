/**
 * Helper Functions
 */
import { API } from './api.js';

let cachedVendors = [];
let cachedWallets = [];

// Pre-fetch names for looking up IDs quickly
const loadCache = async () => {
    const [vendors, wallets] = await Promise.all([
        API.get('vendors'),
        API.get('wallets')
    ]);
    cachedVendors = vendors;
    cachedWallets = wallets;
};

export const utils = {
    init: async () => {
        await loadCache();
    },

    formatCurrency: (num) => '₦ ' + Number(num).toLocaleString('en-NG', { minimumFractionDigits: 2 }),

    getVendorName: (id) => cachedVendors.find(v => v.id === id)?.name || 'Unknown Vendor',
    getWalletName: (id) => cachedWallets.find(w => w.id === id)?.name || 'Unknown Wallet',

    getStatusClass: (status) => {
        if (status === 'Paid') return 'badge-paid';
        if (status === 'Partial') return 'badge-partial';
        return 'badge-unpaid';
    },

    generateId: (prefix) => prefix + '-' + Math.floor(100000 + Math.random() * 900000),

    today: () => new Date().toISOString().split('T')[0],

    // Refresh cache if needed (e.g., after adding a vendor)
    refreshCache: async () => await loadCache()
};