// MessageItem component - single message display
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import Avatar from '../UI/Avatar';
import EmojiBar from './EmojiBar';
import './MessageItem.css';

const MessageItem = ({ message, isOwn, onUserClick, showAvatar = true }) => {
  const [showEmojiBar, setShowEmojiBar] = useState(false);
  const [isDeleted, setIsDeleted] = useState(message.is_deleted);

  const formatTime = (dateString) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch {
      return '';
    }
  };

  const handleMouseEnter = () => setShowEmojiBar(true);
  const handleMouseLeave = () => setShowEmojiBar(false);

  return (
    <motion.div
      className={`message-item ${isOwn ? 'own' : 'other'}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {!isOwn && showAvatar && (
        <div className="message-avatar">
          <Avatar user={message.sender} size="small" />
        </div>
      )}

      <div className="message-content">
        {!isOwn && <span className="sender-name">{message.sender?.username}</span>}
        
        <div className="message-bubble">
          {isDeleted ? (
            <span className="deleted-message">This message was deleted</span>
          ) : (
            <>
              {message.type === 'image' ? (
                <img src={message.content} alt="message" className="message-image" />
              ) : (
                <p className="message-text">{message.content}</p>
              )}
            </>
          )}
        </div>

        <div className="message-meta">
          <span className="message-time">{formatTime(message.created_at)}</span>
          {isOwn && message.status === 'sent' && (
            <span className="message-status">✓</span>
          )}
        </div>

        <EmojiBar
          visible={showEmojiBar}
          reactions={message.reactions}
          messageId={message.id}
        />
      </div>
    </motion.div>
  );
};

export default MessageItem;