import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import TicketInput from '../components/TicketInput';
import MessageList from '../components/MessageList';
import LanguageSwitcher from '../components/LanguageSwitcher';
import { translations } from '../data/translations';
import { styles } from '../data/styles';

const ChatbotPage = ({ lang, setLang }) => {
  
  const navigate = useNavigate();
  const t = translations[lang];
  
  const [chats, setChats] = useState(() => {
    const saved = localStorage.getItem('wingman_chats');
    return saved ? JSON.parse(saved) : [{ id: Date.now(), title: "Current Flight", messages: [{ text: translations[lang].welcomeMsg, sender: "bot" }] }];
  });
  
  const [currentChatIndex, setCurrentChatIndex] = useState(0);
  const [userInput, setUserInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);  // <- AJOUTER ICI

  useEffect(() => {
    localStorage.setItem('wingman_chats', JSON.stringify(chats));
  }, [chats]);

  const startNewChat = () => {
    setChats([{ id: Date.now(), title: "New Mission", messages: [{ text: t.welcomeMsg, sender: "bot" }] }, ...chats]);
    setCurrentChatIndex(0);
    setSessionId(null);  // <- Reset la session pour un nouveau chat
  };

  const deleteChat = (chatId) => {
    if (chats.length === 1) {
      setChats([{ id: Date.now(), title: "Current Flight", messages: [{ text: t.welcomeMsg, sender: "bot" }] }]);
      setCurrentChatIndex(0);
      setSessionId(null);  // <- Reset la session
      return;
    }

    const indexToRemove = chats.findIndex(chat => chat.id === chatId);
    const updatedChats = chats.filter(chat => chat.id !== chatId);
    setChats(updatedChats);

    if (currentChatIndex === indexToRemove) {
      setCurrentChatIndex(0);
      setSessionId(null);  // <- Reset la session
    } else if (currentChatIndex > indexToRemove) {
      setCurrentChatIndex(prev => prev - 1);
    }
  };

  const sendMessage = async (manualText = null) => {
    const textToSend = manualText || userInput;
    if (textToSend.trim() === "" || isLoading) return;

    const updatedChats = [...chats];
    updatedChats[currentChatIndex].messages.push({ text: textToSend, sender: "user" });
    if (updatedChats[currentChatIndex].messages.length === 2) updatedChats[currentChatIndex].title = textToSend.substring(0, 20);
    
    setChats(updatedChats);
    setUserInput("");
    setIsLoading(true);

    try {
      console.log("Envoi avec session_id:", sessionId);  // <- Debug

      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: textToSend, 
          language: lang,
          session_id: sessionId  // <- ENVOYER LE SESSION_ID
        }),
      });
      
      const data = await response.json();
      console.log("Réponse backend:", data);  // <- Debug

      // Sauvegarder le session_id retourné
      if (data.session_id) {
        setSessionId(data.session_id);
        console.log("Session_id sauvegardé:", data.session_id);  // <- Debug
      }

      const finalChats = [...chats];
      finalChats[currentChatIndex].messages.push({ text: data.answer, sender: "bot" });
      setChats(finalChats);
    } catch (error) {
      const errorChats = [...chats];
      errorChats[currentChatIndex].messages.push({ text: "⚠️ ERROR", sender: "bot" });
      setChats(errorChats);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.chatContainer}>
      <LanguageSwitcher lang={lang} setLang={setLang} />
      <Sidebar 
        chats={chats} 
        currentChatIndex={currentChatIndex} 
        setCurrentChatIndex={setCurrentChatIndex} 
        startNewChat={startNewChat} 
        deleteChat={deleteChat} 
        navigate={navigate} 
        t={t} 
      />
      <div style={styles.chatMain}>
        <div style={styles.chatScroll}>
          <MessageList messages={chats[currentChatIndex].messages} isLoading={isLoading} />
          {!isLoading && (
            <div style={styles.quickActions}>
              <button style={styles.actBtn} onClick={() => sendMessage(t.quickActionAirbnb)}>{t.quickActionAirbnb}</button>
              <button style={styles.actBtn} onClick={() => sendMessage(t.quickActionActivities)}>{t.quickActionActivities}</button>
            </div>
          )}
        </div>
        <TicketInput userInput={userInput} setUserInput={setUserInput} sendMessage={sendMessage} t={t} />
      </div>
      <style>{`.radiating-logo { animation: pulseGlow 3s infinite ease-in-out; } @keyframes pulseGlow { 0% { filter: drop-shadow(0 0 5px rgba(59,130,246,0.4)); } 50% { filter: drop-shadow(0 0 15px rgba(59,130,246,0.8)); } 100% { filter: drop-shadow(0 0 5px rgba(59,130,246,0.4)); } } .dot { width: 8px; height: 8px; background: #3B82F6; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out; } .dot:nth-child(2) { animation-delay: 0.2s; } .dot:nth-child(3) { animation-delay: 0.4s; } @keyframes bounce { 0%, 100% { transform: translateY(0); opacity: 0.3; } 50% { transform: translateY(-5px); opacity: 1; } } .send-button-hover:hover { transform: scale(1.1); filter: brightness(1.2); transition: 0.2s; }`}</style>
    </div>
  );
};

export default ChatbotPage;