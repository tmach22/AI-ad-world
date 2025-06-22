import React, { useState, useCallback } from 'react';
import styles from './SimulationController.module.css';

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
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [adCopy, setAdCopy] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setCsvFile(file);
      setError(null);
    }
  };

  const handleRecreateAgents = useCallback(async () => {
    if (!csvFile) {
      setError('Please select a CSV file first.');
      return;
    }
    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', csvFile);

    try {
      const response = await fetch('http://localhost:8000/agents/recreate', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to recreate agents.');
      }
      const data = await response.json();
      alert(data.message); // Simple feedback for now
    } catch (err: any) {
      setError(err.message);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [csvFile, setIsLoading]);

  const handleAddAgents = useCallback(async () => {
    if (!csvFile) {
      setError('Please select a CSV file first.');
      return;
    }
    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', csvFile);

    try {
      const response = await fetch('http://localhost:8000/agents/add', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to add agents.');
      }
      const data = await response.json();
      alert(data.message);
    } catch (err: any) {
      setError(err.message);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [csvFile, setIsLoading]);

  const handleRunSimulation = useCallback(async () => {
    if (!adCopy.trim()) {
      setError('Please enter ad copy to run the simulation.');
      return;
    }
    setIsLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await fetch(`http://localhost:8000/simulate?ad_copy=${encodeURIComponent(adCopy)}`, {
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
  }, [adCopy, setIsLoading, setResults]);

  return (
    <div className={styles.container}>
      {error && <p className={styles.error}>{error}</p>}
      
      <div className={styles.controlSection}>
        <h2>1. Upload Persona CSV</h2>
        <p>Define your audience by uploading a CSV file with persona descriptions.</p>
        <input type="file" accept=".csv" onChange={handleFileChange} />
        <div className={styles.buttonGroup}>
          <button onClick={handleRecreateAgents} disabled={!csvFile || isLoading}>
            Replace Agents
          </button>
          <button onClick={handleAddAgents} disabled={!csvFile || isLoading}>
            Add Agents
          </button>
        </div>
      </div>

      <div className={styles.controlSection}>
        <h2>2. Provide Ad Copy</h2>
        <p>Enter the ad copy you want to test against the personas.</p>
        <textarea
          className={styles.tweetTextarea}
          value={adCopy}
          onChange={(e) => setAdCopy(e.target.value)}
          placeholder="What's happening?"
          rows={5}
        />
        <button onClick={handleRunSimulation} disabled={!adCopy.trim() || isLoading}>
          Run Simulation
        </button>
      </div>
    </div>
  );
};

export default SimulationController; 