const technical = require('./technical_analysis');
const sentiment = require('./sentiment_engine');

class PsychologyModel {
    constructor() {
        this.marketStates = new Map();
        this.fearGreedIndex = 50; // Neutral starting point
        this.momentum = 0;
    }

    async analyzePsychology(symbol) {
        try {
            const [technicalData, sentimentData] = await Promise.all([
                technical.getIndicators(symbol),
                sentiment.analyzeMarketSentiment(symbol)
            ]);

            const psychology = {
                fearGreedIndex: this.calculateFearGreedIndex(technicalData, sentimentData),
                marketPressure: this.calculateMarketPressure(technicalData),
                emotionalState: this.determineEmotionalState(technicalData, sentimentData),
                volumePressure: this.analyzeVolumePressure(technicalData),
                marketPhase: this.determineMarketPhase(technicalData),
                confidence: this.calculateTradeConfidence(technicalData, sentimentData),
                recommendation: this.generateRecommendation(technicalData, sentimentData)
            };

            this.updateMarketState(symbol, psychology);
            return psychology;
        } catch (error) {
            console.error('Psychology analysis error:', error);
            throw error;
        }
    }

    calculateFearGreedIndex(technical, sentiment) {
        const factors = {
            volatility: this.normalizeValue(technical.volatility, 0, 100),
            momentum: this.normalizeValue(technical.momentum, -100, 100),
            sentiment: sentiment.overall,
            volume: this.normalizeValue(technical.volume, 0, 100)
        };

        return Math.round(
            factors.volatility * 0.25 +
            factors.momentum * 0.30 +
            factors.sentiment * 0.25 +
            factors.volume * 0.20
        );
    }

    calculateMarketPressure(technical) {
        const buyPressure = technical.buyVolume / technical.totalVolume;
        const sellPressure = technical.sellVolume / technical.totalVolume;
        
        return {
            buying: buyPressure,
            selling: sellPressure,
            ratio: buyPressure / sellPressure,
            trend: this.determinePressureTrend(buyPressure, sellPressure)
        };
    }

    determineEmotionalState(technical, sentiment) {
        const fearGreed = this.calculateFearGreedIndex(technical, sentiment);
        
        if (fearGreed >= 80) return 'Extreme Greed';
        if (fearGreed >= 60) return 'Greed';
        if (fearGreed >= 40) return 'Neutral';
        if (fearGreed >= 20) return 'Fear';
        return 'Extreme Fear';
    }

    analyzeVolumePressure(technical) {
        const volumeMA = technical.volumeSMA;
        const currentVolume = technical.volume;
        
        return {
            pressure: currentVolume / volumeMA,
            abnormal: currentVolume > volumeMA * 1.5,
            trend: this.determineVolumeTrend(technical)
        };
    }

    determineMarketPhase(technical) {
        const trends = {
            shortTerm: technical.shortTermTrend,
            mediumTerm: technical.mediumTermTrend,
            longTerm: technical.longTermTrend
        };

        if (trends.shortTerm === 'up' && trends.mediumTerm === 'up') {
            return 'Accumulation';
        } else if (trends.shortTerm === 'down' && trends.mediumTerm === 'down') {
            return 'Distribution';
        } else if (trends.shortTerm === 'up' && trends.mediumTerm === 'down') {
            return 'Reversal Possible';
        }
        return 'Consolidation';
    }

    calculateTradeConfidence(technical, sentiment) {
        const factors = {
            technicalStrength: technical.signalStrength,
            sentimentAlignment: this.checkSentimentAlignment(technical, sentiment),
            trendConfirmation: this.getTrendConfirmation(technical),
            volumeSupport: this.getVolumeSupport(technical)
        };

        return Object.values(factors).reduce((a, b) => a + b) / Object.keys(factors).length;
    }

    generateRecommendation(technical, sentiment) {
        const confidence = this.calculateTradeConfidence(technical, sentiment);
        const fearGreed = this.calculateFearGreedIndex(technical, sentiment);
        
        return {
            action: this.determineAction(confidence, fearGreed),
            confidence: confidence,
            stopLoss: this.calculateStopLoss(technical),
            takeProfit: this.calculateTakeProfit(technical),
            timeframe: this.suggestTimeframe(technical, sentiment)
        };
    }

    normalizeValue(value, min, max) {
        return (value - min) / (max - min) * 100;
    }

    updateMarketState(symbol, psychology) {
        this.marketStates.set(symbol, {
            ...psychology,
            timestamp: new Date().toISOString()
        });
    }

    determinePressureTrend(buyPressure, sellPressure) {
        const ratio = buyPressure / sellPressure;
        if (ratio > 1.2) return 'Strong Buying';
        if (ratio > 1.05) return 'Moderate Buying';
        if (ratio < 0.8) return 'Strong Selling';
        if (ratio < 0.95) return 'Moderate Selling';
        return 'Neutral';
    }

    determineAction(confidence, fearGreed) {
        if (confidence > 0.8 && fearGreed > 70) return 'STRONG_BUY';
        if (confidence > 0.6 && fearGreed > 60) return 'BUY';
        if (confidence < 0.3 && fearGreed < 30) return 'STRONG_SELL';
        if (confidence < 0.4 && fearGreed < 40) return 'SELL';
        return 'HOLD';
    }

    calculateStopLoss(technical) {
        return technical.price * 0.98; // 2% stop loss, adjust based on volatility
    }

    calculateTakeProfit(technical) {
        return technical.price * 1.04; // 4% take profit, adjust based on strategy
    }

    suggestTimeframe(technical, sentiment) {
        if (sentiment.overall > 0.8) return 'LONG';
        if (technical.volatility > 0.7) return 'SHORT';
        return 'MEDIUM';
    }
}

module.exports = new PsychologyModel();
