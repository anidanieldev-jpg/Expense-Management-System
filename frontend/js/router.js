/**
 * Router Module
 * Handles View switching and initialization.
 */
import { store } from './store.js';
import { ui } from './ui.js?v=4';

export const router = {
    registry: {},

    register: (view, controller) => {
        router.registry[view] = controller;
    },

    navigate: async (view) => {
        store.currentView = view;
        store.selectedId = null;

        ui.setActiveNav(view);
        ui.closeDetail();

        // Titles and Buttons
        const titles = { expenses: 'Manage Expenses', payments: 'Payment History', vendors: 'Manage Vendors', wallets: 'My Wallets', settings: 'Sync Settings' };
        const btnTexts = { expenses: 'New Expense', payments: 'Record Payment', vendors: 'Add Vendor', wallets: 'Add Wallet' };

        if (titles[view]) document.getElementById('page-title').innerText = titles[view];

        const mainBtn = document.getElementById('main-action-btn');
        if (btnTexts[view]) {
            document.getElementById('main-action-text').innerText = btnTexts[view];
            mainBtn.classList.remove('hidden');
            mainBtn.onclick = () => router.registry[view].form(null);
        } else {
            mainBtn.classList.add('hidden');
        }

        // Load List
        await router.registry[view].list();
    },

    openEdit: (id) => {
        router.registry[store.currentView].form(id);
    }
};