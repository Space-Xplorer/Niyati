# Project Niyati — Backend Full Expansion (Function-level)

This file provides detailed, function-by-function explanations for backend modules. Use the workspace links to inspect implementations.

---

## backend/app.py
Link: [backend/app.py](backend/app.py)

- Module-level import behavior
  - Attempts `from orchestration.llm_agent import execute_workflow_sync` at import time.
  - If orchestration missing, `ORCHESTRATION_AVAILABLE=False` and `execute_workflow_sync=None`. This allows the Flask app to start in environments without the orchestration package.

- Flask app configuration
  - `load_dotenv()` pulls environment variables from `.env`.
  - `SQLALCHEMY_DATABASE_URI` is read from `DATABASE_URL` with fallback to `sqlite:///niyati.db`.
  - `SECRET_KEY` obtained via `get_secret_key()` from `auth` module.
  - `db.init_app(app)` registers SQLAlchemy.
  - `db.create_all()` inside `app.app_context()` creates tables on startup.

- Endpoints
  - `health_check()` — simple JSON return; no parameters.
  - `generate(current_user)` — protected by `@token_required`:
    - Reads JSON body using `request.get_json()`.
    - Expects `'prompt'` key; validates presence.
    - Returns 503 when orchestration unavailable.
    - Currently returns placeholder AI response; intended to integrate with orchestration later.
    - Catches generic Exception and returns 500 with error string.
  - `admin_data(current_user)` — protected by `@admin_required`; returns user email and a placeholder sensitive data string.

- Execution: `if __name__ == '__main__': app.run(debug=True, port=5000)` — development server only.

---

## backend/app_fastapi.py
Link: [backend/app_fastapi.py](backend/app_fastapi.py)

This file is the main API surface with many responsibilities. Key components:

- App initialization and Flask compatibility
  - `flask_app = Flask(__name__)` used only to initialize SQLAlchemy and Bcrypt; SQLAlchemy is bound to FlaskApp to reuse ORM models.
  - `db.init_app(flask_app)` then `db.create_all()` inside `flask_app.app_context()`.

- JWT-based authentication
  - `security = HTTPBearer()` used for dependency injection.
  - `get_current_user(credentials)` decodes token using `jwt.decode(token, get_secret_key(), algorithms=["HS256"])`.
  - Extracts `user_id` and queries `User` model in Flask app context. If missing or invalid raises HTTP 401.
  - Adds `token_role` and `token_gstin` attributes to returned `user`.
  - `require_admin(current_user=Depends(get_current_user))` checks `current_user.role == 'Admin'` and raises 403 if not.

- SSE log streaming
  - `event_queue: Optional[asyncio.Queue] = None` holds global queue for orchestration messages.
  - `broadcast_event(message)` asynchronously puts message on queue when set.
  - `event_generator()` creates a new asyncio.Queue for each client; sets global `event_queue` and passes to orchestration via `set_event_queue(event_queue)`.
  - `/logs/stream` returns `StreamingResponse(event_generator(), media_type='text/event-stream')`.

- Auth endpoints
  - `register(request: RegisterRequest)` validates role, prevents duplicate users, hashes password via Flask-Bcrypt, persists user, returns 201 on success.
  - `login(request: LoginRequest)` validates password using `bcrypt.check_password_hash`, then creates JWT token with `exp` of 24 hours.

- CSV ingestion endpoint — `/sync`
  - Accepts six `UploadFile` fields (multipart/form-data).
  - For each file, validates extension `.csv` and parses into pandas DataFrame using `pd.read_csv(pd.io.common.BytesIO(content))` where `content = await file.read()`.
  - On parse errors, raises HTTP 400 with details.
  - Calls `result = await execute_workflow(csv_files)` where `execute_workflow` comes from orchestration.
  - If workflow returns status `'failed'` raises HTTP 500 with error list.
  - On success returns summary including `execution_time_seconds` and `summary` dictionary.

- `/pre-audit`
  - Accepts `gstin` in `PreAuditRequest`.
  - Runs RBAC `check_access_permission` to ensure callers can access requested GSTIN.
  - Queries `RiskPrediction`, `FraudPattern`, `AuditNarrative` using Flask app context and database session.
  - Aggregates counts: `circular_trade_count`, `ghost_invoice_count`, `spider_web_involvement` and returns structured JSON including top drivers and narrative text.
  - Logs an informational message if `risk_pred.risk_level` is `HIGH_RISK` (email sending is TODO).

- `/dashboard`
  - RBAC-aware: Admin sees all `RiskPrediction`, Business_Owner sees only their GSTIN.
  - Computes `health_score = 100 - (risk_probability * 100)` for primary prediction.
  - Returns top drivers array, vendor_risks (TODO), and patterns summary computed from `FraudPattern` table.

- `/graph`
  - Connects to Neo4j via `neo4j.GraphDatabase.driver(NEO4J_URI, auth=(user, password))`.
  - Performs role-specific Cypher queries; Admin uses broad queries while Business_Owner parametrizes queries with `$gstin`.
  - Converts result cursors into `nodes` and `edges` lists and returns them.

- `/risk/{gstin}`
  - RBAC check and DB queries for `RiskPrediction` and `ShapePlot` objects.
  - Formats shape plot JSON arrays for frontend and returns risk-level, probability, top drivers, and `shape_plots`.

- Error handlers
  - `http_exception_handler` logs and returns JSON with `message` set to `exc.detail`.
  - `general_exception_handler` logs full exception with `exc_info=True` and returns generic 500 message.

---

## backend/auth.py
Link: [backend/auth.py](backend/auth.py)

- `get_secret_key()` returns `JWT_SECRET_KEY` or default string.
- `token_required(f)` decorator:
  - Checks `Authorization` header for `Bearer` token.
  - Uses `jwt.decode(token, get_secret_key())` to validate.
  - Fetches `User` from DB by `id` inside global DB session (Flask app context must exist).
  - On token errors returns 401 JSON responses with explanatory messages.
  - On success calls wrapped function as `f(current_user, *args, **kwargs)`.
- `admin_required(f)` wraps `token_required` and enforces `current_user.role == 'Admin'`.
- `signup()`/`register()` endpoints:
  - Validate incoming JSON, ensure `email` and `password`, validate `role` among allowed values.
  - Hash password using `bcrypt.generate_password_hash` and store a new `User` model in DB. Rolls back on DB error.
- `login()` endpoint:
  - Validates user credentials using `bcrypt.check_password_hash` and returns JWT token and user object.
- `business_owner_or_admin_required` decorator ensures either `Admin` or `Business_Owner` role.

---

## backend/database.py
Link: [backend/database.py](backend/database.py)

- Single symbol export: `db = SQLAlchemy()`.
- All other modules import `db` and rely on application code to call `db.init_app(app)` to bind to a Flask app instance.

---

## backend/models.py
Link: [backend/models.py](backend/models.py)

Provides SQLAlchemy model classes. Key notes per model:

- `User`:
  - `email`: unique identifier.
  - `password_hash`: store result of bcrypt hashing.
  - `role`: must be 'Admin' or 'Business_Owner'.
  - `gstin`: optional (Business_Owner tenants).
  - `__repr__` returns `<User email>`.

- `RawInvoice` and `RawEwayBill`:
  - Designed to persist raw ingestion CSV rows. Primary keys are `id`; `irn` is unique for invoices.

- `EntityMaster`:
  - Stores taxpayer business metadata keyed by `gstin`.

- `EngineeredFeatures`:
  - Stores computed signals for ML input; columns are numeric or boolean as required by model.

- `RiskPrediction`:
  - Stores per-GSTIN prediction probability and risk-level with the top 3 driver names and contributions.

- `FraudPattern`:
  - `gstin_list` is stored in `db.Column(db.JSON)` for SQLite compatibility (in Postgres could be an ARRAY).
  - Contains `pattern_metadata` JSON for IRN lists and cluster info.

- `AuditNarrative`, `ShapePlot`:
  - Narratives persisted for retrieval; shape plots store arrays as JSON for frontend usage.

---

## backend/rbac.py
Link: [backend/rbac.py](backend/rbac.py)

- `apply_neo4j_tenant_filter(cypher_query, user_role, user_gstin, params=None)`
  - Inspects query string for Taxpayer matches and injects a `WHERE <var>.gstin = $SESSION_GSTIN` clause if role is `Business_Owner`.
  - Returns modified Cypher text and params dict with `SESSION_GSTIN` set.
  - Raises `PermissionError` for unknown roles or missing GSTIN where needed.
  - Caveats: textual replacements may break complex Cypher queries; prefer to build queries with parameters.

- `apply_postgres_tenant_filter(base_query, user_role, user_gstin, table_alias='t')`
  - For `Business_Owner` returns `base_query.filter_by(gstin=user_gstin)`; for Admin returns unmodified query.

- `check_access_permission(user_role, user_gstin, requested_gstin)`
  - For Admin returns True; for Business_Owner raises `PermissionError` when `user_gstin != requested_gstin`.

- `rbac_error_handler(error)` converts `PermissionError` into Flask JSON 403.

---

## backend/init_db.py
Link: [backend/init_db.py](backend/init_db.py)

- `init_database()` binds `db` to a Flask app configured from `DATABASE_URL` then calls `db.create_all()`.
- Prints a table list and uses SQLAlchemy inspector to verify table creation.
- For local development only; `db.drop_all()` is present but commented out.

---

## Orchestration — core functions (quick reference)

For complete per-function details of each agent, consult the following files in the `backend/orchestration/` directory. Each agent provides an asynchronous main function and a synchronous wrapper for LangGraph.

- `agent_ingestion_wrangler.py` (Agent 1)
  - `ingestion_wrangler_node(state)` — validates CSVs via `validate_all_csvs`, performs change detection using `detect_all_changes`, hashes PII fields with `hash_pii`, computes features with `compute_engineered_features`, updates `state`.
  - `_fetch_existing_data()` — connects to Postgres via `get_postgres_connection()` and attempts to fetch all configured tables; if connection fails returns empty DataFrames.
  - `ingestion_wrangler_node_sync(state)` — `asyncio.run(...)` wrapper.

- `agent_graph_architect.py` (Agent 2)
  - `graph_architect_node(state)` — connects to Neo4j (via `get_neo4j_driver()`), creates uniqueness constraints using `create_constraints`, constructs Taxpayer/Invoice/EwayBill nodes via `create_nodes_batch`, and relationships via `create_relationships_batch`. Uses helper `_prepare_*` functions to transform pandas rows into node/relationship dicts.
  - `graph_architect_node_sync(state)` synchronous wrapper.

- `agent_risk_detective.py` (Agent 3)
  - `risk_detective_node(state)` — requires `state['graph_built'] == True`; runs `_detect_circular_trade`, `_detect_ghost_invoices`, `_detect_spider_webs` by executing Cypher queries and building pattern dicts with computed risk scores.
  - `_calculate_cluster_transaction_volume(session, gstins)` helper to aggregate invoice sums for a cluster.
  - `risk_detective_node_sync(state)` synchronous wrapper.

- `agent_predictive_analyst.py` (Agent 4)
  - `load_ebm_model()` loads `backend/model/daksha_ebm.pkl` via `joblib.load` and caches it in `_model_cache` to avoid repeated loads.
  - `classify_risk_level(probability)` uses thresholds `{>=0.7: HIGH_RISK, >=0.4: MEDIUM_RISK, else LOW_RISK}`.
  - `extract_top_drivers(ebm_model, features_df, gstin, top_n=3)` calls `ebm_model.explain_local(X)` and extracts local `scores` and `names` to return top contributing features sorted by absolute contribution.
  - `extract_shape_plot_data(...)` uses `ebm_model.explain_global()` to get global shape function data and prepares `x_values` and `y_values` arrays for the feature shape plots persisted in `state['shape_plots']`.
  - `predictive_analyst_node(state)` orchestrates loading model, computing `predict_proba`, validating bounds, computing per-entity predictions, top drivers, shape plots, and counts of risk levels.
  - `predictive_analyst_node_sync(state)` synchronous wrapper.

- `agent_niyati_explainer.py` (Agent 5)
  - `get_llm_client()` reads `LLM_PROVIDER` and `LLM_API_KEY` and instantiates a LangChain client for Groq or OpenAI. Raises a helpful `ValueError` when not configured.
  - `format_structured_prompt(...)` builds a human-readable, structured prompt including top drivers and structural patterns for the LLM.
  - `call_llm_with_circuit_breaker(llm_client, prompt)` wraps the LLM call using the global `circuit_breaker` instance; the inner function `llm_client.invoke(prompt)` is called and its output extracted.
  - `validate_narrative(narrative)` checks type and length (>=50 chars).
  - `ensure_high_risk_prefix(narrative, risk_level)` enforces `HIGH RISK —` prefix for high risk narratives.
  - `generate_narrative_for_entity(...)` composes prompt, calls LLM with circuit breaker, validates response, and falls back to `generate_template_narrative()` when needed.
  - `niyati_explainer_node(state)` initializes LLM client, aggregates structural patterns by GSTIN, and generates narratives for each entity; updates `state['narratives']`.
  - `niyati_explainer_node_sync(state)` synchronous wrapper.

- `llm_agent.py` (Orchestration entry)
  - `set_event_queue(queue)` propagates queue to all agents so they can broadcast via SSE.
  - `concurrent_analysis_node(state)` runs Agent 3 and Agent 4 concurrently using `asyncio.to_thread` + `asyncio.gather` and merges results into `state`.
  - `should_continue(state)` conditional function: routes to `error_handler` when `state['errors']` is non-empty.
  - `create_workflow()` builds a `StateGraph` (LangGraph) with nodes and conditional edges for error handling and concurrency.
  - `execute_workflow(csv_files)` top-level function: constructs `initial_state = create_initial_state(csv_files)`, compiles workflow and invokes it (via `asyncio.to_thread(workflow.invoke, initial_state)`), measures execution time, broadcasts completion events, and returns either a `summary` dict or `failed` with errors.
  - `execute_workflow_sync(csv_files)` runs the async function via `asyncio.run` for synchronous callers.

---

## Utilities — key functions and notes

### backend/utils/csv_validation.py
Link: [backend/utils/csv_validation.py](backend/utils/csv_validation.py)
- `REQUIRED_FIELDS` dictionary lists required columns for validation.
- `validate_csv_fields(df, csv_type)`:
  - Checks existence of required columns and collects missing fields.
  - Scans each required column for NaNs and returns row indices with missing values.
  - Returns `(True, None)` on success else `(False, error_details)` where `error_details` includes `missing_fields` or `rows_affected`.
- `validate_all_csvs(csv_files)` iterates expected types, ensures presence of each key, and calls `validate_csv_fields`.

### backend/utils/change_detection.py
Link: [backend/utils/change_detection.py](backend/utils/change_detection.py)
- `compute_record_hash(row, key_columns)` builds a pipe-delimited string over `key_columns` and returns SHA-256 hex digest.
- `detect_changes(new_data, existing_data, primary_key, content_columns)` computes `_record_hash` on both DataFrames, and:
  - `new_records` = rows where primary key not present in existing.
  - `updated_records` = rows where primary key present but `_record_hash` differs.
  - `unchanged_records` = rows with same hash.
  - Removes `_record_hash` before returning.
- `detect_all_changes(csv_files, existing_data)` applies detection configuration for the six CSV types and returns a dict mapping csv_type -> {new, updated, unchanged, totals}.

### backend/utils/feature_engineering_wrapper.py
Link: [backend/utils/feature_engineering_wrapper.py](backend/utils/feature_engineering_wrapper.py)
- `compute_engineered_features(csv_files)` normalizes input frames and computes features:
  - Normalization helpers `_normalize_*` adjust column names and add placeholders where necessary.
  - Constructs `features` DataFrame with base `Gstin`, `KycScore`, `is_cancelled`.
  - Computes shared contact flag using `SharedContact` column or `Phone`/`Email` matching.
  - Computes payment gap and payment gap percent using returns_summary; ghost invoice counts by left-joining invoices with eway bills and computing `_merge == 'left_only'`.
  - Filing delay statistics, self-invoice detection, and excess ITC flag are aggregated and merged.
  - Returns a cleaned `features` DataFrame ready for EBM inference.

### backend/utils/db_connection.py
Link: [backend/utils/db_connection.py](backend/utils/db_connection.py)
- `PostgreSQLConnection` class implements a context manager returning itself on `__enter__` after calling `connect()` which uses either `DATABASE_URL` or individual PG env vars.
- Methods: `execute(query, params)`, `fetchall()`, `fetchone()`, `commit()`, `rollback()`, `close()`.
- `Neo4jConnection` wraps `GraphDatabase.driver` and provides `execute_query()` and `execute_write()` helpers plus context manager semantics.
- `get_postgres_connection()` and `get_neo4j_connection()` return the respective connection classes.

### backend/utils/neo4j_batching.py
Link: [backend/utils/neo4j_batching.py](backend/utils/neo4j_batching.py)
- `create_nodes_batch(session, node_label, nodes_data, unique_key, batch_size=500, max_retries=3)`
  - Splits nodes list into batches and runs an UNWIND MERGE query: `UNWIND $batch AS node MERGE (n:Label {unique_key: node.unique_key}) SET n += node RETURN count(n) as created`.
  - Returns sum of `created` counts from each batch's result.
- `create_relationships_batch(session, relationship_type, relationships_data, source_label, source_key, target_label, target_key, batch_size=500, max_retries=3)`
  - Builds UNWIND queries that `MATCH` nodes by source/target and `MERGE` relationships, optionally setting relationship properties.
- `_execute_with_retry(session, query, parameters, max_retries)` implements exponential backoff with sleeps of 1,2,4 seconds and raises if all attempts fail.
- `create_constraints(session, constraints)` issues `CREATE CONSTRAINT ... IF NOT EXISTS FOR (n:Label) REQUIRE n.prop IS UNIQUE` and prints warnings on failure.

### backend/utils/pii_hashing.py
Link: [backend/utils/pii_hashing.py](backend/utils/pii_hashing.py)
- `hash_pii(value)` returns `None` for empty inputs, otherwise `hashlib.sha256(value.encode('utf-8')).hexdigest()`.
- `mask_pii_display(value, pii_type)` returns masked forms for `email` (***@***.com) and `phone` (***-***-last4).

### backend/utils/circuit_breaker.py
Link: [backend/utils/circuit_breaker.py](backend/utils/circuit_breaker.py)
- `CircuitState` Enum defines `CLOSED`, `OPEN`, `HALF_OPEN`.
- `CircuitBreaker` object tracks `failure_count`, `state`, `last_failure_time`, `failure_threshold`, and `recovery_timeout`.
- `call(func, *args, **kwargs)` checks if circuit `OPEN` and whether recovery should be attempted. It executes `func` and calls `_on_success()` or `_on_failure()` accordingly; raises on OPEN.
- `generate_template_narrative(...)` builds readable fallback narratives using top drivers and structural patterns.

---

## Closing notes
- This expansion file focuses on backend functions and flows. I can continue by:
  - Adding example inputs/outputs and small execution traces for each function.
  - Creating per-file markdown files in `docs/` for easier navigation (if you prefer one-file-per-module).

If you want the combined `docs/DETAILED_CODE_DOCUMENTATION.md` updated to include a link to this file, I can patch it now.

---

Generated: 2026-02-27
