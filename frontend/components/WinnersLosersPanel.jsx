import React, { useEffect, useState } from 'react';

export default function WinnersLosersPanel() {
  const [trades, setTrades] = useState([]);

  useEffect(() => {
    fetch('http://localhost:3001/api/trades')
      .then(res => res.json())
      .then(data => setTrades(data));
  }, []);

  const sorted = [...trades].sort((a, b) => b.pnl - a.pnl);
  const top = sorted.slice(0, 3);
  const bottom = sorted.slice(-3).reverse();

  return (
    <div className="panel">
      <h2>🏆 Biggest Winners & Losers</h2>
      <div>
        <h3 style={{ color: '#00ff99' }}>Top Winners</h3>
        <ul>
          {top.map(t => (
            <li key={t.id}>{t.coin} ${t.pnl.toFixed(2)} ({t.strategy})</li>
          ))}
        </ul>
        <h3 style={{ color: '#ff4d4d' }}>Top Losers</h3>
        <ul>
          {bottom.map(t => (
            <li key={t.id}>{t.coin} ${t.pnl.toFixed(2)} ({t.strategy})</li>
          ))}
        </ul>
      </div>
    </div>
  );
}