// MemberList.jsx - list of group members
import React from 'react';
import Avatar from '../UI/Avatar';
import './MemberList.css';

const MemberList = ({ members = [], onUserClick }) => {
  return (
    <div className="member-list">
      <h4>Members ({members.length})</h4>
      <ul>
        {members.map((member) => (
          <li key={member.id} onClick={() => onUserClick?.(member)}>
            <Avatar user={member} size="small" showStatus />
            <div className="member-info">
              <span className="member-name">
                {member.nickname || member.display_name || member.username}
              </span>
              {member.role !== 'member' && (
                <span className={`member-role role-${member.role}`}>
                  {member.role.replace('_', ' ')}
                </span>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default MemberList;