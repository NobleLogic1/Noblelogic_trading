import React, { useState, useEffect } from 'react';
import { apiRequest, API_CONFIG } from '../config.js';

function ActiveTradesPanel() {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTrades = async () => {
      try {
        setLoading(true);
        const data = await apiRequest(API_CONFIG.ENDPOINTS.TRADES);
        setTrades(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch trades:', err);
        setError('Failed to load trades');
      } finally {
        setLoading(false);
      }
    };

    fetchTrades(); // initial load
    const interval = setInterval(fetchTrades, API_CONFIG.POLLING_INTERVALS.TRADES);

    return () => clearInterval(interval); // cleanup on unmount
  }, []);

  if (loading && trades.length === 0) {
    return (
      <div className="panel">
        <h2>Active Trades</h2>
        <p>Loading trades...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel">
        <h2>Active Trades</h2>
        <p style={{ color: '#ff6b6b' }}>Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>Active Trades</h2>
      {trades.length === 0 ? (
        <p>No active trades</p>
      ) : (
        <ul>
          {trades.map((trade, index) => (
            <li key={trade.id || index}>
              <strong>{trade.symbol}</strong> | Status: {trade.status} | PnL: {trade.pnl}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default ActiveTradesPanel;