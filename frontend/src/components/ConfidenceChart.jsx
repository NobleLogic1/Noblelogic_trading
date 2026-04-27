import React, { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import 'chart.js/auto';

export default function ConfidenceChart() {
  const [trades, setTrades] = useState([]);

  useEffect(() => {
    fetch('http://localhost:3001/api/trades')
      .then(res => res.json())
      .then(data => setTrades(data));
  }, []);

  const labels = trades.map(t => t.id);
  const confidence = trades.map(t => t.confidence * 100);

  const data = {
    labels,
    datasets: [
      {
        label: 'Confidence (%)',
        data: confidence,
        backgroundColor: '#ffd700',
      },
    ],
  };

  return (
    <div className="panel">
      <h2>📶 Confidence Levels</h2>
      <Bar data={data} />
    </div>
  );
}