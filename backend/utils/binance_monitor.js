const { Spot } = require('@binance/connector');
const dotenv = require('dotenv');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const mlEngine = spawn('python', ['../ml/ml_engine.py']);

dotenv.config();

class BinanceMonitor {
    constructor(testMode = true, initialTestBalance = 100) {
        this.testMode = testMode;
        
        if (!testMode) {
            const secureKeyManager = require('./secure_key_manager');
            const keys = secureKeyManager.decryptApiKeys();
            
            if (!keys) {
                throw new Error('Failed to load API keys');
            }

            this.client = new Spot(
                keys.apiKey,
                keys.secretKey,
                { 
                    baseURL: 'https://api.binance.us',
                    options: { 
                        adjustForTimeDifference: true,
                        recvWindow: 5000
                    }
                }
            );
        } else {
            // Initialize test environment
            this.testEnv = {
                balance: initialTestBalance,
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

            // Create test client and initialize performance analyzer
            this.client = this.createTestClient();
            const PerformanceAnalyzer = require('./performance_analyzer');
            this.metricsCollector = this.getMetricsCollector();
            this.performanceAnalyzer = new PerformanceAnalyzer(this.metricsCollector, this);
        }
            
            if (!keys) {
                throw new Error('Failed to load API keys');
            }

            this.client = new Spot(
                keys.apiKey,
                keys.secretKey,
                { 
                    baseURL: 'https://api.binance.us',
                    options: { 
                        adjustForTimeDifference: true,
                        recvWindow: 5000
                    }
                }
            );
        } else {
            // Initialize test environment
            this.testEnv = {
                balance: initialTestBalance,
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

            // Create mock client for test mode
            this.client = this.createTestClient();
        }
        
        this.activePositions = new Map();
        this.tradeLog = path.join(__dirname, '../trade_log.json');
        this.autoTradeEnabled = false;

        // Initialize test data storage
        this.testDataPath = path.join(__dirname, '../test_data');
        if (!fs.existsSync(this.testDataPath)) {
            fs.mkdirSync(this.testDataPath);
        }

    }

    createTestClient() {
        const TestClient = require('./test_client');
        return new TestClient(this.testEnv);
    }

    getMetricsCollector() {
        if (!this.testMode) {
            throw new Error('Metrics collector is only available in test mode');
        }
        if (!this.metricsCollector) {
            const TestMetricsCollector = require('./test_metrics_collector');
            this.metricsCollector = new TestMetricsCollector();
        }
        return this.metricsCollector;
        
        // Profit targeting parameters
        this.profitTargets = {
            daily: 500.0,         // $500 daily target
            minimumProfit: 5.0,   // Minimum profit per trade
            totalProfit: 0,
            dailyProfit: 0,
            profitScaling: {
                enabled: true,
                baseTarget: 500.0,
                scalingFactor: 1.1,    // Increase targets by 10% after consistent success
                reductionFactor: 0.9,  // Reduce by 10% after missing targets
                consecutiveHits: 0,
                consecutiveMisses: 0,
                scaleUpThreshold: 5,   // Scale up after 5 consecutive successful days
                scaleDownThreshold: 3,  // Scale down after 3 consecutive misses
                maxDailyTarget: 1000.0, // Cap at $1000 daily
                minDailyTarget: 250.0   // Don't go below $250 daily
            },
            timeBlocks: [
                { start: 0, end: 4, targetMultiplier: 0.5 },    // Reduced activity
                { start: 4, end: 8, targetMultiplier: 0.8 },    // Asian session
                { start: 8, end: 12, targetMultiplier: 1.2 },   // European session
                { start: 12, end: 16, targetMultiplier: 1.5 },  // US session peak
                { start: 16, end: 20, targetMultiplier: 1.2 },  // US session closing
                { start: 20, end: 24, targetMultiplier: 0.8 }   // Evening wind-down
            ]
        };
        
        // Risk management parameters
        this.riskControls = {
            dailyLossLimit: 25.0,          // $25 daily loss limit
            maxDrawdown: 50.0,             // Maximum drawdown allowed
            riskPerTrade: 0.02,            // 2% risk per trade
            maxPositionSize: 0.15,         // 15% of capital per position
            minWinRate: 0.80,              // Minimum 80% win rate required
            maxOpenPositions: 15,          // Maximum number of concurrent positions
            maxDailyTrades: this.calculateOptimalTradeCount(),
            currentDailyLoss: 0,
            dailyTradeCount: 0,
            consecutiveLosses: 0,
            maxConsecutiveLosses: 3,
            lastResetDate: new Date().toDateString(),
            positionRisk: new Map(),       // Track risk for each position
            marketVolatility: new Map(),   // Track volatility per symbol
            adaptivePositionSizing: true   // Enable dynamic position sizing
        };

        // Trading interval parameters
        this.tradingIntervals = {
            min: 1 * 60 * 1000,    // 1 minute minimum for high volatility
            max: 3 * 60 * 1000,    // 3 minutes maximum for low volatility
            normal: 2 * 60 * 1000, // 2 minutes for normal conditions
            current: 2 * 60 * 1000,// Start with normal interval
            lastTradeTime: null,
            intervalTimer: null,
            volatilityThresholds: {
                high: 0.015,        // 1.5% change for high volatility
                low: 0.005         // 0.5% change for low volatility
            },
            marketHours: {
                peak: {start: 12, end: 20},     // UTC hours for peak trading
                off: {start: 2, end: 6}         // UTC hours for reduced trading
            }
        };

        // Trading costs and profitability parameters
        this.tradingCosts = {
            makerFee: 0.001,  // 0.1% maker fee on Binance.US
            takerFee: 0.001,  // 0.1% taker fee on Binance.US
            minProfitMargin: 0.003, // 0.3% minimum profit margin after fees
            gasCost: 0,       // No gas costs on CEX
            slippageEstimate: 0.0005, // 0.05% estimated slippage
            totalFeesPerRoundTrip: 0.0025, // 0.25% total fees for buy+sell
            minimumPriceMovement: 0.002, // 0.2% minimum price movement needed
            dailyFeeTracker: {
                total: 0,
                trades: 0,
                date: new Date().toDateString()
            }
        };
    }

    async initialize() {
        await this.updateAccountBalance();
        this.startPriceStream();
        this.startTradingInterval();
        
        if (this.testMode) {
            console.log('Starting test mode with $100 initial balance');
            console.log('Performance analysis will be generated after 10 minutes');
            // Performance analyzer is already initialized in constructor
        }
    }

    async updateAccountBalance() {
        try {
            const account = await this.client.account();
            this.balance = account.data.balances.find(b => b.asset === 'USDT');
            return this.balance;
        } catch (error) {
            console.error('Error updating balance:', error);
            throw error;
        }
    }

    startPriceStream() {
        const wsClient = this.client.createWebsocketStream();
        const symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']; // Add more pairs as needed
        
        symbols.forEach(symbol => {
            wsClient.ticker(symbol, {
                callback: (ticker) => this.handleTickerUpdate(symbol, ticker)
            });
        });
    }

    handleTickerUpdate(symbol, ticker) {
        if (this.autoTradeEnabled) {
            this.updateTradingInterval(symbol, ticker);
        }
        this.broadcastUpdate(symbol, ticker);
    }

    startTradingInterval() {
        this.tradingIntervals.intervalTimer = setInterval(() => {
            if (this.autoTradeEnabled) {
                this.executeIntervalTrades();
            }
        }, this.tradingIntervals.current);
    }

    updateTradingInterval(symbol, ticker) {
        // Store last price for volatility calculation
        const lastPrice = this.activePositions.get(symbol)?.lastPrice;
        const currentPrice = parseFloat(ticker.price);
        
        if (lastPrice) {
            // Calculate price change percentage
            const priceChange = Math.abs((currentPrice - lastPrice) / lastPrice);
            const hour = new Date().getUTCHours();
            
            // Determine market period
            const isPeakHours = hour >= this.tradingIntervals.marketHours.peak.start && 
                              hour < this.tradingIntervals.marketHours.peak.end;
            const isOffHours = hour >= this.tradingIntervals.marketHours.off.start && 
                             hour < this.tradingIntervals.marketHours.off.end;
            
            // Calculate optimal interval based on conditions
            let newInterval = this.tradingIntervals.normal; // Default to normal interval

            // Adjust for volatility
            if (priceChange > this.tradingIntervals.volatilityThresholds.high) {
                newInterval = this.tradingIntervals.min;
                console.log(`High volatility detected (${(priceChange * 100).toFixed(2)}%) - Setting interval to 1 minute`);
            } else if (priceChange < this.tradingIntervals.volatilityThresholds.low) {
                newInterval = this.tradingIntervals.max;
                console.log(`Low volatility (${(priceChange * 100).toFixed(2)}%) - Setting interval to 3 minutes`);
            } else {
                console.log(`Normal volatility (${(priceChange * 100).toFixed(2)}%) - Setting interval to 2 minutes`);
            }

            // Adjust for market hours
            if (isPeakHours) {
                newInterval = Math.max(newInterval * 0.8, this.tradingIntervals.min); // 20% faster during peak
            } else if (isOffHours) {
                newInterval = Math.min(newInterval * 1.5, this.tradingIntervals.max); // 50% slower during off hours
            }

            // Update interval if changed
            if (newInterval !== this.tradingIntervals.current) {
                this.tradingIntervals.current = newInterval;
                if (this.tradingIntervals.intervalTimer) {
                    clearInterval(this.tradingIntervals.intervalTimer);
                    this.startTradingInterval();
                }
                console.log(`New trading interval set to ${newInterval/1000} seconds for ${symbol}`);
            }
        }

        // Update last price
        this.activePositions.set(symbol, {
            ...this.activePositions.get(symbol),
            lastPrice: currentPrice
        });
    }

    async executeIntervalTrades() {
        const now = Date.now();
        
        // Check if enough time has passed since last trade
        if (this.tradingIntervals.lastTradeTime && 
            (now - this.tradingIntervals.lastTradeTime) < this.tradingIntervals.current) {
            return;
        }

        try {
            // Get trading opportunities for all monitored symbols
            const symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT'];
            
            for (const symbol of symbols) {
                const ticker = await this.client.ticker(symbol);
                
                // Get ML prediction and analyze trade opportunity
                const mlPrediction = await this.getMLPrediction(symbol, ticker.data);
                if (!mlPrediction || mlPrediction.confidence < 0.75) {
                    console.log(`ML confidence too low for ${symbol}: ${mlPrediction?.confidence}`);
                    continue;
                }

                const prediction = await this.analyzeTradingOpportunity(symbol, ticker.data, mlPrediction);
                if (prediction.shouldTrade) {
                    const tradeResult = await this.executeTrade(symbol, prediction.action, prediction.quantity);
                    await this.updateMLModel(symbol, prediction, tradeResult);
                }
            }

            this.tradingIntervals.lastTradeTime = now;
        } catch (error) {
            console.error('Error executing interval trades:', error);
        }
    }

    async getEnhancedMarketData(symbol) {
        try {
            // Fetch historical klines for comprehensive analysis
            const klines = await this.client.klines(symbol, '1m', { limit: 1000 });
            
            // Extract price and volume data
            const historicalData = klines.data.map(k => ({
                timestamp: k[0],
                open: parseFloat(k[1]),
                high: parseFloat(k[2]),
                low: parseFloat(k[3]),
                close: parseFloat(k[4]),
                volume: parseFloat(k[5])
            }));

            return {
                historicalPrices: historicalData.map(d => d.close),
                historicalVolumes: historicalData.map(d => d.volume),
                ohlcv: historicalData,
                timeframe: '1m',
                dataPoints: historicalData.length
            };
        } catch (error) {
            console.error('Error fetching enhanced market data:', error);
            throw error;
        }
    }

    async getMLPrediction(symbol, ticker) {
        try {
            // Get enhanced market data
            const marketData = await this.getEnhancedMarketData(symbol);
            
            // Prepare feature data with advanced metrics
            const features = {
                symbol,
                price: parseFloat(ticker.price),
                volume: parseFloat(ticker.volume),
                timestamp: new Date().toISOString(),
                technical: await this.getTechnicalData(symbol),
                sentiment: await this.getSentimentData(symbol),
                news: await this.getNewsData(symbol),
                market: marketData,
                metrics: {
                    volatility: this.calculateVolatility(marketData.historicalPrices),
                    momentum: this.calculateMomentum(marketData.historicalPrices),
                    trendStrength: this.calculateTrendStrength(marketData.historicalPrices),
                    volumeProfile: this.analyzeVolumeProfile(marketData.historicalVolumes),
                    priceAction: this.analyzePriceAction(marketData.historicalPrices),
                    marketRegime: this.determineMarketRegime(marketData),
                    supportResistance: this.findSupportResistance(marketData.historicalPrices)
                }
            };

            // Send to ML engine
            return new Promise((resolve, reject) => {
                mlEngine.stdin.write(JSON.stringify({ action: 'predict', data: features }) + '\n');
                
                mlEngine.stdout.once('data', (data) => {
                    try {
                        const prediction = JSON.parse(data.toString());
                        resolve(prediction);
                    } catch (error) {
                        reject(error);
                    }
                });
            });
        } catch (error) {
            console.error('Error getting ML prediction:', error);
            return null;
        }
    }

    async analyzeTradingOpportunity(symbol, ticker, mlPrediction) {
        const ProfitOptimizer = require('./profit_optimizer');
        const MarketOpportunityScorer = require('./market_opportunity_scorer');
        
        const technicalSignals = await this.getTechnicalSignals(symbol);
        const sentimentData = await this.getSentimentData(symbol);
        const tradeCosts = this.calculateTradeCosts(1, parseFloat(ticker.price));
        const orderBook = await this.client.depth(symbol);
        
        // Get current market conditions
        const marketData = {
            volatility: this.riskControls.marketVolatility.get(symbol) || 0.01,
            volume: parseFloat(ticker.volume),
            avgVolume: this.getAverageVolume(symbol),
            orderBook: {
                bids: orderBook.data.bids.length,
                asks: orderBook.data.asks.length,
                spread: (orderBook.data.asks[0][0] - orderBook.data.bids[0][0]) / orderBook.data.bids[0][0],
                depth: orderBook.data.bids.reduce((sum, [,qty]) => sum + parseFloat(qty), 0)
            }
        };

        // Calculate opportunity score
        const opportunityScore = MarketOpportunityScorer.calculateOpportunityScore(
            symbol,
            marketData,
            technicalSignals,
            sentimentData
        );

        // Get time-based target
        const timeBasedTarget = ProfitOptimizer.calculateTimeBasedTarget(
            this.profitTargets.timeBlocks,
            this.profitTargets.daily
        );

        // Combine all signals
        const signals = {
            ml: mlPrediction.action,
            technical: technicalSignals.action,
            sentiment: sentimentData.action,
            costs: tradeCosts,
            opportunityScore,
            timeBasedTarget
        };

        // Calculate optimal position size
        const quantity = this.calculateOptimalPosition(
            parseFloat(ticker.price),
            mlPrediction.confidence,
            tradeCosts
        );

        return {
            shouldTrade: this.shouldExecuteTrade(signals, mlPrediction.confidence),
            action: mlPrediction.action,
            quantity,
            confidence: mlPrediction.confidence,
            signals
        };
    }

    async updateMLModel(symbol, prediction, tradeResult) {
        try {
            // Prepare update data
            const updateData = {
                action: 'update',
                data: {
                    symbol,
                    prediction,
                    result: tradeResult,
                    timestamp: new Date().toISOString()
                }
            };

            // Send update to ML engine
            mlEngine.stdin.write(JSON.stringify(updateData) + '\n');
        } catch (error) {
            console.error('Error updating ML model:', error);
        }
    }

    shouldExecuteTrade(signals, confidence) {
        // Require high ML confidence
        if (confidence < 0.75) return false;

        // Check if signals align
        const signalAlignment = [signals.ml, signals.technical, signals.sentiment]
            .filter(signal => signal === signals.ml).length;

        // Require at least 2 signals to align
        return signalAlignment >= 2;
    }

    calculateOptimalPosition(symbol, price, confidence, tradeCosts) {
        // Get remaining profit target for the day
        const remainingProfit = this.profitTargets.daily - this.profitTargets.dailyProfit;
        const remainingTrades = this.riskControls.maxDailyTrades - this.riskControls.dailyTradeCount;
        
        if (remainingTrades <= 0) return 0;

        // Calculate required profit per trade
        const requiredProfitPerTrade = (remainingProfit / remainingTrades) * 1.2; // 20% buffer
        
        // Get market volatility
        const volatility = this.riskControls.marketVolatility.get(symbol) || 0.01;
        
        // Calculate base position size
        const expectedReturn = volatility * confidence;
        let basePosition = requiredProfitPerTrade / expectedReturn;
        
        // Apply position limits
        const maxPositionValue = this.balance * this.riskControls.maxPositionSize;
        basePosition = Math.min(basePosition, maxPositionValue);
        
        // Adjust for market conditions
        if (this.riskControls.adaptivePositionSizing) {
            // Reduce position size if near daily loss limit
            const lossLimitFactor = 1 - (this.riskControls.currentDailyLoss / this.riskControls.dailyLossLimit);
            basePosition *= Math.max(0.5, lossLimitFactor);
            
            // Reduce position if too many open positions
            const openPositionsFactor = 1 - (this.activePositions.size / this.riskControls.maxOpenPositions);
            basePosition *= Math.max(0.5, openPositionsFactor);
            
            // Adjust for consecutive losses
            const consecutiveLossesFactor = Math.pow(0.8, this.riskControls.consecutiveLosses);
            basePosition *= consecutiveLossesFactor;
        }
        
        // Adjust for trading costs
        const costAdjusted = basePosition * (1 - tradeCosts.totalCostPercentage);
        
        // Calculate final quantity
        const quantity = Math.floor(costAdjusted / price * 100000) / 100000; // Round to 5 decimals
        
        // Update position risk tracking
        this.riskControls.positionRisk.set(symbol, {
            size: quantity * price,
            confidence,
            expectedReturn,
            timestamp: Date.now()
        });
        
        return quantity;
    }

    async evaluatePosition(symbol, currentPrice, confidence) {
        if (!this.autoTradeEnabled) return;
        
        // Reset daily metrics if needed
        const today = new Date().toDateString();
        if (today !== this.riskControls.lastResetDate) {
            this.resetDailyMetrics();
        }

        // Enhanced risk and profit checks
        if (this.riskControls.currentDailyLoss >= this.riskControls.dailyLossLimit ||
            this.riskControls.dailyTradeCount >= this.riskControls.maxDailyTrades ||
            this.riskControls.consecutiveLosses >= this.riskControls.maxConsecutiveLosses ||
            this.profitTargets.dailyProfit >= this.profitTargets.daily) {
            
            console.log('Trading limits status:');
            console.log(`Daily Loss: $${this.riskControls.currentDailyLoss.toFixed(2)}`);
            console.log(`Daily Trades: ${this.riskControls.dailyTradeCount}`);
            console.log(`Daily Profit: $${this.profitTargets.dailyProfit.toFixed(2)}`);
            console.log(`Consecutive Losses: ${this.riskControls.consecutiveLosses}`);
            return;
        }

        try {
            // Calculate position size based on current capital
            const account = await this.client.account();
            const balance = account.balances.find(b => b.asset === 'USDT');
            const availableCapital = parseFloat(balance.free);
            
            // Calculate optimal position size based on profit target
            const remainingProfit = this.profitTargets.daily - this.profitTargets.dailyProfit;
            const expectedWinRate = 0.80; // 80% target win rate
            const remainingTrades = this.riskControls.maxDailyTrades - this.riskControls.dailyTradeCount;
            
            // Required profit per trade to meet daily goal
            const requiredProfitPerTrade = remainingProfit / (remainingTrades * expectedWinRate);
            
            // Calculate position size needed for required profit
            const minPriceMovement = this.tradingCosts.minimumPriceMovement;
            const positionSize = Math.min(
                (requiredProfitPerTrade / minPriceMovement) * 1.5, // 1.5x buffer for safety
                availableCapital * this.riskControls.maxPositionSize // Max position size limit
            );

            // Only trade if confidence meets our threshold
            if (confidence < this.riskControls.minWinRate) {
                console.log(`Insufficient confidence (${confidence}) for ${symbol}`);
                return;
            }

            // Get technical analysis and sentiment data
            const technicalSignals = await this.getTechnicalSignals(symbol);
            const sentimentData = await this.getSentimentData(symbol);
            
            // Execute trade if conditions align
            if (this.shouldExecuteTrade({
                technical: technicalSignals,
                sentiment: sentimentData,
                confidence: confidence
            })) {
                const side = technicalSignals.signal === 'buy' ? 'BUY' : 'SELL';
                await this.executeTrade(symbol, side, positionSize / currentPrice);
            }
        } catch (error) {
            console.error('Error evaluating position:', error);
        }
    }

    updateMarketConditions(symbol, price, volume) {
        const MarketAnalysis = require('./market_analysis');
        
        // Get historical data for the symbol
        const history = this.activePositions.get(symbol)?.priceHistory || [];
        history.push({ price, volume, timestamp: Date.now() });
        
        // Keep last 1000 data points
        if (history.length > 1000) history.shift();
        
        // Calculate volatility
        const prices = history.map(h => h.price);
        const volatility = MarketAnalysis.calculateVolatility(prices);
        this.riskControls.marketVolatility.set(symbol, volatility);
        
        // Update position history
        this.activePositions.set(symbol, {
            ...this.activePositions.get(symbol),
            priceHistory: history,
            lastUpdate: Date.now()
        });
        
        // Adjust trading parameters based on market conditions
        this.adaptToMarketConditions(symbol, volatility);
    }
    
    adaptToMarketConditions(symbol, volatility) {
        // Adjust position sizing based on volatility
        if (volatility > 0.03) { // High volatility
            this.riskControls.maxPositionSize = 0.10; // Reduce max position size
            this.riskControls.riskPerTrade = 0.015; // Reduce risk per trade
        } else if (volatility < 0.01) { // Low volatility
            this.riskControls.maxPositionSize = 0.15; // Normal position size
            this.riskControls.riskPerTrade = 0.02; // Normal risk per trade
        }
        
        // Update trading intervals based on volatility
        this.updateTradingInterval(symbol, { price: this.activePositions.get(symbol)?.lastPrice });
    }

    async executeTrade(symbol, side, quantity) {
        // Check risk controls before executing trade
        if (!this.checkRiskControls()) {
            throw new Error('Risk controls prevented trade execution');
        }
        
        // Check open positions limit
        if (this.activePositions.size >= this.riskControls.maxOpenPositions) {
            throw new Error('Maximum open positions limit reached');
        }

        // Calculate expected costs and check profitability
        const currentPrice = await this.getCurrentPrice(symbol);
        const tradeCosts = this.calculateTradeCosts(quantity, currentPrice);
        
        // Check if trade meets minimum profitability requirements
        if (!this.isProfitableAfterCosts(symbol, side, quantity, currentPrice, tradeCosts)) {
            console.log(`Trade rejected: Insufficient profit margin after costs for ${symbol}`);
            return null;
        }

        try {
            const order = await this.client.newOrder(symbol, side, 'MARKET', {
                quantity: quantity
            });
            
            const tradeData = {
                symbol,
                side,
                quantity,
                price: order.data.price,
                timestamp: new Date().toISOString(),
                costs: tradeCosts,
                estimatedProfit: this.calculateEstimatedProfit(order.data.price, currentPrice, quantity, side)
            };
            
            this.logTrade(tradeData);
            this.updateRiskMetrics(tradeData);
            this.updateFeeTracker(tradeCosts.totalFees);

            return order;
        } catch (error) {
            console.error('Trade execution error:', error);
            throw error;
        }
    }

    calculateTradeCosts(quantity, price) {
        const tradeValue = quantity * price;
        const takerFee = tradeValue * this.tradingCosts.takerFee;
        const slippageCost = tradeValue * this.tradingCosts.slippageEstimate;
        const totalFees = takerFee + slippageCost;

        return {
            tradeValue,
            takerFee,
            slippageCost,
            totalFees,
            totalCostPercentage: (totalFees / tradeValue) * 100
        };
    }

    isProfitableAfterCosts(symbol, side, quantity, currentPrice, tradeCosts) {
        // Get the expected price movement from our strategy analysis
        const expectedMove = this.getExpectedPriceMovement(symbol);
        
        // Calculate potential profit
        const potentialProfit = quantity * currentPrice * expectedMove;
        
        // Calculate total costs (entry + exit)
        const roundTripCosts = tradeCosts.totalFees * 2; // Both entry and exit costs
        
        // Check if potential profit exceeds our minimum requirements
        const netProfit = potentialProfit - roundTripCosts;
        const profitMargin = netProfit / (quantity * currentPrice);

        return profitMargin >= this.tradingCosts.minProfitMargin;
    }

    updateFeeTracker(fees) {
        const today = new Date().toDateString();
        
        // Reset if it's a new day
        if (today !== this.tradingCosts.dailyFeeTracker.date) {
            this.tradingCosts.dailyFeeTracker = {
                total: 0,
                trades: 0,
                date: today
            };
        }

        // Update fee tracking
        this.tradingCosts.dailyFeeTracker.total += fees;
        this.tradingCosts.dailyFeeTracker.trades += 1;
    }

    getExpectedPriceMovement(symbol) {
        // Get the volatility and trend strength from our analysis
        const position = this.activePositions.get(symbol);
        if (!position) return this.tradingCosts.minimumPriceMovement;

        // Use historical volatility or recent price movement as baseline
        const baselineMovement = position.recentVolatility || this.tradingCosts.minimumPriceMovement;
        
        // Adjust based on current market conditions
        return Math.max(baselineMovement, this.tradingCosts.minimumPriceMovement);
    }

    async getCurrentPrice(symbol) {
        try {
            const ticker = await this.client.ticker(symbol);
            return parseFloat(ticker.data.price);
        } catch (error) {
            console.error('Error getting current price:', error);
            throw error;
        }
    }

    calculateEstimatedProfit(executionPrice, entryPrice, quantity, side) {
        const priceDiff = side === 'BUY' ? 
            executionPrice - entryPrice : 
            entryPrice - executionPrice;
        
        const grossProfit = priceDiff * quantity;
        const tradeCosts = this.calculateTradeCosts(quantity, executionPrice);
        return grossProfit - tradeCosts.totalFees;
    }

    checkRiskControls() {
        // Reset daily metrics if it's a new day
        const currentDate = new Date().toDateString();
        if (currentDate !== this.riskControls.lastResetDate) {
            this.resetDailyMetrics();
        }

        // Check daily loss limit
        if (Math.abs(this.riskControls.currentDailyLoss) >= this.riskControls.dailyLossLimit) {
            console.error('Daily loss limit reached: $' + this.riskControls.dailyLossLimit);
            this.autoTradeEnabled = false; // Automatically disable trading
            return false;
        }

        // Check maximum open positions
        if (this.activePositions.size >= this.riskControls.maxOpenPositions) {
            console.error('Maximum open positions reached');
            return false;
        }

        // Check maximum daily trades
        if (this.riskControls.dailyTradeCount >= this.riskControls.maxDailyTrades) {
            console.error('Maximum daily trades reached');
            return false;
        }

        // Check win rate
        const trades = this.getTodaysTrades();
        if (trades.length >= 10) { // Only check after sufficient trades
            const winRate = trades.filter(t => t.profit > 0).length / trades.length;
            if (winRate < this.riskControls.minWinRate) {
                console.error(`Win rate below threshold: ${(winRate * 100).toFixed(2)}%`);
                return false;
            }
        }

        // Check drawdown
        const drawdown = this.calculateDrawdown();
        if (drawdown > this.riskControls.maxDrawdown) {
            console.error(`Maximum drawdown exceeded: ${drawdown.toFixed(2)}%`);
            this.autoTradeEnabled = false;
            return false;
        }

        // Check position concentration
        const totalRisk = Array.from(this.riskControls.positionRisk.values())
            .reduce((sum, pos) => sum + pos.size, 0);
        if (totalRisk > this.balance * 0.5) { // Max 50% total exposure
            console.error('Maximum portfolio exposure reached');
            return false;
        }

        return true;
    }

    updateRiskMetrics(tradeData) {
        // Update daily trade count
        this.riskControls.dailyTradeCount++;

        // Calculate and update P&L if this is a closing trade
        if (this.activePositions.has(tradeData.symbol)) {
            const position = this.activePositions.get(tradeData.symbol);
            const pnl = this.calculatePnL(position, tradeData);
            this.riskControls.currentDailyLoss -= pnl; // Subtract because loss is positive
            
            // Log significant losses
            if (pnl < 0) {
                console.warn(`Trade loss: $${Math.abs(pnl).toFixed(2)} | Daily loss: $${this.riskControls.currentDailyLoss.toFixed(2)}`);
            }
        }
    }

    resetDailyMetrics() {
        this.riskControls.currentDailyLoss = 0;
        this.riskControls.dailyTradeCount = 0;
        this.riskControls.lastResetDate = new Date().toDateString();
        console.log('Daily risk metrics reset');
    }

    calculatePnL(position, closingTrade) {
        const entryValue = position.quantity * position.price;
        const exitValue = closingTrade.quantity * closingTrade.price;
        return position.side === 'BUY' ? exitValue - entryValue : entryValue - exitValue;
    }

    logTrade(tradeData) {
        let trades = [];
        try {
            trades = JSON.parse(fs.readFileSync(this.tradeLog));
        } catch (error) {
            // File doesn't exist or is empty
        }
        
        trades.push(tradeData);
        fs.writeFileSync(this.tradeLog, JSON.stringify(trades, null, 2));
    }

    setAutoTradeEnabled(enabled) {
        this.autoTradeEnabled = enabled;
        return { success: true, autoTradeEnabled: this.autoTradeEnabled };
    }
}

module.exports = new BinanceMonitor();
