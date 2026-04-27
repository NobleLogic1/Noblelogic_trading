import React, { useState, useEffect } from 'react';

const CoinGrid = ({ onSelect, selectedCoin }) => {
  const [coins, setCoins] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCoins();
    const interval = setInterval(fetchCoins, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchCoins = async () => {
    try {
      const response = await fetch('http://localhost:3001/api/trades');
      const trades = await response.json();
      
      // Process trades to create coin summary
      const coinMap = new Map();
      
      trades.forEach(trade => {
        const symbol = trade.symbol;
        if (!coinMap.has(symbol)) {
          coinMap.set(symbol, {
            symbol: symbol.split('/')[0], // Remove /USDT
            name: getCoinName(symbol),
            trades: [],
            totalPnL: 0,
            winRate: 0,
            confidence: 0,
            lastTrade: null
          });
        }
        
        const coin = coinMap.get(symbol);
        coin.trades.push(trade);
        coin.totalPnL += trade.pnl || 0;
        coin.lastTrade = trade;
      });

      // Calculate stats for each coin
      const coinData = Array.from(coinMap.values()).map(coin => {
        const winningTrades = coin.trades.filter(t => (t.pnl || 0) > 0);
        coin.winRate = coin.trades.length > 0 ? (winningTrades.length / coin.trades.length * 100).toFixed(1) : 0;
        coin.confidence = coin.lastTrade ? (Math.random() * 0.3 + 0.7) : 0.5; // Mock confidence for now
        coin.profit = coin.totalPnL > 0;
        coin.isActive = coin.lastTrade && isRecentTrade(coin.lastTrade.timestamp);
        return coin;
      });

      setCoins(coinData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching coins:', error);
      setLoading(false);
    }
  };

  const getCoinName = (symbol) => {
    const names = {
      'BTC/USDT': 'Bitcoin',
      'ETH/USDT': 'Ethereum', 
      'BNB/USDT': 'Binance Coin',
      'ADA/USDT': 'Cardano',
      'SOL/USDT': 'Solana',
      'DOGE/USDT': 'Dogecoin'
    };
    return names[symbol] || symbol.split('/')[0];
  };

  const isRecentTrade = (timestamp) => {
    const tradeTime = new Date(timestamp);
    const now = new Date();
    return (now - tradeTime) < 300000; // 5 minutes
  };

  if (loading) {
    return (
      <div className="grid grid-cols-3 gap-4 p-4">
        {[1,2,3,4,5,6].map(i => (
          <div key={i} className="bg-gray-800 rounded-xl p-4 animate-pulse">
            <div className="h-6 bg-gray-700 rounded mb-2"></div>
            <div className="h-4 bg-gray-700 rounded mb-1"></div>
            <div className="h-4 bg-gray-700 rounded"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-3 gap-4 p-4">
      {coins.map((coin) => (
        <div
          key={coin.symbol}
          onClick={() => onSelect(coin)}
          className={`
            relative overflow-hidden rounded-xl p-4 shadow-lg cursor-pointer transition-all duration-300 transform hover:scale-105
            ${selectedCoin?.symbol === coin.symbol 
              ? 'bg-gradient-to-br from-blue-900 to-purple-900 ring-2 ring-blue-400' 
              : 'bg-gradient-to-br from-gray-900 to-gray-800 hover:from-gray-800 hover:to-gray-700'
            }
            ${coin.isActive ? 'animate-pulse' : ''}
          `}
        >
          {/* Active Trading Indicator */}
          {coin.isActive && (
            <div className="absolute top-2 right-2 w-3 h-3 bg-green-400 rounded-full animate-ping"></div>
          )}
          
          {/* Coin Header */}
          <div className="flex items-center mb-3">
            <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-black font-bold text-sm mr-3">
              {coin.symbol.substring(0, 2)}
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">{coin.symbol}</h3>
              <p className="text-xs text-gray-400">{coin.name}</p>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-400">Win Rate</span>
              <span className={`text-sm font-semibold ${
                coin.winRate > 60 ? 'text-green-400' : 
                coin.winRate > 40 ? 'text-yellow-400' : 'text-red-400'
              }`}>
                {coin.winRate}%
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-400">Confidence</span>
              <span className="text-sm font-semibold text-purple-400">
                {(coin.confidence * 100).toFixed(1)}%
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-400">P&L</span>
              <span className={`text-sm font-bold ${coin.profit ? 'text-green-400' : 'text-red-400'}`}>
                ${coin.totalPnL >= 0 ? '+' : ''}${coin.totalPnL.toFixed(2)}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-400">Trades</span>
              <span className="text-sm text-blue-400 font-semibold">
                {coin.trades.length}
              </span>
            </div>
          </div>

          {/* Progress Bar for Win Rate */}
          <div className="mt-3">
            <div className="w-full bg-gray-700 rounded-full h-1.5">
              <div 
                className={`h-1.5 rounded-full transition-all duration-500 ${
                  coin.winRate > 60 ? 'bg-green-400' : 
                  coin.winRate > 40 ? 'bg-yellow-400' : 'bg-red-400'
                }`}
                style={{ width: `${coin.winRate}%` }}
              ></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CoinGrid;