import React from 'react';
import { styles } from '../data/styles';

const MessageList = ({ messages, isLoading }) => (
  <>
    {messages.map((msg, i) => (
      <div key={i} style={msg.sender === "user" ? styles.userWrap : styles.botWrap}>
        <div style={msg.sender === "user" ? styles.userBub : styles.botBub}>{msg.text}</div>
      </div>
    ))}
    {isLoading && (
      <div style={styles.botWrap}>
        <div style={styles.loadingBubble}>
          <div className="dot"></div><div className="dot"></div><div className="dot"></div>
        </div>
      </div>
    )}
  </>
);

export default MessageList;