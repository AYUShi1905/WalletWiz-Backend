# WalletWiz Backend - Pending Tasks & Progress Tracker

This document tracks the development tasks for the WalletWiz backend. Development should follow the layered architecture and modular design guidelines.

## 📋 Road Map & Status

### 1. Environment & Database Configuration
- [x] Set up environment variables template in `app/.example.env` and configuration loader in `app/core/config.py`
- [x] Initialize Beanie ODM and establish connection to MongoDB Atlas in `app/core/database.py`
- [x] Set up structured logging in `app/utils/logger.py` and exception handlers in `app/core/exceptions.py`

### 2. Core Models & Schema Definitions
- [x] Define Beanie DB User document model in `app/models/db_user.py`
- [x] Define Beanie DB Transaction document model in `app/models/db_transaction.py`
- [x] Implement Pydantic request models in `app/models/request.py`
- [x] Implement Pydantic response models in `app/models/response.py`

### 3. Authentication & Security
- [x] Implement security utilities (password hashing, JWT token generation & parsing) in `app/core/security.py`
- [x] Create user authentication service logic in `app/services/auth.py`
- [x] Implement registration, login, and Google OAuth flow routes in `app/api/v1/auth.py`
- [x] Create JWT validation dependency `get_current_user` in `app/api/dependencies.py`

### 4. Transactions & Analytics
- [x] Implement transaction CRUD logic in `app/services/transaction.py`
- [x] Create transaction endpoints (GET/POST/PUT/DELETE) in `app/api/v1/transactions.py`
- [x] Implement analytics aggregation pipelines in `app/services/analytics.py`
- [x] Create analytics dashboard endpoints in `app/api/v1/analytics.py`

### 5. Conversational LLM Agent & Tools Integration
- [x] Initialize Gemini 1.5 Flash client & LangChain integration in `app/services/llm_provider.py`
- [x] Define agent tool logic (dynamic user binding for `log_transaction` and `query_database`) in `app/services/query_processor.py`
- [x] Construct LLM system instructions and prompt templates in `app/services/prompt_builder.py`
- [x] Implement conversational Q&A endpoint (`POST /chat`) in `app/api/v1/query.py`
- [x] Implement rate limiting (20 RPM) for LLM-related endpoints in API layer

### 6. Testing & Utility Scripts
- [ ] Implement mock data generator in `app/scripts/seed_mock_data.py`
- [ ] Implement datetime parsing helper in `app/utils/datetime_helpers.py` for handling relative inputs like "yesterday"
- [ ] Write unit & integration tests under `app/tests/`
