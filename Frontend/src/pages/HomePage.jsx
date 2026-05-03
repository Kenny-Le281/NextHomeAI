import { useState } from "react";
import { sendAgentMessage } from "../api/agentApi";
import ChatPanel from "../components/ChatPanel";
import ListingsGrid from "../components/ListingsGrid";
import BookingSummary from "../components/BookingSummary";


function HomePage() {
  const [sessionId] = useState(() => crypto.randomUUID());

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hi! Tell me what kind of property you're looking for.",
    },
  ]);

  const [listings, setListings] = useState([]);
  const [booking, setBooking] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSendMessage(message) {
    if (!message.trim() || isLoading) return;

    const userMessage = {
      role: "user",
      content: message,
    };

    setMessages((previousMessages) => [...previousMessages, userMessage]);
    setIsLoading(true);

    try {
      const result = await sendAgentMessage(message, sessionId);

      const assistantMessage = {
        role: "assistant",
        content: result.reply,
      };

      setMessages((previousMessages) => [...previousMessages, assistantMessage]);

      if (Array.isArray(result.listings)) {
        setListings(result.listings);
      }

      if (result.booking) {
        setBooking(result.booking);
      }
    } catch (error) {
      console.error(error);

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          role: "assistant",
          content: "Something went wrong while contacting the backend.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
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

            <p className="listing-count">{listings.length} listings found</p>
          </div>

          <ListingsGrid listings={listings} />
        </section>
      )}
    </main>
  );
}

export default HomePage;