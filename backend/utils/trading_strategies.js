const technicalAnalysis = require('technicalindicators');
const psychologyModel = require('./psychology_model');
const sentimentEngine = require('./sentiment_engine');

class TradingStrategies {
    constructor() {
        this.strategies = {
            scalping: this.scalpingStrategy.bind(this),
            momentum: this.momentumStrategy.bind(this),
            meanReversion: this.meanReversionStrategy.bind(this),
            breakout: this.breakoutStrategy.bind(this),
            sentimentBased: this.sentimentStrategy.bind(this)
        };
        
        this.successRates = new Map();
        this.profitTargets = {
            daily: 500,
            perTrade: 20
        };
    }

    async evaluatePosition(symbol, price, volume) {
        const [technical, psychology, sentiment] = await Promise.all([
            this.getTechnicalIndicators(symbol, price, volume),
            psychologyModel.analyzePsychology(symbol),
            sentimentEngine.analyzeMarketSentiment(symbol)
        ]);

        const signals = await Promise.all([
            this.scalpingStrategy(technical, psychology, sentiment),
            this.momentumStrategy(technical, psychology, sentiment),
            this.meanReversionStrategy(technical, psychology, sentiment),
            this.breakoutStrategy(technical, psychology, sentiment),
            this.sentimentStrategy(technical, psychology, sentiment)
        ]);

        return this.combineSignals(signals, psychology.confidence);
    }

    async scalpingStrategy(technical, psychology, sentiment) {
        // Quick profits from small price movements
        const conditions = {
            priceAboveEMA: technical.price > technical.ema9,
            volumeSpike: technical.volume > technical.volumeSMA * 1.2,
            lowSpread: technical.spread < technical.averageSpread,
            positivesentiment: sentiment.overall > 0.6
        };

        const confidence = Object.values(conditions).filter(Boolean).length / Object.keys(conditions).length;

        return {
            type: 'SCALPING',
            signal: confidence > 0.75 ? 'BUY' : confidence < 0.3 ? 'SELL' : 'HOLD',
            confidence: confidence,
            stopLoss: technical.price * 0.997, // 0.3% stop loss
            takeProfit: technical.price * 1.006 // 0.6% take profit
        };
    }

    async momentumStrategy(technical, psychology, sentiment) {
        // Follows strong trends
        const conditions = {
            strongTrend: technical.adx > 25,
            positiveMACD: technical.macd.histogram > 0,
            risingVolume: technical.volume > technical.volumeSMA,
            psychologySupport: psychology.fearGreedIndex > 60
        };

        const confidence = Object.values(conditions).filter(Boolean).length / Object.keys(conditions).length;

        return {
            type: 'MOMENTUM',
            signal: confidence > 0.8 ? 'BUY' : confidence < 0.2 ? 'SELL' : 'HOLD',
            confidence: confidence,
            stopLoss: technical.price * 0.98, // 2% stop loss
            takeProfit: technical.price * 1.04 // 4% take profit
        };
    }

    async meanReversionStrategy(technical, psychology, sentiment) {
        // Trades bounces from oversold/overbought conditions
        const conditions = {
            oversold: technical.rsi < 30,
            overbought: technical.rsi > 70,
            volumeConfirmation: technical.volume > technical.volumeSMA,
            psychologyExtreme: psychology.fearGreedIndex < 20 || psychology.fearGreedIndex > 80
        };

        const confidence = Object.values(conditions).filter(Boolean).length / Object.keys(conditions).length;

        return {
            type: 'MEAN_REVERSION',
            signal: technical.rsi < 30 ? 'BUY' : technical.rsi > 70 ? 'SELL' : 'HOLD',
            confidence: confidence,
            stopLoss: technical.price * 0.985, // 1.5% stop loss
            takeProfit: technical.price * 1.03 // 3% take profit
        };
    }

    async breakoutStrategy(technical, psychology, sentiment) {
        // Trades breakouts from consolidation
        const conditions = {
            priceBreakout: technical.price > technical.upperBB || technical.price < technical.lowerBB,
            volumeBreakout: technical.volume > technical.volumeSMA * 1.5,
            trendConfirmation: technical.adx > 20,
            psychologySupport: psychology.marketPhase === 'Accumulation' || psychology.marketPhase === 'Distribution'
        };

        const confidence = Object.values(conditions).filter(Boolean).length / Object.keys(conditions).length;

        return {
            type: 'BREAKOUT',
            signal: confidence > 0.75 ? (technical.price > technical.upperBB ? 'BUY' : 'SELL') : 'HOLD',
            confidence: confidence,
            stopLoss: technical.price * 0.975, // 2.5% stop loss
            takeProfit: technical.price * 1.05 // 5% take profit
        };
    }

    async sentimentStrategy(technical, psychology, sentiment) {
        // Trades based on market sentiment and psychology
        const conditions = {
            strongSentiment: Math.abs(sentiment.overall - 0.5) > 0.3,
            volumeSupport: technical.volume > technical.volumeSMA,
            psychologyAlignment: psychology.emotionalState !== 'Neutral',
            trendConfirmation: technical.macd.histogram > 0
        };

        const confidence = Object.values(conditions).filter(Boolean).length / Object.keys(conditions).length;

        return {
            type: 'SENTIMENT',
            signal: sentiment.overall > 0.7 ? 'BUY' : sentiment.overall < 0.3 ? 'SELL' : 'HOLD',
            confidence: confidence,
            stopLoss: technical.price * 0.97, // 3% stop loss
            takeProfit: technical.price * 1.06 // 6% take profit
        };
    }

    combineSignals(signals, psychologyConfidence) {
        let weightedSignal = 0;
        let totalConfidence = 0;

        const weights = {
            SCALPING: 0.25,
            MOMENTUM: 0.25,
            MEAN_REVERSION: 0.15,
            BREAKOUT: 0.20,
            SENTIMENT: 0.15
        };

        signals.forEach(signal => {
            const weight = weights[signal.type];
            if (signal.signal === 'BUY') weightedSignal += signal.confidence * weight;
            if (signal.signal === 'SELL') weightedSignal -= signal.confidence * weight;
            totalConfidence += signal.confidence * weight;
        });

        // Adjust based on psychology confidence
        weightedSignal *= psychologyConfidence;

        return {
            signal: weightedSignal > 0.3 ? 'BUY' : weightedSignal < -0.3 ? 'SELL' : 'HOLD',
            confidence: Math.abs(weightedSignal),
            strategies: signals,
            psychologyConfidence
        };
    }

    updateSuccessRate(strategy, success) {
        const current = this.successRates.get(strategy) || { total: 0, success: 0 };
        current.total++;
        if (success) current.success++;
        this.successRates.set(strategy, current);
    }

    getSuccessRate(strategy) {
        const stats = this.successRates.get(strategy);
        if (!stats || stats.total === 0) return 0;
        return (stats.success / stats.total) * 100;
    }
}

module.exports = new TradingStrategies();