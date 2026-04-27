class TestMetricsCollector {
    constructor() {
        this.trades = [];
        this.metrics = {
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
            largestLoss: 0,
            dailyStats: new Map(),
            hourlyStats: new Map(),
            symbolStats: new Map()
        };
    }

    recordTrade(trade) {
        this.trades.push(trade);
        this.updateMetrics(trade);
        this.updateTimeBasedStats(trade);
        this.updateSymbolStats(trade);
    }

    updateMetrics(trade) {
        this.metrics.totalTrades++;
        
        if (trade.profit > 0) {
            this.metrics.successfulTrades++;
            this.metrics.largestWin = Math.max(this.metrics.largestWin, trade.profit);
        } else {
            this.metrics.failedTrades++;
            this.metrics.largestLoss = Math.min(this.metrics.largestLoss, trade.profit);
        }

        // Update win rate
        this.metrics.winRate = this.metrics.successfulTrades / this.metrics.totalTrades;

        // Update average win/loss
        const wins = this.trades.filter(t => t.profit > 0);
        const losses = this.trades.filter(t => t.profit <= 0);
        
        this.metrics.averageWin = wins.reduce((sum, t) => sum + t.profit, 0) / wins.length;
        this.metrics.averageLoss = losses.reduce((sum, t) => sum + t.profit, 0) / losses.length;

        // Calculate profit factor
        const grossProfit = wins.reduce((sum, t) => sum + t.profit, 0);
        const grossLoss = Math.abs(losses.reduce((sum, t) => sum + t.profit, 0));
        this.metrics.profitFactor = grossProfit / (grossLoss || 1);

        // Calculate Sharpe Ratio
        this.metrics.sharpeRatio = this.calculateSharpeRatio();

        // Update max drawdown
        this.metrics.maxDrawdown = this.calculateMaxDrawdown();
    }

    updateTimeBasedStats(trade) {
        const date = new Date(trade.timestamp);
        const dateKey = date.toISOString().split('T')[0];
        const hourKey = date.getUTCHours();

        // Update daily stats
        if (!this.metrics.dailyStats.has(dateKey)) {
            this.metrics.dailyStats.set(dateKey, {
                trades: 0,
                profit: 0,
                volume: 0
            });
        }
        const dailyStats = this.metrics.dailyStats.get(dateKey);
        dailyStats.trades++;
        dailyStats.profit += trade.profit;
        dailyStats.volume += trade.quantity * trade.price;

        // Update hourly stats
        if (!this.metrics.hourlyStats.has(hourKey)) {
            this.metrics.hourlyStats.set(hourKey, {
                trades: 0,
                profit: 0,
                volume: 0
            });
        }
        const hourlyStats = this.metrics.hourlyStats.get(hourKey);
        hourlyStats.trades++;
        hourlyStats.profit += trade.profit;
        hourlyStats.volume += trade.quantity * trade.price;
    }

    updateSymbolStats(trade) {
        if (!this.metrics.symbolStats.has(trade.symbol)) {
            this.metrics.symbolStats.set(trade.symbol, {
                trades: 0,
                profit: 0,
                volume: 0,
                wins: 0,
                losses: 0
            });
        }
        const stats = this.metrics.symbolStats.get(trade.symbol);
        stats.trades++;
        stats.profit += trade.profit;
        stats.volume += trade.quantity * trade.price;
        if (trade.profit > 0) stats.wins++;
        else stats.losses++;
    }

    calculateSharpeRatio() {
        const returns = this.trades.map(t => t.profit);
        const meanReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;
        const stdDev = Math.sqrt(
            returns.reduce((sum, r) => sum + Math.pow(r - meanReturn, 2), 0) / returns.length
        );
        return meanReturn / (stdDev || 1);
    }

    calculateMaxDrawdown() {
        let peak = 0;
        let maxDrawdown = 0;
        let runningTotal = 0;

        for (const trade of this.trades) {
            runningTotal += trade.profit;
            if (runningTotal > peak) {
                peak = runningTotal;
            }
            const drawdown = peak - runningTotal;
            maxDrawdown = Math.max(maxDrawdown, drawdown);
        }

        return maxDrawdown;
    }

    generateReport() {
        return {
            summary: {
                totalTrades: this.metrics.totalTrades,
                winRate: this.metrics.winRate,
                profitFactor: this.metrics.profitFactor,
                sharpeRatio: this.metrics.sharpeRatio,
                maxDrawdown: this.metrics.maxDrawdown,
                averageWin: this.metrics.averageWin,
                averageLoss: this.metrics.averageLoss,
                largestWin: this.metrics.largestWin,
                largestLoss: this.metrics.largestLoss
            },
            timeAnalysis: {
                daily: Object.fromEntries(this.metrics.dailyStats),
                hourly: Object.fromEntries(this.metrics.hourlyStats)
            },
            symbolAnalysis: Object.fromEntries(this.metrics.symbolStats),
            detailedTrades: this.trades
        };
    }

    saveReport(filePath) {
        const report = this.generateReport();
        fs.writeFileSync(filePath, JSON.stringify(report, null, 2));
        return report;
    }
}

module.exports = TestMetricsCollector;