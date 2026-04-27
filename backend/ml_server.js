const fs = require('fs');
const path = require('path');

function updateStrategyOutput(strategies) {
  fs.writeFileSync('./strategy_output.json', JSON.stringify(strategies, null, 2));
}

function updateHealthStatus(accuracy) {
  const status = {
    accuracy: accuracy,
    status: accuracy >= 0.75 ? 'Optimal' : 'Warning',
    timestamp: new Date().toISOString()
  };
  fs.writeFileSync('./health_status.json', JSON.stringify(status, null, 2));
}

function logTrade(trade) {
  const filePath = './trade_log.json';
  const existing = fs.existsSync(filePath) ? JSON.parse(fs.readFileSync(filePath)) : [];
  existing.push(trade);
  fs.writeFileSync(filePath, JSON.stringify(existing, null, 2));
}

module.exports = {
  updateStrategyOutput,
  updateHealthStatus,
  logTrade
};