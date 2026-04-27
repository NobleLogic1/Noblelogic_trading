// Test mode initialization helper
function initializeTestMode(monitor) {
    const PerformanceAnalyzer = require('./utils/performance_analyzer');
    
    // Initialize metrics collector if not already initialized
    if (!monitor.metricsCollector) {
        const TestMetricsCollector = require('./utils/test_metrics_collector');
        monitor.metricsCollector = new TestMetricsCollector();
    }
    
    // Initialize performance analyzer
    monitor.performanceAnalyzer = new PerformanceAnalyzer(monitor.metricsCollector, monitor);
    
    console.log('Starting test mode with $100 initial balance');
    console.log('Performance analysis will be generated after 10 minutes');
    
    // Start collecting metrics
    monitor.testEnv = {
        balance: 100, // $100 initial balance
        positions: new Map(),
        orderHistory: [],
        tradeHistory: [],
        fees: { maker: 0.001, taker: 0.001 },
        slippage: 0.001,
        timestamp: Date.now(),
        priceData: new Map(),
        testMetrics: {
            totalTrades: 0,
            successfulTrades: 0,
            failedTrades: 0,
            profitFactor: 0,
            sharpeRatio: 0,
            maxDrawdown: 0,
            winRate: 0,
            averageWin: 0,
            averageLoss: 0,
            largestWin: 0,
            largestLoss: 0
        }
    };
}

module.exports = { initializeTestMode };