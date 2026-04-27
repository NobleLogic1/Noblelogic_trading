#!/usr/bin/env python3
"""
Simplified test script to validate live trading enhancements
"""

import asyncio
import time
import json
import random
from datetime import datetime
from live_data_fetcher import LiveDataFetcher

# Mock classes for testing
class MockMLEngine:
    def __init__(self):
        self.gpu_available = False
        
    async def predict(self, features):
        """Mock prediction"""
        # Simulate ML processing time
        await asyncio.sleep(0.1)
        
        # Random prediction
        action = random.choices([0, 1, 2], weights=[0.6, 0.2, 0.2])[0]
        return {
            'action': action,
            'confidence': random.uniform(0.6, 0.95),
            'gpu_used': False,
            'reasoning': "Mock prediction for testing"
        }

class MockRiskAssessor:
    def __init__(self):
        self.market_regime = "NORMAL"

class MockTradingSystem:
    def __init__(self):
        self.data_fetcher = LiveDataFetcher()
        self.ml_engine = MockMLEngine()
        self.risk_assessor = MockRiskAssessor()
        
        # Multi-timeframe configuration
        self.timeframes = ["5m", "15m", "1h", "4h"]
        self.timeframe_weights = {"5m": 0.2, "15m": 0.3, "1h": 0.3, "4h": 0.2}
        
        # Universe and symbols
        self.universe = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT', 
            'DOGE/USDT', 'DOT/USDT', 'AVAX/USDT', 'LINK/USDT', 'MATIC/USDT'
        ]
        self.symbols = self.universe[:5]
        
        # Symbol metrics
        self.symbol_metrics = {symbol: {
            'opportunity_score': random.random(),
            'volatility': random.random() * 0.2,
            'trading_volume': random.random(),
            'signal_consistency': random.random(),
            'last_signals': []
        } for symbol in self.universe}
        
        # Performance tracking
        self.performance_metrics = {
            'ml_response_times': [],
            'api_response_times': [],
            'parallel_efficiency': []
        }
    
    async def analyze_single_timeframe(self, symbol, timeframe, price, klines=None, stats=None):
        """Mock timeframe analysis"""
        # Simulate analysis time
        await asyncio.sleep(0.05)
        
        # Generate random signal with bias based on timeframe
        # Shorter timeframes more volatile
        if timeframe == "5m":
            weights = [0.4, 0.3, 0.3]  # More trading signals
        elif timeframe == "15m":
            weights = [0.5, 0.25, 0.25]
        elif timeframe == "1h":
            weights = [0.6, 0.2, 0.2]
        else:  # 4h
            weights = [0.7, 0.15, 0.15]  # More conservative
            
        action = random.choices([0, 1, 2], weights=weights)[0]
        action_map = {0: 'HOLD', 1: 'BUY', 2: 'SELL'}
        signal = action_map[action]
        
        return {
            'timeframe': timeframe,
            'signal': signal,
            'confidence': random.uniform(0.6, 0.95),
            'features': [random.random() for _ in range(10)]
        }
    
    async def analyze_multiple_timeframes(self, symbol, price, stats=None):
        """Analyze a symbol across multiple timeframes"""
        results = {}
        tasks = []
        
        for timeframe in self.timeframes:
            # Create task for this timeframe
            task = self.analyze_single_timeframe(symbol, timeframe, price)
            tasks.append(task)
        
        # Execute all timeframe analyses in parallel
        timeframe_results = await asyncio.gather(*tasks)
        
        # Organize results by timeframe
        for i, timeframe in enumerate(self.timeframes):
            results[timeframe] = timeframe_results[i]
            
        return results
    
    def combine_timeframe_signals(self, timeframe_results):
        """Combine signals from multiple timeframes using weighted voting"""
        signal_votes = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 0.0}
        total_weight = 0.0
        
        for timeframe, result in timeframe_results.items():
            signal = result['signal']
            confidence = result['confidence']
            weight = self.timeframe_weights.get(timeframe, 0.25)
            
            weighted_vote = weight * confidence
            signal_votes[signal] += weighted_vote
            total_weight += weighted_vote
        
        # Normalize the votes
        if total_weight > 0:
            for signal in signal_votes:
                signal_votes[signal] /= total_weight
        
        # Find the signal with the highest weighted vote
        winning_signal = max(signal_votes, key=signal_votes.get)
        winning_confidence = signal_votes[winning_signal]
        
        return winning_signal, winning_confidence
    
    async def fetch_live_data(self, symbols=None):
        """Fetch live market data"""
        symbols_to_fetch = symbols or self.symbols
        return self.data_fetcher.get_multiple_prices(symbols_to_fetch)
    
    async def select_active_symbols(self):
        """Select most promising assets to trade"""
        sorted_symbols = sorted(
            self.universe,
            key=lambda s: self.symbol_metrics[s]['opportunity_score'], 
            reverse=True
        )
        
        # Always include major coins
        major_coins = ['BTC/USDT', 'ETH/USDT']
        selected = [c for c in major_coins if c in self.universe]
        
        # Fill remaining slots with highest opportunity assets
        remaining_slots = 5 - len(selected)
        for symbol in sorted_symbols:
            if symbol not in selected and len(selected) < 5:
                selected.append(symbol)
        
        self.symbols = selected
        return selected
    
    def generate_reasoning(self, timeframe_results):
        """Generate reasoning text based on multi-timeframe analysis"""
        signal_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        for tf, result in timeframe_results.items():
            signal_counts[result['signal']] += 1
        
        dominant_signal = max(signal_counts, key=signal_counts.get)
        dominant_count = signal_counts[dominant_signal]
        
        if dominant_count == len(self.timeframes):
            return f"Strong {dominant_signal} signal across all timeframes."
        elif dominant_count > len(self.timeframes) / 2:
            return f"{dominant_signal} signal on majority of timeframes ({dominant_count}/{len(self.timeframes)})."
        else:
            return "Mixed signals across timeframes."
            
async def test_multi_timeframe():
    """Test multi-timeframe analysis"""
    print("\n==== Testing Multi-Timeframe Analysis ====")
    
    # Create mock trading system
    trading_system = MockTradingSystem()
    
    # Test single symbol with multi-timeframe analysis
    symbol = "BTC/USDT"
    prices = await trading_system.fetch_live_data([symbol])
    
    if not prices or symbol not in prices:
        print(f"❌ Could not fetch price data for {symbol}")
        return
    
    price = prices[symbol]
    print(f"Analyzing {symbol} at ${price:.2f} across {len(trading_system.timeframes)} timeframes...")
    
    # Run multi-timeframe analysis
    timeframe_results = await trading_system.analyze_multiple_timeframes(symbol, price)
    
    # Combine signals
    combined_signal, combined_confidence = trading_system.combine_timeframe_signals(timeframe_results)
    
    # Display results
    print(f"\nCombined Signal: {combined_signal} with {combined_confidence:.1%} confidence\n")
    
    print("Individual timeframe results:")
    for tf, result in sorted(timeframe_results.items()):
        print(f"  {tf}: {result['signal']} ({result['confidence']:.1%})")
    
    # Generate reasoning
    reasoning = trading_system.generate_reasoning(timeframe_results)
    print(f"\nReasoning: {reasoning}")
            
async def test_dynamic_selection():
    """Test dynamic asset selection"""
    print("\n==== Testing Dynamic Asset Selection ====")
    
    # Create mock trading system
    trading_system = MockTradingSystem()
    
    print("Before selection:", trading_system.symbols)
    
    # Update metrics with some realistic data
    for symbol in trading_system.universe:
        metrics = trading_system.symbol_metrics[symbol]
        metrics['opportunity_score'] = random.random()
    
    # Force higher scores for some symbols to test selection
    trading_system.symbol_metrics['DOGE/USDT']['opportunity_score'] = 0.95
    trading_system.symbol_metrics['LINK/USDT']['opportunity_score'] = 0.92
    trading_system.symbol_metrics['ADA/USDT']['opportunity_score'] = 0.15
    
    # Run selection
    selected = await trading_system.select_active_symbols()
    print("After selection:", selected)
    
    # Show top opportunities
    top_symbols = sorted(
        trading_system.symbol_metrics.items(),
        key=lambda x: x[1]['opportunity_score'],
        reverse=True
    )[:5]
    
    print("\nTop 5 assets by opportunity score:")
    for symbol, metrics in top_symbols:
        print(f"{symbol}: {metrics['opportunity_score']:.2f}")
            
async def test_parallel_processing():
    """Test parallel signal processing"""
    print("\n==== Testing Parallel Signal Processing ====")
    
    # Create mock trading system
    trading_system = MockTradingSystem()
    
    # Fetch data for active symbols
    print(f"Fetching data for {len(trading_system.symbols)} active symbols...")
    price_data = await trading_system.fetch_live_data()
    
    if not price_data:
        print("❌ Could not fetch price data")
        return
    
    # Sequential processing test
    print("\nTesting sequential processing...")
    seq_start = time.time()
    
    for symbol, price in price_data.items():
        # Process each symbol and each timeframe sequentially
        for timeframe in trading_system.timeframes:
            await trading_system.analyze_single_timeframe(symbol, timeframe, price)
    
    seq_time = time.time() - seq_start
    print(f"Sequential processing time: {seq_time:.2f}s")
    
    # Parallel processing test
    print("\nTesting parallel processing...")
    parallel_start = time.time()
    
    # Create all tasks
    tasks = []
    for symbol, price in price_data.items():
        # For each symbol, create a multi-timeframe analysis task
        task = trading_system.analyze_multiple_timeframes(symbol, price)
        tasks.append(task)
    
    # Execute all symbol analyses concurrently
    await asyncio.gather(*tasks)
    
    parallel_time = time.time() - parallel_start
    print(f"Parallel processing time: {parallel_time:.2f}s")
    print(f"Speedup factor: {seq_time / parallel_time:.1f}x")

async def main():
    """Run all tests"""
    print("TESTING LIVE TRADING ENHANCEMENTS")
    print("=" * 60)
    
    await test_multi_timeframe()
    await test_dynamic_selection()
    await test_parallel_processing()
    
    print("\n✅ All enhancement tests complete!")

if __name__ == "__main__":
    asyncio.run(main())