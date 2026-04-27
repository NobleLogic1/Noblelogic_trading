const axios = require('axios');
const natural = require('natural');
const tokenizer = new natural.WordTokenizer();

class SentimentEngine {
    constructor() {
        this.newsCache = new Map();
        this.socialCache = new Map();
        this.tokenizer = tokenizer;
        this.updateInterval = 5 * 60 * 1000; // 5 minutes
    }

    async initialize() {
        this.startPeriodicUpdate();
    }

    async analyzeMarketSentiment(symbol) {
        try {
            const [news, social, technical] = await Promise.all([
                this.getNewsData(symbol),
                this.getSocialData(symbol),
                this.getTechnicalData(symbol)
            ]);

            const sentiment = {
                overall: this.calculateOverallSentiment(news, social, technical),
                newsScore: news.score,
                socialScore: social.score,
                technicalScore: technical.score,
                confidence: this.calculateConfidence(news, social, technical),
                trends: this.analyzeTrends(news, social),
                timestamp: new Date().toISOString()
            };

            return sentiment;
        } catch (error) {
            console.error('Sentiment analysis error:', error);
            throw error;
        }
    }

    async getNewsData(symbol) {
        // Using CryptoCompare News API
        const response = await axios.get(
            `https://min-api.cryptocompare.com/data/v2/news/?categories=${symbol}&excludeCategories=Sponsored`
        );
        
        const news = response.data.Data.slice(0, 10);
        let score = 0;
        
        news.forEach(article => {
            const words = this.tokenizer.tokenize(article.title + ' ' + article.body);
            score += this.analyzeSentimentScore(words);
        });

        return {
            score: score / news.length,
            articles: news
        };
    }

    async getSocialData(symbol) {
        // Using Twitter API v2 for social sentiment
        // Note: Implementation requires Twitter API credentials
        return {
            score: 0.5, // Placeholder
            volume: 1000,
            trending: true
        };
    }

    async getTechnicalData(symbol) {
        const indicators = await this.calculateTechnicalIndicators(symbol);
        return {
            score: indicators.score,
            rsi: indicators.rsi,
            macd: indicators.macd,
            volume: indicators.volume
        };
    }

    calculateOverallSentiment(news, social, technical) {
        const weights = {
            news: 0.3,
            social: 0.3,
            technical: 0.4
        };

        return (
            news.score * weights.news +
            social.score * weights.social +
            technical.score * weights.technical
        );
    }

    calculateConfidence(news, social, technical) {
        // Confidence based on agreement between different data sources
        const scores = [news.score, social.score, technical.score];
        const variance = this.calculateVariance(scores);
        return Math.max(0, 1 - variance);
    }

    analyzeTrends(news, social) {
        return {
            shortTerm: this.calculateShortTermTrend(news, social),
            mediumTerm: this.calculateMediumTermTrend(news, social),
            longTerm: this.calculateLongTermTrend(news, social)
        };
    }

    calculateVariance(numbers) {
        const mean = numbers.reduce((a, b) => a + b) / numbers.length;
        const squareDiffs = numbers.map(value => Math.pow(value - mean, 2));
        return Math.sqrt(squareDiffs.reduce((a, b) => a + b) / numbers.length);
    }

    startPeriodicUpdate() {
        setInterval(() => {
            this.updateSentimentData();
        }, this.updateInterval);
    }

    async updateSentimentData() {
        // Update cached sentiment data periodically
        const symbols = ['BTC', 'ETH', 'ADA']; // Add more as needed
        for (const symbol of symbols) {
            const sentiment = await this.analyzeMarketSentiment(symbol);
            this.newsCache.set(symbol, sentiment);
        }
    }
}

module.exports = new SentimentEngine();
