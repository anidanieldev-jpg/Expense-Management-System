/**
 * Application Entry Point
 * Orchestrates initialization.
 */
import { store } from './store.js';
import { utils } from './utils.js';
import { router } from './router.js';
import { ui } from './ui.js?v=4';
import { Controllers } from './controllers.js';

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Initialize Utils (Cache loading)
    await utils.init();

    // Expose router to window for inline HTML onclick handlers
    window.router = router;

    // 2. Register Controllers with Router
    router.register('expenses', Controllers.expenses);
    router.register('vendors', Controllers.vendors);
    router.register('wallets', Controllers.wallets);
    router.register('payments', Controllers.payments);
    router.register('settings', Controllers.settings);

    // 3. Setup Global Navigation Listeners
    document.querySelectorAll('.nav-item').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            // In a real app we might use data-link attributes
            const view = link.id.replace('nav-', '');
            router.navigate(view);
        });
    });

    // 4. Setup Global Event Delegation for Table Actions (Edit/Delete)
    const mainView = document.getElementById('main-view');
    mainView.addEventListener('click', (e) => {
        // Handle Row Click (Detail View)
        const row = e.target.closest('tr');
        if (row && row.dataset.id) {
            // Check if we clicked a button inside the row
            const btn = e.target.closest('button');
            if (btn) {
                const action = btn.dataset.action;
                const id = btn.dataset.id;
                e.stopPropagation(); // Don't trigger row click

                if (action === 'edit') router.openEdit(id);
                if (action === 'delete') ui.confirmDelete(id, (delId) => Controllers[store.currentView].delete(delId));
                if (action === 'add-funds') Controllers.wallets.addFunds(id);
            } else {
                // Regular row click
                // Use registry or Controllers directly is fine now that circular dep is gone
                Controllers[store.currentView].detail(row.dataset.id);
            }
        }
    });

    // 5. Setup Global UI Closers
    document.getElementById('close-detail-btn').onclick = ui.closeDetail;
    document.getElementById('close-form-btn-icon').onclick = ui.closeForm;
    document.getElementById('close-form-btn-text').onclick = ui.closeForm;
    // 6. Global Action Delegation (Document Level)
    // This catches clicks anywhere, including the dynamic Detail Panel and Modals
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('button');
        if (!btn) return;

        // Add Funds Action
        if (btn.dataset.action === 'add-funds') {
            e.preventDefault();
            e.stopPropagation();
            const id = btn.dataset.id;
            if (id && Controllers.wallets) {
                Controllers.wallets.addFunds(id);
            }
        }
    });

    // 6. Initial Route
    router.navigate('expenses');
});
