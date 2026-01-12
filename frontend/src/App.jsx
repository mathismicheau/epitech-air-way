import React, { useState } from 'react';

function App() {
  // --- 1. STATE ---
  const initialGreeting = { 
    text: "Welcome aboard! I'm Wingman, your co-pilot. Where is our next flight path heading?", 
    sender: "bot" 
  };
  
  const [messages, setMessages] = useState([initialGreeting]);
  const [userInput, setUserInput] = useState("");
  const [history, setHistory] = useState([]);
  const [isHovered, setIsHovered] = useState(false);
  const [isLoading, setIsLoading] = useState(false); // NEW: Loading state

  // --- 2. LOGIC ---
  const startNewChat = () => {
    if (messages.length > 1) {
      const firstUserMsg = messages.find(m => m.sender === "user");
      const title = firstUserMsg ? firstUserMsg.text : "Previous Flight";
      setHistory((prev) => [{ title: title, chats: [...messages] }, ...prev]);
    }
    setMessages([initialGreeting]);
    setIsLoading(false);
  };

  const loadOldChat = (savedTrip) => {
    setMessages(savedTrip.chats);
    setIsLoading(false);
  };

  const sendMessage = async () => {
    if (userInput.trim() === "" || isLoading) return;

    const newMsg = { text: userInput, sender: "user" };
    setMessages((prev) => [...prev, newMsg]);
    setUserInput("");
    setIsLoading(true); // Start animation

    try {
      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: newMsg.text }),
      });
      const data = await response.json();
      setMessages((prev) => [...prev, { text: data.reply, sender: "bot" }]);
    } catch (error) {
      setMessages((prev) => [...prev, { text: "⚠️ SYSTEM: Check connection.", sender: "bot" }]);
    } finally {
      setIsLoading(false); // Stop animation
    }
  };

  // --- 3. UI ---
  return (
    <div style={styles.container}>
      {/* SIDEBAR */}
      <div style={styles.sidebar}>
        <div style={styles.logoSection}>
          <img src="/LOGO-wingman.png" alt="Logo" style={styles.logoImg} />
          <h2 style={styles.logoText}>Wingman</h2>
        </div>
        <button style={styles.newChatBtn} onClick={startNewChat}>+ NEW FLIGHT</button>
        <div style={styles.historyContainer}>
          <label style={styles.historyLabel}>FLIGHT LOGS</label>
          <div style={styles.historyList}>
            {history.map((item, index) => (
              <div key={index} style={styles.historyItem} onClick={() => loadOldChat(item)}>
                <span>✈️</span> {item.title.substring(0, 20)}...
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* MAIN CHAT */}
      <div style={styles.mainArea}>
        <div style={styles.chatWindow}>
          {messages.map((msg, index) => (
            <div key={index} style={msg.sender === "user" ? styles.userWrapper : styles.botWrapper}>
              <div style={msg.sender === "user" ? styles.userBubble : styles.botBubble}>{msg.text}</div>
            </div>
          ))}

          {/* LOADING ANIMATION BUBBLE */}
          {isLoading && (
            <div style={styles.botWrapper}>
              <div style={styles.loadingBubble}>
                <div className="dot" style={styles.dot}></div>
                <div className="dot" style={{...styles.dot, animationDelay: '0.2s'}}></div>
                <div className="dot" style={{...styles.dot, animationDelay: '0.4s'}}></div>
              </div>
            </div>
          )}
        </div>
        
        {/* INPUT AREA */}
        <div style={styles.inputWrapper}>
          <div style={styles.boardingPass}>
            <div style={styles.ticketMain}>
              <div style={styles.ticketHeader}><span></span><span>BOARDING PASS</span></div>
              <input 
                style={styles.inputField}
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Search flights or ask a question..." 
                disabled={isLoading}
              />
              <div style={styles.ticketFooter}><span></span><span></span></div>
            </div>
            <div style={styles.perforation}></div>
            <div style={styles.ticketStub}>
              <div style={styles.stubLabel}>SEND</div>
              <button 
                style={{
                  ...styles.geminiBtn,
                  backgroundColor: userInput.trim() && !isLoading ? '#0F172A' : '#F1F5F9',
                  transform: isHovered && userInput.trim() ? 'translateY(-2px)' : 'translateY(0)',
                }}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
                onClick={sendMessage}
                disabled={!userInput.trim() || isLoading}
              >
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                  <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill={userInput.trim() && !isLoading ? "white" : "#CBD5E1"}/>
                </svg>
              </button>
              <div style={styles.stubSerial}></div>
            </div>
          </div>
        </div>
      </div>

      {/* INLINE ANIMATION STYLES */}
      <style>{`
        @keyframes bounce {
          0%, 100% { transform: translateY(0); opacity: 0.3; }
          50% { transform: translateY(-5px); opacity: 1; }
        }
        .dot {
          animation: bounce 1.4s infinite ease-in-out;
        }
      `}</style>
    </div>
  );
}

// --- STYLES ---
const styles = {
  // ... (previous styles remain the same)
  container: { display: 'flex', height: '100vh', width: '100vw', backgroundImage: "linear-gradient(rgba(248, 250, 252, 0.7), rgba(248, 250, 252, 0.7)), url('/hero-bg.png')", backgroundSize: 'cover', backgroundPosition: 'center', fontFamily: 'Inter, sans-serif', overflow: 'hidden' },
  sidebar: { width: '300px', backgroundColor: 'rgba(255, 255, 255, 0.9)', backdropFilter: 'blur(12px)', borderRight: '1px solid #E2E8F0', padding: '32px 24px', display: 'flex', flexDirection: 'column' },
  logoSection: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px', marginBottom: '40px' },
  logoImg: { width: '140px', height: 'auto' },
  logoText: { fontSize: '1.8rem', fontWeight: '900', color: '#0F172A' },
  newChatBtn: { backgroundColor: '#0F172A', color: '#FFFFFF', border: 'none', padding: '16px', borderRadius: '12px', fontWeight: '700', cursor: 'pointer' },
  historyContainer: { marginTop: '40px', flex: 1, overflowY: 'auto' },
  historyLabel: { fontSize: '0.75rem', fontWeight: '700', color: '#94A3B8', textAlign: 'center', display: 'block' },
  historyItem: { padding: '12px 0', fontSize: '0.85rem', color: '#475569', borderBottom: '1px solid #F1F5F9', cursor: 'pointer', textAlign: 'center' },
  mainArea: { flex: 1, display: 'flex', flexDirection: 'column', position: 'relative' },
  chatWindow: { flex: 1, overflowY: 'auto', padding: '40px 12% 220px 12%' },
  userWrapper: { display: 'flex', justifyContent: 'flex-end', marginBottom: '22px' },
  botWrapper: { display: 'flex', justifyContent: 'flex-start', marginBottom: '22px' },
  userBubble: { backgroundColor: '#3B82F6', color: '#FFFFFF', padding: '14px 22px', borderRadius: '22px 22px 4px 22px', maxWidth: '75%' },
  botBubble: { backgroundColor: 'white', color: '#1E293B', padding: '14px 22px', borderRadius: '22px 22px 22px 4px', maxWidth: '75%', border: '1px solid #E2E8F0' },
  
  // LOADING BUBBLE STYLE
  loadingBubble: { backgroundColor: 'white', padding: '18px 25px', borderRadius: '22px 22px 22px 4px', border: '1px solid #E2E8F0', display: 'flex', gap: '5px', alignItems: 'center' },
  dot: { width: '8px', height: '8px', backgroundColor: '#3B82F6', borderRadius: '50%' },

  inputWrapper: { position: 'absolute', bottom: '30px', left: '10%', right: '10%', display: 'flex', flexDirection: 'column', alignItems: 'center' },
  boardingPass: { display: 'flex', width: '100%', maxWidth: '800px', height: '140px', backgroundColor: 'white', borderRadius: '15px', boxShadow: '0 15px 35px rgba(0,0,0,0.12)', overflow: 'hidden', border: '1px solid #E2E8F0' },
  ticketMain: { flex: 3, padding: '20px 30px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' },
  ticketHeader: { display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', fontWeight: 'bold', color: '#94A3B8' },
  ticketFooter: { display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#94A3B8' },
  inputField: { border: 'none', outline: 'none', fontSize: '1.4rem', fontFamily: '"Courier New", Courier, monospace', textTransform: 'uppercase', color: '#0F172A', backgroundColor: 'transparent' },
  perforation: { borderLeft: '2px dashed #E2E8F0', margin: '15px 0' },
  ticketStub: { flex: 1, backgroundColor: '#F8FAFC', padding: '15px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'space-between' },
  stubLabel: { fontSize: '0.75rem', fontWeight: 'bold', color: '#94A3B8' },
  stubSerial: { fontSize: '0.65rem', color: '#CBD5E1' },
  geminiBtn: { width: '52px', height: '52px', borderRadius: '50%', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'all 0.2s' }
};

export default App;