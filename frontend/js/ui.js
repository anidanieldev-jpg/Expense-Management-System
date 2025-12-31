/**
 * UI Controller
 * Handles generic DOM manipulations like Tables, Panels, Modals, and Forms.
 */
import { store } from './store.js';

export const ui = {
    // Icons
    renderIcons: () => {
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        } else {
            setTimeout(() => { if (typeof lucide !== 'undefined') lucide.createIcons() }, 100);
        }
    },

    // Navigation Styling
    setActiveNav: (view) => {
        document.querySelectorAll('.nav-item').forEach(el => {
            el.classList.remove('bg-blue-50', 'text-blue-600', 'border-blue-600');
            el.classList.add('border-transparent');
        });
        const active = document.getElementById(`nav-${view}`);
        if (active) {
            active.classList.add('bg-blue-50', 'text-blue-600', 'border-blue-600');
            active.classList.remove('border-transparent');
        }
    },

    setPageTitle: (title) => {
        const el = document.getElementById('page-title');
        if (el) el.innerText = title;
    },

    hideMainAction: () => {
        const btn = document.getElementById('main-action-btn');
        if (btn) btn.classList.add('hidden');
    },

    showMainAction: (text, onClick) => {
        const btn = document.getElementById('main-action-btn');
        if (btn) {
            btn.classList.remove('hidden');
            document.getElementById('main-action-text').innerText = text;
            btn.onclick = onClick;
        }
    },

    // --- View Renderer ---
    renderView: (html) => {
        const container = document.getElementById('main-view');
        if (container) {
            container.innerHTML = html;
            ui.renderIcons();
        }
    },

    // --- Table Renderer ---
    renderTable: (columns, rows, onRowClickName) => {
        const container = document.getElementById('main-view');
        if (!container) return;

        if (rows.length === 0) {
            container.innerHTML = `<div class="p-10 text-center text-gray-500 bg-white rounded-lg border border-gray-200 shadow-sm">No records found. Click "New" to create one.</div>`;
            return;
        }

        let html = `
            <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            ${columns.map(col => `
                                <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">
                                    ${col}
                                </th>
                            `).join('')}
                            <th class="px-6 py-3 text-right"></th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
        `;

        rows.forEach(row => {
            html += `<tr class="hover:bg-blue-50 cursor-pointer transition-colors group table-row-item" data-id="${row.id}">
                ${row.cells.map(cell => `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${cell}</td>`).join('')}
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button data-action="edit" data-id="${row.id}" class="text-blue-600 hover:text-blue-800 opacity-0 group-hover:opacity-100 transition-opacity mr-4" title="Edit">
                        <i data-lucide="pencil" class="w-4 h-4 pointer-events-none"></i>
                    </button>
                    <button data-action="delete" data-id="${row.id}" class="text-red-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity" title="Delete">
                        <i data-lucide="trash-2" class="w-4 h-4 pointer-events-none"></i>
                    </button>
                </td>
            </tr>`;
        });

        html += `</tbody></table></div>`;
        container.innerHTML = html;
        ui.renderIcons();
    },

    // --- Detail Panel ---
    openDetail: (subtitle, title, contentHtml, onEdit, onDelete) => {
        document.getElementById('detail-subtitle').innerText = subtitle;
        document.getElementById('detail-title').innerText = title;
        document.getElementById('detail-content').innerHTML = contentHtml;

        const panel = document.getElementById('detail-panel');
        panel.classList.remove('hidden');
        panel.classList.add('flex');

        // Setup Edit Button
        const editBtn = document.getElementById('detail-edit-btn');
        const newEditBtn = editBtn.cloneNode(true);
        editBtn.parentNode.replaceChild(newEditBtn, editBtn);

        if (onEdit) {
            newEditBtn.onclick = onEdit;
            newEditBtn.classList.remove('hidden');
        } else {
            newEditBtn.classList.add('hidden');
        }

        // Setup Delete Button
        const delBtn = document.getElementById('detail-delete-btn');
        const newDelBtn = delBtn.cloneNode(true);
        delBtn.parentNode.replaceChild(newDelBtn, delBtn);

        if (onDelete) {
            newDelBtn.onclick = onDelete;
            newDelBtn.classList.remove('hidden');
        } else {
            newDelBtn.classList.add('hidden');
        }

        ui.renderIcons();
    },

    closeDetail: () => {
        const panel = document.getElementById('detail-panel');
        panel.classList.add('hidden');
        panel.classList.remove('flex');
    },

    // --- Modal ---
    confirmDelete: (id, onConfirm) => {
        store.selectedId = id;
        const modal = document.getElementById('confirm-modal');
        modal.classList.remove('hidden');

        const confirmBtn = document.getElementById('confirm-delete-btn');
        // Clean listener
        const newBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newBtn, confirmBtn);

        newBtn.onclick = async () => {
            newBtn.disabled = true;
            newBtn.innerHTML = '<i data-lucide="loader" class="w-4 h-4 animate-spin"></i>';
            ui.renderIcons();

            try {
                await onConfirm(id);
                // Success: close modal and detail
                modal.classList.add('hidden');
                ui.closeDetail();
            } catch (error) {
                // Close confirm modal FIRST
                modal.classList.add('hidden');

                console.error("Delete failed:", error);

                // Show custom error modal with a slight delay for better UX
                setTimeout(() => {
                    ui.showAlert("Delete Failed", error.message || "Unknown error occurred.");
                }, 300);

            } finally {
                newBtn.disabled = false;
                newBtn.innerHTML = "Yes, Delete";
            }
        };

        const cancelBtn = document.getElementById('modal-cancel-btn');
        cancelBtn.onclick = () => {
            modal.classList.add('hidden');
        };
    },

    closeModal: () => document.getElementById('confirm-modal').classList.add('hidden'),

    // --- Alert Modal ---
    showAlert: (title, message) => {
        const modal = document.getElementById('alert-modal');
        document.getElementById('alert-title').innerText = title;
        document.getElementById('alert-message').innerText = message;

        modal.classList.remove('hidden');

        const okBtn = document.getElementById('alert-ok-btn');
        // Clean listener
        const newBtn = okBtn.cloneNode(true);
        okBtn.parentNode.replaceChild(newBtn, okBtn);

        newBtn.onclick = () => {
            modal.classList.add('hidden');
        };

        ui.renderIcons();
    },

    // --- Form ---
    openForm: (title, html, onSave) => {
        document.getElementById('form-title').innerText = title;
        document.getElementById('form-content').innerHTML = html;
        document.getElementById('full-screen-form').classList.remove('hidden');

        const saveBtn = document.getElementById('form-save-btn');
        // Clean listener
        const newBtn = saveBtn.cloneNode(true);
        saveBtn.parentNode.replaceChild(newBtn, saveBtn);

        newBtn.onclick = onSave;
        ui.renderIcons();
    },

    closeForm: () => document.getElementById('full-screen-form').classList.add('hidden'),

    toggleSidebar: () => {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('-translate-x-full');
    },

    renderIcons: () => {
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        } else {
            setTimeout(() => { if (typeof lucide !== 'undefined') lucide.createIcons() }, 100);
        }
    }
};