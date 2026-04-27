import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';

export default function PnLGraph() {
  const [trades, setTrades] = useState([]);

  useEffect(() => {
    fetch('http://localhost:3001/api/trades')
      .then(res => res.json())
      .then(data => setTrades(data));
  }, []);

  const labels = trades.map(t => t.timestamp.slice(11, 16));
  const pnlData = trades.map(t => t.pnl);

  const data = {
    labels,
    datasets: [
      {
        label: 'PnL ($)',
        data: pnlData,
        borderColor: '#6ec1e4',
        backgroundColor: 'rgba(110,193,228,0.2)',
        tension: 0.3,
      },
    ],
  };

  return (
    <div className="panel">
      <h2>📊 PnL Over Time</h2>
      <Line data={data} />
    </div>
  );
}