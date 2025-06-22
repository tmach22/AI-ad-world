import React from 'react';
import styles from './ResultsDisplay.module.css';

// This type will be moved to a central types file later
interface PersonaResult {
  agent_name: string;
  description: string;
  reaction: 'like' | 'dislike' | 'comment' | 'repost' | 'ignore';
  confidence: number;
  reasoning: string;
  tags: string[];
  final_message: string;
}

interface ResultsDisplayProps {
  results: PersonaResult[];
}

const ReactionIcon = ({ reaction }: { reaction: PersonaResult['reaction'] }) => {
  // Simple emoji mapping for now
  const iconMap = {
    like: '👍',
    dislike: '👎',
    comment: '💬',
    repost: '🔁',
    ignore: '🙈',
  };
  return <span className={styles.reactionIcon}>{iconMap[reaction]}</span>;
};

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results }) => {
  if (results.length === 0) {
    return null; // Don't render anything if there are no results
  }

  return (
    <div className={styles.resultsContainer}>
      <h2>Persona Engagement Results</h2>
      <div className={styles.grid}>
        {results.map((result) => (
          <div key={result.agent_name} className={styles.personaCard}>
            <div className={styles.cardHeader}>
              <h3>{result.agent_name}</h3>
              <span className={`${styles.reaction} ${styles[result.reaction]}`}>
                <ReactionIcon reaction={result.reaction} /> {result.reaction}
              </span>
            </div>
            <p className={styles.description}>{result.description}</p>
            
            <div className={styles.confidenceSection}>
              <label>Confidence: {result.confidence}%</label>
              <div className={styles.progressBar}>
                <div style={{ width: `${result.confidence}%` }}></div>
              </div>
            </div>

            <div className={styles.reasoningSection}>
              <h4>Reasoning:</h4>
              <p>{result.reasoning}</p>
            </div>

            <div className={styles.tagsSection}>
              {result.tags.map((tag) => (
                <span key={tag} className={styles.tag}>{tag}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResultsDisplay; 