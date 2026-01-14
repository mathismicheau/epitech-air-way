import React from 'react';
import { styles } from '../data/styles';

const TicketInput = ({ userInput, setUserInput, sendMessage, t }) => (
  <div style={styles.inputArea}>
    <div style={styles.ticket}>
      <div style={styles.ticketLeft}>
        <div style={styles.ticketTop}><span>{t.economy}</span><span>{t.boardingPass}</span></div>
        <input 
          style={styles.ticketInput} 
          value={userInput} 
          onChange={(e) => setUserInput(e.target.value)} 
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()} 
          placeholder={t.placeholder} 
        />
        <div style={styles.ticketBottom}><span>WINGMAN / EPITECH AIRWAYS</span><span>{t.gate}</span></div>
      </div>
      <div style={styles.dash}></div>
      <div style={styles.ticketRight}>
        <span style={styles.stubLabel}>SEND</span>
        <button 
          className="send-button-hover"
          style={{
            ...styles.sendBtn, 
            backgroundColor: userInput.trim() ? '#0F172A' : '#F1F5F9',
            cursor: userInput.trim() ? 'pointer' : 'default'
          }} 
          onClick={() => sendMessage()}
        >
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
            <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill={userInput.trim() ? "white" : "#CBD5E1"}/>
          </svg>
        </button>
        <span style={styles.stubSerial}>WM-2026</span>
      </div>
    </div>
  </div>
);

export default TicketInput;