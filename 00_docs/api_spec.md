# API Specification - WalletWiz

This document details the REST API endpoints for the WalletWiz backend.

All endpoints are prefixed with `/api/v1`.

---

## 1. Authentication Endpoints

### 1.1 Register User
* **URL**: `/auth/register`
* **Method**: `POST`
* **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "strongpassword123",
    "first_name": "Ayushi"
  }
  ```
* **Success Response (Code 201)**:
  ```json
  {
    "message": "User registered successfully",
    "user_id": "d3b07384-d113-4956-bfdc-e00e00817c1f"
  }
  ```

### 1.2 Login User
* **URL**: `/auth/login`
* **Method**: `POST`
* **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "strongpassword123"
  }
  ```
* **Success Response (Code 200)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```

### 1.3 Google OAuth Login
* **URL**: `/auth/google`
* **Method**: `POST`
* **Request Body**:
  ```json
  {
    "id_token": "eyJhbGciOiJSUzI1Ni..."
  }
  ```
* **Success Response (Code 200)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "is_new_user": false
  }
  ```

---

## 2. Transaction Endpoints (Standard CRUD)
*All requests require header `Authorization: Bearer <token>`*

### 2.1 Create Transaction (Manual / Confirmed LLM Entry)
* **URL**: `/transactions`
* **Method**: `POST`
* **Request Body**:
  ```json
  {
    "amount": 450.00,
    "category": "Food & Dining",
    "payment_method": "UPI",
    "merchant": "Pizza Hut",
    "transaction_date": "2026-07-07T20:00:00Z",
    "description": "Dinner with friends",
    "source_type": "llm" 
  }
  ```
* **Success Response (Code 201)**:
  ```json
  {
    "id": "e5b07384-d113-4956-bfdc-e00e00817c2f",
    "amount": 450.00,
    "category": "Food & Dining",
    "payment_method": "UPI",
    "merchant": "Pizza Hut",
    "transaction_date": "2026-07-07T20:00:00Z",
    "description": "Dinner with friends",
    "source_type": "llm",
    "created_at": "2026-07-08T11:19:00Z"
  }
  ```

### 2.2 List Transactions (with Filtering & Pagination)
* **URL**: `/transactions`
* **Method**: `GET`
* **Query Parameters**:
  * `page` (optional, default: 1)
  * `limit` (optional, default: 20)
  * `start_date` (optional, format: `YYYY-MM-DD`)
  * `end_date` (optional, format: `YYYY-MM-DD`)
  * `category` (optional, choose from: `Food & Dining`, `Shopping`, `Travel & Transport`, `Bills & Utilities`, `Entertainment`, `Health & Medical`, `Others`)
  * `payment_method` (optional, choose from: `Cash`, `Card`, `UPI`)
* **Success Response (Code 200)**:
  ```json
  {
    "data": [
      {
        "id": "e5b07384-d113-4956-bfdc-e00e00817c2f",
        "amount": 450.00,
        "category": "Food & Dining",
        "payment_method": "UPI",
        "merchant": "Pizza Hut",
        "transaction_date": "2026-07-07T20:00:00Z",
        "description": "Dinner with friends",
        "source_type": "llm"
      }
    ],
    "pagination": {
      "total_items": 120,
      "page": 1,
      "limit": 20,
      "total_pages": 6
    }
  }
  ```

### 2.3 Update Transaction
* **URL**: `/transactions/{id}`
* **Method**: `PUT`
* **Request Body** (Any fields to update):
  ```json
  {
    "category": "Food & Dining",
    "amount": 480.00,
    "payment_method": "Card"
  }
  ```
* **Success Response (Code 200)**:
  ```json
  {
    "id": "e5b07384-d113-4956-bfdc-e00e00817c2f",
    "amount": 480.00,
    "category": "Food & Dining",
    "payment_method": "Card",
    "merchant": "Pizza Hut",
    "transaction_date": "2026-07-07T20:00:00Z",
    "description": "Dinner with friends",
    "source_type": "llm"
  }
  ```

### 2.4 Delete Transaction
* **URL**: `/transactions/{id}`
* **Method**: `DELETE`
* **Success Response (Code 204)**: No Content.

---

## 3. Agentic Conversational Endpoints
*All requests require header `Authorization: Bearer <token>`*

### 3.1 Conversational Chat Session
* **URL**: `/chat`
* **Method**: `POST`
* **Request Body**:
  ```json
  {
    "message": "And how much of that was at Starbucks?",
    "history": [
      {
        "role": "user",
        "content": "How much did I spend in total last week?"
      },
      {
        "role": "assistant",
        "content": "Last week you spent a total of 1850.00."
      }
    ]
  }
  ```
* **Success Response (Code 200)**:
  *Returns the agent's conversational response along with metadata about any tools triggered.*
  
  **Case A: Tool `query_database` Triggered**
  ```json
  {
    "response": "Out of that 1850.00, you spent 1200.00 at Starbucks last week.",
    "tool_triggered": "query_database",
    "metadata": {
      "query_filters": {
        "category": "Food & Dining",
        "merchant": "Starbucks",
        "start_date": "2026-06-29T00:00:00Z",
        "end_date": "2026-07-05T23:59:59Z"
      },
      "results_count": 2
    }
  }
  ```

  **Case B: Tool `log_transaction` Triggered**
  ```json
  {
    "response": "Got it! I've logged an expense of 300.00 for Starbucks today.",
    "tool_triggered": "log_transaction",
    "metadata": {
      "transaction": {
        "id": "e5b07384-d113-4956-bfdc-e00e00817c2f",
        "amount": 300.00,
        "category": "Food & Dining",
        "merchant": "Starbucks",
        "transaction_date": "2026-07-08T12:00:00Z",
        "description": "Starbucks coffee"
      }
    }
  }
  ```

  **Case C: Direct Conversational Response (No Tool Triggered)**
  ```json
  {
    "response": "I can only help you track and query your expenses. Try saying something like 'I spent 200 on Uber today'.",
    "tool_triggered": null,
    "metadata": {}
  }
  ```

---

## 4. Analytics & Dashboard Endpoints
*All requests require header `Authorization: Bearer <token>`*

### 4.1 Dashboard Overview
* **URL**: `/analytics/dashboard`
* **Method**: `GET`
* **Query Parameters**:
  * `timeframe` (optional, e.g., `this-month`, `last-30-days`, `this-year`)
* **Success Response (Code 200)**:
  ```json
  {
    "total_spent": 12450.00,
    "daily_average": 415.00,
    "by_category": [
      { "category": "Bills & Utilities", "amount": 5000.00, "percentage": 40.2 },
      { "category": "Food & Dining", "amount": 4200.00, "percentage": 33.7 },
      { "category": "Shopping", "amount": 1750.00, "percentage": 14.1 },
      { "category": "Travel & Transport", "amount": 1500.00, "percentage": 12.0 }
    ],
    "by_payment_method": [
      { "payment_method": "UPI", "amount": 7500.00, "percentage": 60.2 },
      { "payment_method": "Card", "amount": 4000.00, "percentage": 32.1 },
      { "payment_method": "Cash", "amount": 950.00, "percentage": 7.7 }
    ],
    "daily_trend": [
      { "date": "2026-07-01", "amount": 150.00 },
      { "date": "2026-07-02", "amount": 600.00 },
      { "date": "2026-07-03", "amount": 0.00 },
      { "date": "2026-07-04", "amount": 1200.00 }
    ],
    "recent_transactions": [
      {
        "id": "e5b07384-d113-4956-bfdc-e00e00817c2f",
        "amount": 250.00,
        "category": "Travel & Transport",
        "payment_method": "UPI",
        "merchant": "Uber",
        "transaction_date": "2026-07-08T09:30:00Z",
        "description": "Uber ride to office"
      },
      {
        "id": "f6c07384-d113-4956-bfdc-e00e00817c3f",
        "amount": 120.00,
        "category": "Food & Dining",
        "payment_method": "Cash",
        "merchant": "Starbucks",
        "transaction_date": "2026-07-07T15:00:00Z",
        "description": "Latte"
      }
    ]
  }
  ```
