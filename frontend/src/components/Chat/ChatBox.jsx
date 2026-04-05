// ChatBox component - main chat area
import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import MessageItem from './MessageItem';
import InputBox from './InputBox';
import { useChatStore } from '../../store/chatStore';
import './ChatBox.css';

const ChatBox = ({ conversation, onUserClick }) => {
  const { messages, sendMessage, isLoading } = useChatStore();
  const messagesEndRef = useRef(null);
  const conversationKey = conversation?.user_id;
  const conversationMessages = messages[conversationKey] || [];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversationMessages]);

  const handleSend = async (content) => {
    if (!conversation?.user_id) return;
    await sendMessage(conversation.user_id, content);
  };

  if (!conversation) {
    return (
      <div className="chat-box empty">
        <div className="empty-state">
          <span className="empty-icon">💬</span>
          <h3>Select a conversation</h3>
          <p>Choose a conversation from the sidebar to start chatting</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-box">
      <div className="chat-header">
        <div className="chat-header-info">
          <h3>{conversation.display_name || conversation.username}</h3>
          <span className="status">{conversation.status}</span>
        </div>
      </div>

      <div className="chat-messages">
        {isLoading && conversationMessages.length === 0 ? (
          <div className="loading-messages">
            <div className="loading-spinner" />
            <p>Loading messages...</p>
          </div>
        ) : conversationMessages.length === 0 ? (
          <div className="no-messages">
            <p>No messages yet. Start the conversation!</p>
          </div>
        ) : (
          <AnimatePresence>
            {conversationMessages.map((msg, index) => (
              <MessageItem
                key={msg.id}
                message={msg}
                isOwn={msg.sender_id === conversation.user_id ? false : true}
                onUserClick={onUserClick}
              />
            ))}
          </AnimatePresence>
        )}
        <div ref={messagesEndRef} />
      </div>

      <InputBox onSend={handleSend} />
    </div>
  );
};

export default ChatBox;