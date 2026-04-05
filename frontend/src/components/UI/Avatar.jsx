// Avatar component - user avatar display with click → profile modal
import React, { useState } from 'react';
import './Avatar.css';

const Avatar = ({ 
  user, 
  size = 'medium', 
  showStatus = false, 
  onClick,
  className = ''
}) => {
  const [imageError, setImageError] = useState(false);
  
  const sizeClass = `avatar-${size}`;
  const initials = user?.username?.slice(0, 2).toUpperCase() || '?';
  
  // Generate a color based on user ID
  const getColor = (userId) => {
    if (!userId) return '#6366f1';
    const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e', '#14b8a6', '#06b6d4', '#3b82f6'];
    let hash = 0;
    for (let i = 0; i < userId.length; i++) {
      hash = userId.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
  };

  const handleClick = (e) => {
    if (onClick) {
      e.stopPropagation();
      onClick(user);
    }
  };

  const avatarStyle = {
    backgroundColor: getColor(user?.id),
  };

  const shouldShowImage = user?.avatar && !imageError;

  return (
    <div 
      className={`avatar ${sizeClass} ${className} ${onClick ? 'clickable' : ''}`}
      onClick={handleClick}
      title={user?.display_name || user?.username}
    >
      {shouldShowImage ? (
        <img 
          src={user.avatar} 
          alt={user?.username}
          onError={() => setImageError(true)}
        />
      ) : (
        <span className="avatar-initials" style={avatarStyle}>
          {initials}
        </span>
      )}
      
      {showStatus && user?.status && (
        <span className={`avatar-status status-${user.status}`} />
      )}
    </div>
  );
};

export default Avatar;