import React, { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import 'chart.js/auto';

export default function StrategyChart() {
  const [trades, setTrades] = useState([]);

  useEffect(() => {
    fetch('http://localhost:3001/api/trades')
      .then(res => res.json())
      .then(data => setTrades(data));
  }, []);

  const strategies = [...new Set(trades.map(t => t.strategy))];
  const pnlByStrategy = strategies.map(strat =>
    trades.filter(t => t.strategy === strat).reduce((sum, t) => sum + t.pnl, 0)
  );

  const data = {
    labels: strategies,
    datasets: [
      {
        label: 'Total PnL by Strategy',
        data: pnlByStrategy,
        backgroundColor: '#6ec1e4',
      },
    ],
  };

  return (
    <div className="panel">
      <h2>📈 Strategy Performance</h2>
      <Bar data={data} />
    </div>
  );
}