// Chat page - private chat UI
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import useUserStore from '../../store/userStore';
import useChatStore from '../../store/chatStore';
import ChatBox from '../../components/Chat/ChatBox';
import Avatar from '../../components/UI/Avatar';
import Modal from '../../components/UI/Modal';
import './Chat.css';

const ChatPage = () => {
  const { user, isAuthenticated } = useUserStore();
  const { conversations, activeConversation, setActiveConversation, fetchConversations, searchUsers } = useChatStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showProfile, setShowProfile] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    } else {
      fetchConversations();
    }
  }, [isAuthenticated, navigate]);

  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (query.length > 2) {
      const results = await searchUsers(query);
      setSearchResults(results.data || []);
    } else {
      setSearchResults([]);
    }
  };

  const handleUserClick = (user) => {
    setSelectedUser(user);
    setShowProfile(true);
  };

  const handleStartChat = (user) => {
    setActiveConversation(user);
    setSearchQuery('');
    setSearchResults([]);
  };

  return (
    <div className="chat-page">
      <div className="chat-sidebar">
        <div className="sidebar-header">
          <h2>Messages</h2>
          <button className="new-chat-btn">+</button>
        </div>
        
        <div className="search-box">
          <input
            type="text"
            placeholder="Search users..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
          />
          {searchResults.length > 0 && (
            <div className="search-results">
              {searchResults.map((u) => (
                <div 
                  key={u.id} 
                  className="search-result"
                  onClick={() => handleStartChat(u)}
                >
                  <Avatar user={u} size="small" />
                  <span>{u.display_name || u.username}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="conversations-list">
          {conversations.map((conv) => (
            <motion.div
              key={conv.id || conv.user_id}
              className={`conversation-item ${activeConversation?.user_id === conv.user_id ? 'active' : ''}`}
              onClick={() => setActiveConversation(conv)}
              whileHover={{ backgroundColor: '#f3f4f6' }}
            >
              <Avatar user={conv} size="medium" showStatus />
              <div className="conv-info">
                <span className="conv-name">{conv.display_name || conv.username}</span>
                <span className="conv-preview">{conv.last_message}</span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="chat-main">
        <ChatBox 
          conversation={activeConversation} 
          onUserClick={handleUserClick}
        />
      </div>

      <Modal 
        isOpen={showProfile} 
        onClose={() => setShowProfile(false)}
        title="Profile"
      >
        {selectedUser && (
          <div className="profile-modal">
            <Avatar user={selectedUser} size="large" showStatus />
            <h2>{selectedUser.display_name || selectedUser.username}</h2>
            <span className="username">@{selectedUser.username}</span>
            <span className="status">
              <span className={`status-dot status-${selectedUser.status}`}></span>
              {selectedUser.status}
            </span>
            {selectedUser.bio && <p className="bio">{selectedUser.bio}</p>}
            <div className="actions">
              <button onClick={() => handleStartChat(selectedUser)}>Send Message</button>
              <button>Add Friend</button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ChatPage;