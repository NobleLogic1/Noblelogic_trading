import React, { useEffect, useState } from 'react';

export default function NewCoinRadar() {
  const [coins, setCoins] = useState([]);

  useEffect(() => {
    fetch('https://api.binance.us/api/v3/exchangeInfo')
      .then(res => res.json())
      .then(data => {
        const recent = data.symbols.filter(s => s.status === 'TRADING').slice(-5);
        setCoins(recent);
      });
  }, []);

  return (
    <div className="panel">
      <h2>📈 New Coin Radar</h2>
      <ul>
        {coins.map((c, i) => (
          <li key={i}>
            {c.symbol} - AutoTrade: <button>Enable</button>
          </li>
        ))}
      </ul>
    </div>
  );
}