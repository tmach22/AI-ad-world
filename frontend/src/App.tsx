import React, { useState } from 'react';
import './App.css';
import SimulationController from './components/SimulationController';
import ResultsDisplay from './components/ResultsDisplay';

// Define the structure of a single persona result based on the backend
// This will be moved to a types file later
interface PersonaResult {
  agent_name: string;
  description: string;
  reaction: 'like' | 'dislike' | 'comment' | 'repost' | 'ignore';
  confidence: number;
  reasoning: string;
  tags: string[];
  final_message: string;
}

function App() {
  const [results, setResults] = useState<PersonaResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Persona Engagement Simulator</h1>
      </header>
      <main>
        <SimulationController 
          setResults={setResults}
          isLoading={isLoading}
          setIsLoading={setIsLoading}
        />
        
        {isLoading && <div className="loader"></div>}
        
        {!isLoading && results.length > 0 && (
          <ResultsDisplay results={results} />
        )}
        
        {!isLoading && results.length === 0 && (
          <div style={{ textAlign: 'center', marginTop: '2rem', color: '#888' }}>
            Upload a CSV and run a simulation to see results.
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
