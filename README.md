# NextHomeAI

NextHomeAI is a full-stack real estate assistant that lets users search for property listings through natural language and request property tours from the same chat-based interface.

The app combines a React frontend, a Python backend, an LLM-powered agent, a PostgreSQL/Supabase listings database, and Playwright-based booking automation.

## Features

- Natural language property search
- LLM-based intent classification
- LLM-based search filter parsing
- PostgreSQL/Supabase listing queries
- Listing cards with address, price, beds, baths, square footage, property type, and images
- Expanded listing details page with image gallery
- Booking flow for property tours
- Booking state tracking across multiple messages
- Direct address lookup for booking
- React Router pages for Home, Listing Details, Settings, and About
- Accessibility-focused settings such as larger fonts, readable font style, high contrast, and reduced motion
- Frontend session persistence using localStorage
- Backend session storage by frontend session ID
`


## Environment variables

Create a `.env` file at the project root:

```env
SUPABASE_DB_PASSWORD=your_supabase_database_password
REDFIN_KEY=your_redfinapi_key_if_used
```

Create a frontend `.env` file inside `Frontend/`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Do not commit real API keys, database passwords, or secrets.

## Running the project

Run the backend first, then the frontend.

### Backend

```bash
cd Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

On Windows PowerShell:

```powershell
cd Backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The backend should run at:

```text
http://localhost:8000
```

You can test it at:

```text
http://localhost:8000/health
```

### Frontend

```bash
cd Frontend
npm install
npm run dev
```

The frontend should run at:

```text
http://localhost:5173
```

## Local services required

The backend expects Ollama to be running locally if using the configured Ollama client:

```bash
ollama serve
```

The configured model should also be available locally:

```bash
ollama pull llama3.1:latest
```

## API response shape

The frontend expects the backend `/chat` route to return a response shaped like this:

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

The most important fields for the frontend are:

- `reply`: shown as the assistant chat message
- `listings`: rendered as listing cards
- `booking`: rendered in the booking progress panel