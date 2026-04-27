class TestClient {
    constructor(testEnv) {
        this.testEnv = testEnv;
        this.historicalData = new Map();
        this.priceFeeds = new Map();
        this.lastPriceUpdate = Date.now();
    }

    async loadHistoricalData(symbol, timeframe = '1m', daysBack = 30) {
        const filePath = path.join(__dirname, `../test_data/${symbol}_${timeframe}_historical.json`);
        try {
            if (fs.existsSync(filePath)) {
                const data = JSON.parse(fs.readFileSync(filePath));
                this.historicalData.set(symbol, data);
                return data;
            }
            // If no historical data, generate synthetic data
            return this.generateSyntheticData(symbol, timeframe, daysBack);
        } catch (error) {
            console.error('Error loading historical data:', error);
            return this.generateSyntheticData(symbol, timeframe, daysBack);
        }
    }

    generateSyntheticData(symbol, timeframe, daysBack) {
        const data = [];
        const basePrice = this.getBasePrice(symbol);
        const volatility = 0.02; // 2% daily volatility
        const intervals = this.getIntervalCount(timeframe, daysBack);
        
        let currentPrice = basePrice;
        let currentTime = Date.now() - (daysBack * 24 * 60 * 60 * 1000);
        
        for (let i = 0; i < intervals; i++) {
            const random = Math.random() * 2 - 1; // Random number between -1 and 1
            const priceChange = currentPrice * volatility * random;
            currentPrice += priceChange;
            
            const candleData = {
                openTime: currentTime,
                open: currentPrice - (priceChange / 2),
                high: currentPrice + Math.abs(priceChange),
                low: currentPrice - Math.abs(priceChange),
                close: currentPrice,
                volume: Math.random() * 1000000,
                closeTime: currentTime + this.getIntervalMilliseconds(timeframe)
            };
            
            data.push(candleData);
            currentTime += this.getIntervalMilliseconds(timeframe);
        }
        
        this.historicalData.set(symbol, data);
        return data;
    }

    getBasePrice(symbol) {
        const prices = {
            'BTCUSDT': 50000,
            'ETHUSDT': 3000,
            'BNBUSDT': 300,
            'ADAUSDT': 1.5,
            'DOGEUSDT': 0.1
        };
        return prices[symbol] || 100;
    }

    getIntervalMilliseconds(timeframe) {
        const intervals = {
            '1m': 60 * 1000,
            '5m': 5 * 60 * 1000,
            '15m': 15 * 60 * 1000,
            '1h': 60 * 60 * 1000,
            '4h': 4 * 60 * 60 * 1000,
            '1d': 24 * 60 * 60 * 1000
        };
        return intervals[timeframe] || 60 * 1000;
    }

    getIntervalCount(timeframe, daysBack) {
        const millisPerDay = 24 * 60 * 60 * 1000;
        const intervalMs = this.getIntervalMilliseconds(timeframe);
        return Math.floor((daysBack * millisPerDay) / intervalMs);
    }

    async simulateMarketOrder(symbol, side, quantity) {
        const currentPrice = await this.getCurrentPrice(symbol);
        const slippage = currentPrice * this.testEnv.slippage * (side === 'BUY' ? 1 : -1);
        const executionPrice = currentPrice + slippage;
        const fee = quantity * executionPrice * this.testEnv.fees.taker;
        
        const order = {
            symbol,
            side,
            quantity,
            price: executionPrice,
            executedQty: quantity,
            cummulativeQuoteQty: quantity * executionPrice,
            status: 'FILLED',
            type: 'MARKET',
            fee,
            timestamp: Date.now()
        };

        this.updateTestBalance(order);
        this.testEnv.orderHistory.push(order);
        
        return { data: order };
    }

    updateTestBalance(order) {
        const total = order.executedQty * order.price;
        if (order.side === 'BUY') {
            this.testEnv.balance -= (total + order.fee);
        } else {
            this.testEnv.balance += (total - order.fee);
        }
    }

    async getCurrentPrice(symbol) {
        const data = this.historicalData.get(symbol);
        if (!data || data.length === 0) {
            await this.loadHistoricalData(symbol);
        }
        
        const timeSinceLastUpdate = Date.now() - this.lastPriceUpdate;
        if (timeSinceLastUpdate >= 1000) { // Update price every second
            const lastPrice = this.priceFeeds.get(symbol) || this.getBasePrice(symbol);
            const volatility = 0.0002; // 0.02% per second
            const random = Math.random() * 2 - 1;
            const newPrice = lastPrice * (1 + volatility * random);
            this.priceFeeds.set(symbol, newPrice);
            this.lastPriceUpdate = Date.now();
            return newPrice;
        }
        
        return this.priceFeeds.get(symbol) || this.getBasePrice(symbol);
    }

    async account() {
        return {
            balances: [{
                asset: 'USDT',
                free: this.testEnv.balance.toString(),
                locked: '0.00000000'
            }]
        };
    }

    async klines(symbol, interval, options) {
        let data = this.historicalData.get(symbol);
        if (!data) {
            data = await this.loadHistoricalData(symbol, interval);
        }
        
        const limit = options?.limit || 500;
        return { data: data.slice(-limit) };
    }

    async depth(symbol) {
        const currentPrice = await this.getCurrentPrice(symbol);
        const spreadPercentage = 0.0005; // 0.05% spread
        const spread = currentPrice * spreadPercentage;
        
        // Generate mock order book
        const bids = Array.from({length: 10}, (_, i) => {
            const price = currentPrice - (spread * (i + 1));
            const quantity = Math.random() * 10;
            return [price.toFixed(8), quantity.toFixed(8)];
        });
        
        const asks = Array.from({length: 10}, (_, i) => {
            const price = currentPrice + (spread * (i + 1));
            const quantity = Math.random() * 10;
            return [price.toFixed(8), quantity.toFixed(8)];
        });
        
        return { data: { bids, asks } };
    }

    async ticker(symbol) {
        const currentPrice = await this.getCurrentPrice(symbol);
        return {
            data: {
                symbol,
                price: currentPrice.toString(),
                volume: (Math.random() * 1000000).toString()
            }
        };
    }
}

module.exports = TestClient;