const express = require('express');
const fs = require('fs');
const cors = require('cors');
const { initializeTestMode } = require('./test_mode');
const BinanceMonitor = require('./utils/binance_monitor');

const app = express();
const PORT = 3001;

// Configure CORS more securely
const corsOptions = {
  origin: ['http://localhost:5173', 'http://127.0.0.1:5173'], // Only allow frontend origins
  methods: ['GET', 'POST'],
  credentials: false
};

app.use(cors(corsOptions));
app.use(express.json({ limit: '10mb' })); // Limit request size

// Helper function to safely read JSON files
function safeReadJSON(filePath, defaultValue = []) {
  try {
    if (!fs.existsSync(filePath)) {
      return defaultValue;
    }
    const data = fs.readFileSync(filePath);
    return JSON.parse(data);
  } catch (error) {
    console.error(`Error reading ${filePath}:`, error.message);
    return defaultValue;
  }
}

// Input validation helper
function validateFileExists(filePath) {
  return fs.existsSync(filePath);
}

// Initialize monitor in test mode
const monitor = new BinanceMonitor(true); // Start in test mode
initializeTestMode(monitor);

// Initialize the monitor
monitor.initialize().then(() => {
    console.log('Trading monitor initialized in test mode');
    monitor.setAutoTradeEnabled(true);
}).catch(error => {
    console.error('Error initializing monitor:', error);
});

app.get('/api/strategy', (req, res) => {
  try {
    const data = safeReadJSON('./strategy_output.json', { strategy: 'Unknown', confidence: 0, active: false });
    res.json(data);
  } catch (error) {
    console.error('Strategy endpoint error:', error);
    res.status(500).json({ error: 'Failed to load strategy data' });
  }
});

app.get('/api/health', (req, res) => {
  try {
    const data = safeReadJSON('./health_status.json', { accuracy: 0, status: 'Unknown' });
    res.json(data);
  } catch (error) {
    console.error('Health endpoint error:', error);
    res.status(500).json({ error: 'Failed to load health data' });
  }
});

app.get('/api/trades', (req, res) => {
  try {
    const trades = safeReadJSON('./trade_log.json', []);
    // Validate and sanitize trade data
    const normalizedTrades = trades.map(trade => {
      if (typeof trade !== 'object' || trade === null) {
        return null;
      }
      return {
        id: trade.id || 'unknown',
        symbol: trade.symbol || trade.coin || 'UNKNOWN',
        status: trade.status || 'Unknown',
        confidence: typeof trade.confidence === 'number' ? trade.confidence : 0,
        strategy: trade.strategy || 'Unknown',
        direction: trade.direction || 'Unknown',
        pnl: typeof trade.pnl === 'number' ? trade.pnl : 0,
        signal: trade.signal || 'Unknown',
        timestamp: trade.timestamp || new Date().toISOString()
      };
    }).filter(trade => trade !== null); // Remove invalid trades
    
    res.json(normalizedTrades);
  } catch (error) {
    console.error('Trades endpoint error:', error);
    res.status(500).json({ error: 'Failed to load trade data' });
  }
});

// Health check endpoint
app.get('/api/status', (req, res) => {
  res.json({ 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Error handler
app.use((error, req, res, next) => {
  console.error('Unhandled error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// New test mode endpoints
app.get('/api/test/status', (req, res) => {
    const status = {
        autoTradeEnabled: monitor.autoTradeEnabled,
        balance: monitor.testEnv.balance,
        activePositions: Array.from(monitor.activePositions.entries()),
        testMetrics: monitor.testEnv.testMetrics,
        startTime: monitor.testEnv.timestamp,
        currentTime: Date.now()
    };
    res.json(status);
});

app.post('/api/test/toggle-trading', (req, res) => {
    const result = monitor.setAutoTradeEnabled(!monitor.autoTradeEnabled);
    res.json(result);
});

app.get('/api/test/performance', (req, res) => {
    if (!monitor.performanceAnalyzer) {
        return res.status(400).json({ error: 'Performance analyzer not initialized' });
    }
    const analysis = monitor.performanceAnalyzer.generateImprovementReport();
    res.json(analysis);
});

app.listen(PORT, () => {
    console.log(`[Backend] Server running on port ${PORT}`);
    console.log('[Test Mode] Starting with $100 initial balance');
    console.log('[Test Mode] Performance report will be generated after 10 minutes of trading');
});