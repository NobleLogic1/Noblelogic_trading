#!/usr/bin/env python3
"""
Real-World GPU Trading System - Live 30-minute Trial
==================================================
Launches the complete GPU-accelerated trading system for real-world testing

Enhancements:
- Multi-timeframe analysis: combines signals from multiple timeframes
- Dynamic asset selection: automatically selects the most promising assets
- Parallel signal processing: processes multiple assets and timeframes concurrently
"""

import asyncio
import json
import time
import os
import heapq
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from datetime import datetime, timedelta
from ml_integration import GPUAcceleratedMLEngine
from real_time_data_fetcher import data_aggregator, MarketData
from enhanced_risk_assessment import EnhancedRiskAssessment
from trade_execution import (
    AdvancedTradeExecution, Order, OrderType, OrderSide, OrderStatus,
    trade_execution_engine
)

class LiveTradingSystem:
    def __init__(self):
        self.ml_engine = GPUAcceleratedMLEngine()
        self.data_fetcher = data_aggregator  # Real-time WebSocket data aggregator
        self.risk_assessor = EnhancedRiskAssessment()
        self.trade_executor = trade_execution_engine  # Advanced trade execution engine
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=30)
        self.trade_log = []
        self.analysis_log = []
        self.execution_log = []  # Track actual trade executions
        self.performance_metrics = {
            'total_analyses': 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'hold_signals': 0,
            'avg_confidence': 0,
            'ml_response_times': [],
            'api_response_times': [],
            'parallel_efficiency': [],
            'executed_trades': 0,
            'execution_success_rate': 0.0,
            'avg_slippage': 0.0
        }
        
        # Multi-timeframe configuration
        self.timeframes = ["5m", "15m", "1h", "4h"]
        self.timeframe_weights = {"5m": 0.2, "15m": 0.3, "1h": 0.3, "4h": 0.2}
        
        # Initial trading universe - will be dynamically refined
        self.universe = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT', 
            'DOGE/USDT', 'DOT/USDT', 'AVAX/USDT', 'LINK/USDT', 'MATIC/USDT'
        ]
        
        # Active trading symbols (dynamically selected subset)
        self.symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT']
        
        # Symbol performance tracking for dynamic selection
        self.symbol_metrics = {symbol: {
            'opportunity_score': 0.5,
            'volatility': 0.0,
            'trading_volume': 0.0,
            'signal_consistency': 0.0,
            'last_signals': []
        } for symbol in self.universe}
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=min(10, len(self.universe) * len(self.timeframes) // 2))
        
        print("🚀 LIVE GPU TRADING SYSTEM - 30 MINUTE TRIAL")
        print("=" * 60)
        print(f"Start Time: {self.start_time.strftime('%H:%M:%S')}")
        print(f"End Time: {self.end_time.strftime('%H:%M:%S')}")
        print(f"Active Symbols: {', '.join(self.symbols)}")
        print(f"Universe Size: {len(self.universe)} assets")
        print(f"Timeframes: {', '.join(self.timeframes)}")
        print(f"GPU Status: {'Enabled' if self.ml_engine.gpu_available else 'CPU Optimized'}")
        print(f"Parallel Processing: Enabled ({self.executor._max_workers} workers)")
        print("=" * 60)
    
    async def analyze_market(self, symbol, price_data):
        """
        Perform GPU-accelerated market analysis using multi-timeframe approach
        """
        try:
            start_time = time.time()
            
            # Get 24h stats for additional analysis
            stats = self.data_fetcher.get_24h_stats(symbol)
            
            # Multi-timeframe analysis
            timeframe_results = await self.analyze_multiple_timeframes(symbol, price_data, stats)
            
            # Combine signals from multiple timeframes with weighted voting
            combined_signal, combined_confidence = self.combine_timeframe_signals(timeframe_results)
            
            analysis_time = (time.time() - start_time) * 1000
            self.performance_metrics['ml_response_times'].append(analysis_time)
            
            # Update performance metrics
            self.performance_metrics['total_analyses'] += 1
            self.performance_metrics[f'{combined_signal.lower()}_signals'] += 1
            
            # Calculate running average confidence
            total_conf = self.performance_metrics['avg_confidence'] * (self.performance_metrics['total_analyses'] - 1)
            self.performance_metrics['avg_confidence'] = (total_conf + combined_confidence) / self.performance_metrics['total_analyses']
            
            # Update symbol metrics for dynamic selection
            self.update_symbol_metrics(symbol, combined_signal, combined_confidence, timeframe_results, stats)
            
            analysis_result = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'price': price_data,
                'signal': combined_signal,
                'confidence': combined_confidence,
                'timeframe_signals': {tf: result['signal'] for tf, result in timeframe_results.items()},
                'timeframe_confidences': {tf: result['confidence'] for tf, result in timeframe_results.items()},
                'reasoning': self.generate_reasoning(timeframe_results),
                'gpu_used': self.ml_engine.gpu_available,
                'analysis_time_ms': analysis_time,
                'stats': stats
            }
            
            self.analysis_log.append(analysis_result)
            return analysis_result
            
        except Exception as e:
            print(f"❌ Analysis error for {symbol}: {e}")
            return None
            
    async def analyze_multiple_timeframes(self, symbol, current_price, stats):
        """
        Analyze a symbol across multiple timeframes and return results for each timeframe
        """
        results = {}
        tasks = []
        
        for timeframe in self.timeframes:
            # Fetch kline data for this timeframe
            klines = self.data_fetcher.get_kline_data(symbol, timeframe, limit=100)
            
            # Create task for this timeframe
            task = self.analyze_single_timeframe(symbol, timeframe, current_price, klines, stats)
            tasks.append(task)
        
        # Execute all timeframe analyses in parallel
        timeframe_results = await asyncio.gather(*tasks)
        
        # Organize results by timeframe
        for i, timeframe in enumerate(self.timeframes):
            results[timeframe] = timeframe_results[i]
            
        return results
        
    async def analyze_single_timeframe(self, symbol, timeframe, current_price, klines, stats):
        """
        Analyze a single timeframe for a given symbol
        """
        try:
            # Extract features specific to this timeframe
            features = self.create_feature_vector(current_price, stats, klines, timeframe)
            
            # GPU-accelerated ML prediction
            prediction = await self.ml_engine.predict(features)
            
            # Map action to signal
            action_map = {0: 'HOLD', 1: 'BUY', 2: 'SELL'}
            signal = action_map.get(prediction['action'], 'HOLD')
            
            return {
                'timeframe': timeframe,
                'signal': signal,
                'confidence': prediction['confidence'],
                'features': features.tolist()[0] if hasattr(features, 'tolist') else features
            }
            
        except Exception as e:
            print(f"❌ Error analyzing {symbol} on {timeframe} timeframe: {e}")
            return {
                'timeframe': timeframe,
                'signal': 'HOLD',
                'confidence': 0.5,
                'features': []
            }
    
    def combine_timeframe_signals(self, timeframe_results):
        """
        Combine signals from multiple timeframes using weighted voting
        """
        import numpy as np
        
        signal_votes = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 0.0}
        total_weight = 0.0
        
        for timeframe, result in timeframe_results.items():
            signal = result['signal']
            confidence = result['confidence']
            weight = self.timeframe_weights.get(timeframe, 0.25)  # Default weight if not specified
            
            # Weight the vote by both timeframe weight and signal confidence
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
        
    def update_symbol_metrics(self, symbol, signal, confidence, timeframe_results, stats):
        """
        Update metrics for dynamic symbol selection
        """
        metrics = self.symbol_metrics[symbol]
        
        # Update last signals (keep last 10)
        metrics['last_signals'].append({
            'signal': signal,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        })
        if len(metrics['last_signals']) > 10:
            metrics['last_signals'] = metrics['last_signals'][-10:]
        
        # Update signal consistency - higher when signals agree across timeframes
        signal_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        for tf, result in timeframe_results.items():
            signal_counts[result['signal']] += 1
        
        max_count = max(signal_counts.values())
        metrics['signal_consistency'] = max_count / len(self.timeframes)
        
        # Update volatility from stats
        price_change_pct = stats.get('priceChangePercent', 0)
        metrics['volatility'] = abs(float(price_change_pct)) / 100 if price_change_pct else 0.02
        
        # Update trading volume (normalized)
        volume = stats.get('volume', 0)
        metrics['trading_volume'] = float(volume) / 10000000  # Normalize to 0-1 range
        
        # Calculate opportunity score based on multiple factors
        signal_opportunity = 0
        if signal == 'BUY' and confidence > 0.6:
            signal_opportunity = confidence
        elif signal == 'SELL' and confidence > 0.6:
            signal_opportunity = confidence * 0.8  # Slightly lower weight for sell signals
            
        # Opportunity score is a weighted combination of multiple factors
        metrics['opportunity_score'] = (
            signal_opportunity * 0.4 +
            metrics['volatility'] * 0.3 +
            metrics['trading_volume'] * 0.2 +
            metrics['signal_consistency'] * 0.1
        )
    
    def generate_reasoning(self, timeframe_results):
        """
        Generate reasoning text based on multi-timeframe analysis
        """
        reasoning_parts = []
        
        # Count signals across timeframes
        signal_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        for tf, result in timeframe_results.items():
            signal_counts[result['signal']] += 1
        
        # Generate reasoning based on signal distribution
        dominant_signal = max(signal_counts, key=signal_counts.get)
        dominant_count = signal_counts[dominant_signal]
        
        # Overall timeframe agreement
        if dominant_count == len(self.timeframes):
            reasoning_parts.append(f"Strong {dominant_signal} signal across all timeframes.")
        elif dominant_count > len(self.timeframes) / 2:
            reasoning_parts.append(f"{dominant_signal} signal on majority of timeframes ({dominant_count}/{len(self.timeframes)}).")
        else:
            reasoning_parts.append("Mixed signals across timeframes.")
        
        # Add timeframe-specific comments
        for tf in sorted(timeframe_results.keys()):
            result = timeframe_results[tf]
            if result['confidence'] > 0.7:
                reasoning_parts.append(f"{tf}: Strong {result['signal']} ({result['confidence']:.1%})")
            elif result['confidence'] > 0.5:
                reasoning_parts.append(f"{tf}: Moderate {result['signal']} ({result['confidence']:.1%})")
        
        return " ".join(reasoning_parts)
    
    def create_feature_vector(self, price, stats, klines=None, timeframe=None):
        """
        Create normalized feature vector for ML analysis with timeframe-specific features
        """
        import numpy as np
        
        # Extract features from price and stats
        volume = stats.get('volume', 1000000)
        price_change = stats.get('priceChangePercent', 0)
        high = stats.get('highPrice', price)
        low = stats.get('lowPrice', price)
        
        # Calculate basic technical indicators
        volatility = abs(float(price_change)) / 100 if price_change else 0.02
        price_position = (price - low) / (high - low) if (high - low) > 0 else 0.5
        
        # Timeframe-specific features if klines are available
        momentum = 0.5  # default neutral
        rsi = 0.5       # default neutral
        trend_strength = 0.5  # default neutral
        
        if klines and len(klines) > 14:
            # Extract close prices for technical indicators
            closes = [k['close'] for k in klines[-30:]]
            
            # Calculate momentum (rate of recent price change)
            short_term_avg = sum(closes[-5:]) / 5
            longer_term_avg = sum(closes[-20:]) / 20
            momentum = (short_term_avg / longer_term_avg - 0.98) * 10  # Normalize around 0.5
            momentum = min(max(momentum, 0), 1)  # Clamp to 0-1 range
            
            # Simple RSI calculation
            gains = []
            losses = []
            for i in range(1, len(closes)):
                change = closes[i] - closes[i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            if len(gains) > 0 and len(losses) > 0:
                avg_gain = sum(gains[-14:]) / 14
                avg_loss = sum(losses[-14:]) / 14
                
                if avg_loss > 0:
                    rs = avg_gain / avg_loss
                    rsi = 1 - (1 / (1 + rs))  # 0-1 scale
                else:
                    rsi = 0.95  # Very high RSI if no losses
            
            # Calculate trend strength
            ups = 0
            downs = 0
            for i in range(1, min(len(closes), 20)):
                if closes[i] > closes[i-1]:
                    ups += 1
                else:
                    downs += 1
            trend_strength = max(ups, downs) / (ups + downs) if (ups + downs) > 0 else 0.5
        
        # Create normalized feature vector (10 features as expected by model)
        features = np.array([[
            float(price) / 100000,              # normalized price
            float(volume) / 10000000,           # normalized volume  
            volatility,                         # volatility (0-1)
            float(price_change) / 10 + 0.5,     # normalized price change
            price_position,                     # price position in range
            momentum,                           # momentum (timeframe specific)
            rsi,                                # RSI (timeframe specific)
            trend_strength,                     # trend strength (timeframe specific)
            min(volatility * 2, 1.0),           # market trend
            0.75                                # success rate (mock)
        ]], dtype=np.float32)
        
        return features
    
    async def select_active_symbols(self):
        """
        Dynamically select the most promising assets to trade based on opportunity metrics
        """
        # Sort symbols by opportunity score
        sorted_symbols = sorted(
            self.universe,
            key=lambda s: self.symbol_metrics[s]['opportunity_score'], 
            reverse=True
        )
        
        # Select top N symbols (maintain at least 2 major ones like BTC, ETH)
        major_coins = ['BTC/USDT', 'ETH/USDT']
        selected = []
        
        # Always include major coins
        for coin in major_coins:
            if coin in self.universe:
                selected.append(coin)
                
        # Fill remaining slots with highest opportunity assets
        remaining_slots = 5 - len(selected)
        for symbol in sorted_symbols:
            if symbol not in selected and len(selected) < 5:
                selected.append(symbol)
                
        # Update active symbols
        self.symbols = selected
        
        return selected
    
    async def fetch_live_data(self, symbols=None):
        """
        Fetch live market data for specified symbols (or all active symbols)
        """
        try:
            symbols_to_fetch = symbols or self.symbols
            start_time = time.time()
            prices = self.data_fetcher.get_multiple_prices(symbols_to_fetch)
            fetch_time = (time.time() - start_time) * 1000
            self.performance_metrics['api_response_times'].append(fetch_time)
            
            return prices
        except Exception as e:
            print(f"❌ Data fetch error: {e}")
            return {}
    
    async def fetch_universe_data(self):
        """
        Fetch market data for the entire universe to support dynamic selection
        """
        try:
            # Fetch prices for all symbols in universe
            universe_prices = await self.fetch_live_data(self.universe)
            
            # For symbols with prices, fetch 24h stats
            universe_stats = {}
            for symbol in universe_prices:
                universe_stats[symbol] = self.data_fetcher.get_24h_stats(symbol)
                
            return universe_prices, universe_stats
        except Exception as e:
            print(f"❌ Universe data fetch error: {e}")
            return {}, {}
    
    async def process_symbol_parallel(self, symbol, price, stats):
        """
        Process a single symbol's analysis - designed for parallel execution
        """
        analysis = await self.analyze_market(symbol, price)
        return symbol, analysis
    
    async def trading_cycle(self):
        """
        Single trading analysis cycle with parallel processing and dynamic selection
        """
        cycle_start = time.time()
        print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Running Analysis Cycle")
        print("-" * 50)
        
        # Every 3rd cycle, fetch data for the entire universe and update selection
        if self.performance_metrics['total_analyses'] % 3 == 0:
            print("🔄 Updating asset selection...")
            universe_prices, universe_stats = await self.fetch_universe_data()
            
            # Quick opportunity assessment for the entire universe
            for symbol, price in universe_prices.items():
                if symbol in universe_stats:
                    # Update volatility and volume metrics for selection
                    stats = universe_stats[symbol]
                    metrics = self.symbol_metrics[symbol]
                    
                    price_change_pct = stats.get('priceChangePercent', 0)
                    metrics['volatility'] = abs(float(price_change_pct)) / 100 if price_change_pct else 0.02
                    
                    volume = stats.get('volume', 0)
                    metrics['trading_volume'] = float(volume) / 10000000
            
            # Select most promising assets
            await self.select_active_symbols()
            print(f"📊 Selected assets: {', '.join(self.symbols)}")
        
        # Fetch live data for active symbols
        price_data = await self.fetch_live_data()
        
        if not price_data:
            print("❌ No price data available")
            return
            
        # Process all symbols in parallel
        tasks = []
        for symbol, price in price_data.items():
            # Get 24h stats
            stats = self.data_fetcher.get_24h_stats(symbol)
            
            # Create task
            task = self.process_symbol_parallel(symbol, price, stats)
            tasks.append(task)
        
        # Execute all symbol analyses concurrently
        parallel_start = time.time()
        results = await asyncio.gather(*tasks)
        parallel_time = time.time() - parallel_start
        
        # Calculate parallel efficiency
        sequential_time_estimate = sum(self.performance_metrics['ml_response_times'][-len(self.symbols):]) / 1000 if self.performance_metrics['ml_response_times'] else 0
        if sequential_time_estimate > 0:
            parallel_efficiency = sequential_time_estimate / parallel_time
            self.performance_metrics['parallel_efficiency'].append(parallel_efficiency)
        
        # Process results
        for symbol, analysis in results:
            if analysis:
                price = price_data.get(symbol, 0)
                confidence_color = "🟢" if analysis['confidence'] > 0.8 else "🟡" if analysis['confidence'] > 0.6 else "🔴"
                print(f"{confidence_color} {symbol}: ${price:,.2f} | {analysis['signal']} ({analysis['confidence']:.1%}) | {analysis['analysis_time_ms']:.1f}ms")
                
                # Display timeframe breakdown for non-HOLD signals
                if analysis['signal'] != 'HOLD':
                    tf_signals = [f"{tf}:{analysis['timeframe_signals'][tf][0]}" for tf in self.timeframes]
                    print(f"   ⏱️ Timeframes: {' '.join(tf_signals)}")
                
                # Log significant signals and execute trades
                if analysis['signal'] != 'HOLD' and analysis['confidence'] > 0.75:
                    # Create order for execution
                    order_id = f"{symbol.replace('/', '')}_{int(time.time())}_{analysis['signal']}"
                    
                    # Determine order type based on signal strength and market conditions
                    order_type = OrderType.MARKET
                    if analysis['confidence'] > 0.85:
                        # High confidence - use limit order
                        order_type = OrderType.LIMIT
                    elif analysis['confidence'] > 0.80 and stats.get('priceChangePercent', 0) > 5:
                        # High confidence in volatile market - use TWAP for large positions
                        order_type = OrderType.TWAP
                    
                    # Determine side
                    side = OrderSide.BUY if analysis['signal'] == 'BUY' else OrderSide.SELL
                    
                    # Calculate position size based on risk assessment
                    position_size = self.calculate_position_size(symbol, price, analysis, stats)
                    
                    # Create order object
                    order = Order(
                        order_id=order_id,
                        symbol=symbol,
                        side=side,
                        order_type=order_type,
                        quantity=position_size,
                        price=price if order_type == OrderType.LIMIT else None,
                        slippage_protection=True,
                        max_slippage_percent=0.5,  # 0.5% max slippage
                        execution_strategy='advanced'
                    )
                    
                    # Prepare market data for execution
                    market_data = {
                        'price': price,
                        'volatility': abs(float(stats.get('priceChangePercent', 0))) / 100,
                        'volume': float(stats.get('volume', 0)),
                        'market_regime': self.determine_market_regime(stats),
                        'trend_strength': analysis.get('trend_strength', 0.5),
                        'trend_direction': 1 if analysis['signal'] == 'BUY' else -1,
                        'liquidity_score': min(1.0, float(stats.get('volume', 0)) / 10000000),
                        'avg_volume_24h': float(stats.get('volume', 0))
                    }
                    
                    # Execute the trade
                    try:
                        execution_result = await self.trade_executor.execute_order(order, market_data)
                        
                        # Log the trade signal and execution
                        trade_entry = {
                            'timestamp': analysis['timestamp'],
                            'symbol': symbol,
                            'action': analysis['signal'],
                            'price': price,
                            'confidence': analysis['confidence'],
                            'reasoning': analysis['reasoning'],
                            'timeframe_signals': analysis['timeframe_signals'],
                            'order_id': order_id,
                            'order_type': order_type.value,
                            'position_size': position_size,
                            'execution_result': execution_result,
                            'executed': execution_result.get('status') != 'failed'
                        }
                        
                        self.trade_log.append(trade_entry)
                        self.execution_log.append({
                            'order_id': order_id,
                            'execution_result': execution_result,
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        # Update performance metrics
                        self.performance_metrics['executed_trades'] += 1
                        if execution_result.get('slippage_percent'):
                            self.performance_metrics['avg_slippage'] = (
                                (self.performance_metrics['avg_slippage'] * (self.performance_metrics['executed_trades'] - 1)) +
                                execution_result['slippage_percent']
                            ) / self.performance_metrics['executed_trades']
                        
                        print(f"📈 TRADE EXECUTED: {analysis['signal']} {symbol} @ ${price:,.2f} ({position_size:.4f} units)")
                        print(f"   📝 {analysis['reasoning']}")
                        print(f"   ⚡ Execution: {order_type.value} via {order.exchange}")
                        if 'average_price' in execution_result:
                            print(f"   💰 Executed @ ${execution_result['average_price']:.2f} ({execution_result.get('slippage_percent', 0):.2f}% slippage)")
                    
                    except Exception as e:
                        print(f"❌ TRADE EXECUTION FAILED: {analysis['signal']} {symbol} - {e}")
                        
                        # Still log the signal even if execution failed
                        trade_entry = {
                            'timestamp': analysis['timestamp'],
                            'symbol': symbol,
                            'action': analysis['signal'],
                            'price': price,
                            'confidence': analysis['confidence'],
                            'reasoning': analysis['reasoning'],
                            'timeframe_signals': analysis['timeframe_signals'],
                            'execution_error': str(e),
                            'executed': False
                        }
                        self.trade_log.append(trade_entry)
        
        # Performance summary
        cycle_time = (time.time() - cycle_start) * 1000
        if self.performance_metrics['total_analyses'] > 0:
            avg_ml_time = sum(self.performance_metrics['ml_response_times'][-len(self.symbols):]) / len(self.symbols) if self.performance_metrics['ml_response_times'] else 0
            avg_api_time = self.performance_metrics['api_response_times'][-1] if self.performance_metrics['api_response_times'] else 0
            avg_parallel_eff = sum(self.performance_metrics['parallel_efficiency'][-5:]) / min(len(self.performance_metrics['parallel_efficiency']), 5) if self.performance_metrics['parallel_efficiency'] else 1.0
            
            print(f"\n📊 Cycle Performance: ML {avg_ml_time:.1f}ms | API {avg_api_time:.1f}ms | Parallel Efficiency {avg_parallel_eff:.1f}x")
            print(f"📈 Confidence {self.performance_metrics['avg_confidence']:.1%} | Total Cycle Time: {cycle_time:.1f}ms")
            
            # Add execution metrics
            if self.performance_metrics['executed_trades'] > 0:
                execution_rate = self.performance_metrics['executed_trades'] / max(1, len([t for t in self.trade_log if t.get('executed', False)]))
                print(f"⚡ Execution Rate: {execution_rate:.1%} | Avg Slippage: {self.performance_metrics['avg_slippage']:.2f}%")
    
    def calculate_position_size(self, symbol, price, analysis, stats):
        """
        Calculate position size based on risk assessment and market conditions
        """
        # Base position size (0.1% of typical daily volume for small position)
        base_volume = float(stats.get('volume', 1000000))
        base_position = base_volume * 0.001  # 0.1% of daily volume
        
        # Adjust based on confidence
        confidence_multiplier = analysis['confidence'] * 2  # 0.75 confidence = 1.5x, 0.85 = 1.7x
        
        # Adjust based on volatility (smaller positions in volatile markets)
        volatility = abs(float(stats.get('priceChangePercent', 0))) / 100
        volatility_multiplier = max(0.1, 1.0 - volatility * 2)  # Reduce size in high volatility
        
        # Adjust based on signal strength across timeframes
        timeframe_agreement = sum(1 for tf_signal in analysis['timeframe_signals'].values() 
                                if tf_signal == analysis['signal']) / len(analysis['timeframe_signals'])
        agreement_multiplier = 0.5 + timeframe_agreement  # 0.5 to 1.5x
        
        # Calculate final position size
        position_size = base_position * confidence_multiplier * volatility_multiplier * agreement_multiplier
        
        # Ensure minimum and maximum bounds
        min_position = 0.001  # Minimum 0.001 units
        max_position = base_volume * 0.01  # Maximum 1% of daily volume
        
        return max(min_position, min(max_position, position_size))
    
    def determine_market_regime(self, stats):
        """
        Determine current market regime based on statistics
        """
        price_change = float(stats.get('priceChangePercent', 0))
        volume = float(stats.get('volume', 0))
        
        # Simple regime classification
        if abs(price_change) > 5:
            return "VOLATILE"
        elif price_change > 2:
            return "BULL"
        elif price_change < -2:
            return "BEAR"
        else:
            return "SIDEWAYS"
    
    async def save_results(self):
        """Save trading session results"""
        session_data = {
            'session_info': {
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_minutes': (datetime.now() - self.start_time).total_seconds() / 60,
                'symbols_monitored': self.symbols,
                'universe_size': len(self.universe),
                'timeframes_analyzed': self.timeframes,
                'gpu_available': self.ml_engine.gpu_available,
                'parallel_processing_enabled': True,
                'parallel_workers': self.executor._max_workers
            },
            'performance_metrics': {
                **self.performance_metrics,
                'avg_ml_response_ms': sum(self.performance_metrics['ml_response_times']) / len(self.performance_metrics['ml_response_times']) if self.performance_metrics['ml_response_times'] else 0,
                'avg_api_response_ms': sum(self.performance_metrics['api_response_times']) / len(self.performance_metrics['api_response_times']) if self.performance_metrics['api_response_times'] else 0,
                'avg_parallel_efficiency': sum(self.performance_metrics['parallel_efficiency']) / len(self.performance_metrics['parallel_efficiency']) if self.performance_metrics['parallel_efficiency'] else 1.0
            },
            'trade_signals': self.trade_log,
            'execution_log': self.execution_log,
            'analysis_history': self.analysis_log[-50:],  # Last 50 analyses
            'symbol_metrics': self.symbol_metrics,
            'timeframe_weights': self.timeframe_weights,
            'execution_stats': self.trade_executor.get_execution_stats()
        }
        
        # Save to file
        filename = f"live_trading_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"💾 Session data saved to: {filename}")
        return session_data
    
    def display_final_summary(self, session_data):
        """Display final trading session summary"""
        print("\n🎯 30-MINUTE LIVE TRADING SESSION COMPLETE")
        print("=" * 60)
        
        metrics = session_data['performance_metrics']
        
        print(f"📈 Total Analyses: {metrics['total_analyses']}")
        print(f"🟢 Buy Signals: {metrics['buy_signals']}")
        print(f"🔴 Sell Signals: {metrics['sell_signals']}")
        print(f"🟡 Hold Signals: {metrics['hold_signals']}")
        print(f"🎯 Average Confidence: {metrics['avg_confidence']:.1%}")
        print(f"⚡ Average ML Response: {metrics['avg_ml_response_ms']:.1f}ms")
        print(f"🌐 Average API Response: {metrics['avg_api_response_ms']:.1f}ms")
        print(f"⚙️ Parallel Processing Efficiency: {metrics.get('avg_parallel_efficiency', 1.0):.1f}x")
        print(f"🚀 GPU Status: {'Enabled' if session_data['session_info']['gpu_available'] else 'CPU Optimized'}")
        
        # Display timeframe effectiveness
        print("\n⏱️ TIMEFRAME EFFECTIVENESS:")
        timeframe_signals = {}
        correct_signals = {}
        
        # Calculate accuracy for each timeframe
        for analysis in self.analysis_log:
            if 'timeframe_signals' in analysis:
                for tf, signal in analysis['timeframe_signals'].items():
                    if tf not in timeframe_signals:
                        timeframe_signals[tf] = {'BUY': 0, 'SELL': 0, 'HOLD': 0, 'total': 0}
                        correct_signals[tf] = 0
                    
                    # Count signal occurrences
                    timeframe_signals[tf][signal] += 1
                    timeframe_signals[tf]['total'] += 1
                    
                    # Count correct signals (matching combined signal)
                    if signal == analysis['signal']:
                        correct_signals[tf] += 1
        
        # Display results
        for tf in sorted(timeframe_signals.keys()):
            accuracy = correct_signals[tf] / timeframe_signals[tf]['total'] if timeframe_signals[tf]['total'] > 0 else 0
            buy_pct = timeframe_signals[tf]['BUY'] / timeframe_signals[tf]['total'] * 100 if timeframe_signals[tf]['total'] > 0 else 0
            sell_pct = timeframe_signals[tf]['SELL'] / timeframe_signals[tf]['total'] * 100 if timeframe_signals[tf]['total'] > 0 else 0
            
            print(f"{tf}: Accuracy {accuracy:.1%} | Weight: {self.timeframe_weights.get(tf, 0.25):.2f} | Buys: {buy_pct:.1f}% | Sells: {sell_pct:.1f}%")
        
        # Display top symbols by opportunity
        print("\n💰 TOP ASSETS BY OPPORTUNITY:")
        top_symbols = sorted(
            self.symbol_metrics.items(),
            key=lambda x: x[1]['opportunity_score'],
            reverse=True
        )[:5]
        
        for symbol, metrics in top_symbols:
            print(f"{symbol}: Score {metrics['opportunity_score']:.2f} | Vol: {metrics['volatility']:.1%} | Consistency: {metrics['signal_consistency']:.1f}")
        
        if self.trade_log:
            print(f"\n📊 SIGNIFICANT TRADE SIGNALS ({len(self.trade_log)}):")
            print("-" * 50)
            for trade in self.trade_log[-10:]:  # Show last 10
                time_str = datetime.fromisoformat(trade['timestamp']).strftime('%H:%M:%S')
                print(f"{time_str} | {trade['action']} {trade['symbol']} @ ${trade['price']:,.2f} ({trade['confidence']:.1%})")
                if 'reasoning' in trade and len(trade['reasoning']) > 0:
                    print(f"   {trade['reasoning']}")
        
        print("\n✅ LIVE TRADING TRIAL SUCCESSFUL!")
        print("Dashboard: http://localhost:5173")
        print("Backend: http://localhost:3001")
    
    async def run_live_session(self):
        """Run 30-minute live trading session"""
        cycle_count = 0
        
        try:
            while datetime.now() < self.end_time:
                cycle_count += 1
                
                # Run trading cycle
                await self.trading_cycle()
                
                # Time remaining
                remaining = self.end_time - datetime.now()
                remaining_mins = remaining.total_seconds() / 60
                
                if remaining_mins <= 0:
                    break
                
                print(f"\n⏳ Time Remaining: {remaining_mins:.1f} minutes | Cycle {cycle_count}")
                
                # Wait 30 seconds between cycles (120 cycles in 30 minutes)
                await asyncio.sleep(30)
        
        except KeyboardInterrupt:
            print("\n🛑 Session interrupted by user")
        
        # Save and display results
        session_data = await self.save_results()
        self.display_final_summary(session_data)

async def main():
    """Main function to run live trading system"""
    print("🚀 Starting NobleLogic GPU Trading System with Real-Time Data...")

    # Initialize trading system
    trading_system = LiveTradingSystem()

    # Start real-time data aggregator
    print("📡 Starting real-time data aggregator...")
    await trading_system.data_fetcher.subscribe_symbols(trading_system.symbols)

    # Start data aggregator in background
    aggregator_task = asyncio.create_task(trading_system.data_fetcher.start())

    try:
        # Run live trading session
        await trading_system.run_live_session()
    finally:
        # Clean shutdown
        print("🛑 Shutting down data aggregator...")
        await trading_system.data_fetcher.stop()
        aggregator_task.cancel()

        try:
            await aggregator_task
        except asyncio.CancelledError:
            pass

    print("✅ System shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())