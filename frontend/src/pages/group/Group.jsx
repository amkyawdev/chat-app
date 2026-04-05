// Group page - group chat UI
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import useUserStore from '../../store/userStore';
import useGroupStore from '../../store/groupStore';
import GroupChat from '../../components/Group/GroupChat';
import Modal from '../../components/UI/Modal';
import Button from '../../components/UI/Button';
import './Group.css';

const GroupPage = () => {
  const { user, isAuthenticated } = useUserStore();
  const { groups, activeGroup, setActiveGroup, fetchGroups, createGroup } = useGroupStore();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');
  const [newGroupDesc, setNewGroupDesc] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    } else {
      fetchGroups();
    }
  }, [isAuthenticated, navigate]);

  const handleCreateGroup = async () => {
    if (!newGroupName.trim()) return;
    const group = await createGroup(newGroupName, newGroupDesc);
    if (group) {
      setActiveGroup(group);
      setShowCreateModal(false);
      setNewGroupName('');
      setNewGroupDesc('');
    }
  };

  const handleUserClick = (user) => {
    // Show user profile modal
  };

  return (
    <div className="group-page">
      <div className="group-sidebar">
        <div className="sidebar-header">
          <h2>Groups</h2>
          <button className="new-group-btn" onClick={() => setShowCreateModal(true)}>+</button>
        </div>

        <div className="groups-list">
          {groups.map((group) => (
            <motion.div
              key={group.id}
              className={`group-item ${activeGroup?.id === group.id ? 'active' : ''}`}
              onClick={() => setActiveGroup(group)}
              whileHover={{ backgroundColor: '#f3f4f6' }}
            >
              <div className="group-avatar-placeholder">
                {group.name.charAt(0).toUpperCase()}
              </div>
              <div className="group-info">
                <span className="group-name">{group.name}</span>
                <span className="group-preview">{group.description}</span>
              </div>
            </motion.div>
          ))}
          
          {groups.length === 0 && (
            <div className="no-groups">
              <p>No groups yet</p>
              <Button onClick={() => setShowCreateModal(true)}>Create Group</Button>
            </div>
          )}
        </div>
      </div>

      <div className="group-main">
        <GroupChat group={activeGroup} onUserClick={handleUserClick} />
      </div>

      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create Group"
      >
        <div className="create-group-form">
          <div className="form-group">
            <label>Group Name</label>
            <input
              type="text"
              value={newGroupName}
              onChange={(e) => setNewGroupName(e.target.value)}
              placeholder="Enter group name"
            />
          </div>
          <div className="form-group">
            <label>Description (optional)</label>
            <textarea
              value={newGroupDesc}
              onChange={(e) => setNewGroupDesc(e.target.value)}
              placeholder="Enter group description"
              rows={3}
            />
          </div>
          <div className="form-actions">
            <Button variant="secondary" onClick={() => setShowCreateModal(false)}>Cancel</Button>
            <Button onClick={handleCreateGroup}>Create</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default GroupPage;