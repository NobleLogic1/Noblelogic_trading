import React, { useState, useEffect } from 'react';

const ManualTradeForm = () => {
  const [symbol, setSymbol] = useState('BTCUSD');
  const [side, setSide] = useState('BUY');
  const [quantity, setQuantity] = useState(0.001);
  const [orderType, setOrderType] = useState('MARKET');
  const [price, setPrice] = useState('');
  const [currentPrice, setCurrentPrice] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [tradeResult, setTradeResult] = useState(null);
  const [liveMode, setLiveMode] = useState(false);
  const [availableSymbols, setAvailableSymbols] = useState([
    'BTCUSD', 'ETHUSD', 'BNBUSD', 'ADAUSD', 'XRPUSD', 'SOLUSD', 
    'DOGEUSD', 'DOTUSD', 'AVAXUSD', 'MATICUSD'
  ]);

  // Fetch current price
  useEffect(() => {
    if (symbol) {
      fetchCurrentPrice();
    }
  }, [symbol]);

  const fetchCurrentPrice = async () => {
    try {
      const response = await fetch(`http://localhost:3001/api/market-price/${symbol}`);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setCurrentPrice(data.price);
          // Set default limit price to current price
          if (orderType === 'LIMIT') {
            setPrice(data.price);
          }
        }
      }
    } catch (error) {
      console.error('Error fetching price:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setTradeResult(null);

    try {
      // Prepare trade data
      const tradeData = {
        symbol,
        side,
        quantity: parseFloat(quantity),
        type: orderType,
        live_mode: liveMode
      };

      // Add price for LIMIT orders
      if (orderType === 'LIMIT') {
        tradeData.price = parseFloat(price);
      }

      // Execute the trade
      const response = await fetch('http://localhost:3001/api/execute-trade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(tradeData),
      });

      const result = await response.json();
      setTradeResult(result);
      
      // If trade successful, refresh price
      if (result.success) {
        fetchCurrentPrice();
      }
    } catch (error) {
      setTradeResult({
        success: false,
        message: error.message || 'Failed to execute trade'
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      padding: '24px',
      background: 'rgba(255, 255, 255, 0.05)',
      backdropFilter: 'blur(20px)',
      borderRadius: '16px',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      marginBottom: '24px'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px'
      }}>
        <h3 style={{ margin: 0, color: '#ffffff', fontSize: '1.3rem' }}>
          🛒 Manual Trading
        </h3>
        <div style={{
          padding: '8px 12px',
          borderRadius: '8px',
          background: liveMode ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)',
          color: liveMode ? '#ef4444' : '#10b981',
          fontWeight: '600',
          fontSize: '0.9rem'
        }}>
          {liveMode ? '🔴 LIVE MODE' : '🟢 DEMO MODE'}
        </div>
      </div>

      {currentPrice && (
        <div style={{
          marginBottom: '20px',
          padding: '12px',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.7)' }}>
            Current {symbol} Price
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#3b82f6' }}>
            ${currentPrice.toLocaleString()}
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '16px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'rgba(255, 255, 255, 0.7)' }}>
              Symbol
            </label>
            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                color: 'white'
              }}
            >
              {availableSymbols.map(sym => (
                <option key={sym} value={sym}>{sym}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'rgba(255, 255, 255, 0.7)' }}>
              Side
            </label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                type="button"
                onClick={() => setSide('BUY')}
                style={{
                  flex: 1,
                  padding: '10px',
                  background: side === 'BUY' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(255, 255, 255, 0.05)',
                  border: `1px solid ${side === 'BUY' ? 'rgba(16, 185, 129, 0.5)' : 'rgba(255, 255, 255, 0.1)'}`,
                  borderRadius: '8px',
                  color: side === 'BUY' ? '#10b981' : 'white',
                  fontWeight: side === 'BUY' ? '700' : '400',
                  cursor: 'pointer'
                }}
              >
                BUY
              </button>
              <button
                type="button"
                onClick={() => setSide('SELL')}
                style={{
                  flex: 1,
                  padding: '10px',
                  background: side === 'SELL' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(255, 255, 255, 0.05)',
                  border: `1px solid ${side === 'SELL' ? 'rgba(239, 68, 68, 0.5)' : 'rgba(255, 255, 255, 0.1)'}`,
                  borderRadius: '8px',
                  color: side === 'SELL' ? '#ef4444' : 'white',
                  fontWeight: side === 'SELL' ? '700' : '400',
                  cursor: 'pointer'
                }}
              >
                SELL
              </button>
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'rgba(255, 255, 255, 0.7)' }}>
              Order Type
            </label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                type="button"
                onClick={() => setOrderType('MARKET')}
                style={{
                  flex: 1,
                  padding: '10px',
                  background: orderType === 'MARKET' ? 'rgba(99, 102, 241, 0.3)' : 'rgba(255, 255, 255, 0.05)',
                  border: `1px solid ${orderType === 'MARKET' ? 'rgba(99, 102, 241, 0.5)' : 'rgba(255, 255, 255, 0.1)'}`,
                  borderRadius: '8px',
                  color: orderType === 'MARKET' ? '#6366f1' : 'white',
                  fontWeight: orderType === 'MARKET' ? '700' : '400',
                  cursor: 'pointer'
                }}
              >
                MARKET
              </button>
              <button
                type="button"
                onClick={() => setOrderType('LIMIT')}
                style={{
                  flex: 1,
                  padding: '10px',
                  background: orderType === 'LIMIT' ? 'rgba(99, 102, 241, 0.3)' : 'rgba(255, 255, 255, 0.05)',
                  border: `1px solid ${orderType === 'LIMIT' ? 'rgba(99, 102, 241, 0.5)' : 'rgba(255, 255, 255, 0.1)'}`,
                  borderRadius: '8px',
                  color: orderType === 'LIMIT' ? '#6366f1' : 'white',
                  fontWeight: orderType === 'LIMIT' ? '700' : '400',
                  cursor: 'pointer'
                }}
              >
                LIMIT
              </button>
            </div>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'rgba(255, 255, 255, 0.7)' }}>
              Quantity
            </label>
            <input
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              min="0.0001"
              step="0.0001"
              required
              style={{
                width: '100%',
                padding: '10px',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                color: 'white'
              }}
            />
          </div>
        </div>

        {orderType === 'LIMIT' && (
          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'rgba(255, 255, 255, 0.7)' }}>
              Limit Price (USD)
            </label>
            <input
              type="number"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              min="0.01"
              step="0.01"
              required
              style={{
                width: '100%',
                padding: '10px',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                color: 'white'
              }}
            />
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '16px', alignItems: 'center' }}>
          <div>
            <label style={{ 
              position: 'relative', 
              display: 'inline-block',
              width: '52px',
              height: '28px'
            }}>
              <input
                type="checkbox"
                checked={liveMode}
                onChange={(e) => setLiveMode(e.target.checked)}
                style={{
                  opacity: 0,
                  width: 0,
                  height: 0
                }}
              />
              <span style={{
                position: 'absolute',
                cursor: 'pointer',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: liveMode ? '#ef4444' : '#10b981',
                transition: '.4s',
                borderRadius: '34px'
              }}>
                <span style={{
                  position: 'absolute',
                  content: '""',
                  height: '20px',
                  width: '20px',
                  left: '4px',
                  bottom: '4px',
                  backgroundColor: 'white',
                  transition: '.4s',
                  borderRadius: '50%',
                  transform: liveMode ? 'translateX(24px)' : 'translateX(0)'
                }}></span>
              </span>
            </label>
          </div>
          <div style={{ color: liveMode ? '#ef4444' : '#10b981', fontWeight: '600' }}>
            {liveMode ? '⚠️ LIVE MODE - REAL FUNDS WILL BE USED' : '🔒 Demo Mode - No real trades'}
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          style={{
            padding: '14px',
            background: side === 'BUY' ? 'rgba(16, 185, 129, 0.8)' : 'rgba(239, 68, 68, 0.8)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontWeight: '700',
            fontSize: '1.1rem',
            cursor: isLoading ? 'wait' : 'pointer',
            opacity: isLoading ? 0.7 : 1
          }}
        >
          {isLoading ? 'Processing...' : `${side} ${symbol}`}
        </button>
      </form>

      {tradeResult && (
        <div style={{
          marginTop: '20px',
          padding: '16px',
          background: tradeResult.success ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
          border: `1px solid ${tradeResult.success ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
          borderRadius: '8px',
          color: tradeResult.success ? '#10b981' : '#ef4444'
        }}>
          <div style={{ fontWeight: '700', marginBottom: '8px' }}>
            {tradeResult.success ? '✅ Trade Executed' : '❌ Trade Failed'}
          </div>
          <div>{tradeResult.message}</div>
          {tradeResult.success && tradeResult.order && (
            <div style={{ marginTop: '12px', fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.7)' }}>
              <div>Order ID: {tradeResult.order.orderId}</div>
              <div>Status: {tradeResult.order.status}</div>
              {tradeResult.demo_mode && (
                <div style={{ color: '#10b981', fontWeight: '600', marginTop: '8px' }}>
                  ℹ️ Demo trade - no real funds used
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ManualTradeForm;