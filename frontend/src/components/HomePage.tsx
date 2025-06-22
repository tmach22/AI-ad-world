import React from 'react';
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
    return (
        <div>
            <SimulationController
                setResults={setResults}
                isLoading={isLoading}
                setIsLoading={setIsLoading}
            />
            <div className={styles.placeholder}>
                <p>Run a simulation to see the results.</p>
            </div>
        </div>
    );
};

export default HomePage; 