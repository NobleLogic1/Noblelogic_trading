import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Legend,
  Tooltip
} from 'chart.js';

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Legend, Tooltip);

function StrategyChart({ closedTrades }) {
  if (!closedTrades || closedTrades.length === 0) return <p>No closed trades to chart.</p>;

  const strategies = ['scalp', 'breakout', 'vwap', 'liquidity', 'news'];
  const grouped = {};

  strategies.forEach((s) => {
    grouped[s] = closedTrades.filter(t => t.strategy === s);
  });

  const datasets = strategies.map((s, index) => {
    const pnlSeries = grouped[s].map((t, i) => ({
      x: i,
      y: t.pnl
    }));

    return {
      label: s.charAt(0).toUpperCase() + s.slice(1),
      data: pnlSeries,
      borderColor: `hsl(${index * 72}, 70%, 70%)`,
      backgroundColor: `hsla(${index * 72}, 70%, 70%, 0.2)`,
      tension: 0.3
    };
  });

  const chartData = { datasets };
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      tooltip: { mode: 'index', intersect: false }
    },
    scales: {
      x: { title: { display: true, text: 'Trade Index' }, ticks: { color: '#E0E0E0' } },
      y: { title: { display: true, text: 'PnL ($)' }, ticks: { color: '#E0E0E0' } }
    }
  };

  return (
    <div style={{ marginTop: '2rem' }}>
      <h3 style={{ color: '#66B2FF' }}>📈 Strategy Performance</h3>
      <Line data={chartData} options={chartOptions} />
    </div>
  );
}

export default StrategyChart;