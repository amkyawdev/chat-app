// GroupChat.jsx - group chat component
import React from 'react';
import { motion } from 'framer-motion';
import ChatBox from '../Chat/ChatBox';
import MemberList from './MemberList';
import GroupInfo from './GroupInfo';
import './GroupChat.css';

const GroupChat = ({ group, onUserClick }) => {
  if (!group) {
    return (
      <div className="group-chat empty">
        <div className="empty-state">
          <span className="empty-icon">👥</span>
          <h3>Select a group</h3>
          <p>Choose a group from the sidebar to start chatting</p>
        </div>
      </div>
    );
  }

  return (
    <div className="group-chat">
      <div className="group-main">
        <div className="group-header">
          <h2>{group.name}</h2>
          {group.description && <p className="group-desc">{group.description}</p>}
        </div>
        <ChatBox conversation={group} onUserClick={onUserClick} />
      </div>
      <div className="group-sidebar">
        <MemberList members={group.members} onUserClick={onUserClick} />
        <GroupInfo group={group} />
      </div>
    </div>
  );
};

export default GroupChat;