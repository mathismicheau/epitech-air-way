import React from 'react';
import { styles } from '../data/styles';

const Sidebar = ({ chats, currentChatIndex, setCurrentChatIndex, startNewChat, deleteChat, navigate, t }) => (
  <div style={styles.sidebar}>
    <div style={styles.logoSection} onClick={() => navigate('/')}>
      <img src="/LOGO-wingman.png" alt="Logo" style={styles.sidebarLogo} className="radiating-logo" />
      <h2 style={styles.logoText}>Wingman</h2>
    </div>
    
    <button style={styles.newChatBtn} onClick={startNewChat}>{t.newFlight}</button>
    
    <div style={styles.historyBox}>
      <label style={styles.historyLabel}>{t.flightLogs}</label>
      <div style={styles.logsList}>
        {chats.map((chat, idx) => (
          <div 
            key={chat.id} 
            onClick={() => setCurrentChatIndex(idx)}
            style={{
              ...styles.logItem, 
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-start', 
              whiteSpace: 'normal',         
              overflow: 'visible',          
              paddingRight: '5px'
            }}
          >
            {/* L'icône Avion */}
            <span style={{ marginRight: '8px', flexShrink: 0 }}>✈️</span>

            {/* LE TITRE (On force une largeur pour qu'il ne disparaisse pas) */}
            <span style={{ 
              flex: 1,
              fontSize: '0.85rem',
              color: currentChatIndex === idx ? '#3B82F6' : '#1E293B',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 1,
              WebkitBoxOrient: 'vertical',
              lineHeight: '1.2'
            }}>
              {chat.title}
            </span>

            {/* LE BOUTON (On le rend très visible pour le test) */}
            <button 
              onClick={(e) => {
                e.stopPropagation(); 
                deleteChat(chat.id);
              }}
              style={{
                background: 'none',
                border: 'none',
                color: '#94A3B8', 
                cursor: 'pointer',
                fontSize: '1.2rem',
                fontWeight: 'bold',
                padding: '0 5px',
                flexShrink: 0
              }}
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </div>
    <button style={styles.backBtn} onClick={() => navigate('/')}>{t.quit}</button>
  </div>
);

export default Sidebar;