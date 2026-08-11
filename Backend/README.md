# NextHomeAI Backend

This is the Python backend for NextHomeAI. It exposes a FastAPI API for the React frontend, runs the LLM-powered agent, queries property listings from PostgreSQL/Supabase, and handles property tour booking automation.

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## Install dependencies

From the `Backend/` folder:

```bash
python -m pip install -r requirements.txt
```

Install Playwright browser binaries:

```bash
playwright install
```

## Environment variables

Create a `.env` file at the project root, not inside `Backend/`:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5.6-luna
OPENAI_TIMEOUT_SECONDS=180
DATABASE_HOST=your_supabase_pooler_host
DATABASE_PORT=5432
DATABASE_NAME=postgres
DATABASE_USER=your_supabase_database_user
DATABASE_PASSWORD=your_supabase_database_password
DATABASE_SSLMODE=require
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
REDFIN_KEY=your_redfin_key_if_used
```

See the root `.env.example` for every optional setting. `REDFIN_KEY` is only needed
by `runner.py`. Do not commit real credentials.

## Running the backend

From the `Backend/` folder:

```bash
uvicorn main:app --reload --port 8000
```

The backend should be available at:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/health
```

## Main API routes

### `GET /health`

Returns:

```json
{
  "status": "ok"
}
```

### `POST /chat`

Request:

```json
{
  "message": "Find me a 3-bedroom home in Ottawa under $700,000",
  "session_id": "frontend-generated-session-id"
}
```

Response:

```json
{
  "reply": "Assistant response text",
  "filters": {},
  "context": {},
  "booking": {},
  "done": false,
  "api_params": null,
  "listings": [],
  "intent": "provide_search_info"
}
```

### `POST /reset`

Resets the backend session for a specific session ID.

Request:

```json
{
  "session_id": "frontend-generated-session-id"
}
```

## Agent flow

The main function is `run_agent()` in `agent/agent_orchestrator.py`.

The agent performs these steps:

1. Copy the current session context and booking state.
2. Classify the user intent.
3. Route to search, booking, confirmation, or normal chat flow.
4. Parse structured information with the LLM when needed.
5. Merge parsed values into current state.
6. Query the database or continue collecting missing information.
7. Return a response dictionary to FastAPI.

## Search flow

Search-related messages use:

- `classify_intent_tool.py`
- `parse_filters_tool.py`
- `merge_filters_service.py`
- `search_state_service.py`
- `query_listings_tool.py`
- `response_generation_service.py`

Required search fields are currently:

- city or area
- maximum price
- minimum number of bedrooms

When enough information is available, the backend queries the listings table and returns matching listings to the frontend.

## Listing query behavior

`query_listings_tool.py` builds SQL conditions from `HousingFilters`.

Typical filters include:

- city
- price minimum / maximum
- bedrooms minimum / maximum
- bathrooms minimum / maximum
- property type

The listing query should select all fields the frontend needs, including:

- listing_id
- property_id
- address_name
- city
- state
- zip
- url
- property_type
- beds
- baths
- total_baths
- price
- days_on_market
- latitude
- longitude
- hoa_amount
- last_sold_date
- image_urls
- sqft

If a frontend field is missing, first check that it is included in the SQL `SELECT` statement.

## Booking flow

Booking-related messages use:

- `parse_booking_request_tool.py`
- `booking_state_service.py`
- `listing_selection_service.py`
- `book_showing_tool.py`
- `automation/redfin_tour_booking.py`

The booking flow collects:

- listing address / listing ID / listing URL
- full name
- email
- phone
- preferred date
- preferred time
- tour type
- optional message

The system asks for final confirmation before submitting a showing request.

## LLM setup

The backend uses the OpenAI Responses API. Add these values to the `.env` file at
the project root:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5.6-luna
OPENAI_TIMEOUT_SECONDS=180
```

Only `OPENAI_API_KEY` is required. The model and timeout have the defaults shown
above. Keep the key on the backend and never place it in `Frontend/.env`.

## Common issues

### `fe_sendauth: no password supplied`

Your `.env` file is missing `DATABASE_PASSWORD` (or the legacy
`SUPABASE_DB_PASSWORD`), or it is in the wrong directory.

## Production deployment

Use the root `Dockerfile` for the API and set `ALLOWED_ORIGINS` to the exact
frontend origin. The complete AWS procedure is in the root `DEPLOYMENT.md`.
