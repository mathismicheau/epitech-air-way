export const translations = {
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