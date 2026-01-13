import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';

// --- 1. DICTIONNAIRE DE TRADUCTION ---
const translations = {
  en: {
    heroTitle: "Wingman",
    heroSubtitle: "Your AI co-pilot for the perfect trip. Now finding the best Airbnbs and local activities for you.",
    launchBtn: "OPEN TERMINAL 🚀",
    learnMore: "Learn more ↓",
    howItWorks: "How does Wingman work?",
    howItWorksSub: "Your intelligent co-pilot simplifies every step of your journey.",
    featAirbnbTitle: "Airbnb Stays",
    featAirbnbDesc: "Wingman analyzes thousands of listings to suggest the ideal Airbnb based on your budget and style.",
    featAirbnbImg: "https://images.pexels.com/photos/276724/pexels-photo-276724.jpeg?auto=compress&cs=tinysrgb&w=800",
    featActTitle: "Local Activities",
    featActDesc: "Don't just visit, live the city. Our IA finds hidden gems, secret restaurants, and unusual activities.",
    featActImg: "https://images.pexels.com/photos/2108845/pexels-photo-2108845.jpeg?auto=compress&cs=tinysrgb&w=800",
    featFlightTitle: "Flight Support",
    featFlightDesc: "Integrated with Epitech Airways, Wingman monitors your flights and manages your boarding passes.",
    featFlightImg: "https://images.pexels.com/photos/46148/aircraft-jet-landing-cloud-46148.jpeg?auto=compress&cs=tinysrgb&w=800",
    ctaTitle: "Ready for takeoff?",
    ctaDesc: "Join thousands of travelers who trust Wingman for their adventures.",
    ctaBtn: "START EXPERIENCE 🚀",
    welcomeMsg: "Welcome aboard! I'm Wingman. I can find Airbnbs, activities, or help with your flight. Where to?",
    quickActionAirbnb: "Find Airbnbs 🏠",
    quickActionActivities: "Things to do 🎡",
    newFlight: "+ NEW FLIGHT",
    flightLogs: "FLIGHT LOGS",
    noLogs: "No recent logs",
    quit: "← Leave Terminal",
    placeholder: "Ask about flights, Airbnbs or activities...",
    boardingPass: "BOARDING PASS",
    economy: "ECONOMY CLASS",
    gate: "GATE: 42"
  },
  fr: {
    heroTitle: "Wingman",
    heroSubtitle: "Votre co-pilote IA pour un voyage parfait. Trouvez les meilleurs Airbnbs et activités locales.",
    launchBtn: "OUVRIR LE TERMINAL 🚀",
    learnMore: "En savoir plus ↓",
    howItWorks: "Comment fonctionne Wingman ?",
    howItWorksSub: "Votre copilote intelligent simplifie chaque étape de votre voyage.",
    featAirbnbTitle: "Hébergements Airbnb",
    featAirbnbDesc: "Wingman suggère l'Airbnb idéal selon votre budget et vos envies.",
    featAirbnbImg: "https://images.pexels.com/photos/276724/pexels-photo-276724.jpeg?auto=compress&cs=tinysrgb&w=800",
    featActTitle: "Activités Locales",
    featActDesc: "Notre IA déniche des perles rares et des lieux insolites.",
    featActImg: "https://images.pexels.com/photos/2108845/pexels-photo-2108845.jpeg?auto=compress&cs=tinysrgb&w=800",
    featFlightTitle: "Gestion de Vol",
    featFlightDesc: "Wingman surveille vos vols et gère vos cartes d'embarquement.",
    featFlightImg: "https://images.pexels.com/photos/46148/aircraft-jet-landing-cloud-46148.jpeg?auto=compress&cs=tinysrgb&w=800",
    ctaTitle: "Prêt pour le décollage ?",
    ctaDesc: "Rejoignez des milliers de voyageurs qui font confiance à Wingman.",
    ctaBtn: "DÉMARRER L'EXPÉRIENCE 🚀",
    welcomeMsg: "Bienvenue à bord ! Je suis Wingman. Je peux trouver des Airbnbs ou gérer votre vol. On va où ?",
    quickActionAirbnb: "Trouver un Airbnb 🏠",
    quickActionActivities: "Activités à faire 🎡",
    newFlight: "+ NOUVEAU VOL",
    flightLogs: "LOGS DE VOL",
    noLogs: "Aucun log récent",
    quit: "← Quitter le terminal",
    placeholder: "Vols, Airbnbs ou activités...",
    boardingPass: "CARTE D'EMBARQUEMENT",
    economy: "CLASSE ÉCONOMIE",
    gate: "PORTE: 42"
  }
};

const LanguageSwitcher = ({ lang, setLang }) => (
  <div style={styles.langSwitcher}>
    <span style={{...styles.langItem, fontWeight: lang === 'en' ? 'bold' : 'normal', color: lang === 'en' ? '#3B82F6' : '#94A3B8'}} onClick={() => setLang('en')}>EN</span>
    <span style={{color: 'white', opacity: 0.5}}> | </span>
    <span style={{...styles.langItem, fontWeight: lang === 'fr' ? 'bold' : 'normal', color: lang === 'fr' ? '#3B82F6' : '#94A3B8'}} onClick={() => setLang('fr')}>FR</span>
  </div>
);

// --- 2. LANDING PAGE ---
const LandingPage = ({ lang, setLang }) => {
  const navigate = useNavigate();
  const t = translations[lang];

  return (
    <div style={styles.landingWrapper}>
      <LanguageSwitcher lang={lang} setLang={setLang} />
      <section style={styles.heroFull}>
        <img src="/LOGO-wingman.png" alt="Wingman" style={styles.largeLogo} className="radiating-logo" />
        <h1 style={styles.heroTitle}>{t.heroTitle}</h1>
        <p style={styles.heroSubtitle}>{t.heroSubtitle}</p>
        <div style={styles.heroBtnGroup}>
          <button style={styles.launchBtn} onClick={() => navigate('/chat')}>{t.launchBtn}</button>
          <a href="#details" style={styles.learnMoreLink}>{t.learnMore}</a>
        </div>
      </section>

      <section id="details" style={styles.whiteSection}>
        <h2 style={styles.sectionTitle}>{t.howItWorks}</h2>
        <p style={styles.sectionSub}>{t.howItWorksSub}</p>
        <div style={styles.infoGrid}>
          {[
            { title: t.featAirbnbTitle, desc: t.featAirbnbDesc, img: t.featAirbnbImg },
            { title: t.featActTitle, desc: t.featActDesc, img: t.featActImg },
            { title: t.featFlightTitle, desc: t.featFlightDesc, img: t.featFlightImg }
          ].map((feat, i) => (
            <div key={i} style={styles.featCard}>
              <div style={{...styles.featImg, backgroundImage: `url(${feat.img})`}}></div>
              <div style={{padding: '25px'}}>
                <h3 style={{marginBottom: '10px'}}>{feat.title}</h3>
                <p style={{color: '#64748B', fontSize: '0.95rem'}}>{feat.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section style={styles.ctaSection}>
        <div style={styles.ctaCard}>
          <h2>{t.ctaTitle}</h2>
          <p>{t.ctaDesc}</p>
          <button style={styles.launchBtn} onClick={() => navigate('/chat')}>{t.ctaBtn}</button>
        </div>
      </section>
      <footer style={styles.landingFooter}>© 2026 Epitech Airways - Wingman Project</footer>
    </div>
  );
};

// --- 3. CHATBOT PAGE (AVEC PERSISTANCE LOCALSTORAGE) ---
const ChatbotPage = ({ lang, setLang }) => {
  const navigate = useNavigate();
  const t = translations[lang];
  
  // 1. Charger les messages depuis le localStorage au démarrage
  const [chats, setChats] = useState(() => {
    const saved = localStorage.getItem('wingman_chats');
    return saved ? JSON.parse(saved) : [{ id: Date.now(), title: "Current Flight", messages: [{ text: translations[lang].welcomeMsg, sender: "bot" }] }];
  });
  
  const [currentChatIndex, setCurrentChatIndex] = useState(0);
  const [userInput, setUserInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // 2. Sauvegarder dans le localStorage à chaque changement de 'chats'
  useEffect(() => {
    localStorage.setItem('wingman_chats', JSON.stringify(chats));
  }, [chats]);

  const currentMessages = chats[currentChatIndex]?.messages || [];

  const startNewChat = () => {
    const newChat = {
      id: Date.now(),
      title: "New Mission",
      messages: [{ text: t.welcomeMsg, sender: "bot" }]
    };
    setChats([newChat, ...chats]);
    setCurrentChatIndex(0);
  };

  const sendMessage = async (manualText = null) => {
    const textToSend = manualText || userInput;
    if (textToSend.trim() === "" || isLoading) return;

    const updatedChats = [...chats];
    const userMsg = { text: textToSend, sender: "user" };
    updatedChats[currentChatIndex].messages.push(userMsg);
    
    // Update title on first message
    if (updatedChats[currentChatIndex].messages.length === 2) {
        updatedChats[currentChatIndex].title = textToSend.substring(0, 20);
    }

    setChats(updatedChats);
    setUserInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: textToSend, language: lang }),
      });
      const data = await response.json();
      
      const replyChats = [...updatedChats];
      replyChats[currentChatIndex].messages.push({ text: data.reply, sender: "bot" });
      setChats(replyChats);
    } catch (error) {
      const errorChats = [...updatedChats];
      errorChats[currentChatIndex].messages.push({ text: "⚠️ SYSTEM ERROR.", sender: "bot" });
      setChats(errorChats);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.chatContainer}>
      <LanguageSwitcher lang={lang} setLang={setLang} />
      
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
                    backgroundColor: currentChatIndex === idx ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                    color: currentChatIndex === idx ? '#3B82F6' : '#1E293B',
                    border: currentChatIndex === idx ? '1px solid rgba(59, 130, 246, 0.2)' : '1px solid transparent'
                  }}
                >
                  ✈️ {chat.title}
                </div>
              ))}
          </div>
        </div>
        
        <button style={styles.backBtn} onClick={() => navigate('/')}>{t.quit}</button>
      </div>

      <div style={styles.chatMain}>
        <div style={styles.chatScroll}>
          {currentMessages.map((msg, i) => (
            <div key={i} style={msg.sender === "user" ? styles.userWrap : styles.botWrap}>
              <div style={msg.sender === "user" ? styles.userBub : styles.botBub}>{msg.text}</div>
            </div>
          ))}

          {isLoading && (
            <div style={styles.botWrap}>
              <div style={styles.loadingBubble}>
                <div className="dot"></div>
                <div className="dot"></div>
                <div className="dot"></div>
              </div>
            </div>
          )}

          {!isLoading && (
            <div style={styles.quickActions}>
              <button style={styles.actBtn} onClick={() => sendMessage(t.quickActionAirbnb)}>{t.quickActionAirbnb}</button>
              <button style={styles.actBtn} onClick={() => sendMessage(t.quickActionActivities)}>{t.quickActionActivities}</button>
            </div>
          )}
        </div>

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
      </div>
      <style>{`
        @keyframes pulseGlow { 0% { filter: drop-shadow(0 0 5px rgba(59, 130, 246, 0.4)); } 50% { filter: drop-shadow(0 0 15px rgba(59, 130, 246, 0.8)); } 100% { filter: drop-shadow(0 0 5px rgba(59, 130, 246, 0.4)); } }
        .radiating-logo { animation: pulseGlow 3s infinite ease-in-out; }
        @keyframes bounce { 0%, 100% { transform: translateY(0); opacity: 0.3; } 50% { transform: translateY(-5px); opacity: 1; } }
        .dot { width: 8px; height: 8px; background: #3B82F6; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out; }
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }
        .send-button-hover:hover { transform: scale(1.1); filter: brightness(1.2); transition: 0.2s; }
      `}</style>
    </div>
  );
};

export default function App() {
  const [lang, setLang] = useState('en');
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage lang={lang} setLang={setLang} />} />
        <Route path="/chat" element={<ChatbotPage lang={lang} setLang={setLang} />} />
      </Routes>
    </Router>
  );
}

// --- 4. STYLES ---
const styles = {
  landingWrapper: { width: '100vw', backgroundColor: '#0F172A', color: 'white', fontFamily: 'Inter, sans-serif', overflowX: 'hidden' },
  heroFull: { height: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', background: 'radial-gradient(circle at center, #1E293B 0%, #0F172A 100%)', textAlign: 'center' },
  heroTitle: { fontSize: '4.5rem', fontWeight: '900' },
  heroSubtitle: { fontSize: '1.2rem', color: '#94A3B8', maxWidth: '600px', marginBottom: '40px' },
  largeLogo: { width: '150px', marginBottom: '20px' },
  launchBtn: { background: '#3B82F6', color: 'white', padding: '18px 45px', borderRadius: '50px', border: 'none', fontWeight: 'bold', cursor: 'pointer' },
  heroBtnGroup: { display: 'flex', flexDirection: 'column', gap: '15px', alignItems: 'center' },
  learnMoreLink: { color: '#94A3B8', textDecoration: 'none' },
  whiteSection: { padding: '100px 10%', backgroundColor: 'white', color: '#0F172A', textAlign: 'center' },
  sectionTitle: { fontSize: '2.5rem', fontWeight: '800' },
  sectionSub: { color: '#64748B', marginBottom: '50px' },
  infoGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '30px' },
  featCard: { borderRadius: '20px', backgroundColor: '#F8FAFC', border: '1px solid #E2E8F0', overflow: 'hidden', textAlign: 'left' },
  featImg: { width: '100%', height: '200px', backgroundSize: 'cover', backgroundPosition: 'center' },
  ctaSection: { padding: '80px 10%', backgroundColor: '#F8FAFC' },
  ctaCard: { background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)', padding: '60px', borderRadius: '30px', textAlign: 'center' },
  landingFooter: { padding: '40px', textAlign: 'center', color: '#94A3B8', background: 'white' },
  langSwitcher: { position: 'fixed', top: '20px', right: '30px', zIndex: 1000, background: 'rgba(0,0,0,0.2)', padding: '10px 20px', borderRadius: '30px', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.1)', color: 'white' },
  langItem: { cursor: 'pointer', margin: '0 5px' },

  chatContainer: { display: 'flex', height: '100vh', width: '100vw', backgroundImage: "linear-gradient(rgba(248, 250, 252, 0.8), rgba(248, 250, 252, 0.8)), url('/hero-bg.png')", backgroundSize: 'cover', backgroundPosition: 'center', fontFamily: 'Inter, sans-serif' },
  sidebar: { width: '300px', backgroundColor: 'rgba(255,255,255,0.9)', backdropFilter: 'blur(12px)', borderRight: '1px solid #E2E8F0', padding: '30px', display: 'flex', flexDirection: 'column' },
  sidebarLogo: { width: '140px' },
  logoSection: { display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '40px', cursor: 'pointer' },
  logoText: { fontSize: '1.8rem', fontWeight: '900', color: '#0F172A' },
  newChatBtn: { backgroundColor: '#0F172A', color: 'white', padding: '16px', borderRadius: '12px', border: 'none', fontWeight: 'bold', cursor: 'pointer' },
  historyBox: { flex: 1, marginTop: '40px', overflowY: 'auto' },
  historyLabel: { fontSize: '0.75rem', color: '#94A3B8', fontWeight: 'bold', textAlign: 'center', display: 'block', marginBottom: '15px' },
  logsList: { display: 'flex', flexDirection: 'column', gap: '8px' },
  logItem: { padding: '12px', borderRadius: '10px', fontSize: '0.85rem', cursor: 'pointer', transition: '0.2s', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' },
  backBtn: { background: 'none', border: 'none', color: '#94A3B8', cursor: 'pointer', borderTop: '1px solid #E2E8F0', paddingTop: '20px', fontWeight: '600' },
  chatMain: { flex: 1, display: 'flex', flexDirection: 'column', position: 'relative' },
  chatScroll: { flex: 1, overflowY: 'auto', padding: '40px 12% 200px 12%' },
  userWrap: { display: 'flex', justifyContent: 'flex-end', marginBottom: '20px' },
  botWrap: { display: 'flex', justifyContent: 'flex-start', marginBottom: '20px' },
  userBub: { backgroundColor: '#3B82F6', color: 'white', padding: '14px 22px', borderRadius: '22px 22px 4px 22px', maxWidth: '75%' },
  botBub: { backgroundColor: 'white', color: '#1E293B', padding: '14px 22px', borderRadius: '22px 22px 22px 4px', maxWidth: '75%', border: '1px solid #E2E8F0' },
  loadingBubble: { background: 'white', border: '1px solid #E2E8F0', padding: '15px 25px', borderRadius: '22px 22px 22px 4px', display: 'flex', gap: '5px', alignItems: 'center' },
  quickActions: { display: 'flex', gap: '10px', marginBottom: '20px' },
  actBtn: { background: 'white', border: '1px solid #3B82F6', color: '#3B82F6', padding: '8px 16px', borderRadius: '20px', cursor: 'pointer', fontWeight: '600' },
  inputArea: { position: 'absolute', bottom: '30px', left: '10%', right: '10%' },
  ticket: { display: 'flex', height: '140px', backgroundColor: 'white', borderRadius: '15px', boxShadow: '0 15px 35px rgba(0,0,0,0.1)', overflow: 'hidden', border: '1px solid #E2E8F0' },
  ticketLeft: { flex: 3, padding: '20px 30px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' },
  ticketTop: { display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', fontWeight: 'bold', color: '#94A3B8' },
  ticketBottom: { display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#94A3B8' },
  ticketInput: { border: 'none', outline: 'none', fontSize: '1.4rem', fontFamily: '"Courier New", Courier, monospace', textTransform: 'uppercase', color: '#0F172A', backgroundColor: 'white', width: '100%', marginTop: '10px' },
  dash: { borderLeft: '2px dashed #E2E8F0', margin: '15px 0' },
  ticketRight: { flex: 1, backgroundColor: '#F8FAFC', padding: '15px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'space-between' },
  stubLabel: { fontSize: '0.75rem', fontWeight: 'bold', color: '#94A3B8' },
  sendBtn: { width: '52px', height: '52px', borderRadius: '50%', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'all 0.2s' },
  stubSerial: { fontSize: '0.6rem', color: '#CBD5E1', fontWeight: 'bold' }
};