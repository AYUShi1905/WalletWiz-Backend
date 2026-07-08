# WalletWiz Backend - Frontend Integration Guide

Welcome! This guide outlines the API endpoints, schemas, authentication flows, and data structures of the WalletWiz backend. It is designed to help a frontend developer (or frontend agent) integrate a client application with the API.

---

## 🛠️ Tech Stack & Server Configuration
* **Language/Framework**: Python 3.10 / FastAPI
* **Database**: MongoDB Atlas with Beanie ODM
* **LLM Engine**: Google Gemini 2.5 Flash via LangChain
* **Local Run Command**: `python main.py` (run from the `app` directory)
* **Default URL**: `http://localhost:8000`
* **Base API Prefix**: `/api/v1`

---

## 🔑 Authentication Flow

WalletWiz uses **JWT Bearer Token** authentication. 

1. **Obtaining a Token**: The frontend must send credentials to either `/api/v1/auth/login` (email/password) or `/api/v1/auth/google` (Google OAuth ID Token).
2. **Using the Token**: On success, the API returns an `access_token`. The frontend must store this token and attach it to the `Authorization` header of all subsequent requests:
   ```http
   Authorization: Bearer <your_jwt_access_token>
   ```
3. **Token Expiry**: The JWT token is valid for **7 days** (10,080 minutes) to prevent frequent logouts.

---

## 📊 Predefined Enums

To prevent validation errors, the frontend must strictly adhere to the following string enumerations when sending payloads.

### 1. Transaction Category (`TransactionCategory`)
* `"Food & Dining"`
* `"Shopping"`
* `"Travel & Transport"`
* `"Bills & Utilities"`
* `"Entertainment"`
* `"Health & Medical"`
* `"Others"`

### 2. Payment Method (`PaymentMethod`)
* `"Cash"`
* `"Card"`
* `"UPI"`

---

## 📌 Endpoint Reference

### 1. Authentication Endpoints

#### 1.1 User Registration
* **URL**: `/api/v1/auth/register`
* **Method**: `POST`
* **Auth Required**: No
* **Request Body (JSON)**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123",
    "first_name": "John"
  }
  ```
* **Response (JSON - 210 Created)**:
  ```json
  {
    "message": "User registered successfully",
    "user_id": "65e8f498c4f92b77a06c8b01"
  }
  ```
* **Common Errors**:
  * `400 Bad Request`: Email already in use (`"User with this email already registered"`).

#### 1.2 User Login
* **URL**: `/api/v1/auth/login`
* **Method**: `POST`
* **Auth Required**: No
* **Request Body (JSON)**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123"
  }
  ```
* **Response (JSON - 200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```
* **Common Errors**:
  * `401 Unauthorized`: Invalid credentials (`"Incorrect email or password"`).

#### 1.3 Google OAuth Sign-In
* **URL**: `/api/v1/auth/google`
* **Method**: `POST`
* **Auth Required**: No
* **Request Body (JSON)**:
  ```json
  {
    "id_token": "ya29.a0AfH6SMCm..."
  }
  ```
* **Response (JSON - 200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "is_new_user": false
  }
  ```
* **Common Errors**:
  * `400 Bad Request`: Invalid token signature/expiry (`"Invalid Google OAuth token"`).

---

### 2. Transactions CRUD Endpoints

All endpoints require a valid `Authorization: Bearer <token>` header.

#### 2.1 Create Transaction
* **URL**: `/api/v1/transactions`
* **Method**: `POST`
* **Request Body (JSON)**:
  ```json
  {
    "amount": 250.50,
    "category": "Food & Dining",
    "payment_method": "UPI",
    "merchant": "Starbucks",
    "description": "Iced Latte",
    "transaction_date": "2026-07-08T12:00:00Z"
  }
  ```
  *(Note: `transaction_date` is optional; if omitted, the backend defaults to the current UTC timestamp).*
* **Response (JSON - 201 Created)**:
  ```json
  {
    "id": "65e8f498c4f92b77a06c8b05",
    "amount": 250.5,
    "category": "Food & Dining",
    "payment_method": "UPI",
    "merchant": "Starbucks",
    "description": "Iced Latte",
    "transaction_date": "2026-07-08T12:00:00Z",
    "source_type": "manual",
    "created_at": "2026-07-08T12:00:05.123000Z"
  }
  ```

#### 2.2 List Transactions (Paginated & Filterable)
* **URL**: `/api/v1/transactions`
* **Method**: `GET`
* **Query Parameters** (All optional):
  * `page` (integer, default: `1`): Page number.
  * `limit` (integer, default: `20`, max: `100`): Results per page.
  * `start_date` (string, `YYYY-MM-DD`): Filter starting date.
  * `end_date` (string, `YYYY-MM-DD`): Filter ending date.
  * `category` (string): Filter by category.
  * `payment_method` (string): Filter by payment method.
* **Response (JSON - 200 OK)**:
  ```json
  {
    "data": [
      {
        "id": "65e8f498c4f92b77a06c8b05",
        "amount": 250.5,
        "category": "Food & Dining",
        "payment_method": "UPI",
        "merchant": "Starbucks",
        "description": "Iced Latte",
        "transaction_date": "2026-07-08T12:00:00Z",
        "source_type": "manual",
        "created_at": "2026-07-08T12:00:05Z"
      }
    ],
    "pagination": {
      "total_items": 43,
      "page": 1,
      "limit": 20,
      "total_pages": 3
    }
  }
  ```

#### 2.3 Update Transaction
* **URL**: `/api/v1/transactions/{id}`
* **Method**: `PUT`
* **Path Parameters**:
  * `id` (string, required): The transaction document ID.
* **Request Body (JSON - All fields optional)**:
  ```json
  {
    "amount": 280.00,
    "merchant": "Starbucks Coffee"
  }
  ```
* **Response (JSON - 200 OK)**:
  ```json
  {
    "id": "65e8f498c4f92b77a06c8b05",
    "amount": 280.0,
    "category": "Food & Dining",
    "payment_method": "UPI",
    "merchant": "Starbucks Coffee",
    "description": "Iced Latte",
    "transaction_date": "2026-07-08T12:00:00Z",
    "source_type": "manual",
    "created_at": "2026-07-08T12:00:05Z"
  }
  ```
* **Common Errors**:
  * `404 Not Found`: Transaction doesn't exist or doesn't belong to the logged-in user.

#### 2.4 Delete Transaction
* **URL**: `/api/v1/transactions/{id}`
* **Method**: `DELETE`
* **Path Parameters**:
  * `id` (string, required): The transaction document ID.
* **Response (JSON - 200 OK)**:
  ```json
  {
    "message": "Transaction deleted successfully"
  }
  ```
* **Common Errors**:
  * `404 Not Found`: Transaction doesn't exist or doesn't belong to the logged-in user.

---

### 3. Analytics Dashboard Endpoint

#### 3.1 Fetch Dashboard Summary
* **URL**: `/api/v1/analytics/dashboard`
* **Method**: `GET`
* **Query Parameters**:
  * `timeframe` (string, optional): One of `"this-month"` (default), `"last-30-days"`, or `"this-year"`.
* **Response (JSON - 200 OK)**:
  ```json
  {
    "total_spent": 9658.0,
    "daily_average": 1379.71,
    "by_category": [
      {
        "category": "Shopping",
        "total_amount": 4500.0,
        "percentage": 46.59
      },
      {
        "category": "Bills & Utilities",
        "total_amount": 3200.0,
        "percentage": 33.13
      }
    ],
    "by_payment_method": [
      {
        "payment_method": "UPI",
        "total_amount": 4200.0,
        "percentage": 43.49
      }
    ],
    "daily_trend": [
      {
        "date": "2026-07-01",
        "amount": 250.0
      },
      {
        "date": "2026-07-02",
        "amount": 850.0
      }
    ],
    "recent_transactions": [
      {
        "id": "65e8f498c4f92b77a06c8b05",
        "amount": 250.5,
        "category": "Food & Dining",
        "payment_method": "UPI",
        "merchant": "Starbucks",
        "description": "Iced Latte",
        "transaction_date": "2026-07-08T12:00:00Z",
        "source_type": "manual",
        "created_at": "2026-07-08T12:00:05Z"
      }
    ]
  }
  ```

---

### 4. Conversational Chat Endpoint

The chat endpoint integrates the Gemini LLM to execute actions directly on MongoDB via natural language.

#### 4.1 Process Chat Query
* **URL**: `/api/v1/chat`
* **Method**: `POST`
* **Request Body (JSON)**:
  ```json
  {
    "message": "how much did I spend in total on coffee?",
    "history": [
      {
        "role": "user",
        "content": "Hi WalletWiz!"
      },
      {
        "role": "assistant",
        "content": "Hello! How can I help you manage your expenses today?"
      }
    ]
  }
  ```
  *(Note: `history` is an optional array of previous conversation messages. The frontend should maintain this state and pass it to keep chat memory active).*
* **Response (JSON - 200 OK)**:
  ```json
  {
    "response": "You have spent a total of 250.50 on coffee. This includes 1 transaction at Starbucks.",
    "tool_triggered": "query_database",
    "metadata": {
      "query_filters": {
        "merchant": "coffee"
      },
      "results_count": 1
    }
  }
  ```
  *When logging a new transaction via chat (e.g., `"spent 350 on UPI at Starbucks for coffee today"`), the response format remains the same:*
  ```json
  {
    "response": "Alright, I've logged a transaction of 350.00 for Food & Dining at Starbucks via UPI today.",
    "tool_triggered": "log_transaction",
    "metadata": {
      "query_filters": {
        "amount": 350.0,
        "category": "Food & Dining",
        "payment_method": "UPI",
        "merchant": "Starbucks",
        "transaction_date": "2026-07-08T15:08:00.000Z",
        "description": "coffee"
      },
      "results_count": 1
    }
  }
  ```

#### ⚠️ Rate Limiting on Chat
The `/chat` endpoint implements global rate limiting of **20 Requests Per Minute (RPM)** per client IP address.
* If a client exceeds this limit, the backend returns status code **`429 Too Many Requests`**.
* The response payload is:
  ```json
  {
    "detail": "Rate limit exceeded: 20 per 1 minute"
  }
  ```
* The frontend should gracefully intercept 429 status codes and show a toast warning to the user (e.g. *"Slow down! You are sending too many messages."*).

---

## 🧪 Quick Test Connection Command
For developers using `curl` to test connection (after running the server inside `app/`):

```bash
curl -X GET http://localhost:8000/
```
Output:
```json
{"status":"online","message":"Welcome to WalletWiz API!","version":"1.0.0"}
```
