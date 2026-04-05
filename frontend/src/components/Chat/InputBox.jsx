// InputBox component - send message input
import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import './InputBox.css';

const InputBox = ({ onSend, placeholder = 'Type a message...' }) => {
  const [message, setMessage] = useState('');
  const inputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim()) return;
    
    onSend(message.trim());
    setMessage('');
    inputRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form className="input-box" onSubmit={handleSubmit}>
      <div className="input-container">
        <textarea
          ref={inputRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          rows={1}
          className="message-input"
        />
        
        <div className="input-actions">
          <button 
            type="button" 
            className="action-btn"
            title="Add emoji"
          >
            😊
          </button>
          <button 
            type="button" 
            className="action-btn"
            title="Attach file"
          >
            📎
          </button>
        </div>
      </div>

      <motion.button
        type="submit"
        className="send-btn"
        disabled={!message.trim()}
        whileTap={{ scale: 0.95 }}
      >
        ➤
      </motion.button>
    </form>
  );
};

export default InputBox;