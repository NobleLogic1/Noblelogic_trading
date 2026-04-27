import React, { useEffect, useState } from 'react';

export default function StrategyInsights() {
  const [strategy, setStrategy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStrategy = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:3001/api/strategy');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setStrategy(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch strategy data:', err);
        setError('Failed to load strategy insights');
      } finally {
        setLoading(false);
      }
    };

    fetchStrategy();
    // Refresh strategy data every 10 seconds
    const interval = setInterval(fetchStrategy, 10000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="panel">
        <h2>🧠 Strategy Insights</h2>
        <p>Loading strategy data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel">
        <h2>🧠 Strategy Insights</h2>
        <p style={{ color: '#ff6b6b' }}>Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>🧠 Strategy Insights</h2>
      {strategy ? (
        <ul>
          <li>
            {strategy.strategy}: {strategy.confidence}% confidence {strategy.active ? '✅' : '❌'}
          </li>
        </ul>
      ) : (
        <p>No strategy data available</p>
      )}
    </div>
  );
}