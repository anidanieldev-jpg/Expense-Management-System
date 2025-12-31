# Expense Manager API Reference

**Base URL:** `http://localhost:3000/v1`

Welcome to the **Expense Management System (EMS) API**. This documentation provides detailed information on how to interact with the EMS backend. Our API follows RESTful principles and returns JSON-formatted responses.

---

## Table of Contents
1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [Errors](#errors)
4. [Standard Response Structure](#standard-response-structure)
5. [Resources](#resources)
    - [Vendors](#vendors)
    - [Wallets](#wallets)
    - [Expenses](#expenses)
    - [Payments](#payments)
    - [Sync](#sync)

---

## Introduction
The EMS API allows developers to manage business expenses, track vendor debts, and handle wallet-based payments. It is designed to be lightweight and efficient, perfect for running on `localhost` during development.

---

## Authentication
Currently, the API does not require authentication for local development. However, for production-ready versions, we recommend using the `X-API-Key` header.

| Header | Description |
| :--- | :--- |
| `Content-Type` | `application/json` |
| `X-API-Key` | (Optional) Your private API key |

---

## Errors
The EMS API uses standard HTTP status codes combined with a specific JSON error structure to communicate failures.

### Error Response Schema
```json
{
  "code": 1002,
  "message": "Resource not found."
}
```

### HTTP Status Codes
| Status Code | Description |
| :--- | :--- |
| `200 OK` | The request was successful. |
| `201 Created` | A new resource was successfully created. |
| `400 Bad Request` | Malformed parameters or business logic failure. |
| `401 Unauthorized` | Invalid or missing API key. |
| `404 Not Found` | The requested resource or URL does not exist. |
| `500 Internal Error` | An unexpected error occurred on the server. |

---

## Standard Response Structure
All successful API responses return a JSON object containing a `code` (0 for success) and the resource data.

### Single Resource
```json
{
  "code": 0,
  "message": "success",
  "vendor": {
    "id": "VND-001",
    "name": "Fair Aunty",
    "address": "Ayetoro (Poultry)",
    "phone": "08012345678"
  }
}
```

### Collection of Resources
```json
{
  "code": 0,
  "message": "success",
  "vendors": [
    { "id": "VND-001", "name": "Fair Aunty" },
    { "id": "VND-002", "name": "Mama Favor" }
  ]
}
```

---

## Resources

### Vendors
Manage your business suppliers and service providers.

#### List All Vendors
`GET /vendors`

**Example Request:**
`GET http://localhost:3000/v1/vendors`

**Example Response:**
```json
{
  "code": 0,
  "message": "success",
  "vendors": [
    {
      "id": "VND-001",
      "name": "Fair Aunty (Silifat)",
      "address": "Ayetoro (Poultry)",
      "phone": "08012345678"
    },
    {
      "id": "VND-002",
      "name": "Mama Favor",
      "address": "Market Road, Shop 22",
      "phone": "08087654321"
    }
  ]
}
```

#### Create a Vendor
`POST /vendors`

**Example Request Body:**
```json
{
  "name": "Poultry Feeders Ltd",
  "address": "Ikeja Industrial Estate",
  "phone": "08099887766"
}
```

**Example Response:**
```json
{
  "code": 0,
  "message": "Vendor created successfully",
  "vendor": {
    "id": "VND-004",
    "name": "Poultry Feeders Ltd",
    "address": "Ikeja Industrial Estate",
    "phone": "08099887766"
  }
}
```

---

### Wallets
Track your bank accounts, mobile wallets, and cash on hand.

#### List Wallets
`GET /wallets`

**Example Response:**
```json
{
  "code": 0,
  "message": "success",
  "wallets": [
    { "id": "WLT-01", "name": "Opay (Main)", "balance": 38300, "currency": "NGN" },
    { "id": "WLT-02", "name": "GTBank", "balance": 125000, "currency": "NGN" }
  ]
}
```

#### Update Wallet
`PATCH /wallets/:id`

**Example Request Body:**
```json
{
  "balance": 45000,
  "name": "Opay (Savings)"
}
```

**Example Response:**
```json
{
  "code": 0,
  "message": "Wallet updated",
  "wallet": {
    "id": "WLT-01",
    "name": "Opay (Savings)",
    "balance": 45000,
    "currency": "NGN"
  }
}
```

---

### Expenses
Manage invoices and bills from vendors.

#### List Expenses
`GET /expenses`

**Example Response:**
```json
{
  "code": 0,
  "message": "success",
  "expenses": [
    {
      "id": "AEX-000001",
      "vendorId": "VND-001",
      "date": "2025-12-01",
      "total": 5300,
      "balance": 0,
      "status": "Paid",
      "category": "Poultry",
      "description": "Monthly broiler feed stock"
    }
  ]
}
```

#### Record New Expense
`POST /expenses`

**Example Request Body:**
```json
{
  "vendorId": "VND-002",
  "date": "2025-12-29",
  "total": 7500,
  "category": "Logistics",
  "description": "Transport for day-old chicks"
}
```

**Example Response:**
```json
{
  "code": 0,
  "message": "Expense recorded",
  "expense": {
    "id": "AEX-000004",
    "vendorId": "VND-002",
    "date": "2025-12-29",
    "total": 7500,
    "balance": 7500,
    "status": "Unpaid",
    "category": "Logistics"
  }
}
```

---

### Payments & Deposits (Unified)
Handle flow of funds both in and out.

#### Record Transfer
`POST /payments`

**Description:** Records a financial transaction.
- **Type `payment`**: Money sends OUT. Deducts from wallet, reduces vendor debt.
- **Type `deposit`**: Money comes IN. Adds to wallet, does NOT affect vendor debt.

**Example Request Body (Payment):**
```json
{
  "type": "payment",
  "vendorId": "VND-001",
  "walletId": "WLT-01",
  "amount": 10000,
  "allocations": [
    { "id": "AEX-000002", "amount": 8000 },
    { "id": "AEX-000003", "amount": 2000 }
  ]
}
```

**Example Request Body (Deposit):**
```json
{
  "type": "deposit",
  "vendorId": "VND-001",
  "walletId": "WLT-01",
  "amount": 50000
}
```

#### List Deposits
`GET /deposits`

**Example Response:**
```json
{
  "code": 0,
  "message": "success",
  "deposits": [
    {
       "id": "DEP-78392",
       "date": "2025-12-30",
       "amount": 50000,
       "walletId": "WLT-01",
       "source": "Vendor Transfer",
       "vendorId": "VND-001"
    }
  ]
}
```

**Example Response (Success):**
```json
{
  "code": 0,
  "message": "Payment processed successfully",
  "payment": {
    "id": "PAY-00003",
    "date": "2025-12-29",
    "amount": 10000,
    "walletId": "WLT-01",
    "vendorId": "VND-001",
    "refs": ["AEX-000002", "AEX-000003"]
  }
}
```

**Example Response (Failure - Insufficient Balance):**
```json
{
  "code": 2001,
  "message": "Insufficient funds in source wallet. Current balance: 5000 NGN."
}
```

---

### Sync
Manage Google Sheets synchronization between local cache and cloud.

#### Get Sync Status
`GET /sync/status`

Returns current sync state, pending changes count, and settings.

**Example Response:**
```json
{
  "code": 0,
  "message": "success",
  "pending_count": 3,
  "last_sync": {
    "time": "2025-12-30T15:30:00.000Z",
    "status": "Success",
    "details": "Full pull complete"
  },
  "settings": {
    "sync_frequency": 300
  }
}
```

---

#### Get Sync Diff
`GET /sync/diff`

Compares local data with cloud data and returns detailed breakdown of changes.

**Example Response:**
```json
{
  "code": 0,
  "message": "success",
  "pending_push": 2,
  "pending_pull": 5,
  "details": {
    "Vendors": { "push": 0, "pull": 1 },
    "Wallets": { "push": 1, "pull": 0 },
    "Expenses": { "push": 1, "pull": 3 },
    "Payments": { "push": 0, "pull": 1 },
    "Deposits": { "push": 0, "pull": 0 }
  }
}
```

---

#### Force Full Sync
`POST /sync/force`

Triggers a unified sync operation: pushes all local changes, then pulls latest cloud state.

**Example Response:**
```json
{
  "code": 0,
  "message": "Full sync (Push + Pull) completed"
}
```

---

#### Force Pull
`POST /sync/pull`

Overwrites local cache with cloud data. **Use with caution** - discards unpushed local changes.

**Example Response:**
```json
{
  "code": 0,
  "message": "Full pull triggered from remote"
}
```

---

#### Update Settings
`POST /sync/settings`

Updates sync configuration.

**Example Request Body:**
```json
{
  "sync_frequency": 60
}
```

**Example Response:**
```json
{
  "code": 0,
  "message": "Settings updated"
}
```
