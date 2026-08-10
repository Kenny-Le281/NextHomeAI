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
## Images
<img width="1470" height="833" alt="Screenshot 2026-05-11 at 11 32 05 AM" src="https://github.com/user-attachments/assets/1b75bfb7-0f7b-4078-94ab-2d9586099646"/>
<br>
<img width="1470" height="833" alt="Screenshot 2026-05-11 at 11 37 30 AM" src="https://github.com/user-attachments/assets/1fc1372b-c01a-43a9-93d6-5243b181b0a5"/>
<br>
<img width="1470" height="834" alt="Screenshot 2026-05-11 at 11 40 32 AM" src="https://github.com/user-attachments/assets/dc05a147-8644-411f-8978-ec6bba07be5a"/>
<br>
<img width="1470" height="822" alt="Screenshot 2026-05-11 at 11 40 43 AM" src="https://github.com/user-attachments/assets/d36d2c9a-d9d9-4a01-804d-c422428f4e14"/>
<br>
<img width="1470" height="832" alt="Screenshot 2026-05-11 at 11 40 56 AM" src="https://github.com/user-attachments/assets/30672ebd-2f38-421c-8244-fa3547e95999"/>


## Environment variables

Create a `.env` file at the project root:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5.6-luna
OPENAI_TIMEOUT_SECONDS=180
SUPABASE_DB_PASSWORD=your_supabase_database_password
REDFIN_KEY=your_redfinapi_key_if_used
```

`OPENAI_MODEL` and `OPENAI_TIMEOUT_SECONDS` are optional. The defaults shown above
are used when they are omitted.

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

## OpenAI API

The backend calls the OpenAI Responses API. Add your API key to the project-root
`.env` file before starting the backend. The key is read only by the Python backend;
do not add it to `Frontend/.env` or expose it through a `VITE_` variable.

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
