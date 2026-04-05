// GroupInfo.jsx - group details and settings
import React from 'react';
import Avatar from '../UI/Avatar';
import Button from '../UI/Button';
import './GroupInfo.css';

const GroupInfo = ({ group }) => {
  if (!group) return null;

  return (
    <div className="group-info">
      <div className="group-avatar">
        <Avatar user={{ ...group, username: group.name }} size="large" />
      </div>
      
      <h3>{group.name}</h3>
      {group.description && <p className="description">{group.description}</p>}
      
      <div className="info-stats">
        <div className="stat">
          <span className="stat-value">{group.member_count || 0}</span>
          <span className="stat-label">Members</span>
        </div>
        <div className="stat">
          <span className="stat-value">{group.created_at ? new Date(group.created_at).toLocaleDateString() : '-'}</span>
          <span className="stat-label">Created</span>
        </div>
      </div>

      <div className="info-actions">
        <Button variant="secondary" size="small">View Details</Button>
        <Button variant="ghost" size="small">Settings</Button>
      </div>
    </div>
  );
};

export default GroupInfo;