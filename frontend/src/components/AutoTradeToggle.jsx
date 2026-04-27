import React, { useState, useEffect } from 'react';

export default function AutoTradeToggle() {
  const [enabled, setEnabled] = useState(false);

  const toggle = async () => {
    try {
      const response = await fetch('http://localhost:3001/api/autotrade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled: !enabled }),
      });
      const data = await response.json();
      if (data.success) {
        setEnabled(!enabled);
        console.log(`[AutoTrade] ${enabled ? 'Stopped' : 'Started'}`);
      }
    } catch (error) {
      console.error('Failed to toggle autotrading:', error);
    }
  };

  useEffect(() => {
    // Get initial state
    fetch('http://localhost:3001/api/autotrade')
      .then(res => res.json())
      .then(data => setEnabled(data.enabled))
      .catch(console.error);
  }, []);

  return (
    <div className="panel auto-trade-toggle">
      <h2>🔄 AutoTrade Control</h2>
      <button 
        onClick={toggle}
        className={enabled ? 'active' : ''}
      >
        {enabled ? '🛑 Stop AutoTrade' : '✅ Start AutoTrade'}
      </button>
      <div className="status">
        Status: {enabled ? '🟢 Running' : '⚫ Stopped'}
      </div>
    </div>
  );
}