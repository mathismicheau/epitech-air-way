import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import ChatbotPage from './pages/ChatbotPage';

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