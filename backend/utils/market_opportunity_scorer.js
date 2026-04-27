class MarketOpportunityScorer {
    static calculateOpportunityScore(symbol, marketData, technicalSignals, sentimentData) {
        const scores = {
            volatility: this.scoreVolatility(marketData.volatility),
            trend: this.scoreTrend(technicalSignals),
            volume: this.scoreVolume(marketData.volume, marketData.avgVolume),
            sentiment: this.scoreSentiment(sentimentData),
            timing: this.scoreMarketTiming(),
            liquidity: this.scoreLiquidity(marketData.orderBook)
        };

        // Calculate weighted average
        const weights = {
            volatility: 0.2,
            trend: 0.25,
            volume: 0.15,
            sentiment: 0.2,
            timing: 0.1,
            liquidity: 0.1
        };

        const totalScore = Object.keys(scores).reduce((total, key) => 
            total + (scores[key] * weights[key]), 0);

        return {
            totalScore,
            breakdown: scores,
            isViable: totalScore >= 0.7 // Minimum threshold for trade consideration
        };
    }

    static scoreVolatility(volatility) {
        // Optimal volatility range: 0.5% - 2%
        if (volatility < 0.001) return 0.2; // Too stable
        if (volatility < 0.005) return 0.6; // Low but tradeable
        if (volatility <= 0.02) return 1.0; // Optimal range
        if (volatility <= 0.03) return 0.7; // Getting risky
        return 0.3; // Too volatile
    }

    static scoreTrend(signals) {
        const {
            shortTrend,
            mediumTrend,
            longTrend,
            momentum
        } = signals;

        let score = 0;
        
        // Trend alignment
        if (shortTrend === mediumTrend && mediumTrend === longTrend) {
            score += 0.4; // Strong trend alignment
        } else if (shortTrend === mediumTrend) {
            score += 0.2; // Partial alignment
        }

        // Momentum alignment
        if (momentum > 0 && shortTrend === 'up') score += 0.3;
        if (momentum < 0 && shortTrend === 'down') score += 0.3;

        // Add momentum strength
        score += Math.min(0.3, Math.abs(momentum) / 10);

        return Math.min(1, score);
    }

    static scoreVolume(currentVolume, avgVolume) {
        const volumeRatio = currentVolume / avgVolume;
        
        if (volumeRatio < 0.5) return 0.3; // Too low volume
        if (volumeRatio < 0.8) return 0.6; // Below average
        if (volumeRatio <= 1.5) return 1.0; // Optimal range
        if (volumeRatio <= 2.0) return 0.8; // High but manageable
        return 0.4; // Too high - potential manipulation
    }

    static scoreSentiment(sentimentData) {
        const {
            newsScore,
            socialScore,
            technicalScore
        } = sentimentData;

        // Normalize scores to 0-1 range
        const normalized = {
            news: (newsScore + 1) / 2,
            social: (socialScore + 1) / 2,
            technical: (technicalScore + 1) / 2
        };

        // Weight the components
        return (normalized.news * 0.3) + 
               (normalized.social * 0.3) + 
               (normalized.technical * 0.4);
    }

    static scoreMarketTiming() {
        const hour = new Date().getUTCHours();
        
        // Score based on market hours (UTC)
        if (hour >= 12 && hour < 16) return 1.0;    // US market peak
        if (hour >= 8 && hour < 12) return 0.9;     // European session
        if (hour >= 16 && hour < 20) return 0.8;    // US afternoon
        if (hour >= 4 && hour < 8) return 0.7;      // Asian session
        if (hour >= 20 || hour < 4) return 0.5;     // Off-peak hours
        
        return 0.6; // Default score
    }

    static scoreLiquidity(orderBook) {
        if (!orderBook) return 0.5; // Default if no order book data

        const {
            bids,
            asks,
            spread,
            depth
        } = orderBook;

        let score = 1.0;

        // Penalize for wide spreads
        if (spread > 0.001) score -= 0.2;
        if (spread > 0.002) score -= 0.3;

        // Check depth
        const depthScore = Math.min(1, depth / 1000000); // Normalize to 1M depth
        score *= (0.7 + (0.3 * depthScore));

        // Check bid/ask imbalance
        const imbalance = Math.abs(1 - (bids / asks));
        if (imbalance > 0.2) score *= 0.9;
        if (imbalance > 0.5) score *= 0.8;

        return Math.max(0, Math.min(1, score));
    }
}

module.exports = MarketOpportunityScorer;