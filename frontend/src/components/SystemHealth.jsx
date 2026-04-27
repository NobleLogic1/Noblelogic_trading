import React, { useEffect, useState } from 'react';
import { apiRequest, API_CONFIG } from '../config.js';

export default function SystemHealth() {
  const [health, setHealth] = useState({ accuracy: 0, status: 'Unknown' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        setLoading(true);
        const data = await apiRequest(API_CONFIG.ENDPOINTS.HEALTH);
        setHealth(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch health data:', err);
        setError('Failed to load system health');
      } finally {
        setLoading(false);
      }
    };

    fetchHealth();
    // Refresh health data based on config
    const interval = setInterval(fetchHealth, API_CONFIG.POLLING_INTERVALS.HEALTH);
    
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <span style={{ color: '#ffd700' }}>🔄 Loading system health...</span>;
  }

  if (error) {
    return <span style={{ color: '#ff6b6b' }}>❌ {error}</span>;
  }

  return (
    <div>
      {health.status === 'Optimal' ? (
        <span style={{ color: '#00ff99' }}>🟢 System Health: Optimal (Accuracy: {health.accuracy}%)</span>
      ) : (
        <span style={{ color: '#ffd700' }}>🟡 System Alert - Accuracy: {health.accuracy}%</span>
      )}
    </div>
  );
}