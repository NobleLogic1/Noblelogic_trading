import React from 'react';

const TradeStats = ({ coin, trades = [] }) => {
  // Calculate advanced statistics
  const calculateStats = () => {
    if (!trades.length) return {
      winRate: 0,
      avgProfit: 0,
      avgLoss: 0,
      bestTrade: 0,
      worstTrade: 0,
      profitFactor: 0,
      sharpeRatio: 0
    };

    const winningTrades = trades.filter(t => (t.pnl || 0) > 0);
    const losingTrades = trades.filter(t => (t.pnl || 0) < 0);
    
    const totalProfit = winningTrades.reduce((sum, t) => sum + (t.pnl || 0), 0);
    const totalLoss = Math.abs(losingTrades.reduce((sum, t) => sum + (t.pnl || 0), 0));
    
    const avgProfit = winningTrades.length ? totalProfit / winningTrades.length : 0;
    const avgLoss = losingTrades.length ? totalLoss / losingTrades.length : 0;
    
    const allPnL = trades.map(t => t.pnl || 0);
    const bestTrade = Math.max(...allPnL, 0);
    const worstTrade = Math.min(...allPnL, 0);
    
    const profitFactor = totalLoss > 0 ? totalProfit / totalLoss : totalProfit > 0 ? 999 : 0;
    
    // Simple Sharpe ratio calculation
    const avgReturn = allPnL.reduce((sum, pnl) => sum + pnl, 0) / allPnL.length;
    const variance = allPnL.reduce((sum, pnl) => sum + Math.pow(pnl - avgReturn, 2), 0) / allPnL.length;
    const stdDev = Math.sqrt(variance);
    const sharpeRatio = stdDev > 0 ? avgReturn / stdDev : 0;

    return {
      winRate: (winningTrades.length / trades.length * 100),
      avgProfit,
      avgLoss,
      bestTrade,
      worstTrade,
      profitFactor,
      sharpeRatio: Math.max(-10, Math.min(10, sharpeRatio)) // Cap between -10 and 10
    };
  };

  const stats = calculateStats();

  const StatCard = ({ title, value, color = 'text-white', suffix = '', prefix = '' }) => (
    <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
      <div className="text-gray-400 text-sm mb-1">{title}</div>
      <div className={`text-lg font-bold ${color}`}>
        {prefix}{value}{suffix}
      </div>
    </div>
  );

  const getColorByValue = (value, reverse = false) => {
    if (value > 0) return reverse ? 'text-red-400' : 'text-green-400';
    if (value < 0) return reverse ? 'text-green-400' : 'text-red-400';
    return 'text-gray-400';
  };

  return (
    <div className="space-y-6">
      {/* AI Insights Panel */}
      <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 rounded-lg p-4 border border-purple-500/30">
        <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
          <span className="mr-2">🧠</span>
          AI Trading Insights
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-400">
              {(coin.confidence * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-400">Current Confidence</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">
              {trades.length}
            </div>
            <div className="text-sm text-gray-400">Total Trades</div>
          </div>
          <div className="text-center">
            <div className={`text-2xl font-bold ${getColorByValue(coin.totalPnL)}`}>
              ${coin.totalPnL >= 0 ? '+' : ''}${coin.totalPnL.toFixed(2)}
            </div>
            <div className="text-sm text-gray-400">Net P&L</div>
          </div>
        </div>
        
        {/* AI Reasoning (Mock) */}
        <div className="mt-4 p-3 bg-gray-800/50 rounded border border-gray-700">
          <div className="text-sm text-gray-300">
            <span className="text-blue-400 font-semibold">AI Analysis:</span> {
              coin.confidence > 0.8 ? 
                `High confidence in ${coin.symbol} due to strong technical indicators and favorable market sentiment.` :
              coin.confidence > 0.6 ?
                `Moderate confidence in ${coin.symbol}. Monitoring volatility and volume patterns.` :
                `Lower confidence due to uncertain market conditions. Proceeding with caution.`
            }
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard 
          title="Win Rate" 
          value={`${stats.winRate.toFixed(1)}%`}
          color={stats.winRate > 60 ? 'text-green-400' : stats.winRate > 40 ? 'text-yellow-400' : 'text-red-400'}
        />
        
        <StatCard 
          title="Profit Factor" 
          value={stats.profitFactor.toFixed(2)}
          color={stats.profitFactor > 1.5 ? 'text-green-400' : stats.profitFactor > 1 ? 'text-yellow-400' : 'text-red-400'}
        />
        
        <StatCard 
          title="Sharpe Ratio" 
          value={stats.sharpeRatio.toFixed(2)}
          color={stats.sharpeRatio > 1 ? 'text-green-400' : stats.sharpeRatio > 0 ? 'text-yellow-400' : 'text-red-400'}
        />
        
        <StatCard 
          title="Best Trade" 
          value={`$${stats.bestTrade.toFixed(2)}`}
          color="text-green-400"
          prefix="+"
        />
      </div>

      {/* Risk Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatCard 
          title="Avg Profit" 
          value={`$${stats.avgProfit.toFixed(2)}`}
          color="text-green-400"
        />
        
        <StatCard 
          title="Avg Loss" 
          value={`$${stats.avgLoss.toFixed(2)}`}
          color="text-red-400"
        />
        
        <StatCard 
          title="Worst Trade" 
          value={`$${stats.worstTrade.toFixed(2)}`}
          color="text-red-400"
        />
      </div>

      {/* Risk Meter */}
      <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
        <h5 className="text-white font-semibold mb-3 flex items-center">
          <span className="mr-2">⚡</span>
          Risk Assessment
        </h5>
        
        <div className="space-y-3">
          {/* Volatility Meter */}
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-400">Volatility</span>
              <span className="text-yellow-400">Medium</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div className="bg-yellow-400 h-2 rounded-full" style={{ width: '60%' }}></div>
            </div>
          </div>
          
          {/* Confidence Meter */}
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-400">AI Confidence</span>
              <span className="text-purple-400">{(coin.confidence * 100).toFixed(0)}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div className="bg-purple-400 h-2 rounded-full" style={{ width: `${coin.confidence * 100}%` }}></div>
            </div>
          </div>
          
          {/* Performance Meter */}
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-400">Performance</span>
              <span className={getColorByValue(stats.winRate - 50)}>
                {stats.winRate > 60 ? 'Excellent' : stats.winRate > 40 ? 'Good' : 'Needs Improvement'}
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${
                  stats.winRate > 60 ? 'bg-green-400' : stats.winRate > 40 ? 'bg-yellow-400' : 'bg-red-400'
                }`} 
                style={{ width: `${Math.min(100, stats.winRate)}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Next Predicted Move (Mock AI Prediction) */}
      <div className="bg-gradient-to-r from-blue-900/30 to-green-900/30 rounded-lg p-4 border border-blue-500/30">
        <h5 className="text-white font-semibold mb-3 flex items-center">
          <span className="mr-2">🔮</span>
          Next Predicted Move
        </h5>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-lg font-bold text-white">
              {coin.confidence > 0.7 ? 'BULLISH' : coin.confidence > 0.4 ? 'NEUTRAL' : 'BEARISH'}
            </div>
            <div className="text-sm text-gray-400">
              Next 1-4 hours • {(coin.confidence * 100).toFixed(0)}% confidence
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl">
              {coin.confidence > 0.7 ? '📈' : coin.confidence > 0.4 ? '↔️' : '📉'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradeStats;