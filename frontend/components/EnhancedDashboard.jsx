import React, { useState, useEffect, useRef } from 'react';
import CoinGrid from './CoinGrid';
import CoinDetail from './CoinDetail';
import GPUChart from './GPUChart';
import GPUParticles from './GPUParticles';

const EnhancedDashboard = () => {
  const [selectedCoin, setSelectedCoin] = useState(null);
  const [systemStatus, setSystemStatus] = useState('operational');
  const [totalBalance, setTotalBalance] = useState(100);
  const [totalPnL, setTotalPnL] = useState(0);
  const [isAutoTrading, setIsAutoTrading] = useState(false);
  const [marketSentiment, setMarketSentiment] = useState('Bullish');
  const [aiConfidence, setAiConfidence] = useState(87);
  const [gpuAcceleration, setGpuAcceleration] = useState(false);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    fetchSystemData();
    const interval = setInterval(fetchSystemData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchSystemData = async () => {
    try {
      const healthResponse = await fetch('http://localhost:3001/api/health');
      const healthData = await healthResponse.json();
      setSystemStatus(healthData.status || 'operational');
      setGpuAcceleration(healthData.gpu_acceleration || false);
      
      const tradesResponse = await fetch('http://localhost:3001/api/trades');
      const trades = await tradesResponse.json();
      const totalPnL = trades.reduce((sum, trade) => sum + (trade.pnl || 0), 0);
      setTotalPnL(totalPnL);
      
      // Fetch chart data for GPU rendering
      const chartResponse = await fetch('http://localhost:3001/api/chart-data');
      const chartDataResult = await chartResponse.json();
      setChartData(chartDataResult.data || []);
      
    } catch (error) {
      console.error('Error fetching system data:', error);
      setSystemStatus('error');
    }
  };

  const handleCoinSelect = (coin) => {
    setSelectedCoin(coin);
  };

  const toggleAutoTrading = () => {
    setIsAutoTrading(!isAutoTrading);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'operational': return 'text-emerald-400';
      case 'degraded': return 'text-amber-400';
      case 'error': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  const MetricCard = ({ title, value, change, icon, color = "blue" }) => (
    <div className="bg-slate-900/60 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 hover:border-slate-600/50 transition-all duration-300">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-xl bg-gradient-to-br from-${color}-500/20 to-${color}-600/20`}>
          <span className="text-2xl">{icon}</span>
        </div>
        {change && (
          <span className={`text-sm font-medium px-2 py-1 rounded-lg ${
            change >= 0 ? 'text-emerald-400 bg-emerald-400/10' : 'text-red-400 bg-red-400/10'
          }`}>
            {change >= 0 ? '+' : ''}{change.toFixed(2)}%
          </span>
        )}
      </div>
      <h3 className="text-slate-400 text-sm font-medium mb-1">{title}</h3>
      <p className="text-white text-2xl font-bold">{value}</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/5 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/5 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 w-60 h-60 bg-emerald-500/5 rounded-full blur-3xl"></div>
      </div>

      {/* Header */}
      <header className="relative border-b border-slate-700/50 bg-slate-900/30 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-8xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo and Title */}
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/25">
                  <span className="font-bold text-white text-lg">NL</span>
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-400 rounded-full animate-pulse"></div>
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-emerald-400 bg-clip-text text-transparent">
                  NobleLogic Pro
                </h1>
                <p className="text-slate-400 text-sm font-medium">Advanced AI Trading Platform</p>
              </div>
            </div>

            {/* Header Controls */}
            <div className="flex items-center space-x-6">
              {/* Portfolio Value */}
              <div className="text-right">
                <div className="text-slate-400 text-sm font-medium">Portfolio Value</div>
                <div className="text-2xl font-bold text-white">
                  ${(totalBalance + totalPnL).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </div>
                <div className={`text-sm font-medium ${totalPnL >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {totalPnL >= 0 ? '+' : ''}${totalPnL.toFixed(2)} Today
                </div>
              </div>

              {/* AI Trading Toggle */}
              <div className="flex flex-col items-center space-y-2">
                <span className="text-slate-400 text-sm font-medium">AI Trading</span>
                <button
                  onClick={toggleAutoTrading}
                  className={`relative inline-flex h-7 w-14 items-center rounded-full transition-all duration-300 ${
                    isAutoTrading 
                      ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 shadow-lg shadow-emerald-500/25' 
                      : 'bg-slate-600'
                  }`}
                >
                  <span
                    className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform duration-300 shadow-lg ${
                      isAutoTrading ? 'translate-x-8' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              {/* System Status */}
              <div className="text-right">
                <div className="text-slate-400 text-sm font-medium">System Status</div>
                <div className={`flex items-center space-x-2 ${getStatusColor(systemStatus)}`}>
                  <div className="w-2 h-2 rounded-full bg-current animate-pulse"></div>
                  <span className="text-sm font-semibold">{systemStatus.toUpperCase()}</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-2">
                <button
                  onClick={fetchSystemData}
                  className="p-3 bg-slate-800/50 hover:bg-slate-700/50 border border-slate-600/50 rounded-xl transition-all duration-300 hover:shadow-lg"
                  title="Refresh Data"
                >
                  <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
                <button className="p-3 bg-slate-800/50 hover:bg-slate-700/50 border border-slate-600/50 rounded-xl transition-all duration-300 hover:shadow-lg">
                  <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="relative max-w-8xl mx-auto px-6 py-8">
        {/* Top Metrics Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <MetricCard 
            title="Total Assets" 
            value={`$${(totalBalance + totalPnL).toLocaleString()}`} 
            change={((totalPnL / totalBalance) * 100)} 
            icon="💰" 
            color="emerald" 
          />
          <MetricCard 
            title="AI Confidence" 
            value={`${aiConfidence}%`} 
            change={12.5} 
            icon="🧠" 
            color="blue" 
          />
          <MetricCard 
            title="Market Sentiment" 
            value={marketSentiment} 
            change={8.3} 
            icon="📈" 
            color="purple" 
          />
          <MetricCard 
            title="Active Trades" 
            value="7" 
            change={-2.1} 
            icon="⚡" 
            color="amber" 
          />
        </div>

        {/* GPU-Accelerated Chart Section */}
        <div className="mb-8 relative">
          <GPUParticles width={800} height={400} particleCount={1500} />
          <GPUChart 
            data={chartData} 
            width={800} 
            height={400} 
            symbol={selectedCoin?.symbol || 'BTC'} 
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
          {/* Coins Grid - Takes up 3/4 on large screens */}
          <div className="xl:col-span-3">
            <div className="bg-slate-900/60 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-8 hover:border-slate-600/50 transition-all duration-300">
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h2 className="text-3xl font-bold text-white mb-2">Live Market Data</h2>
                  <p className="text-slate-400">Real-time cryptocurrency analysis and trading signals</p>
                </div>
                <div className="flex items-center space-x-3 bg-emerald-500/10 px-4 py-2 rounded-xl border border-emerald-500/20">
                  <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                  <span className="text-emerald-400 text-sm font-medium">Live Updates</span>
                </div>
              </div>
              <CoinGrid onSelect={handleCoinSelect} selectedCoin={selectedCoin} />
            </div>
          </div>

          {/* Sidebar - Takes up 1/4 on large screens */}
          <div className="xl:col-span-1 space-y-6">
            {/* Coin Detail */}
            <div className="sticky top-28">
              <CoinDetail coin={selectedCoin} />
            </div>
            
            {/* AI Insights Panel */}
            <div className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 backdrop-blur-sm border border-blue-500/20 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center">
                <span className="mr-3 text-2xl">🤖</span>
                AI Insights
                <span className={`ml-auto px-2 py-1 rounded-lg text-xs ${
                  gpuAcceleration ? 'bg-green-600/20 text-green-400' : 'bg-amber-600/20 text-amber-400'
                }`}>
                  {gpuAcceleration ? 'GPU' : 'CPU'}
                </span>
              </h3>
              <div className="space-y-4">
                <div className="bg-slate-800/30 rounded-xl p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-slate-400 text-sm">Market Prediction</span>
                    <span className="text-emerald-400 text-sm font-bold">+87% Bullish</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div className="bg-gradient-to-r from-emerald-500 to-emerald-400 h-2 rounded-full" style={{width: '87%'}}></div>
                  </div>
                </div>
                <div className="bg-slate-800/30 rounded-xl p-4">
                  <div className="text-slate-400 text-sm mb-1">Next Signal</div>
                  <div className="text-white font-bold">BTC Long Entry</div>
                  <div className="text-emerald-400 text-sm">Expected in 2h 15m</div>
                </div>
              </div>
            </div>

            {/* Performance Summary */}
            <div className="bg-gradient-to-br from-emerald-900/20 to-blue-900/20 backdrop-blur-sm border border-emerald-500/20 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center">
                <span className="mr-3 text-2xl">📊</span>
                Performance
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-slate-400">Win Rate</span>
                  <span className="text-emerald-400 font-bold">73.2%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Avg. Return</span>
                  <span className="text-emerald-400 font-bold">+12.8%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Max Drawdown</span>
                  <span className="text-red-400 font-bold">-5.2%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Sharpe Ratio</span>
                  <span className="text-blue-400 font-bold">2.34</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedDashboard;