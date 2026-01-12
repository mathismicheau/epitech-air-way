import React, { useState } from 'react';

function App() {
  // --- 1. MEMORY (State) ---
  const [messages, setMessages] = useState([
    { text: "Welcome to Epitech  Airways! How can I help you today?", sender: "bot" }
  ]);
  const [userInput, setUserInput] = useState("");
  const [history, setHistory] = useState([]);

  // --- 2. THE BRAIN (Logic) ---

  const startNewChat = () => {
    // Save current chat to history before clearing
    if (messages.length > 1) {
      const firstUserMsg = messages.find(m => m.sender === "user");
      const title = firstUserMsg ? firstUserMsg.text : "Previous Trip";
      setHistory((prev) => [title, ...prev]);
    }
    // Reset messages
    setMessages([{ text: "New flight path initialized. Where to?", sender: "bot" }]);
  };

  const sendMessage = async () => {
    if (userInput.trim() === "") return;

    const newMsg = { text: userInput, sender: "user" };
    setMessages((prev) => [...prev, newMsg]);
    const currentInput = userInput; // Store it before clearing
    setUserInput("");

    try {
      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: currentInput }),
      });

      const data = await response.json();
      setMessages((prev) => [...prev, { text: data.reply, sender: "bot" }]);
    } catch (error) {
      setMessages((prev) => [...prev, { text: "⚠️ System: Connection to flight server lost. Please check if the backend is running.", sender: "bot" }]);
    }
  };

  // --- 3. THE FACE (UI) ---
  return (
    <div style={styles.container}>
      
      {/* SIDEBAR */}
      <div style={styles.sidebar}>
        <div style={styles.logoSection}>
          <span style={styles.logoIcon}>✈️</span>
          <h2 style={styles.logoText}>Epitech Airways</h2>
        </div>
        
        <button style={styles.modernBtn} onClick={startNewChat}>
          <span style={{fontSize: '1.2rem'}}>+</span> Plan New Trip
        </button>
        
        <div style={styles.historyContainer}>
          <label style={styles.historyLabel}>RECENT SEARCHES</label>
          <div style={styles.historyList}>
            {history.length === 0 && <p style={{color: '#94A3B8', fontSize: '0.8rem'}}>No recent trips</p>}
            {history.map((item, index) => (
              <div key={index} style={styles.historyItem}>
                <span style={{opacity: 0.5}}>📍</span> {item.length > 18 ? item.substring(0, 18) + "..." : item}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* MAIN CHAT AREA */}
      <div style={styles.mainArea}>
        
        <div style={styles.chatWindow}>
          {messages.map((msg, index) => (
            <div key={index} style={msg.sender === "user" ? styles.userWrapper : styles.botWrapper}>
              <div style={msg.sender === "user" ? styles.userBubble : styles.botBubble}>
                {msg.text}
              </div>
            </div>
          ))}
        </div>
        
        {/* INPUT SECTION */}
        <div style={styles.inputWrapper}>
          <div style={styles.suggestionRow}>
            {['Flights to Tokyo', 'Cheap flights to NYC', 'Status BA123'].map(sugg => (
              <div key={sugg} style={styles.chip} onClick={() => setUserInput(sugg)}>{sugg}</div>
            ))}
          </div>
          <div style={styles.inputBox}>
            <input 
              style={styles.inputField}
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Where do you want to fly?"
            />
            <button style={styles.sendIconBtn} onClick={sendMessage}>🚀</button>
          </div>
          <p style={styles.footerText}>Powered by Epitech Airways Flight Engine • 2026</p>
        </div>

      </div>
    </div>
  );
}

// --- 4. THE DESIGN (Forcing Light Mode Colors) ---
const styles = {
  container: { 
    display: 'flex', height: '100vh', width: '100vw', 
    backgroundColor: '#F8FAFC', color: '#1E293B', 
    fontFamily: 'Inter, system-ui, sans-serif', overflow: 'hidden' 
  },
  sidebar: { 
    width: '300px', backgroundColor: '#FFFFFF', borderRight: '1px solid #E2E8F0',
    padding: '32px 24px', display: 'flex', flexDirection: 'column' 
  },
  logoSection: { display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '40px' },
  logoIcon: { background: '#3B82F6', color: 'white', padding: '8px', borderRadius: '10px' },
  logoText: { fontSize: '1.25rem', fontWeight: '800', margin: 0, color: '#1E293B' },
  
  modernBtn: { 
    backgroundColor: '#F1F5F9', color: '#1E293B', border: 'none', 
    padding: '12px', borderRadius: '12px', fontWeight: '600', 
    cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px'
  },
  
  historyContainer: { marginTop: '40px', flex: 1, overflowY: 'auto' },
  historyLabel: { fontSize: '0.7rem', fontWeight: '700', color: '#94A3B8', letterSpacing: '0.1em', marginBottom: '15px', display: 'block' },
  historyItem: { padding: '10px 0', fontSize: '0.9rem', color: '#64748B', display: 'flex', alignItems: 'center', gap: '10px', borderBottom: '1px solid #F1F5F9' },
  
  mainArea: { flex: 1, display: 'flex', flexDirection: 'column', position: 'relative' },
  chatWindow: { flex: 1, overflowY: 'auto', padding: '40px 15% 180px 15%' },
  
  userWrapper: { display: 'flex', justifyContent: 'flex-end', marginBottom: '20px' },
  botWrapper: { display: 'flex', justifyContent: 'flex-start', marginBottom: '20px' },
  
  userBubble: { 
    backgroundColor: '#3B82F6', color: '#FFFFFF', padding: '14px 22px', 
    borderRadius: '22px 22px 4px 22px', maxWidth: '80%', boxShadow: '0 4px 15px rgba(59, 130, 246, 0.2)' 
  },
  botBubble: { 
    backgroundColor: '#FFFFFF', color: '#1E293B', padding: '14px 22px', 
    borderRadius: '22px 22px 22px 4px', maxWidth: '80%', border: '1px solid #E2E8F0', boxShadow: '0 2px 5px rgba(0,0,0,0.02)' 
  },

  inputWrapper: { position: 'absolute', bottom: '30px', left: '10%', right: '10%' },
  suggestionRow: { display: 'flex', gap: '10px', marginBottom: '15px', justifyContent: 'center' },
  chip: { padding: '6px 14px', backgroundColor: 'white', border: '1px solid #E2E8F0', borderRadius: '100px', fontSize: '0.75rem', cursor: 'pointer', color: '#64748B' },
  
  inputBox: { 
    display: 'flex', backgroundColor: 'white', padding: '10px 10px 10px 25px', 
    borderRadius: '20px', border: '1px solid #E2E8F0', boxShadow: '0 10px 30px rgba(0,0,0,0.08)', alignItems: 'center' 
  },
  inputField: { flex: 1, border: 'none', outline: 'none', fontSize: '1rem', color: '#1E293B', backgroundColor: 'transparent' },
  sendIconBtn: { backgroundColor: '#3B82F6', border: 'none', borderRadius: '12px', width: '45px', height: '45px', cursor: 'pointer', fontSize: '1.2rem' },
  footerText: { textAlign: 'center', fontSize: '0.7rem', color: '#94A3B8', marginTop: '15px' }
};

export default App;