class PerformanceAnalyzer {
    constructor(metricsCollector, binanceMonitor) {
        this.metrics = metricsCollector;
        this.monitor = binanceMonitor;
        this.startTime = Date.now();
        this.analysisInterval = 10 * 60 * 1000; // 10 minutes
        this.startAnalysis();
    }

    startAnalysis() {
        this.intervalId = setInterval(() => {
            this.generateImprovementReport();
        }, this.analysisInterval);
    }

    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }
    }

    async generateImprovementReport() {
        const report = this.metrics.generateReport();
        const analysis = {
            tradingPerformance: this.analyzeTradingPerformance(report),
            timeAnalysis: this.analyzeTimePatterns(report),
            symbolAnalysis: this.analyzeSymbolPerformance(report),
            riskAnalysis: this.analyzeRiskMetrics(report),
            improvementSuggestions: []
        };

        // Get current market conditions
        const marketConditions = await this.getCurrentMarketConditions();
        
        // Generate specific improvement suggestions
        this.generateSuggestions(analysis, marketConditions);

        // Save the report
        const fs = require('fs');
        const path = require('path');
        const reportPath = path.join(__dirname, '../test_data/improvement_report.json');
        fs.writeFileSync(reportPath, JSON.stringify(analysis, null, 2));

        // Log key findings
        this.logKeyFindings(analysis);
        
        return analysis;
    }

    analyzeTradingPerformance(report) {
        const { summary } = report;
        return {
            profitability: {
                status: this.categorizePerformance(summary.profitFactor),
                actual: summary.profitFactor,
                target: 1.5,
                improvement: summary.profitFactor < 1.5
            },
            winRate: {
                status: this.categorizeWinRate(summary.winRate),
                actual: summary.winRate,
                target: 0.8,
                improvement: summary.winRate < 0.8
            },
            efficiency: {
                tradeFrequency: summary.totalTrades / (10/60), // trades per hour
                optimalFrequency: this.calculateOptimalFrequency(summary),
                needsAdjustment: Math.abs(summary.totalTrades / (10/60) - this.calculateOptimalFrequency(summary)) > 5
            }
        };
    }

    analyzeTimePatterns(report) {
        const { hourly } = report.timeAnalysis;
        const hourlyPerformance = Object.entries(hourly).map(([hour, stats]) => ({
            hour: parseInt(hour),
            profitability: stats.profit / stats.trades || 0,
            volume: stats.volume,
            trades: stats.trades
        }));

        return {
            bestHours: hourlyPerformance
                .sort((a, b) => b.profitability - a.profitability)
                .slice(0, 3),
            worstHours: hourlyPerformance
                .sort((a, b) => a.profitability - b.profitability)
                .slice(0, 3),
            needsTimeAdjustment: this.checkTimeAdjustmentNeeded(hourlyPerformance)
        };
    }

    analyzeSymbolPerformance(report) {
        const symbolAnalysis = Object.entries(report.symbolAnalysis).map(([symbol, stats]) => ({
            symbol,
            profitability: stats.profit / stats.trades || 0,
            winRate: stats.wins / (stats.wins + stats.losses),
            volume: stats.volume,
            trades: stats.trades
        }));

        return {
            bestPerforming: symbolAnalysis
                .sort((a, b) => b.profitability - a.profitability)
                .slice(0, 3),
            worstPerforming: symbolAnalysis
                .sort((a, b) => a.profitability - b.profitability)
                .slice(0, 3),
            recommendedSymbols: this.getRecommendedSymbols(symbolAnalysis)
        };
    }

    analyzeRiskMetrics(report) {
        const { summary } = report;
        return {
            riskReturnRatio: {
                actual: Math.abs(summary.averageWin / summary.averageLoss),
                target: 2.0,
                needsImprovement: Math.abs(summary.averageWin / summary.averageLoss) < 2.0
            },
            drawdown: {
                actual: summary.maxDrawdown,
                critical: summary.maxDrawdown > 25,
                recommendation: this.getDrawdownRecommendation(summary.maxDrawdown)
            },
            positionSizing: this.analyzePositionSizing(report)
        };
    }

    async getCurrentMarketConditions() {
        const symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'];
        const conditions = {};
        
        for (const symbol of symbols) {
            const volatility = this.monitor.riskControls.marketVolatility.get(symbol);
            const sentiment = await this.monitor.getSentimentData(symbol);
            conditions[symbol] = { volatility, sentiment };
        }
        
        return conditions;
    }

    generateSuggestions(analysis, marketConditions) {
        const suggestions = [];

        // Trading Performance Suggestions
        if (analysis.tradingPerformance.winRate.improvement) {
            suggestions.push({
                priority: 'HIGH',
                category: 'Win Rate',
                issue: 'Win rate below target of 80%',
                suggestion: 'Increase prediction confidence threshold and strengthen entry criteria'
            });
        }

        if (analysis.tradingPerformance.efficiency.needsAdjustment) {
            suggestions.push({
                priority: 'MEDIUM',
                category: 'Trade Frequency',
                issue: 'Sub-optimal trade frequency',
                suggestion: 'Adjust trading interval based on market volatility and opportunity score'
            });
        }

        // Risk Management Suggestions
        if (analysis.riskAnalysis.riskReturnRatio.needsImprovement) {
            suggestions.push({
                priority: 'HIGH',
                category: 'Risk-Return',
                issue: 'Risk-return ratio below target',
                suggestion: 'Widen profit targets and tighten stop losses'
            });
        }

        // Market Adaptation Suggestions
        const highVolSymbols = Object.entries(marketConditions)
            .filter(([, data]) => data.volatility > 0.02)
            .map(([symbol]) => symbol);
            
        if (highVolSymbols.length > 0) {
            suggestions.push({
                priority: 'MEDIUM',
                category: 'Volatility',
                issue: `High volatility in ${highVolSymbols.join(', ')}`,
                suggestion: 'Reduce position sizes and tighten stop losses for these symbols'
            });
        }

        analysis.improvementSuggestions = suggestions;
    }

    categorizePerformance(profitFactor) {
        if (profitFactor >= 2.0) return 'EXCELLENT';
        if (profitFactor >= 1.5) return 'GOOD';
        if (profitFactor >= 1.0) return 'FAIR';
        return 'POOR';
    }

    categorizeWinRate(winRate) {
        if (winRate >= 0.8) return 'EXCELLENT';
        if (winRate >= 0.6) return 'GOOD';
        if (winRate >= 0.5) return 'FAIR';
        return 'POOR';
    }

    calculateOptimalFrequency(summary) {
        // Base optimal frequency on profit factor and win rate
        const baseFrequency = 20; // trades per hour
        const performanceMultiplier = Math.min(summary.profitFactor, 2);
        return Math.round(baseFrequency * performanceMultiplier);
    }

    checkTimeAdjustmentNeeded(hourlyPerformance) {
        const avgProfit = hourlyPerformance.reduce((sum, h) => sum + h.profitability, 0) / hourlyPerformance.length;
        const profitVariance = hourlyPerformance.some(h => Math.abs(h.profitability - avgProfit) > avgProfit);
        return profitVariance;
    }

    getRecommendedSymbols(symbolAnalysis) {
        return symbolAnalysis
            .filter(s => s.winRate > 0.6 && s.trades > 5)
            .map(s => s.symbol);
    }

    getDrawdownRecommendation(drawdown) {
        if (drawdown > 25) return 'Immediately reduce position sizes and increase risk controls';
        if (drawdown > 15) return 'Consider reducing position sizes by 25%';
        if (drawdown > 10) return 'Monitor closely and prepare risk reduction measures';
        return 'Current drawdown management is adequate';
    }

    analyzePositionSizing(report) {
        const trades = report.detailedTrades;
        const avgPosition = trades.reduce((sum, t) => sum + (t.quantity * t.price), 0) / trades.length;
        const balance = this.monitor.testEnv.balance;
        const positionToBalance = avgPosition / balance;

        return {
            averagePositionSize: avgPosition,
            positionToBalanceRatio: positionToBalance,
            recommendation: this.getPositionSizingRecommendation(positionToBalance)
        };
    }

    getPositionSizingRecommendation(ratio) {
        if (ratio > 0.15) return 'Reduce position sizes to limit risk exposure';
        if (ratio < 0.05) return 'Consider increasing position sizes for better capital utilization';
        return 'Current position sizing is appropriate';
    }

    logKeyFindings(analysis) {
        console.log('\n=== 10-Minute Trading Analysis ===');
        console.log('\nKey Performance Metrics:');
        console.log(`Win Rate: ${(analysis.tradingPerformance.winRate.actual * 100).toFixed(2)}%`);
        console.log(`Profit Factor: ${analysis.tradingPerformance.profitability.actual.toFixed(2)}`);
        
        console.log('\nTop Improvement Suggestions:');
        analysis.improvementSuggestions
            .sort((a, b) => a.priority === 'HIGH' ? -1 : 1)
            .forEach(suggestion => {
                console.log(`\n[${suggestion.priority}] ${suggestion.category}:`);
                console.log(`Issue: ${suggestion.issue}`);
                console.log(`Solution: ${suggestion.suggestion}`);
            });
    }
}

module.exports = PerformanceAnalyzer;