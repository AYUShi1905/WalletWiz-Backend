# WalletWiz - Project Instructions & Mandates

These instructions guide all code generation, architecture decisions, and task execution for the WalletWiz backend. Adhere to these principles strictly.

---

## 1. Environment Management
* **Mandate**: Whenever a new environment variable is added to `app/core/config.py`, it **MUST** also be added to `app/.example.env` with a placeholder or sensible default.
* **Pre-Modification Check**: Before making any configuration modifications, you **MUST** read `app/core/config.py` and `app/.example.env` to understand the required variables and configuration state.
* **Security Mandate**: Never read, modify, create, or commit the local `.env` file containing real API keys or database credentials. The developer will manage all local `.env` configurations manually. Only the template configuration files (such as `.example.env` and `app/core/config.py`) may be read or modified.

## 2. Documentation Updates
* **Architectural Sync**: Any significant architectural changes, endpoint modifications, database schema shifts, or model updates must be immediately reflected in the relevant documentation files under `00_docs/`.
* **Progress Tracking**: You **MUST** update `00_docs/PENDING_TASKS.md` (or equivalent progress tracker) whenever a task is completed (mark as `[x]`) or a new task is identified. This file serves as the absolute "Source of Truth" for development progress.

## 3. Modular Development
* **Coding Standards**: Adhere strictly to the coding standards and layered architecture documented in `00_docs/architecture.md`. 
* **Separation of Concerns (SRP)**: Keep API Routers (Controllers) strictly isolated from business logic. Always use the Service Layer pattern (e.g., executing DB writes and LLM integrations inside `app/services/` rather than directly inside routes).

## 4. Task Execution & Autonomy
* **Wait for Instruction**: Never jump to the next task or implement new features/endpoints immediately after finishing one.
* **Explicit Approval**: You **MUST** wait for the user to explicitly say "proceed," "next task," or provide a specific directive before moving on to any new work.
