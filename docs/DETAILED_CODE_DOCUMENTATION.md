# Project Niyati — Detailed Code Documentation

This document describes the purpose and behavior of each major file and component in the repository. It focuses on intent, key functions/classes, inputs, outputs, side effects, and important implementation notes.

**Notes:**
- File links are workspace-relative. Use them to inspect implementation details.

**Backend — Core**
- **`backend/app.py`**: [backend/app.py](backend/app.py)
  - Flask-based simple API server (dev-oriented).
  - Key endpoints:
    - `GET /api/health` — returns basic health JSON.
    - `POST /api/generate` — placeholder inference endpoint; requires token (decorated with `@token_required`) and attempts to call orchestration when available.
    - `GET /api/admin/data` — admin-only endpoint using `@admin_required` decorator; returns sensitive admin data.
  - Integrates with SQLAlchemy via `database.db` and registers `auth` blueprint.
  - Loads environment and configures `SECRET_KEY` from `auth.get_secret_key()`.

- **`backend/app_fastapi.py`**: [backend/app_fastapi.py](backend/app_fastapi.py)
  - Production-ready FastAPI app implementing full API surface.
  - Authentication via JWT tokens (`HTTPBearer` dependency). Key helpers:
    - `get_current_user()` decodes JWT, fetches `User` from DB, attaches `token_role` and `token_gstin`.
    - `require_admin()` ensures user role is `Admin`.
  - SSE log stream: `/logs/stream` returns `text/event-stream` using an asyncio.Queue for broadcasting progress messages from agents.
  - Endpoints:
    - `/auth/register` and `/auth/login` — user registration/login using Flask-Bcrypt for password hashing and JWT issuance.  Business owners must include a `gstin` that already exists in the `entity_master` table; otherwise the signup call returns a 400 error.
    - `/sync` — accepts six CSV uploads, parses them into pandas DataFrames, and calls `execute_workflow` (orchestration). Handles validation and parsing errors.
    - `/pre-audit` — per-GSTIN pre-audit; performs RBAC check then reads `RiskPrediction`, `FraudPattern`, `AuditNarrative` from DB and returns assembled detail. Sends placeholder email log for HIGH_RISK.
    - `/dashboard` — returns RBAC‑filtered dashboard summary, health score, top drivers and pattern counts.  The Flask version (when running `app.py`) now also exposes this endpoint so the React UI works without switching to the FastAPI server.
    - `/graph` — queries Neo4j for nodes/edges with RBAC filtering using environment Neo4j credentials.
    - `/risk/{gstin}` — returns detailed risk and shape-plot data for visualization (EBM shape plots stored in DB).
  - Error handlers for HTTPException and Exception produce consistent JSON responses and server-side logging.

- **`backend/auth.py`**: [backend/auth.py](backend/auth.py)
  - Provides `auth_bp` Flask blueprint with endpoints `/signup` (alias `/register`) and `/login`.
  - Decorators:
    - `token_required` — extracts JWT from `Authorization: Bearer <token>`, decodes using `get_secret_key()`, fetches `User` and injects as first arg to wrapped handlers.
    - `admin_required` — ensures `current_user.role == 'Admin'`.
    - `business_owner_or_admin_required` — allows `Admin` or `Business_Owner` roles.
  - Uses `flask_bcrypt` to hash and verify passwords.

- **`backend/database.py`**: [backend/database.py](backend/database.py)
  - Exposes `db = SQLAlchemy()` that other modules import and initialize with a Flask app instance.

- **`backend/models.py`**: [backend/models.py](backend/models.py)
  - SQLAlchemy models used by the app:
    - `User` — email, password_hash, role, gstin, created_at.
    - `RawInvoice`, `RawEwayBill`, `EntityMaster` — raw ingestion tables.
    - `EngineeredFeatures` — computed features per GSTIN.
    - `RiskPrediction` — ML predictions, top drivers and model metadata.
    - `FraudPattern` — detected structural patterns (stored as JSON arrays for gstin_list).
    - `AuditNarrative` — LLM/template narrative per GSTIN.
    - `ShapePlot` — EBM shape plot arrays and metadata for visualization.
  - Numeric precision and default timestamps are defined; JSON columns used for SQLite compatibility.

- **`backend/rbac.py`**: [backend/rbac.py](backend/rbac.py)
  - Role-based access control helpers to apply tenant filtering:
    - `apply_neo4j_tenant_filter` — wraps/edits Cypher queries to inject `$SESSION_GSTIN` filter for `Business_Owner` role.
    - `apply_postgres_tenant_filter` — SQLAlchemy filter_by wrapper.
    - `check_access_permission` — verifies `Business_Owner` only accesses their own GSTIN.
    - `rbac_error_handler` — converts `PermissionError` to JSON response (403).

- **`backend/init_db.py`**: [backend/init_db.py](backend/init_db.py)
  - CLI script to create tables via `db.create_all()`; prints created tables list. Uses environment `DATABASE_URL` fallback to SQLite.

**Backend — Orchestration (multi-agent)**
- Directory: `backend/orchestration/`

- **`state.py`**: [backend/orchestration/state.py](backend/orchestration/state.py)
  - Defines `NiyatiState` TypedDict schema used by LangGraph workflow and helper `create_initial_state(csv_files)`.
  - Key fields: `csv_files`, `validated_data`, `engineered_features`, `change_summary`, `graph_built`, `structural_patterns`, `risk_predictions`, `shape_plots`, `narratives`, `errors`.

- **`agent_ingestion_wrangler.py`**: [backend/orchestration/agent_ingestion_wrangler.py](backend/orchestration/agent_ingestion_wrangler.py)
  - Agent 1: validates CSVs, detects changes vs Postgres (incremental ingestion), hashes PII, and computes engineered features.
  - Uses utilities: `validate_all_csvs`, `detect_all_changes`, `compute_engineered_features`, `hash_pii`.
  - Produces `validated_data`, `engineered_features`, and `change_summary` in the state and broadcasts SSE messages.
  - Provides `ingestion_wrangler_node_sync` wrapper to run async code synchronously.

- **`agent_graph_architect.py`**: [backend/orchestration/agent_graph_architect.py](backend/orchestration/agent_graph_architect.py)
  - Agent 2: builds Neo4j knowledge graph from validated CSVs.
  - Responsibilities:
    - Create uniqueness constraints (Taxpayer.gstin, Invoice.irn, EwayBill.doc_no).
    - Create Taxpayer, Invoice, EwayBill nodes using batching utilities (`create_nodes_batch`).
    - Create relationships: `ISSUED`, `TO`, `BACKED_BY`, `SHARED_CONTACT` using `create_relationships_batch`.
    - Uses `hash_pii` to store shared contact hashes and supports incremental MERGE semantics.
  - Updates `graph_built=True` in state and broadcasts progress.

- **`agent_risk_detective.py`**: [backend/orchestration/agent_risk_detective.py](backend/orchestration/agent_risk_detective.py)
  - Agent 3: structural graph analysis on Neo4j to detect:
    - Circular trade loops (A→B→C→A): identifies loop members, sums invoice values, computes risk score.
    - Ghost invoices: high-value invoices without BACKED_BY relationships.
    - Spider web clusters: connected components of SHARED_CONTACT relationships.
  - Computes simple normalized risk scores per pattern and returns `structural_patterns` in state.

- **`agent_predictive_analyst.py`**: [backend/orchestration/agent_predictive_analyst.py](backend/orchestration/agent_predictive_analyst.py)
  - Agent 4: ML scoring with Explainable Boosting Machine (EBM).
  - Key behaviors:
    - Loads model from `backend/model/daksha_ebm.pkl` using joblib (cached in `_model_cache`).
    - Runs `predict_proba()` on features DataFrame to get risk probabilities.
    - Classifies risk into `HIGH_RISK` (p >= 0.7), `MEDIUM_RISK` (0.4 <= p < 0.7), `LOW_RISK` (p < 0.4).
    - Extracts top drivers via `ebm_model.explain_local()` and shape plot data via `explain_global()`.
    - Stores `risk_predictions` and `shape_plots` in state.

- **`agent_niyati_explainer.py`**: [backend/orchestration/agent_niyati_explainer.py](backend/orchestration/agent_niyati_explainer.py)
  - Agent 5: Generates human-readable audit narratives using an LLM with circuit-breaker protection.
  - LLM configuration:
    - Uses `LLM_PROVIDER` env var (supported `groq` or `openai`) and `LLM_API_KEY`.
    - Falls back to template-based narrative via `utils.circuit_breaker.generate_template_narrative` on failure.
  - Steps per entity: format structured prompt, call LLM via `call_llm_with_circuit_breaker`, validate >=50 chars, ensure `HIGH RISK —` prefix for high-risk narratives.

- **`llm_agent.py`**: [backend/orchestration/llm_agent.py](backend/orchestration/llm_agent.py)
  - Orchestrates the multi-agent workflow using LangGraph's `StateGraph`.
  - Creates nodes for agents and a `concurrent_analysis_node` that runs Agent 3 and Agent 4 in parallel (via `asyncio.gather` / `asyncio.to_thread`).
  - Exposes `execute_workflow(csv_files)` async function and `execute_workflow_sync` wrapper.
  - Uses an `event_queue` (asyncio.Queue) to broadcast SSE messages to clients.

**Backend — Utilities**
- Directory: `backend/utils/`

- **`change_detection.py`**: [backend/utils/change_detection.py](backend/utils/change_detection.py)
  - Computes content hashes per record to detect new/updated/unchanged records.
  - `detect_changes()` returns three DataFrames (new, updated, unchanged) by primary key and content columns.
  - `detect_all_changes()` orchestrates detection for all six CSV types.

- **`csv_validation.py`**: [backend/utils/csv_validation.py](backend/utils/csv_validation.py)
  - Validates presence of required columns and missing values for each CSV type.
  - `validate_all_csvs(csv_files)` returns per-file validation status and row counts or error details.

- **`feature_engineering_wrapper.py`**: [backend/utils/feature_engineering_wrapper.py](backend/utils/feature_engineering_wrapper.py)
  - Adapts feature engineering logic for DataFrames in-memory.
  - Computes features like `payment_gap`, `ghost_invoice_pct`, `shared_contact_flag`, filing delays, `self_invoice_flag`, `excess_itc_flag`, etc.
  - Normalizes column names and merges intermediate stats into a features DataFrame keyed by `Gstin`.

- **`db_connection.py`**: [backend/utils/db_connection.py](backend/utils/db_connection.py)
  - Lightweight connection managers:
    - `PostgreSQLConnection` — context-manager wrapper around psycopg2 with RealDictCursor.
    - `Neo4jConnection` — wraps official Neo4j driver and provides `execute_query`/`execute_write` helpers.
  - `get_postgres_connection()` and `get_neo4j_connection()` helpers return the connection manager classes.

- **`neo4j_batching.py`**: [backend/utils/neo4j_batching.py](backend/utils/neo4j_batching.py)
  - Implements UNWIND-based batching helpers `create_nodes_batch`, `create_relationships_batch` with exponential backoff retry `_execute_with_retry`.
  - `create_constraints` issues `CREATE CONSTRAINT IF NOT EXISTS` Cypher statements.

- **`pii_hashing.py`**: [backend/utils/pii_hashing.py](backend/utils/pii_hashing.py)
  - `hash_pii(value)` — SHA-256 deterministic hash for phone/email used for SHARED_CONTACT detection.
  - `mask_pii_display(value, pii_type)` — masks PII for UI display (not used for storage).

- **`circuit_breaker.py`**: [backend/utils/circuit_breaker.py](backend/utils/circuit_breaker.py)
  - Implements a simple Circuit Breaker with `CLOSED`, `OPEN`, `HALF_OPEN` states.
  - `CircuitBreaker.call(func, ...)` wraps LLM calls; after `failure_threshold` consecutive failures opens the circuit and raises until `recovery_timeout` passes.
  - Provides `generate_template_narrative` fallback used by the explainer.

**Backend — Model & Training**
- **`backend/model/ebm_training.py`** and **`backend/model/feature_engineering.py`**: scripts used to train and prepare the EBM model. The trained model artifact is `backend/model/daksha_ebm.pkl`.

**Frontend — Next.js (app directory)**
- Directory: `frontend/src/app/` and `frontend/src/components/`

- **`frontend/src/app/page.tsx`**: [frontend/src/app/page.tsx](frontend/src/app/page.tsx)
  - Marketing / landing page for the UI explaining the five agents and features.
  - Uses `Button` component and navigates to `/login` and `/signup`.

- **Key UI Components** (all under `frontend/src/components/`):
  - `Button.tsx` — styled button with `isLoading` state and simple hover color manipulation.
  - `AgentLogViewer.tsx` — connects to SSE endpoint (`/logs/stream`) and renders live agent logs; auto-scrolls and color-codes by agent; controls to clear/expand.
  - `VendorRiskTable.tsx` — table of vendor risk entries; clicking a row fetches `/risk/{gstin}` and shows a modal with narrative.
  - `Input.tsx`, `HealthGauge.tsx`, `RiskBadge.tsx`, `ShapePlots.tsx` — smaller UI primitives to display health, risk badges, and shape plot visualizations (open those files for details).

- **Auth Context**: `frontend/src/context/AuthContext.tsx` — provides React context for authentication state, token storage (localStorage), and helper to fetch API with token.

- **Proxy**: `frontend/src/proxy.ts` — local helper to set API base URL using `NEXT_PUBLIC_API_URL`.

**Tests**
- Backend contains multiple unit and integration tests under `backend/tests/` and `backend/tests/unit` and `backend/tests/integration`.
  - Tests exercise ingestion, orchestration, RBAC, and agents. See files like `test_ingestion_wrangler.py`, `test_graph_architect.py`, `test_niyati_explainer.py` for examples.
  - CI/local test notes: `backend/requirements.txt` lists required packages; running tests requires configured environment (Neo4j, Postgres or SQLite fallback) and may mock external services.

**Environment & Running**
- `.env` variables (see `backend/.env.example`):
  - `DATABASE_URL` (Postgres or sqlite:///niyati.db fallback)
  - `JWT_SECRET_KEY` or `NEXT_PUBLIC_API_URL` for frontend
  - `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` for Neo4j
  - `LLM_PROVIDER`, `LLM_API_KEY`, `CIRCUIT_BREAKER_THRESHOLD` for LLM & circuit breaker

- Quick start (development):
  - Backend (FastAPI):
    ```powershell
    cd backend
    python -m venv .venv
    .\.venv\Scripts\activate
    pip install -r requirements.txt
    python init_db.py
    uvicorn app_fastapi:app --reload --port 8000
    ```

  - Frontend (Next.js):
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

**Appendix — Implementation Notes & Caveats**
- The repository mixes Flask (`app.py`, `auth.py`) and FastAPI (`app_fastapi.py`) servers. `app_fastapi.py` is the more complete production-like API; `app.py` is a simpler Flask dev-server and provides compatibility for some examples.
- Many agent functions are written as async and expose synchronous wrappers (LangGraph appears to require sync node functions). The orchestration wraps async work with `asyncio.run` and `asyncio.to_thread` for concurrency.
- Neo4j and Postgres operations include basic retry/backoff patterns but lack transactional rollback that would be required in production for perfect consistency.
- LLM integration requires platform-specific LangChain providers; code performs graceful fallback to template narratives via `CircuitBreaker`.

If you'd like, I can:
- Produce a per-file expanded breakdown with function-by-function explanations and example inputs/outputs for a subset of files you care most about.
- Generate a living `docs/` site or split the documentation into separate per-module markdown files.

---
Generated on: 2026-02-27
