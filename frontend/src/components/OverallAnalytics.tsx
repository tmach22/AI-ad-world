import React from 'react';
import styles from './OverallAnalytics.module.css';

interface PersonaResult {
  agent_name: string;
  reaction: 'like' | 'dislike' | 'comment' | 'repost' | 'ignore';
}

interface OverallAnalyticsProps {
  results: PersonaResult[];
}

const OverallAnalytics: React.FC<OverallAnalyticsProps> = ({ results }) => {
  if (results.length === 0) {
    return null;
  }

  const reactionCounts = results.reduce((acc, result) => {
    acc[result.reaction] = (acc[result.reaction] || 0) + 1;
    return acc;
  }, {} as Record<PersonaResult['reaction'], number>);

  return (
    <div className={styles.container}>
      <h2>Overall Analytics</h2>
      <div className={styles.summary}>
        {Object.entries(reactionCounts).map(([reaction, count]) => (
          <div key={reaction} className={styles.statCard}>
            <span className={styles.count}>{count}</span>
            <span className={styles.label}>{reaction}</span>
          </div>
        ))}
      </div>
      <p>Charts and more detailed analytics will be added here.</p>
    </div>
  );
};

export default OverallAnalytics; 