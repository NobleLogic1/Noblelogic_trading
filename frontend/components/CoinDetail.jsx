import React, { useState, useEffect } from 'react';
import TradeStats from './TradeStats';

const CoinDetail = ({ coin }) => {
  const [trades, setTrades] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [timeRange, setTimeRange] = useState('1H');

  useEffect(() => {
    if (coin) {
      fetchCoinDetails();
    }
  }, [coin]);

  const fetchCoinDetails = async () => {
    try {
      const response = await fetch(`http://localhost:3001/api/trades`);
      const allTrades = await response.json();
      
      // Filter trades for this coin
      const coinTrades = allTrades.filter(trade => 
        trade.symbol.startsWith(coin.symbol)
      );
      
      setTrades(coinTrades);
      generateMockChartData();
    } catch (error) {
      console.error('Error fetching coin details:', error);
    }
  };

  const generateMockChartData = () => {
    // Generate realistic chart data for demo
    const data = [];
    const basePrice = 50000; // Mock base price
    let currentPrice = basePrice;
    
    for (let i = 0; i < 50; i++) {
      const change = (Math.random() - 0.5) * 1000;
      currentPrice += change;
      data.push({
        time: Date.now() - (50 - i) * 60000,
        price: currentPrice,
        volume: Math.random() * 1000000
      });
    }
    setChartData(data);
  };

  if (!coin) {
    return (
      <div className="p-6 bg-gray-900 rounded-xl shadow-lg text-center">
        <div className="text-gray-400 text-lg">Select a coin to view details</div>
        <div className="text-gray-500 text-sm mt-2">Click on any coin from the grid above</div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl shadow-lg border border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-black font-bold text-lg mr-4">
            {coin.symbol.substring(0, 2)}
          </div>
          <div>
            <h2 className="text-3xl text-white font-bold">{coin.name}</h2>
            <p className="text-gray-400 text-lg">{coin.symbol}</p>
          </div>
        </div>
        
        {/* Live Status */}
        <div className={`px-4 py-2 rounded-full text-sm font-semibold ${
          coin.isActive 
            ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
            : 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
        }`}>
          {coin.isActive ? '🟢 Live Trading' : '⚪ Inactive'}
        </div>
      </div>

      {/* Chart Section */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl text-white font-semibold">Price Chart</h3>
          <div className="flex space-x-2">
            {['1H', '4H', '1D', '1W'].map(range => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1 rounded text-sm font-medium transition-all ${
                  timeRange === range
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {range}
              </button>
            ))}
          </div>
        </div>
        
        {/* Mock Chart Container */}
        <div className="bg-gray-800 rounded-lg p-4 h-64 flex items-center justify-center border border-gray-700">
          <div className="text-center">
            <div className="text-2xl mb-2">📈</div>
            <div className="text-gray-400">Chart for {coin.symbol}</div>
            <div className="text-sm text-gray-500 mt-1">
              Real-time price data will be displayed here
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm">Total P&L</div>
          <div className={`text-2xl font-bold ${coin.profit ? 'text-green-400' : 'text-red-400'}`}>
            ${coin.totalPnL >= 0 ? '+' : ''}${coin.totalPnL.toFixed(2)}
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm">Win Rate</div>
          <div className={`text-2xl font-bold ${
            coin.winRate > 60 ? 'text-green-400' : 
            coin.winRate > 40 ? 'text-yellow-400' : 'text-red-400'
          }`}>
            {coin.winRate}%
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm">AI Confidence</div>
          <div className="text-2xl font-bold text-purple-400">
            {(coin.confidence * 100).toFixed(1)}%
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm">Total Trades</div>
          <div className="text-2xl font-bold text-blue-400">
            {coin.trades.length}
          </div>
        </div>
      </div>

      {/* Trade Stats Component */}
      <TradeStats coin={coin} trades={trades} />

      {/* Recent Trades */}
      <div className="mt-6">
        <h3 className="text-xl text-white font-semibold mb-4">Recent Trades</h3>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {trades.slice(0, 10).map((trade, index) => (
            <div key={index} className="bg-gray-800 rounded-lg p-3 border border-gray-700 flex justify-between items-center">
              <div className="flex items-center space-x-4">
                <div className={`px-2 py-1 rounded text-xs font-semibold ${
                  trade.type === 'LONG' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                }`}>
                  {trade.type}
                </div>
                <div className="text-white">${trade.entry_price?.toFixed(4) || 'N/A'}</div>
                <div className="text-gray-400 text-sm">
                  {new Date(trade.timestamp).toLocaleTimeString()}
                </div>
              </div>
              <div className={`font-semibold ${
                (trade.pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                ${trade.pnl >= 0 ? '+' : ''}${trade.pnl?.toFixed(2) || '0.00'}
              </div>
            </div>
          ))}
          
          {trades.length === 0 && (
            <div className="text-center text-gray-400 py-8">
              No trades found for {coin.symbol}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CoinDetail;