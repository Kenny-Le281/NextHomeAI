function MessageBubble({ message }) {
    return (
      <div className={`message-row ${message.role}`}>
        <div className="message-bubble">{message.content}</div>
      </div>
    );
  }
  
  export default MessageBubble;