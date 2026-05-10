# NextHomeAI Frontend

This is the React frontend for NextHomeAI. It provides the chat interface, listing cards, listing details page, settings page, and about page.

## Setup

Install dependencies:

```bash
npm install
```

Create a `.env` file inside `Frontend/`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Run the development server:

```bash
npm run dev
```

The app should run at:

```text
http://localhost:5173
```

## Backend connection

The frontend sends chat messages through `src/api/agentApi.js`.

Expected request:

```json
{
  "message": "Find me a 3-bedroom home in Ottawa under $700,000",
  "session_id": "frontend-generated-session-id"
}
```

Expected response:

```json
{
  "reply": "Assistant message",
  "filters": {},
  "context": {},
  "booking": {},
  "done": false,
  "api_params": null,
  "listings": [],
  "intent": "provide_search_info"
}
```

The frontend currently uses:

- `reply` for assistant chat messages
- `listings` for listing cards and details pages
- `booking` for booking progress display

## Pages

### Home page

The home page contains:

- Hero section
- Chat panel
- Booking progress panel
- Listing grid

### Listing details page

The details page receives the selected listing through React Router state. It can also recover saved listings from localStorage after a refresh.

It displays:

- Main image gallery
- Thumbnails
- Price
- Address
- Beds, baths, square footage
- Property type
- City, state, zip
- HOA amount
- Days on market
- Last sold date
- Coordinates
- Description if available
- Original Redfin/source link

### Settings page

The settings page is accessibility-focused only. It supports:

- Larger font sizes
- Readable / dyslexia-friendly font style
- High contrast
- Reduced motion

### About page

The about page explains the purpose of NextHomeAI and the app’s main features.

## Common issues

### Frontend cannot contact backend

Check that the backend is running at:

```text
http://localhost:8000
```

Also confirm the frontend `.env` file contains:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Restart Vite after changing `.env`.