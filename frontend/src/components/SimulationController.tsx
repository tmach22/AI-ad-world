import React, { useState, useCallback } from 'react';
import styles from './HomePage.module.css'; // Using HomePage styles

// Define the structure of a single persona result based on the backend
interface PersonaResult {
  agent_name: string;
  description: string;
  reaction: 'like' | 'dislike' | 'comment' | 'repost' | 'ignore';
  confidence: number;
  reasoning: string;
  tags: string[];
  final_message: string;
}

interface SimulationControllerProps {
  setResults: (results: PersonaResult[]) => void;
  isLoading: boolean;
  setIsLoading: (isLoading: boolean) => void;
}

const SimulationController: React.FC<SimulationControllerProps> = ({ setResults, isLoading, setIsLoading }) => {
  const [content, setContent] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleRunSimulation = useCallback(async () => {
    if (!content.trim()) {
      setError('Please enter some content to analyze.');
      return;
    }
    setIsLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await fetch(`http://localhost:8000/simulate?ad_copy=${encodeURIComponent(content)}`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to run simulation.');
      }
      const results: PersonaResult[] = await response.json();
      setResults(results);
    } catch (err: any) {
      setError(err.message);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [content, setIsLoading, setResults]);
  
  const handleReset = () => {
      setContent('');
      setResults([]);
      setError(null);
  }

  return (
    <>
      {error && <p className={styles.error}>{error}</p>}
      <h2 className={styles.cardTitle}>Upload Your Post</h2>
      <div className={styles.formGroup}>
          <label htmlFor="content" className={styles.label}>Content</label>
          <textarea 
            id="content" 
            className={styles.textarea} 
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="What's happening?"
          />
      </div>
      <div className={styles.buttonGroup}>
          <button onClick={handleRunSimulation} className={`${styles.button} ${styles.analyzeButton}`} disabled={isLoading}>
            {isLoading ? 'Analyzing...' : 'Analyze Engagement'}
          </button>
          <button onClick={handleReset} className={`${styles.button} ${styles.resetButton}`} disabled={isLoading}>
            Reset
          </button>
      </div>
    </>
  );
};

export default SimulationController; 