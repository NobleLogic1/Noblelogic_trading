const technicalIndicators = require('technicalindicators');

class MarketAnalysis {
    static calculateVolatility(prices, period = 14) {
        const returns = prices.slice(1).map((price, i) => 
            Math.log(price / prices[i])
        );
        
        const mean = returns.reduce((a, b) => a + b) / returns.length;
        const variance = returns.reduce((a, b) => a + Math.pow(b - mean, 2)) / returns.length;
        return Math.sqrt(variance * 252); // Annualized volatility
    }

    static calculateMomentum(prices, period = 14) {
        const ROC = technicalIndicators.ROC;
        const roc = new ROC({ period, values: prices });
        return roc.getResult();
    }

    static calculateTrendStrength(prices) {
        const ADX = technicalIndicators.ADX;
        const period = 14;
        const input = {
            high: prices.map(p => p * 1.001), // Simulated high prices
            low: prices.map(p => p * 0.999),  // Simulated low prices
            close: prices,
            period
        };
        const adx = new ADX(input);
        return adx.getResult();
    }

    static analyzeVolumeProfile(volumes, prices) {
        // Calculate VWAP and volume-based support/resistance
        const totalVolume = volumes.reduce((a, b) => a + b, 0);
        const vwap = volumes.reduce((sum, vol, i) => sum + vol * prices[i], 0) / totalVolume;
        
        // Identify high volume nodes
        const volumeNodes = new Map();
        prices.forEach((price, i) => {
            const priceLevel = Math.round(price * 100) / 100;
            volumeNodes.set(priceLevel, (volumeNodes.get(priceLevel) || 0) + volumes[i]);
        });
        
        // Sort by volume to find significant levels
        const significantLevels = Array.from(volumeNodes.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3);
        
        return {
            vwap,
            significantLevels,
            volumeProfile: {
                totalVolume,
                averageVolume: totalVolume / volumes.length,
                volumeDistribution: significantLevels
            }
        };
    }

    static analyzePriceAction(prices) {
        const SMA = technicalIndicators.SMA;
        const RSI = technicalIndicators.RSI;
        
        // Calculate moving averages
        const sma20 = new SMA({ period: 20, values: prices });
        const sma50 = new SMA({ period: 50, values: prices });
        const sma200 = new SMA({ period: 200, values: prices });
        
        // Calculate RSI
        const rsi = new RSI({ period: 14, values: prices });
        
        // Identify swing points
        const swingHigh = this.findSwingPoints(prices, 'high');
        const swingLow = this.findSwingPoints(prices, 'low');
        
        return {
            movingAverages: {
                sma20: sma20.getResult(),
                sma50: sma50.getResult(),
                sma200: sma200.getResult()
            },
            rsi: rsi.getResult(),
            swingPoints: {
                high: swingHigh,
                low: swingLow
            },
            trendState: this.determineTrendState(sma20.getResult(), sma50.getResult(), sma200.getResult())
        };
    }

    static determineMarketRegime(marketData) {
        const { prices, volumes } = marketData;
        const volatility = this.calculateVolatility(prices);
        const momentum = this.calculateMomentum(prices);
        const trendStrength = this.calculateTrendStrength(prices);
        
        // Classify market regime
        let regime = {
            type: 'unknown',
            confidence: 0,
            characteristics: []
        };
        
        if (volatility > 0.4) { // High volatility threshold
            if (Math.abs(momentum[momentum.length - 1]) > 2) {
                regime.type = momentum[momentum.length - 1] > 0 ? 'trending_up' : 'trending_down';
                regime.characteristics.push('high_volatility');
            } else {
                regime.type = 'choppy';
                regime.characteristics.push('high_volatility', 'directionless');
            }
        } else {
            if (trendStrength[trendStrength.length - 1] > 25) {
                regime.type = momentum[momentum.length - 1] > 0 ? 'trending_up' : 'trending_down';
                regime.characteristics.push('strong_trend');
            } else {
                regime.type = 'ranging';
                regime.characteristics.push('low_volatility');
            }
        }
        
        regime.confidence = this.calculateRegimeConfidence(regime, volatility, momentum, trendStrength);
        return regime;
    }

    static findSupportResistance(prices) {
        const fractals = this.calculateFractals(prices);
        const pivots = this.calculatePivotPoints(prices);
        const fibonacci = this.calculateFibonacciLevels(prices);
        
        return {
            fractals,
            pivots,
            fibonacci,
            dynamicLevels: this.findDynamicLevels(prices)
        };
    }

    static calculateFractals(prices, period = 5) {
        const fractals = {
            bullish: [],
            bearish: []
        };
        
        for (let i = 2; i < prices.length - 2; i++) {
            // Bullish fractal
            if (prices[i-2] > prices[i] && 
                prices[i-1] > prices[i] && 
                prices[i] < prices[i+1] && 
                prices[i] < prices[i+2]) {
                fractals.bullish.push({
                    price: prices[i],
                    index: i
                });
            }
            
            // Bearish fractal
            if (prices[i-2] < prices[i] && 
                prices[i-1] < prices[i] && 
                prices[i] > prices[i+1] && 
                prices[i] > prices[i+2]) {
                fractals.bearish.push({
                    price: prices[i],
                    index: i
                });
            }
        }
        
        return fractals;
    }

    static calculatePivotPoints(prices) {
        const high = Math.max(...prices);
        const low = Math.min(...prices);
        const close = prices[prices.length - 1];
        
        const pp = (high + low + close) / 3;
        const r1 = 2 * pp - low;
        const s1 = 2 * pp - high;
        const r2 = pp + (high - low);
        const s2 = pp - (high - low);
        
        return { pp, r1, s1, r2, s2 };
    }

    static calculateFibonacciLevels(prices) {
        const high = Math.max(...prices);
        const low = Math.min(...prices);
        const diff = high - low;
        
        return {
            level_0: low,
            level_236: low + diff * 0.236,
            level_382: low + diff * 0.382,
            level_500: low + diff * 0.500,
            level_618: low + diff * 0.618,
            level_786: low + diff * 0.786,
            level_1000: high
        };
    }

    static findDynamicLevels(prices) {
        const volumeNodes = this.analyzeVolumeProfile(
            prices.map(() => 1), // Simulated equal volume for price clustering
            prices
        );
        
        return {
            support: volumeNodes.significantLevels
                .filter(level => level[0] < prices[prices.length - 1])
                .map(level => level[0]),
            resistance: volumeNodes.significantLevels
                .filter(level => level[0] > prices[prices.length - 1])
                .map(level => level[0])
        };
    }

    static findSwingPoints(prices, type = 'high', lookback = 5) {
        const points = [];
        for (let i = lookback; i < prices.length - lookback; i++) {
            const window = prices.slice(i - lookback, i + lookback + 1);
            const current = prices[i];
            
            if (type === 'high' && current === Math.max(...window)) {
                points.push({ price: current, index: i });
            } else if (type === 'low' && current === Math.min(...window)) {
                points.push({ price: current, index: i });
            }
        }
        return points;
    }

    static determineTrendState(sma20, sma50, sma200) {
        const current = {
            sma20: sma20[sma20.length - 1],
            sma50: sma50[sma50.length - 1],
            sma200: sma200[sma200.length - 1]
        };
        
        let state = {
            primary: '',
            secondary: '',
            strength: 0
        };
        
        // Determine primary trend
        if (current.sma20 > current.sma50 && current.sma50 > current.sma200) {
            state.primary = 'strong_uptrend';
            state.strength = 1;
        } else if (current.sma20 < current.sma50 && current.sma50 < current.sma200) {
            state.primary = 'strong_downtrend';
            state.strength = -1;
        } else if (current.sma20 > current.sma50) {
            state.primary = 'weak_uptrend';
            state.strength = 0.5;
        } else {
            state.primary = 'weak_downtrend';
            state.strength = -0.5;
        }
        
        // Determine secondary trend
        const sma20Slope = (sma20[sma20.length - 1] - sma20[sma20.length - 5]) / sma20[sma20.length - 5];
        if (Math.abs(sma20Slope) < 0.001) {
            state.secondary = 'consolidating';
        } else {
            state.secondary = sma20Slope > 0 ? 'pullback_up' : 'pullback_down';
        }
        
        return state;
    }

    static calculateRegimeConfidence(regime, volatility, momentum, trendStrength) {
        let confidence = 0.5; // Base confidence
        
        // Adjust based on trend strength
        const latestTrendStrength = trendStrength[trendStrength.length - 1];
        if (latestTrendStrength > 30) confidence += 0.2;
        else if (latestTrendStrength < 15) confidence -= 0.1;
        
        // Adjust based on volatility alignment
        if (regime.type.includes('trending') && volatility > 0.3) confidence += 0.15;
        else if (regime.type === 'ranging' && volatility < 0.2) confidence += 0.15;
        
        // Adjust based on momentum
        const latestMomentum = momentum[momentum.length - 1];
        if (Math.abs(latestMomentum) > 2) {
            if ((regime.type === 'trending_up' && latestMomentum > 0) ||
                (regime.type === 'trending_down' && latestMomentum < 0)) {
                confidence += 0.15;
            } else {
                confidence -= 0.2;
            }
        }
        
        return Math.max(0, Math.min(1, confidence));
    }
}

module.exports = MarketAnalysis;