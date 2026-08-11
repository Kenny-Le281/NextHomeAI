import { useEffect, useState } from "react";
import { sendAgentMessage } from "../api/agentApi";
import ChatPanel from "../components/ChatPanel";
import ListingsGrid from "../components/ListingsGrid";
import BookingSummary from "../components/BookingSummary";

const STORAGE_KEY = "nextHomeAI.homeState";

const DEFAULT_MESSAGES = [
  {
    role: "assistant",
    content: "Hi! Tell me what kind of property you're looking for.",
  },
];

function loadHomeState() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);

    if (!saved) {
      return {
        sessionId: crypto.randomUUID(),
        messages: DEFAULT_MESSAGES,
        listings: [],
        booking: null,
      };
    }

    const parsed = JSON.parse(saved);

    return {
      sessionId: parsed.sessionId || crypto.randomUUID(),
      messages: Array.isArray(parsed.messages) && parsed.messages.length > 0
        ? parsed.messages
        : DEFAULT_MESSAGES,
      listings: Array.isArray(parsed.listings) ? parsed.listings : [],
      booking: parsed.booking || null,
    };
  } catch {
    return {
      sessionId: crypto.randomUUID(),
      messages: DEFAULT_MESSAGES,
      listings: [],
      booking: null,
    };
  }
}

function HomePage() {
  const [homeState, setHomeState] = useState(loadHomeState);
  const [isLoading, setIsLoading] = useState(false);

  const { sessionId, messages, listings, booking } = homeState;

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(homeState));
  }, [homeState]);

  async function handleSendMessage(message) {
    if (!message.trim() || isLoading) return;

    const userMessage = {
      role: "user",
      content: message,
    };

    setHomeState((previousState) => ({
      ...previousState,
      messages: [...previousState.messages, userMessage],
    }));

    setIsLoading(true);

    try {
      const result = await sendAgentMessage(message, sessionId);

      const assistantMessage = {
        role: "assistant",
        content: result.reply,
      };

      setHomeState((previousState) => ({
        ...previousState,
        messages: [...previousState.messages, assistantMessage],
        listings: Array.isArray(result.listings)
          ? result.listings
          : previousState.listings,
        booking: result.booking || previousState.booking,
      }));
    } catch (error) {
      console.error(error);

      setHomeState((previousState) => ({
        ...previousState,
        messages: [
          ...previousState.messages,
          {
            role: "assistant",
            content: `Something went wrong while contacting the backend: ${error.message}`,
          },
        ],
      }));
    } finally {
      setIsLoading(false);
    }
  }

  function handleClearSession() {
    const freshState = {
      sessionId: crypto.randomUUID(),
      messages: DEFAULT_MESSAGES,
      listings: [],
      booking: null,
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(freshState));
    setHomeState(freshState);
  }

  const hasListings = listings.length > 0;

  return (
    <main className="home-page">
      <section className="hero-section">
        <div>
          <p className="eyebrow">AI-powered property search</p>
          <h1>Find homes faster with NextHomeAI.</h1>
          <p className="hero-description">
            Tell the assistant what you are looking for, refine your search naturally,
            and book property tours from the same conversation.
          </p>

          {(messages.length > 1 || hasListings || booking) && (
            <button
              type="button"
              className="clear-session-button"
              onClick={handleClearSession}
            >
              Start new search
            </button>
          )}
        </div>
      </section>

      <section className={`chat-layout ${hasListings ? "has-listings" : ""}`}>
        <ChatPanel
          messages={messages}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
        />

        {booking && <BookingSummary booking={booking} />}
      </section>

      {hasListings && (
        <section className="listings-section">
          <div className="section-header">
            <div>
              <p className="eyebrow">Search results</p>
              <h2>Listings that match your request</h2>
            </div>

            <p className="listing-count">{listings.length} listings shown</p>
          </div>

          <ListingsGrid listings={listings} />
        </section>
      )}
    </main>
  );
}

export default HomePage;
