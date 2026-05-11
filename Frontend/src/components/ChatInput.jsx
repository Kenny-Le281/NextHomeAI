import { useState } from "react";

function ChatInput({ onSendMessage, disabled }) {
  const [value, setValue] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    const message = value.trim();
    if (!message) return;

    onSendMessage(message);
    setValue("");
  }

  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <input
        value={value}
        disabled={disabled}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Example: Find me a 3-bedroom home in Ottawa under $700,000"
      />

      <button type="submit" disabled={disabled || !value.trim()}>
        Send
      </button>
    </form>
  );
}

export default ChatInput;