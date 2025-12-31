/**
 * Central State Management
 */
export const store = {
    currentView: 'expenses',
    selectedId: null,

    // Simple state setter
    setState(key, value) {
        this[key] = value;
    }
};