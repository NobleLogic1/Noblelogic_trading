const technicalIndicators = require('technicalindicators');
const { SMA, RSI, MACD, BollingerBands } = technicalIndicators;

class TradeAnalyzer {
    constructor() {
        this.requiredAccuracy = 0.80; // 80% target accuracy
        this.minConfidenceThreshold = 0.85; // Minimum confidence required
        this.profitTargetMultiplier = 1.5; // Risk:Reward ratio
        this.historicalAccuracy = [];
        this.consecutiveLosses = 0;
        this.maxConsecutiveLosses = 3;
    }

    async analyzeTrade(symbol, price, volume, marketData, sentiment) {
        try {
            // Multiple validation layers for trade confirmation
            const [
                technicalSignals,
                trendAnalysis,
                volumeAnalysis,
                patternRecognition,
                sentimentAnalysis
            ] = await Promise.all([
                this.getTechnicalSignals(marketData),
                this.analyzeTrend(marketData),
                this.analyzeVolume(volume, marketData),
                this.recognizePatterns(marketData),
                this.analyzeSentiment(sentiment)
            ]);

            // Calculate composite score
            const tradeScore = this.calculateTradeScore({
                technical: technicalSignals,
                trend: trendAnalysis,
                volume: volumeAnalysis,
                patterns: patternRecognition,
                sentiment: sentimentAnalysis
            });

            // Check if trade meets accuracy requirements
            const isValidTrade = this.validateTrade(tradeScore);
            if (!isValidTrade) {
                return {
                    shouldTrade: false,
                    reason: 'Insufficient confidence score'
                };
            }

            // Calculate optimal entry and exit points
            const tradingPoints = this.calculateTradingPoints(price, tradeScore);

            return {
                shouldTrade: true,
                direction: tradeScore.direction,
                confidence: tradeScore.confidence,
                entryPrice: tradingPoints.entry,
                stopLoss: tradingPoints.stopLoss,
                takeProfit: tradingPoints.takeProfit,
                timeframe: tradingPoints.timeframe,
                expectedProfitability: tradeScore.expectedReturn,
                riskRatio: tradeScore.riskRatio,
                signals: {
                    technical: technicalSignals,
                    trend: trendAnalysis,
                    volume: volumeAnalysis,
                    patterns: patternRecognition,
                    sentiment: sentimentAnalysis
                }
            };
        } catch (error) {
            console.error('Trade analysis error:', error);
            return { shouldTrade: false, reason: 'Analysis error' };
        }
    }

    async getTechnicalSignals(marketData) {
        const signals = {
            rsi: await this.calculateRSI(marketData),
            macd: await this.calculateMACD(marketData),
            bollinger: await this.calculateBollingerBands(marketData),
            support: await this.findSupportLevels(marketData),
            resistance: await this.findResistanceLevels(marketData)
        };

        return {
            bullish: this.aggregateBullishSignals(signals),
            bearish: this.aggregateBearishSignals(signals),
            strength: this.calculateSignalStrength(signals),
            reliability: this.calculateSignalReliability(signals)
        };
    }

    calculateTradeScore(signals) {
        const weights = {
            technical: 0.35,
            trend: 0.25,
            volume: 0.15,
            patterns: 0.15,
            sentiment: 0.10
        };

        let compositeScore = 0;
        let signalCount = 0;
        let direction = null;

        // Calculate weighted score
        Object.entries(signals).forEach(([type, signal]) => {
            compositeScore += signal.strength * weights[type];
            if (signal.direction) {
                signalCount += signal.direction === 'buy' ? 1 : -1;
            }
        });

        // Determine trade direction
        direction = signalCount > 0 ? 'buy' : 'sell';

        // Calculate confidence and expected return
        const confidence = Math.min(Math.abs(compositeScore), 1);
        const expectedReturn = this.calculateExpectedReturn(confidence, signals);

        return {
            direction,
            confidence,
            expectedReturn,
            riskRatio: this.calculateRiskRatio(expectedReturn),
            signalStrength: Math.abs(compositeScore)
        };
    }

    validateTrade(tradeScore) {
        // Multiple validation criteria
        const validations = [
            tradeScore.confidence >= this.minConfidenceThreshold,
            tradeScore.riskRatio >= this.profitTargetMultiplier,
            this.consecutiveLosses < this.maxConsecutiveLosses,
            this.calculateHistoricalAccuracy() >= this.requiredAccuracy,
            this.validateMarketConditions(tradeScore)
        ];

        return validations.every(v => v === true);
    }

    calculateTradingPoints(price, score) {
        const volatility = this.calculateVolatility();
        const atr = this.calculateATR();

        return {
            entry: this.calculateOptimalEntry(price, score),
            stopLoss: this.calculateStopLoss(price, atr, score),
            takeProfit: this.calculateTakeProfit(price, atr, score),
            timeframe: this.determineTimeframe(score)
        };
    }

    updateAccuracyMetrics(tradeResult) {
        this.historicalAccuracy.push(tradeResult.successful);
        
        // Keep only recent history (last 100 trades)
        if (this.historicalAccuracy.length > 100) {
            this.historicalAccuracy.shift();
        }

        // Update consecutive losses
        if (!tradeResult.successful) {
            this.consecutiveLosses++;
        } else {
            this.consecutiveLosses = 0;
        }

        // Calculate new accuracy
        return this.calculateHistoricalAccuracy();
    }

    calculateHistoricalAccuracy() {
        if (this.historicalAccuracy.length === 0) return 1;
        const successful = this.historicalAccuracy.filter(x => x).length;
        return successful / this.historicalAccuracy.length;
    }

    // Risk management methods
    calculateRiskRatio(expectedReturn) {
        const riskFreeRate = 0.02; // 2% risk-free rate
        const marketRisk = this.calculateMarketRisk();
        return (expectedReturn - riskFreeRate) / marketRisk;
    }

    calculateExpectedReturn(confidence, signals) {
        const baseReturn = 0.03; // 3% base return expectation
        const marketCondition = this.assessMarketCondition(signals);
        const volatilityAdjustment = this.calculateVolatilityAdjustment();
        
        return baseReturn * confidence * marketCondition * volatilityAdjustment;
    }

    validateMarketConditions(tradeScore) {
        const conditions = {
            volatilityInRange: this.checkVolatilityRange(),
            trendStrength: this.checkTrendStrength(),
            volumeAdequate: this.checkVolumeAdequacy(),
            marketStability: this.checkMarketStability()
        };

        return Object.values(conditions).every(condition => condition);
    }
}

module.exports = new TradeAnalyzer();