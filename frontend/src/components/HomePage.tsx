import React, { useState } from 'react';
import SimulationController from './SimulationController';
import styles from './HomePage.module.css';

interface PersonaResult {
    agent_name: string;
    description: string;
    reaction: 'like' | 'dislike' | 'comment' | 'repost' | 'ignore';
    confidence: number;
    reasoning: string;
    tags: string[];
    final_message: string;
}

interface HomePageProps {
    setResults: (results: PersonaResult[]) => void;
    isLoading: boolean;
    setIsLoading: (isLoading: boolean) => void;
}

const HomePage: React.FC<HomePageProps> = ({ setResults, isLoading, setIsLoading }) => {
    const [csvFile, setCsvFile] = useState<File | null>(null);

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files) {
            setCsvFile(event.target.files[0]);
        }
    };

    const handleAgentAction = async (action: 'recreate' | 'add') => {
        if (!csvFile) {
            alert('Please select a CSV file first.');
            return;
        }
        setIsLoading(true);
        const formData = new FormData();
        formData.append('file', csvFile);

        try {
            const response = await fetch(`http://localhost:8000/agents/${action}`, {
                method: 'POST',
                body: formData,
            });
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || `Failed to ${action} agents.`);
            }
            const data = await response.json();
            alert(data.message);
        } catch (err: any) {
            alert(err.message);
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1 className={styles.title}>Twinsphere AI</h1>
                <p className={styles.subtitle}>
                    Upload your post and instantly see how different AI audience personas will engage with it
                </p>
            </div>
            <div className={styles.card}>
                <SimulationController
                    setResults={setResults}
                    isLoading={isLoading}
                    setIsLoading={setIsLoading}
                />
                <hr className={styles.divider} />
                <h2 className={styles.cardTitle}>Manage Agents</h2>
                <div className={styles.formGroup}>
                    <label htmlFor="agent-csv-upload" className={styles.label}>Upload Persona CSV</label>
                    <input 
                        type="file" 
                        id="agent-csv-upload" 
                        accept=".csv" 
                        onChange={handleFileChange} 
                        className={styles.fileInput} 
                    />
                </div>
                <div className={styles.buttonGroup}>
                    <button onClick={() => handleAgentAction('recreate')} className={`${styles.button} ${styles.analyzeButton}`} disabled={!csvFile || isLoading}>
                        Replace Agents
                    </button>
                    <button onClick={() => handleAgentAction('add')} className={`${styles.button} ${styles.resetButton}`} disabled={!csvFile || isLoading}>
                        Add Agents
                    </button>
                </div>
            </div>
        </div>
    );
};

export default HomePage; 