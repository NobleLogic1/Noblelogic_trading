#!/usr/bin/env python3
"""
Test script to validate live trading enhancements:
1. Multi-timeframe analysis
2. Dynamic asset selection
3. Parallel signal processing
"""

import asyncio
import time
import json
from datetime import datetime
from live_trading_30min import LiveTradingSystem

async def test_multi_timeframe():
    """Test multi-timeframe analysis functionality"""
    print("\n==== Testing Multi-Timeframe Analysis ====")
    
    # Create trading system instance
    trading_system = LiveTradingSystem()
    
    # Test single symbol with multi-timeframe analysis
    symbol = "BTC/USDT"
    prices = trading_system.data_fetcher.get_multiple_prices([symbol])
    
    if not prices or symbol not in prices:
        print(f"❌ Could not fetch price data for {symbol}")
        return
    
    price = prices[symbol]
    stats = trading_system.data_fetcher.get_24h_stats(symbol)
    
    print(f"Analyzing {symbol} at ${price:.2f} across {len(trading_system.timeframes)} timeframes...")
    start_time = time.time()
    
    # Run multi-timeframe analysis
    timeframe_results = await trading_system.analyze_multiple_timeframes(symbol, price, stats)
    
    # Combine signals
    combined_signal, combined_confidence = trading_system.combine_timeframe_signals(timeframe_results)
    
    # Display results
    print(f"\nMulti-timeframe analysis complete ({(time.time() - start_time)*1000:.1f}ms)")
    print(f"Combined Signal: {combined_signal} with {combined_confidence:.1%} confidence\n")
    
    print("Individual timeframe results:")
    for tf, result in timeframe_results.items():
        print(f"  {tf}: {result['signal']} ({result['confidence']:.1%})")
    
    # Generate reasoning
    reasoning = trading_system.generate_reasoning(timeframe_results)
    print(f"\nReasoning: {reasoning}")

async def test_dynamic_selection():
    """Test dynamic asset selection functionality"""
    print("\n==== Testing Dynamic Asset Selection ====")
    
    # Create trading system instance
    trading_system = LiveTradingSystem()
    
    # Initialize metrics for the universe
    print(f"Fetching data for {len(trading_system.universe)} assets in universe...")
    universe_prices, universe_stats = await trading_system.fetch_universe_data()
    
    if not universe_prices:
        print("❌ Could not fetch universe data")
        return
    
    print(f"Successfully fetched data for {len(universe_prices)} assets")
    
    # Perform quick opportunity assessment
    for symbol, price in universe_prices.items():
        if symbol in universe_stats:
            # Update volatility and volume metrics for selection
            stats = universe_stats[symbol]
            metrics = trading_system.symbol_metrics[symbol]
            
            price_change_pct = stats.get('priceChangePercent', 0)
            metrics['volatility'] = abs(float(price_change_pct)) / 100 if price_change_pct else 0.02
            
            volume = stats.get('volume', 0)
            metrics['trading_volume'] = float(volume) / 10000000
            
            # Set random signal consistency for testing
            import random
            metrics['signal_consistency'] = random.random()
            metrics['opportunity_score'] = (
                random.random() * 0.4 +
                metrics['volatility'] * 0.3 +
                metrics['trading_volume'] * 0.2 +
                metrics['signal_consistency'] * 0.1
            )
    
    # Test dynamic selection
    print("Before selection:", trading_system.symbols)
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
        print(f"{symbol}: {metrics['opportunity_score']:.2f} (Vol: {metrics['volatility']:.1%}, Volume: {metrics['trading_volume']:.2f})")

async def test_parallel_processing():
    """Test parallel signal processing"""
    print("\n==== Testing Parallel Signal Processing ====")
    
    # Create trading system instance
    trading_system = LiveTradingSystem()
    
    # Fetch data for active symbols
    print(f"Fetching data for {len(trading_system.symbols)} active symbols...")
    price_data = await trading_system.fetch_live_data()
    
    if not price_data:
        print("❌ Could not fetch price data")
        return
    
    # Sequential processing for comparison
    print("\nTesting sequential processing...")
    seq_start = time.time()
    seq_results = []
    
    for symbol, price in price_data.items():
        stats = trading_system.data_fetcher.get_24h_stats(symbol)
        analysis = await trading_system.analyze_market(symbol, price)
        seq_results.append((symbol, analysis))
    
    seq_time = time.time() - seq_start
    print(f"Sequential processing time: {seq_time:.2f}s")
    
    # Parallel processing
    print("\nTesting parallel processing...")
    tasks = []
    for symbol, price in price_data.items():
        stats = trading_system.data_fetcher.get_24h_stats(symbol)
        task = trading_system.process_symbol_parallel(symbol, price, stats)
        tasks.append(task)
    
    parallel_start = time.time()
    parallel_results = await asyncio.gather(*tasks)
    parallel_time = time.time() - parallel_start
    
    print(f"Parallel processing time: {parallel_time:.2f}s")
    print(f"Speedup factor: {seq_time / parallel_time:.1f}x\n")
    
    # Compare results
    print("Results summary:")
    for symbol, analysis in parallel_results:
        if analysis:
            confidence_color = "🟢" if analysis['confidence'] > 0.8 else "🟡" if analysis['confidence'] > 0.6 else "🔴"
            print(f"{confidence_color} {symbol}: {analysis['signal']} ({analysis['confidence']:.1%})")

async def main():
    """Run all enhancement tests"""
    print("TESTING LIVE TRADING ENHANCEMENTS")
    print("=" * 60)
    
    await test_multi_timeframe()
    await test_dynamic_selection()
    await test_parallel_processing()
    
    print("\n✅ All enhancement tests complete!")

if __name__ == "__main__":
    asyncio.run(main())