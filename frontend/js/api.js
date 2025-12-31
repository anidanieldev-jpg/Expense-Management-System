/**
 * API Service Layer
 * Connects to Python Flask Backend at http://localhost:3000/v1
 */

const BASE_URL = 'http://localhost:3000/v1';

// Key Mapping: Frontend collection names to API response keys
const KEYS = {
    vendors: 'vendors',
    wallets: 'wallets',
    expenses: 'expenses',
    payments: 'payments',
    deposits: 'deposits'
};

const request = async (endpoint, method = 'GET', body = null) => {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (body) options.body = JSON.stringify(body);

    try {
        const response = await fetch(`${BASE_URL}/${endpoint}`, options);
        // Catch 404s or 500s that might return HTML (if backend crashes)
        if (!response.ok) {
            let errorMsg = `Server Error: ${response.status}`;
            try {
                const errBody = await response.json();
                if (errBody.message) errorMsg = errBody.message;
            } catch (e) {
                // response was likely not JSON (e.g. 500 HTML page)
            }
            throw new Error(errorMsg);
        }

        const json = await response.json();

        if (json.code !== 0) {
            throw new Error(json.message || 'API Error');
        }
        return json;
    } catch (error) {
        console.error('API Request Failed:', error);
        throw error;
    }
};

export const API = {
    // Standard request
    req: request,

    // --- GENERIC CRUD ---
    get: async (collection) => {
        const json = await request(collection);
        return json[KEYS[collection]] || [];
    },

    getById: async (collection, id) => {
        const json = await request(`${collection}/${id}`);
        const singularKey = collection.slice(0, -1);
        return json[singularKey] || json[collection];
    },

    create: async (collection, data) => {
        const json = await request(collection, 'POST', data);
        const singularKey = collection.slice(0, -1);
        return json[singularKey];
    },

    update: async (collection, id, updates) => {
        const json = await request(`${collection}/${id}`, 'PATCH', updates);
        const singularKey = collection.slice(0, -1);
        return json[singularKey];
    },

    delete: async (collection, id) => {
        await request(`${collection}/${id}`, 'DELETE');
        return true;
    }
};