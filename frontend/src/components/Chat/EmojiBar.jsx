// EmojiBar component - reactions on messages
import React from 'react';
import { motion } from 'framer-motion';
import './EmojiBar.css';

const EMOJI_LIST = ['👍', '❤️', '😂', '😢', '😮', '😡', '🎉', '🔥'];

const EmojiBar = ({ visible, reactions = {}, messageId, onReact }) => {
  if (!visible) return null;

  return (
    <motion.div
      className="emoji-bar"
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 5 }}
    >
      <div className="emoji-reactions">
        {Object.entries(reactions).map(([emoji, data]) => (
          <button
            key={emoji}
            className="reaction-pill"
            onClick={() => onReact?.(messageId, emoji)}
          >
            <span className="reaction-emoji">{emoji}</span>
            <span className="reaction-count">{data.count}</span>
          </button>
        ))}
      </div>
      
      <div className="emoji-picker">
        {EMOJI_LIST.map((emoji) => (
          <button
            key={emoji}
            className="emoji-btn"
            onClick={() => onReact?.(messageId, emoji)}
          >
            {emoji}
          </button>
        ))}
      </div>
    </motion.div>
  );
};

export default EmojiBar;