# Product Requirements Document (PRD) - WalletWiz (Backend)

## 1. Project Overview
The **WalletWiz** is a backend service designed for individuals and groups of friends to track, analyze, and manage expenses. The core differentiator is its use of the **Gemini LLM** to simplify expense entry (natural language parsing) and enable conversational Q&A/insights on top of expense data.

## 2. Target Audience & Scope
* **Target Audience**: The developer and a small group of friends.
* **Scope**: Backend APIs only. Out of scope for this phase is the frontend client (mobile/web), though the APIs must return structured JSON suitable for rendering graphs/charts and tables on the frontend.

## 3. Core Features

### 3.1. Unified Agentic Conversational Interface
* **Goal**: Provide a single conversational chat interface that maintains context, logs transactions, answers analytical queries, and handles clarifications or feedback.
* **Flow**:
  1. User inputs a message: e.g., `"Spent 450 rupees on dinner with friends at Pizza Hut yesterday."` or *"How much did I spend at Starbucks this month?"*
  2. The client sends this message along with recent chat history (stored client-side) and their JWT token.
  3. The backend runs a **Gemini Agent** equipped with conversation memory and tools bound securely to the user's `user_id`.
  4. The agent executes tool calls as needed:
     * **Tool `log_transaction`**: Parses details (amount, category, merchant, date, description) and saves the transaction to MongoDB Atlas.
     * **Tool `query_database`**: Translates user questions into query filters, pulls data from MongoDB Atlas, and provides it to the agent.
     * **No Tool (Direct Response)**: If the input is unrelated or requires clarification (e.g. asking for a missing amount), the agent responds conversationally asking the user to provide the info.
  5. The backend returns the agent's conversational response along with optional metadata of any actions triggered (e.g. transaction receipt data).

### 3.2. Standard Transaction Management (CRUD)
* Manual creation of transactions (fallback).
* Read/List transactions with pagination, filters (date range, category, min/max amount, payment method).
* Update transaction details (manually correct categories or amounts parsed by LLM).
* Delete transactions.

### 3.3. Analytics & Categorization
* **Predefined Hardcoded Categories**:
  * `Food & Dining`
  * `Shopping`
  * `Travel & Transport`
  * `Bills & Utilities`
  * `Entertainment`
  * `Health & Medical`
  * `Others`
* **Predefined Hardcoded Payment Methods**:
  * `Cash`
  * `Card`
  * `UPI`
* Monthly summaries (Total Spent, Spend by Category, Spend by Payment Method, Daily Average).
* API endpoints that return aggregated data formatted for graphs (Bar charts, Pie charts, Line charts).

### 3.4. Multi-User Support
* User registration and authentication (JWT-based).
* Data isolation (Users can only see and query their own transactions).
* *Future expansion*: Shared groups/split-wise style feature.

## 4. Technology Stack
* **Backend Framework**: Python (FastAPI) (extremely fast, automatic OpenAPI docs, and works seamlessly with Pydantic for Gemini structured JSON parsing).
* **Database**: MongoDB Atlas (Cloud NoSQL Database).
* **AI/LLM**: Google Gemini 1.5 Flash (via Google Gen AI SDK).
* **LLM Orchestration & Tracing**: **LangChain** (for routing & prompt management) and **LangSmith** (for production prompt debugging, token tracking, and monitoring).

## 5. Non-Functional Requirements
* **Response Latency**: LLM operations (parsing/Q&A) should ideally resolve under 2 seconds.
* **Security**: All API routes (except Auth) must require JWT validation. Gemini API keys and MongoDB connection strings must be kept secure.
