import React from 'react';
import { styles } from '../data/styles';

const LanguageSwitcher = ({ lang, setLang }) => (
  <div style={styles.langSwitcher}>
    <span 
      style={{...styles.langItem, fontWeight: lang === 'en' ? 'bold' : 'normal', color: lang === 'en' ? '#3B82F6' : '#94A3B8'}} 
      onClick={() => setLang('en')}
    >EN</span>
    <span style={{color: 'white', opacity: 0.5}}> | </span>
    <span 
      style={{...styles.langItem, fontWeight: lang === 'fr' ? 'bold' : 'normal', color: lang === 'fr' ? '#3B82F6' : '#94A3B8'}} 
      onClick={() => setLang('fr')}
    >FR</span>
  </div>
);

export default LanguageSwitcher;