import React, { useState, useEffect } from 'react';
import { createChart } from 'lightweight-charts';
import SystemHealth from './components/SystemHealth';
import TradesList from './components/TradesList';
import CandlestickChart from './components/CandlestickChart';
import EmergencyControl from './components/EmergencyControl';
import ProfitLossTracker from './components/ProfitLossTracker';
import TradingConfidence from './components/TradingConfidence';
import './styles/dashboard.css';

const Dashboard = () => {
  const [selectedTrade, setSelectedTrade] = useState(null);
  const [systemHealth, setSystemHealth] = useState({
    accuracy: 0,
    confidence: 0,
    uptime: 0,
    errors: []
  });
  const [trades, setTrades] = useState([]);
  const [pnl, setPnL] = useState({
    daily: 0,
    total: 0,
    unrealized: 0
  });

  useEffect(() => {
    // Initialize WebSocket connection
    const ws = new WebSocket('ws://localhost:3001');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    // Fetch initial data
    fetchInitialData();

    return () => ws.close();
  }, []);

  const fetchInitialData = async () => {
    try {
      const [tradesRes, healthRes, pnlRes] = await Promise.all([
        fetch('/api/trades'),
        fetch('/api/system/health'),
        fetch('/api/pnl')
      ]);

      const [tradesData, healthData, pnlData] = await Promise.all([
        tradesRes.json(),
        healthRes.json(),
        pnlRes.json()
      ]);

      setTrades(tradesData);
      setSystemHealth(healthData);
      setPnL(pnlData);
    } catch (error) {
      console.error('Error fetching initial data:', error);
    }
  };

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'TRADE_UPDATE':
        setTrades(prev => [data.trade, ...prev]);
        break;
      case 'HEALTH_UPDATE':
        setSystemHealth(data.health);
        break;
      case 'PNL_UPDATE':
        setPnL(data.pnl);
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const handleEmergencyStop = async () => {
    try {
      await fetch('/api/system/stop', { method: 'POST' });
      alert('Trading system stopped successfully');
    } catch (error) {
      console.error('Failed to stop trading system:', error);
      alert('Failed to stop trading system');
    }
  };

  const handleTradeSelect = (trade) => {
    setSelectedTrade(trade);
  };

  return (
    <div className="dashboard-container">
      <header className="panel-header">
        <h1>NobleLogic Trading Dashboard</h1>
        <EmergencyControl onStop={handleEmergencyStop} />
      </header>

      <div className="dashboard-grid">
        {/* Top Row */}
        <div className="panel system-overview">
          <SystemHealth 
            accuracy={systemHealth.accuracy}
            confidence={systemHealth.confidence}
            uptime={systemHealth.uptime}
            errors={systemHealth.errors}
          />
        </div>

        <div className="panel pnl-overview">
          <ProfitLossTracker
            daily={pnl.daily}
            total={pnl.total}
            unrealized={pnl.unrealized}
          />
        </div>

        {/* Main Content */}
        <div className="panel trading-view">
          {selectedTrade ? (
            <CandlestickChart 
              symbol={selectedTrade.symbol}
              interval="1m"
              tradeTime={selectedTrade.timestamp}
            />
          ) : (
            <div className="no-trade-selected">
              Select a trade to view detailed chart
            </div>
          )}
        </div>

        {/* Trade Details */}
        <div className="panel trade-details">
          <TradesList
            trades={trades}
            onTradeSelect={handleTradeSelect}
            selectedTrade={selectedTrade}
          />
        </div>

        {/* Bottom Row */}
        <div className="panel confidence-panel">
          <TradingConfidence
            systemConfidence={systemHealth.confidence}
            tradeAccuracy={systemHealth.accuracy}
            recentTrades={trades.slice(0, 5)}
          />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;