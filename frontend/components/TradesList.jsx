import React from 'react';

const TradesList = ({ trades, onTradeSelect, selectedTrade }) => {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatConfidence = (confidence) => {
    return `${(confidence * 100).toFixed(1)}%`;
  };

  const getTradeStatusClass = (trade) => {
    const profitDiff = trade.realizedProfit - trade.predictedProfit;
    if (Math.abs(profitDiff) < trade.predictedProfit * 0.1) return 'success';
    if (trade.realizedProfit > 0) return 'warning';
    return 'danger';
  };

  return (
    <div className="trade-list-container">
      <div className="panel-header">
        <h2>Recent Trades</h2>
      </div>
      <div className="trade-list">
        {trades.map((trade) => (
          <div
            key={trade.id}
            className={`trade-item ${selectedTrade?.id === trade.id ? 'selected' : ''} ${getTradeStatusClass(trade)}`}
            onClick={() => onTradeSelect(trade)}
          >
            <div className="trade-item-header">
              <span className="trade-symbol">{trade.symbol}</span>
              <span className="trade-timestamp">
                {new Date(trade.timestamp).toLocaleTimeString()}
              </span>
            </div>
            
            <div className="trade-details-grid">
              <div className="trade-detail">
                <label>Type:</label>
                <span className={`trade-type ${trade.side.toLowerCase()}`}>
                  {trade.side}
                </span>
              </div>
              
              <div className="trade-detail">
                <label>Quantity:</label>
                <span>{trade.quantity}</span>
              </div>
              
              <div className="trade-detail">
                <label>Price:</label>
                <span>{formatCurrency(trade.price)}</span>
              </div>
              
              <div className="trade-detail">
                <label>Predicted Profit:</label>
                <span className="predicted-profit">
                  {formatCurrency(trade.predictedProfit)}
                </span>
              </div>
              
              <div className="trade-detail">
                <label>Realized Profit:</label>
                <span className={`realized-profit ${trade.realizedProfit >= 0 ? 'positive' : 'negative'}`}>
                  {formatCurrency(trade.realizedProfit)}
                </span>
              </div>
              
              <div className="trade-detail">
                <label>Confidence:</label>
                <div className="confidence-wrapper">
                  <div className="confidence-meter">
                    <div 
                      className="confidence-fill"
                      style={{ width: `${trade.confidence * 100}%` }}
                    />
                  </div>
                  <span className="confidence-value">
                    {formatConfidence(trade.confidence)}
                  </span>
                </div>
              </div>
            </div>

            {trade.notes && (
              <div className="trade-notes">
                <i className="trade-notes-icon" />
                {trade.notes}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default TradesList;