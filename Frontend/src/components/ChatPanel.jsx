import ChatInput from "./ChatInput";
import MessageBubble from "./MessageBubble";

function ChatPanel({ messages, isLoading, onSendMessage }) {
  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div>
          <h2>Chat with NextHomeAI</h2>
          <p>Describe your ideal property or ask to book a tour.</p>
        </div>
      </div>

      <div className="messages-area">
        {messages.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}

        {isLoading && (
          <div className="message-row assistant">
            <div className="message-bubble">Thinking...</div>
          </div>
        )}
      </div>

      <ChatInput onSendMessage={onSendMessage} disabled={isLoading} />
    </div>
  );
}

export default ChatPanel;