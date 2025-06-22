import React, { useState } from 'react';
import './App.css';
import HomePage from './components/HomePage';
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
      <HomePage 
        setResults={setResults}
        isLoading={isLoading}
        setIsLoading={setIsLoading}
      />
      <main>
        {isLoading && <div className="loader"></div>}
        
        {!isLoading && results.length > 0 && (
          <ResultsDisplay results={results} />
        )}
      </main>
    </div>
  );
}

export default App;
