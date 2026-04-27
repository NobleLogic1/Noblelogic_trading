import React from 'react';

export default function LiveTradeTracker({ trades }) {

  // Format timestamp to readable date
  const formatDate = (timestamp) => {
    if (!timestamp) return 'Unknown';
    const date = new Date(timestamp);
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
  };

  // Calculate profit/loss class
  const getPnlClass = (pnl) => {
    if (!pnl) return '';
    return parseFloat(pnl) >= 0 ? 'positive-pnl' : 'negative-pnl';
  };

  return (
    <div className="panel" style={{ maxHeight: '400px', overflow: 'auto' }}>
      <h2>📊 Live Trade Tracking</h2>
      
      {trades.length === 0 && (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          No recent trade activity.
        </div>
      )}
      
      {trades.length > 0 && (
        <>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #2f3542' }}>
                <th style={{ textAlign: 'left', padding: '8px' }}>Type</th>
                <th style={{ textAlign: 'left', padding: '8px' }}>Symbol</th>
                <th style={{ textAlign: 'right', padding: '8px' }}>Price</th>
                <th style={{ textAlign: 'right', padding: '8px' }}>Size</th>
                <th style={{ textAlign: 'right', padding: '8px' }}>P&L</th>
                <th style={{ textAlign: 'right', padding: '8px' }}>Time</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((trade) => (
                <tr key={trade.id || trade.orderId} style={{ borderBottom: '1px solid #1e272e' }}>
                  <td style={{ 
                    padding: '8px',
                    color: trade.isBuyer ? '#2ed573' : '#ff6b81'
                  }}>
                    {trade.isBuyer ? '🟢 BUY' : '🔴 SELL'}
                  </td>
                  <td style={{ padding: '8px' }}>{trade.symbol || 'Unknown'}</td>
                  <td style={{ textAlign: 'right', padding: '8px' }}>
                    ${parseFloat(trade.price).toFixed(2)}
                  </td>
                  <td style={{ textAlign: 'right', padding: '8px' }}>
                    {parseFloat(trade.qty).toFixed(4)}
                  </td>
                  <td style={{ 
                    textAlign: 'right', 
                    padding: '8px',
                    className: getPnlClass(trade.pnl)
                  }}>
                    {trade.pnl ? `$${parseFloat(trade.pnl).toFixed(2)}` : '-'}
                  </td>
                  <td style={{ textAlign: 'right', padding: '8px' }}>{formatDate(trade.time)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}