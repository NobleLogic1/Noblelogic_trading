import React, { useEffect, useState } from 'react';
import { apiRequest, API_CONFIG } from '../config.js';

export default function StrategyInsights() {
  const [strategy, setStrategy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStrategy = async () => {
      try {
        setLoading(true);
        const data = await apiRequest(API_CONFIG.ENDPOINTS.STRATEGY);
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
    // Refresh strategy data based on config
    const interval = setInterval(fetchStrategy, API_CONFIG.POLLING_INTERVALS.STRATEGY);
    
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