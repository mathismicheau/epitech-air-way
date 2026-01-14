import React from 'react';
import { styles } from '../data/styles';

const FeatureCard = ({ title, desc, img }) => (
  <div style={styles.featCard}>
    <div style={{...styles.featImg, backgroundImage: `url(${img})`}}></div>
    <div style={{padding: '25px'}}>
      <h3 style={{marginBottom: '10px'}}>{title}</h3>
      <p style={{color: '#64748B', fontSize: '0.95rem'}}>{desc}</p>
    </div>
  </div>
);

export default FeatureCard;