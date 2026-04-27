import React, { useState, useEffect } from 'react';
import AutoTradeToggle from './components/AutoTradeToggle';
import LiveTradeTracker from './components/LiveTradeTracker';

export default function App() {
  const [systemStatus, setSystemStatus] = useState('Loading...');
  const [backendData, setBackendData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [gpuStatus, setGpuStatus] = useState('Unknown');
  const [tradingActive, setTradingActive] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [prices, setPrices] = useState({});
  const [tickerFilter, setTickerFilter] = useState('popular'); // 'popular', 'stablecoins', 'all'
  const [allTickers, setAllTickers] = useState([]);

  // New state for Binance.US balance and trade tracking
  const [accountBalance, setAccountBalance] = useState({});

  const [recentTrades, setRecentTrades] = useState([]);

  // Fetch backend data and update time
  useEffect(() => {
    fetchBackendData();
    const dataInterval = setInterval(fetchBackendData, 5000);
    const timeInterval = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => {
      clearInterval(dataInterval);
      clearInterval(timeInterval);
    };
  }, []);

  useEffect(() => {
    // Fetch the initial trading status from the backend
    const getTradingStatus = async () => {
      try {
        const response = await fetch('http://localhost:3001/api/autotrade');
        if (response.ok) {
          const data = await response.json();
          setTradingActive(data.enabled);
        }
      } catch (error) {
        console.error("Could not fetch trading status:", error);
      }
    };
    getTradingStatus();
  }, []);

  const fetchBackendData = async () => {
    try {
      const response = await fetch('http://localhost:3001/api/health');
      if (response.ok) {
        const data = await response.json();
        setBackendData(data);
        setSystemStatus(data.status || 'operational');
        setGpuStatus(data.gpu_status || 'CPU Only');
        setIsConnected(true);
        
        // Fetch additional data for balance and trades
        fetchBalanceData();
        fetchTradeData();
        fetchTickerData();
      } else {
        setSystemStatus('Backend Error');
        setIsConnected(false);
      }
    } catch (error) {
      setSystemStatus('Connection Failed');
      setIsConnected(false);
      console.error('Backend error:', error);
    }
  };

  const fetchTickerData = async () => {
    try {
      const response = await fetch('http://localhost:3001/api/tickers');
      if (response.ok) {
        const data = await response.json();
        setAllTickers(data); // Store all tickers

        // Convert array to object for easier lookup, and filter for USDT pairs
        const tickerObject = data
          .filter(ticker => ticker.symbol.endsWith('USDT'))
          .reduce((acc, ticker) => {
            const coin = ticker.symbol.replace('USDT', '');
            acc[coin] = {
              price: parseFloat(ticker.lastPrice),
              change: parseFloat(ticker.priceChangePercent),
            };
            return acc;
          }, {});
        
        setPrices(tickerObject);
      } else {
        console.error('❌ Failed to fetch ticker data:', response.status);
      }
    } catch (error) {
      console.log('⚠️ Could not fetch ticker data:', error.message);
    }
  };

  const fetchBalanceData = async () => {
    try {
      const response = await fetch('http://localhost:3001/api/balance');
      if (!response.ok) {
        console.error('❌ Failed to fetch balance data:', response.status, response.statusText);
        setAccountBalance({}); // Clear balance on failure
        return;
      }
      
      const data = await response.json();
      
      if (data.error || !Array.isArray(data)) {
        console.error('API Error or invalid data format fetching balance:', data.error || 'Data is not an array');
        setAccountBalance({}); // Clear balance on error
        return;
      }

      // Convert the array of asset objects into a single object for the state.
      const balanceObject = data.reduce((acc, asset) => {
        acc[asset.asset] = parseFloat(asset.free) + parseFloat(asset.locked);
        return acc;
      }, {});

      console.log('🔄 Updated balance data from API');
      setAccountBalance(balanceObject);

    } catch (error) {
      console.error('⚠️ Exception during fetch balance data:', error);
      setAccountBalance({}); // Clear balance on exception
    }
  };

  const fetchTradeData = async () => {
    try {
      const response = await fetch('http://localhost:3001/api/trades');
      if (response.ok) {
        const data = await response.json();
        setRecentTrades(data);
      }
    } catch (error) {
      console.log('Using demo trade data');
    }
  };

  const toggleLiveTrading = async () => {
    const newTradingStatus = !tradingActive;
    try {
      const response = await fetch('http://localhost:3001/api/autotrade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled: newTradingStatus }),
      });
      const data = await response.json();
      if (data.success) {
        setTradingActive(newTradingStatus);
        console.log(`[AutoTrade] Set to: ${newTradingStatus ? 'Active' : 'Inactive'}`);
      } else {
        console.error('Failed to toggle autotrading:', data.message);
      }
    } catch (error) {
      console.error('Error toggling autotrading:', error);
    }
  };

  const getButtonStyle = (filter) => ({
    padding: '12px 24px',
    borderRadius: '12px',
    border: 'none',
    fontSize: '1rem',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    background: tickerFilter === filter 
      ? 'linear-gradient(135deg, #10b981 0%, #34d399 100%)' 
      : 'rgba(255, 255, 255, 0.05)',
    color: tickerFilter === filter ? '#ffffff' : 'rgba(255, 255, 255, 0.8)',
    boxShadow: tickerFilter === filter ? '0 4px 20px rgba(16, 185, 129, 0.4)' : '0 2px 10px rgba(0, 0, 0, 0.1)',
  });

  const filteredPrices = React.useMemo(() => {
    const popularCoins = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'DOGE'];
    const stablecoins = ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'USDP'];

    if (tickerFilter === 'stablecoins') {
      // For stablecoins, we might not have price changes, so we create a default view
      return stablecoins.map(coin => [coin, { price: 1.00, change: 0.0, isStable: true }]);
    }

    let filtered = Object.entries(prices);

    if (tickerFilter === 'popular') {
      filtered = filtered.filter(([coin]) => popularCoins.includes(coin));
    }
    
    // Always include the currently traded asset if it's not already there
    const tradedAsset = recentTrades.length > 0 ? recentTrades[0].symbol.replace('USDT', '') : 'XRP';
    if (prices[tradedAsset] && !filtered.some(([coin]) => coin === tradedAsset)) {
        filtered.unshift([tradedAsset, prices[tradedAsset]]);
    }

    return filtered;
  }, [prices, tickerFilter, recentTrades]);


  const openGPUDashboard = () => {
    alert('GPU Dashboard would open here!\n\nFeatures:\n- WebGL Charts\n- GPU Particles\n- Real-time Analytics');
  };

  return (
    <>
      <div style={{
        fontFamily: "'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif",
        background: '#0a0a0a',
        color: '#ffffff',
        minHeight: '100vh',
        position: 'relative',
        overflow: 'hidden'
      }}>
      {/* Subtle Background Pattern */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(16, 185, 129, 0.05) 100%)',
        zIndex: 0
      }} />

      <div style={{ position: 'relative', zIndex: 1, padding: '24px' }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '32px 40px',
          marginBottom: '40px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <div>
            <h1 style={{
              fontSize: '2.5rem',
              fontWeight: '700',
              margin: 0,
              letterSpacing: '-0.025em',
              background: 'linear-gradient(135deg, #ffffff 0%, #a1a1aa 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              NobleLogic Trading
            </h1>
            <p style={{
              color: 'rgba(255, 255, 255, 0.6)',
              fontSize: '1rem',
              margin: '8px 0 0 0',
              fontWeight: '400'
            }}>
              GPU-Accelerated Cryptocurrency Platform
            </p>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '24px'
          }}>
            <div style={{
              textAlign: 'right',
              padding: '16px 24px',
              background: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)'
            }}>
              <div style={{
                color: '#10b981',
                fontSize: '1.25rem',
                fontWeight: '600',
                fontFamily: 'monospace'
              }}>
                {currentTime.toLocaleTimeString()}
              </div>
              <div style={{
                color: 'rgba(255, 255, 255, 0.5)',
                fontSize: '0.875rem'
              }}>
                {currentTime.toLocaleDateString()}
              </div>
            </div>
          </div>
        </div>

        {/* Price Ticker Filter */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '16px',
          marginBottom: '32px',
          padding: '0 40px'
        }}>
          <button onClick={() => setTickerFilter('popular')} style={getButtonStyle('popular')}>Popular</button>
          <button onClick={() => setTickerFilter('stablecoins')} style={getButtonStyle('stablecoins')}>Stablecoins</button>
          <button onClick={() => setTickerFilter('all')} style={getButtonStyle('all')}>All USDT Pairs</button>
        </div>

        {/* Price Ticker */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '24px',
          marginBottom: '40px',
          padding: '0 40px'
        }}>
          {filteredPrices.map(([coin, data]) => (
            <div key={coin} style={{
              padding: '24px',
              background: 'rgba(255, 255, 255, 0.03)',
              borderRadius: '16px',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              backdropFilter: 'blur(20px)',
              transition: 'all 0.2s ease',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
            >
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '16px'
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px'
                }}>
                  <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    background: data.change >= 0 ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '1.25rem',
                    fontWeight: '600'
                  }}>
                    {coin[0]}
                  </div>
                  <div>
                    <div style={{
                      fontSize: '1.125rem',
                      fontWeight: '600',
                      color: '#ffffff'
                    }}>
                      {coin}/USDT
                    </div>
                    <div style={{
                      fontSize: '0.875rem',
                      color: 'rgba(255, 255, 255, 0.6)'
                    }}>
                      {data.isStable ? "Stablecoin" : `${coin} Price`}
                    </div>
                  </div>
                </div>
                <div style={{
                  textAlign: 'right'
                }}>
                  <div style={{
                    fontSize: '1.5rem',
                    fontWeight: '700',
                    color: '#ffffff',
                    marginBottom: '4px'
                  }}>
                    ${data.price.toLocaleString()}
                  </div>
                  <div style={{
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    color: data.change >= 0 ? '#10b981' : '#ef4444'
                  }}>
                    {data.isStable ? '±0.00%' : `${data.change >= 0 ? '+' : ''}${data.change.toFixed(2)}%`}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Main Grid - Enhanced Card-Based Layout */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '24px',
          marginBottom: '32px',
          padding: '0 40px'
        }}>
          {/* System Status Card */}
          <div style={{
            padding: '28px',
            background: 'rgba(255, 255, 255, 0.04)',
            backdropFilter: 'blur(20px)',
            borderRadius: '20px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
            position: 'relative',
            overflow: 'hidden'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)';
            e.currentTarget.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.2)';
            e.currentTarget.style.borderColor = 'rgba(16, 185, 129, 0.3)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.12)';
            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
          }}
          >
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '4px',
              background: isConnected ? 'linear-gradient(90deg, #10b981, #34d399)' : 'linear-gradient(90deg, #ef4444, #f87171)'
            }} />
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
              <div style={{
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                backgroundColor: isConnected ? '#10b981' : '#ef4444',
                marginRight: '12px',
                boxShadow: `0 0 12px ${isConnected ? '#10b981' : '#ef4444'}40`
              }} />
              <h3 style={{
                color: '#ffffff',
                fontSize: '1.25rem',
                fontWeight: '600',
                margin: 0,
                letterSpacing: '-0.01em'
              }}>
                System Status
              </h3>
            </div>
            <div style={{
              fontSize: '1.75rem',
              fontWeight: '700',
              marginBottom: '16px',
              color: isConnected ? '#10b981' : '#ef4444',
              letterSpacing: '-0.02em'
            }}>
              {isConnected ? 'OPERATIONAL' : 'OFFLINE'}
            </div>
            <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6' }}>
              <div style={{ marginBottom: '8px' }}>
                <span style={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: '500' }}>Frontend:</span> React {isConnected ? 'Connected' : 'Disconnected'}
              </div>
              <div style={{ marginBottom: '8px' }}>
                <span style={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: '500' }}>Backend:</span> Flask {systemStatus}
              </div>
              <div>
                <span style={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: '500' }}>Last Update:</span> {new Date().toLocaleTimeString()}
              </div>
            </div>
          </div>

          {/* GPU Status Card */}
          <div style={{
            padding: '28px',
            background: 'rgba(255, 255, 255, 0.04)',
            backdropFilter: 'blur(20px)',
            borderRadius: '20px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
            position: 'relative',
            overflow: 'hidden'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)';
            e.currentTarget.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.2)';
            e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.3)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.12)';
            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
          }}
          >
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '4px',
              background: 'linear-gradient(90deg, #3b82f6, #60a5fa)'
            }} />
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
              <div style={{
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                backgroundColor: '#3b82f6',
                marginRight: '12px',
                boxShadow: '0 0 12px #3b82f640'
              }} />
              <h3 style={{
                color: '#ffffff',
                fontSize: '1.25rem',
                fontWeight: '600',
                margin: 0,
                letterSpacing: '-0.01em'
              }}>
                GPU Acceleration
              </h3>
            </div>
            <div style={{
              fontSize: '1.75rem',
              fontWeight: '700',
              marginBottom: '16px',
              color: '#3b82f6',
              letterSpacing: '-0.02em'
            }}>
              {gpuStatus}
            </div>
            <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6' }}>
              <div style={{ marginBottom: '8px' }}>
                <span style={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: '500' }}>WebGL Graphics:</span> Enabled
              </div>
              <div style={{ marginBottom: '8px' }}>
                <span style={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: '500' }}>ML Processing:</span> {gpuStatus}
              </div>
              <div>
                <span style={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: '500' }}>Performance:</span> Optimized
              </div>
            </div>
          </div>

          {/* ML Engine Card */}
          <div style={{
            padding: '28px',
            background: 'rgba(255, 255, 255, 0.04)',
            backdropFilter: 'blur(20px)',
            borderRadius: '20px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
            position: 'relative',
            overflow: 'hidden'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)';
            e.currentTarget.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.2)';
            e.currentTarget.style.borderColor = 'rgba(139, 92, 246, 0.3)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.12)';
            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
          }}
          >
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '4px',
              background: 'linear-gradient(90deg, #8b5cf6, #a78bfa)'
            }} />
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
              <div style={{
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                backgroundColor: '#8b5cf6',
                marginRight: '12px',
                boxShadow: '0 0 12px #8b5cf640'
              }} />
              <h3 style={{
                color: '#ffffff',
                fontSize: '1.25rem',
                fontWeight: '600',
                margin: 0,
                letterSpacing: '-0.01em'
              }}>
                ML Engine
              </h3>
            </div>
            <div style={{
              fontSize: '1.75rem',
              fontWeight: '700',
              marginBottom: '16px',
              color: '#8b5cf6',
              letterSpacing: '-0.02em'
            }}>
              96% Confidence
            </div>
            <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6' }}>
              <div style={{ marginBottom: '8px' }}>
                <span style={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: '500' }}>TensorFlow:</span> {gpuStatus}
              </div>
              <div style={{ marginBottom: '8px' }}>
                <span style={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: '500' }}>Predictions:</span> Real-time
              </div>
              <div>
                <span style={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: '500' }}>Response:</span> ~3ms
              </div>
            </div>
          </div>
        </div>

        {/* Binance.US Account Balance - Enhanced Card */}
        <div style={{
          padding: '32px',
          background: 'rgba(255, 255, 255, 0.04)',
          backdropFilter: 'blur(20px)',
          borderRadius: '20px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
          position: 'relative',
          overflow: 'hidden',
          marginBottom: '32px'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.2)';
          e.currentTarget.style.borderColor = 'rgba(255, 215, 0, 0.3)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.12)';
          e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
        }}
        >
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '4px',
            background: 'linear-gradient(90deg, #ffd700, #ffed4e)'
          }} />
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '24px', justifyContent: 'center' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: '#ffd700',
              marginRight: '12px',
              boxShadow: '0 0 12px #ffd70040'
            }} />
            <h3 style={{
              color: '#ffd700',
              fontSize: '1.25rem',
              fontWeight: '600',
              margin: 0,
              letterSpacing: '-0.01em'
            }}>
              Binance.US Account Balance
            </h3>
          </div>
          {typeof accountBalance.USD === 'undefined' ? (
            <div style={{ color: '#ffd700', fontSize: '1.2rem', margin: '24px 0' }}>
              Loading account balance...
            </div>
          ) : (
            <>
              {/* Main currencies */}
              <div style={{ marginBottom: '12px' }}>
                <h4 style={{ 
                  color: 'rgba(255, 255, 255, 0.7)', 
                  fontSize: '1rem',
                  fontWeight: '600',
                  marginBottom: '12px',
                  borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                  paddingBottom: '8px'
                }}>
                  Main Currencies
                </h4>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '16px',
                  marginBottom: '20px'
                }}>
                  <div style={{
                    padding: '16px',
                    background: 'rgba(255, 215, 0, 0.1)',
                    borderRadius: '12px',
                    border: '1px solid rgba(255, 215, 0, 0.3)',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '8px' }}>USD</div>
                    <div style={{ fontSize: '1.4rem', fontWeight: '700', color: '#ffd700' }}>
                      ${typeof accountBalance.USD === 'number' ? accountBalance.USD.toLocaleString() : '0.00'}
                    </div>
                  </div>
                  <div style={{
                    padding: '16px',
                    background: 'rgba(247, 147, 26, 0.1)',
                    borderRadius: '12px',
                    border: '1px solid rgba(247, 147, 26, 0.3)',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '8px' }}>BTC</div>
                    <div style={{ fontSize: '1.4rem', fontWeight: '700', color: '#f7931a' }}>
                      {typeof accountBalance.BTC === 'number' ? accountBalance.BTC.toFixed(5) : '0.00000'}
                    </div>
                  </div>
                  <div style={{
                    padding: '16px',
                    background: 'rgba(98, 126, 234, 0.1)',
                    borderRadius: '12px',
                    border: '1px solid rgba(98, 126, 234, 0.3)',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '8px' }}>ETH</div>
                    <div style={{ fontSize: '1.4rem', fontWeight: '700', color: '#627eea' }}>
                      {typeof accountBalance.ETH === 'number' ? accountBalance.ETH.toFixed(4) : '0.0000'}
                    </div>
                  </div>
                  <div style={{
                    padding: '16px',
                    background: 'rgba(240, 185, 11, 0.1)',
                    borderRadius: '12px',
                    border: '1px solid rgba(240, 185, 11, 0.3)',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '8px' }}>BNB</div>
                    <div style={{ fontSize: '1.4rem', fontWeight: '700', color: '#f0b90b' }}>
                      {typeof accountBalance.BNB === 'number' ? accountBalance.BNB.toFixed(2) : '0.00'}
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Stablecoins */}
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ 
                  color: 'rgba(255, 255, 255, 0.7)', 
                  fontSize: '1rem',
                  fontWeight: '600',
                  marginBottom: '12px',
                  borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                  paddingBottom: '8px'
                }}>
                  Stablecoins
                </h4>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                  gap: '16px'
                }}>
                  <div style={{
                    padding: '16px',
                    background: 'rgba(38, 161, 123, 0.1)',
                    borderRadius: '12px',
                    border: '1px solid rgba(38, 161, 123, 0.3)',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '8px' }}>USDT</div>
                    <div style={{ fontSize: '1.4rem', fontWeight: '700', color: '#26a17b' }}>
                      {typeof accountBalance.USDT === 'number' ? accountBalance.USDT.toFixed(2) : '0.00'}
                    </div>
                  </div>
                  <div style={{
                    padding: '16px',
                    background: 'rgba(39, 117, 202, 0.1)',
                    borderRadius: '12px',
                    border: '1px solid rgba(39, 117, 202, 0.3)',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '8px' }}>USDC</div>
                    <div style={{ fontSize: '1.4rem', fontWeight: '700', color: '#2775ca' }}>
                      {typeof accountBalance.USDC === 'number' ? accountBalance.USDC.toFixed(2) : '0.00'}
                    </div>
                  </div>
                  <div style={{
                    padding: '16px',
                    background: 'rgba(240, 185, 11, 0.1)',
                    borderRadius: '12px',
                    border: '1px solid rgba(240, 185, 11, 0.3)',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '8px' }}>BUSD</div>
                    <div style={{ fontSize: '1.4rem', fontWeight: '700', color: '#f0b90b' }}>
                      {typeof accountBalance.BUSD === 'number' ? accountBalance.BUSD.toFixed(2) : '0.00'}
                    </div>
                  </div>
                  <div style={{
                    padding: '16px',
                    background: 'rgba(254, 156, 77, 0.1)',
                    borderRadius: '12px',
                    border: '1px solid rgba(254, 156, 77, 0.3)',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '8px' }}>DAI</div>
                    <div style={{ fontSize: '1.4rem', fontWeight: '700', color: '#fe9c4d' }}>
                      {typeof accountBalance.DAI === 'number' ? accountBalance.DAI.toFixed(2) : '0.00'}
                    </div>
                  </div>
                  <div style={{
                    padding: '16px',
                    background: 'rgba(0, 156, 225, 0.1)',
                    borderRadius: '12px',
                    border: '1px solid rgba(0, 156, 225, 0.3)',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '8px' }}>TUSD</div>
                    <div style={{ fontSize: '1.4rem', fontWeight: '700', color: '#009ce1' }}>
                      {typeof accountBalance.TUSD === 'number' ? accountBalance.TUSD.toFixed(2) : '0.00'}
                    </div>
                  </div>
                  <div style={{
                    padding: '16px',
                    background: 'rgba(71, 144, 240, 0.1)',
                    borderRadius: '12px',
                    border: '1px solid rgba(71, 144, 240, 0.3)',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '8px' }}>USDP</div>
                    <div style={{ fontSize: '1.4rem', fontWeight: '700', color: '#4790f0' }}>
                      {typeof accountBalance.USDP === 'number' ? accountBalance.USDP.toFixed(2) : '0.00'}
                    </div>
                  </div>
                </div>
              </div>
              {/* Total portfolio value */}
              <div style={{
                textAlign: 'center',
                padding: '16px',
                background: 'rgba(120, 255, 198, 0.1)',
                borderRadius: '12px',
                border: '1px solid rgba(120, 255, 198, 0.3)'
              }}>
                <div style={{ fontSize: '1.1rem', color: 'rgba(255, 255, 255, 0.8)', marginBottom: '8px' }}>
                  Total Portfolio Value
                </div>
                <div style={{ fontSize: '2rem', fontWeight: '800', color: '#78ffc6' }}>
                  ${typeof accountBalance.totalUSD === 'number' ? accountBalance.totalUSD.toLocaleString() : '0.00'}
                </div>
                {accountBalance.last_updated && (
                  <div style={{ 
                    fontSize: '0.8rem', 
                    color: 'rgba(255, 255, 255, 0.5)', 
                    marginTop: '8px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '4px' 
                  }}>
                    <span>Last updated: {new Date(accountBalance.last_updated).toLocaleTimeString()}</span>
                    {accountBalance.source && accountBalance.source.includes('Demo') && (
                      <span style={{ 
                        background: 'rgba(239, 68, 68, 0.2)',
                        color: '#ef4444',
                        fontSize: '0.7rem',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        fontWeight: '600'
                      }}>
                        DEMO
                      </span>
                    )}
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        {/* Trade Tracking System - Enhanced Card */}
        <div style={{
          padding: '32px',
          background: 'rgba(255, 255, 255, 0.04)',
          backdropFilter: 'blur(20px)',
          borderRadius: '20px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
          position: 'relative',
          overflow: 'hidden',
          marginBottom: '32px'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.2)';
          e.currentTarget.style.borderColor = 'rgba(120, 119, 198, 0.3)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.12)';
          e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
        }}
        >
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '4px',
            background: 'linear-gradient(90deg, #7c77c6, #9f9fed)'
          }} />
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '24px' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: '#7c77c6',
              marginRight: '12px',
              boxShadow: '0 0 12px #7c77c640'
            }} />
            <h3 style={{
              color: '#7c77c6',
              fontSize: '1.25rem',
              fontWeight: '600',
              margin: 0,
              letterSpacing: '-0.01em'
            }}>
              Live Trade Tracking
            </h3>
          </div>
          
          <div style={{ overflowX: 'auto' }}>
            {recentTrades && recentTrades.length > 0 ? (
              <table style={{ 
                width: '100%', 
                borderCollapse: 'collapse',
                fontSize: '0.9rem'
              }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid rgba(65, 105, 225, 0.3)' }}>
                    <th style={{ padding: '12px 8px', textAlign: 'left', color: '#4169e1', fontWeight: '600' }}>Coin</th>
                    <th style={{ padding: '12px 8px', textAlign: 'left', color: '#4169e1', fontWeight: '600' }}>Type</th>
                    <th style={{ padding: '12px 8px', textAlign: 'center', color: '#4169e1', fontWeight: '600' }}>Price</th>
                    <th style={{ padding: '12px 8px', textAlign: 'center', color: '#4169e1', fontWeight: '600' }}>Quantity</th>
                    <th style={{ padding: '12px 8px', textAlign: 'center', color: '#4169e1', fontWeight: '600' }}>Status</th>
                    <th style={{ padding: '12px 8px', textAlign: 'center', color: '#4169e1', fontWeight: '600' }}>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {recentTrades.map((trade) => (
                    <tr key={trade.id || trade.orderId} style={{ 
                      borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                      background: trade.status === 'ACTIVE' ? 'rgba(120, 255, 198, 0.05)' : 'transparent'
                    }}>
                      <td style={{ padding: '16px 8px' }}>{trade.coin || trade.symbol || '-'}</td>
                      <td style={{ padding: '16px 8px' }}>{trade.type || '-'}</td>
                      <td style={{ padding: '16px 8px', textAlign: 'center' }}>{typeof trade.price === 'number' ? trade.price.toLocaleString() : '-'}</td>
                      <td style={{ padding: '16px 8px', textAlign: 'center' }}>{typeof trade.quantity === 'number' ? trade.quantity.toLocaleString() : '-'}</td>
                      <td style={{ padding: '16px 8px', textAlign: 'center' }}>{trade.status || '-'}</td>
                      <td style={{ padding: '16px 8px', textAlign: 'center' }}>{trade.timestamp ? new Date(trade.timestamp).toLocaleString() : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div style={{ color: '#4169e1', fontSize: '1.1rem', padding: '32px 0' }}>
                No trades found. Your account has no recent trading activity.
              </div>
            )}
          </div>
        </div>

        {/* Control Panel - Enhanced Card */}
        <div style={{
          padding: '32px',
          background: 'rgba(255, 255, 255, 0.04)',
          backdropFilter: 'blur(20px)',
          borderRadius: '20px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
          position: 'relative',
          overflow: 'hidden',
          textAlign: 'center'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.2)';
          e.currentTarget.style.borderColor = 'rgba(255, 102, 0, 0.3)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.12)';
          e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
        }}
        >
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '4px',
            background: 'linear-gradient(90deg, #ff6600, #ff8533)'
          }} />
          <h2 style={{
            color: '#ff6600',
            fontSize: '1.5rem',
            fontWeight: '700',
            marginBottom: '16px',
            letterSpacing: '-0.02em'
          }}>
            Trading Control Panel
          </h2>
          <p style={{
            marginBottom: '28px',
            fontSize: '1.1rem',
            color: 'rgba(255, 255, 255, 0.8)',
            lineHeight: '1.5'
          }}>
            GPU-accelerated system ready. {isConnected ? 'All systems operational.' : 'Check backend connection.'}
          </p>
          
          <div style={{ marginBottom: '20px' }}>
            <AutoTradeToggle isEnabled={tradingActive} onToggle={toggleLiveTrading} />
          </div>
          
          <div style={{ marginTop: '20px' }}>
            <LiveTradeTracker trades={recentTrades} />
          </div>
          
          <div style={{ 
            display: 'flex', 
            gap: '16px', 
            justifyContent: 'center', 
            flexWrap: 'wrap',
            marginTop: '20px'
          }}>
            <button 
              onClick={toggleLiveTrading}
              style={{
                background: tradingActive 
                  ? 'linear-gradient(135deg, #ef4444 0%, #f87171 100%)'
                  : 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
                color: '#ffffff',
                padding: '16px 32px',
                border: 'none',
                borderRadius: '12px',
                fontSize: '1.1rem',
                fontWeight: '700',
                cursor: 'pointer',
                boxShadow: `0 4px 20px ${tradingActive ? 'rgba(255, 68, 68, 0.4)' : 'rgba(120, 255, 198, 0.4)'}`,
                transition: 'all 0.3s ease',
                backdropFilter: 'blur(10px)'
              }}
              disabled={!isConnected}
            >
              {tradingActive ? '🛑 Stop Trading' : '▶️ Start Live Trading'}
            </button>
            
            <button 
              onClick={openGPUDashboard}
              style={{
                background: 'linear-gradient(135deg, #4169e1 0%, #1e90ff 100%)',
                color: '#ffffff',
                padding: '16px 32px',
                border: 'none',
                borderRadius: '12px',
                fontSize: '1.1rem',
                fontWeight: '700',
                cursor: 'pointer',
                boxShadow: '0 4px 20px rgba(120, 119, 198, 0.4)',
                transition: 'all 0.3s ease',
                backdropFilter: 'blur(10px)'
              }}
            >
              🎮 GPU Dashboard
            </button>
            
            <button 
              onClick={fetchBackendData}
              style={{
                background: 'linear-gradient(135deg, #1e90ff 0%, #00bfff 100%)',
                color: '#000000',
                padding: '16px 32px',
                border: 'none',
                borderRadius: '12px',
                fontSize: '1.1rem',
                fontWeight: '700',
                cursor: 'pointer',
                boxShadow: '0 4px 20px rgba(255, 119, 198, 0.4)',
                transition: 'all 0.3s ease',
                backdropFilter: 'blur(10px)'
              }}
            >
              🔄 Refresh Status
            </button>
          </div>
        </div>

        {/* System Metrics */}
        {backendData && (
          <div style={{
            marginTop: '24px',
            padding: '24px',
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            borderRadius: '16px',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <h3 style={{ 
              color: '#78ffc6', 
              fontSize: '1.2rem',
              fontWeight: '600',
              marginBottom: '16px'
            }}>
              📊 Real-time System Metrics
            </h3>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '16px',
              fontSize: '0.95rem',
              color: 'rgba(255, 255, 255, 0.8)'
            }}>
              <div>
                <span style={{ color: '#7c77c6', fontWeight: '600' }}>GPU:</span> {backendData.gpu_acceleration ? 'Enabled' : 'CPU Only'}
              </div>
              <div>
                <span style={{ color: '#ff77c6', fontWeight: '600' }}>Components:</span> All Operational
              </div>
              <div>
                <span style={{ color: '#78ffc6', fontWeight: '600' }}>Trading:</span> {tradingActive ? 'ACTIVE' : 'STANDBY'}
              </div>
              <div>
                <span style={{ color: '#ffaa00', fontWeight: '600' }}>Connection:</span> {isConnected ? 'Stable' : 'Unstable'}
              </div>
            </div>
          </div>
        )}
      </div>
      </div>
    </>
  );
}