import React from 'react';
import { useNavigate } from 'react-router-dom';
import LanguageSwitcher from '../components/LanguageSwitcher';
import FeatureCard from '../components/FeatureCard';
import { translations } from '../data/translations';
import { styles } from '../data/styles';

const LandingPage = ({ lang, setLang }) => {
  const navigate = useNavigate();
  const t = translations[lang];

  const features = [
    { title: t.featAirbnbTitle, desc: t.featAirbnbDesc, img: t.featAirbnbImg },
    { title: t.featActTitle, desc: t.featActDesc, img: t.featActImg },
    { title: t.featFlightTitle, desc: t.featFlightDesc, img: t.featFlightImg }
  ];

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
          {features.map((feat, i) => <FeatureCard key={i} {...feat} />)}
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

export default LandingPage;