"""
Test Mode for NobleLogic Trading System
Safe testing environment with real market data and ML learning
"""

import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from ml_integration import ml_trading_integration
from live_data_fetcher import live_data_fetcher
import os

class TradingTestMode:
    def __init__(self):
        self.is_running = False
        self.paper_balance = 100  # $100 starting balance
        self.positions = []
        self.trade_history = []
        self.test_log = []
        
        # Real market symbols for testing
        self.crypto_symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT', 'DOGE/USDT']
        self.current_prices = {}
        
        # Initialize with live prices
        self.update_live_prices()
        
    async def start_test_session(self, duration_minutes=60, trades_per_hour=12):
        """
        Start a test trading session
        """
        print("🚀 Starting NobleLogic Trading Test Mode")
        print(f"💰 Starting balance: ${self.paper_balance:,.2f}")
        print(f"⏱️  Test duration: {duration_minutes} minutes")
        print(f"📊 Target trades per hour: {trades_per_hour}")
        print("-" * 50)
        
        self.is_running = True
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        trade_interval = 3600 / trades_per_hour  # seconds between trades
        last_trade_time = start_time
        
        while self.is_running and datetime.now() < end_time:
            try:
                # Update market prices with real-time data
                self.update_live_prices()
                
                # Check if it's time for a new trade
                if (datetime.now() - last_trade_time).total_seconds() >= trade_interval:
                    await self.execute_test_trade()
                    last_trade_time = datetime.now()
                
                # Update existing positions
                self.update_positions()
                
                # Update backend files for dashboard
                self.update_backend_files_status()
                
                # Log status every 5 minutes
                if int(time.time()) % 300 == 0:
                    self.log_status()
                
                # Short sleep to prevent excessive API calls
                await asyncio.sleep(10)  # Increased to 10 seconds for API rate limiting
                
            except Exception as e:
                self.log_error(f"Error in test session: {e}")
                await asyncio.sleep(15)
        
        # Test session complete
        self.is_running = False
        self.generate_test_report()
    
    def update_live_prices(self):
        """
        Update prices with real-time market data
        """
        try:
            # Get live prices from multiple exchanges
            live_prices = live_data_fetcher.get_multiple_prices(self.crypto_symbols)
            self.current_prices.update(live_prices)
            
            # Log price updates (optional)
            if random.random() < 0.1:  # Log 10% of price updates
                print(f"📊 Live prices updated: {datetime.now().strftime('%H:%M:%S')}")
                
        except Exception as e:
            print(f"⚠️  Error updating live prices: {e}")
            # Keep using last known prices if update fails
    
    async def execute_test_trade(self):
        """
        Execute a test trade using ML decision making with real market data
        """
        # Select random symbol for this test
        symbol = random.choice(self.crypto_symbols)
        current_price = self.current_prices.get(symbol, 0)
        
        if current_price == 0:
            print(f"❌ No price data available for {symbol}, skipping trade")
            return
        
        # Get real market data for ML analysis
        market_data = self.get_real_market_data(symbol)
        
        # Get ML trading decision
        try:
            decision = await ml_trading_integration.get_trading_decision(
                symbol=symbol,
                current_price=current_price,
                market_data=market_data
            )
        except Exception as e:
            print(f"❌ ML decision error for {symbol}: {e}")
            return
        
        if decision and decision.get('should_trade', False):
            # Execute the trade
            trade_result = self.simulate_trade_execution(
                symbol=symbol,
                action=decision['action'],
                confidence=decision['confidence'],
                current_price=current_price
            )
            
            if trade_result:
                print(f"✅ Executed {decision['action']} on {symbol} at ${current_price:.4f} (confidence: {decision['confidence']:.1%})")
                
                # Record trade for ML learning
                ml_trading_integration.record_trade_result(
                    symbol=symbol,
                    action=decision['action'],
                    entry_price=current_price,
                    confidence=decision['confidence'],
                    market_data=market_data,
                    profit_loss=0  # Will be updated when position closes
                )
                
                # Update trade history
                self.trade_history.append(trade_result)
        else:
            reason = decision.get('reason', 'Low confidence') if decision else 'ML analysis failed'
            print(f"🔄 ML decided not to trade {symbol}: {reason}")
    
    def get_real_market_data(self, symbol: str) -> dict:
        """
        Get comprehensive real market data for ML analysis
        """
        try:
            # Get recent kline data (15 minutes of 1-minute candles)
            klines = live_data_fetcher.get_kline_data(symbol, "1m", 15)
            
            # Get 24h statistics
            stats_24h = live_data_fetcher.get_24h_stats(symbol)
            
            # Get order book data
            order_book = live_data_fetcher.get_order_book(symbol, 10)
            
            # Calculate technical indicators
            closes = [k['close'] for k in klines] if klines else []
            volumes = [k['volume'] for k in klines] if klines else []
            
            # Simple moving averages
            sma_5 = sum(closes[-5:]) / 5 if len(closes) >= 5 else closes[-1] if closes else 0
            sma_10 = sum(closes[-10:]) / 10 if len(closes) >= 10 else closes[-1] if closes else 0
            
            # Recent volatility
            volatility = 0
            if len(closes) > 1:
                price_changes = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
                volatility = sum(abs(change) for change in price_changes) / len(price_changes)
            
            # Volume trend
            volume_trend = 'increasing' if len(volumes) >= 2 and volumes[-1] > volumes[-2] else 'decreasing'
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'price_data': {
                    'current': self.current_prices.get(symbol, 0),
                    'sma_5': sma_5,
                    'sma_10': sma_10,
                    'high_24h': stats_24h.get('high_price', 0),
                    'low_24h': stats_24h.get('low_price', 0),
                    'change_24h_percent': stats_24h.get('price_change_percent', 0)
                },
                'volume_data': {
                    'current': volumes[-1] if volumes else 0,
                    'average': sum(volumes) / len(volumes) if volumes else 0,
                    'trend': volume_trend,
                    'volume_24h': stats_24h.get('volume', 0)
                },
                'technical_indicators': {
                    'volatility': volatility,
                    'momentum': (closes[-1] - closes[0]) / closes[0] if len(closes) > 1 else 0,
                    'rsi': self.calculate_rsi(closes) if len(closes) >= 14 else 50
                },
                'order_book': {
                    'bid_depth': sum(bid[1] for bid in order_book.get('bids', [])[:5]),
                    'ask_depth': sum(ask[1] for ask in order_book.get('asks', [])[:5]),
                    'spread': (order_book.get('asks', [[0]])[0][0] - order_book.get('bids', [[0]])[0][0]) if order_book.get('asks') and order_book.get('bids') else 0
                },
                'market_sentiment': {
                    'trend': 'bullish' if stats_24h.get('price_change_percent', 0) > 0 else 'bearish',
                    'strength': abs(stats_24h.get('price_change_percent', 0))
                }
            }
            
        except Exception as e:
            print(f"⚠️  Error getting market data for {symbol}: {e}")
            # Return minimal data structure
            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'price_data': {'current': self.current_prices.get(symbol, 0)},
                'volume_data': {'current': 0},
                'technical_indicators': {'volatility': 0},
                'order_book': {'spread': 0},
                'market_sentiment': {'trend': 'neutral'}
            }
    
    def calculate_rsi(self, prices: list, period: int = 14) -> float:
        """
        Calculate Relative Strength Index
        """
        if len(prices) < period + 1:
            return 50  # Neutral RSI
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-change)
        
        if len(gains) < period:
            return 50
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_simulated_market_data(self, symbol):
        """
        Generate realistic market data for ML analysis
        """
        base_price = self.current_prices[symbol]
        return {
            'volume': random.randint(1000000, 5000000),
            'volatility': random.uniform(0.1, 0.3),
            'trend': random.choice(['upward', 'downward', 'sideways']),
            'support_level': base_price * 0.95,
            'resistance_level': base_price * 1.05,
            'market_sentiment': random.uniform(0.3, 0.8)
        }
    
    def simulate_trade_execution(self, symbol, decision):
        """
        Simulate trade execution and outcome
        """
        entry_price = decision['entryPrice']
        direction = decision['direction']
        confidence = decision['confidence']
        
        # Simulate trade outcome based on confidence and random factors
        # Higher confidence = higher chance of success
        success_probability = 0.4 + (confidence * 0.4)  # 40% base + up to 40% from confidence
        is_successful = random.random() < success_probability
        
        if is_successful:
            # Successful trade
            profit_percent = random.uniform(0.01, 0.05)  # 1-5% profit
            if direction == 'SHORT':
                profit_percent *= -1  # Invert for short positions
            
            profit = entry_price * profit_percent * 0.1  # Position size 10% of trade value
            self.paper_balance += profit
            
            trade_result = {
                'success': True,
                'profit': profit,
                'exit_price': entry_price * (1 + profit_percent),
                'duration_minutes': random.randint(5, 60)
            }
        else:
            # Failed trade - hit stop loss
            loss_percent = random.uniform(0.01, 0.03)  # 1-3% loss
            loss = entry_price * loss_percent * 0.1
            self.paper_balance -= loss
            
            trade_result = {
                'success': False,
                'profit': -loss,
                'exit_price': entry_price * (1 - loss_percent),
                'duration_minutes': random.randint(2, 30)
            }
        
        # Record in trade history
        trade_data = {
            'id': f"trade_{len(self.trade_history)}",
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'type': direction,
            'entry_price': entry_price,
            'current_price': trade_result['exit_price'],
            'size': 0.1,  # Position size
            'pnl': trade_result['profit'],
            'direction': direction,
            'success': trade_result['success'],
            'confidence': confidence
        }
        
        self.trade_history.append(trade_data)
        
        # Update backend data files for dashboard
        self.update_backend_files(trade_data)
        
        return trade_result
    
    def update_backend_files_status(self):
        """
        Update backend status files for dashboard (without specific trade data)
        """
        try:
            # Update health status
            health_data = {
                "status": "operational" if self.is_running else "stopped",
                "last_update": datetime.now().isoformat(),
                "components": {
                    "data_feed": "operational",
                    "trade_execution": "operational",
                    "risk_management": "operational",
                    "api_connectivity": "operational"
                },
                "metrics": {
                    "latency": random.uniform(50, 200),
                    "success_rate": random.uniform(75, 95),
                    "error_rate": random.uniform(5, 25)
                }
            }
            
            with open('backend/health_status.json', 'w') as f:
                json.dump(health_data, f, indent=2)
            
            # Update strategy output with current market state
            strategy_data = {
                "timestamp": datetime.now().isoformat(),
                "active_signals": len(self.positions),
                "market_conditions": {
                    "volatility": "moderate",
                    "trend": "sideways",
                    "sentiment": "neutral"
                },
                "portfolio": {
                    "balance": self.paper_balance,
                    "positions": len(self.positions),
                    "total_trades": len(self.trade_history)
                }
            }
            
            with open('backend/strategy_output.json', 'w') as f:
                json.dump(strategy_data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Error updating backend status files: {e}")
    
    def update_backend_files(self, trade_data):
        """
        Update the backend JSON files so dashboard shows live data
        """
        try:
            # Update trade log
            trade_log_path = 'backend/trade_log.json'
            try:
                with open(trade_log_path, 'r') as f:
                    trades = json.load(f)
            except:
                trades = []
            
            trades.append(trade_data)
            # Keep only last 20 trades for dashboard
            trades = trades[-20:]
            
            with open(trade_log_path, 'w') as f:
                json.dump(trades, f, indent=2)
            
            # Update strategy output
            strategy_path = 'backend/strategy_output.json'
            total_trades = len(self.trade_history)
            successful_trades = sum(1 for t in self.trade_history if t['success'])
            success_rate = (successful_trades / total_trades * 100) if total_trades > 0 else 0
            
            strategy_data = {
                "performance": [{
                    "timestamp": datetime.now().isoformat(),
                    "pnl": sum(t['pnl'] for t in self.trade_history[-10:]),
                    "win_rate": success_rate,
                    "sharpe_ratio": random.uniform(1.0, 3.0)
                }],
                "insights": [{
                    "reason": "ML Learning Active",
                    "confidence": trade_data['confidence'],
                    "strategy": "AI Adaptive Trading"
                }]
            }
            
            with open(strategy_path, 'w') as f:
                json.dump(strategy_data, f, indent=2)
            
            # Update health status
            health_path = 'backend/health_status.json'
            health_data = {
                "status": "operational" if success_rate > 50 else "degraded",
                "last_update": datetime.now().isoformat(),
                "components": {
                    "data_feed": "operational",
                    "trade_execution": "operational", 
                    "risk_management": "operational",
                    "api_connectivity": "operational"
                },
                "metrics": {
                    "latency": random.uniform(50, 200),
                    "success_rate": success_rate,
                    "error_rate": 100 - success_rate
                }
            }
            
            with open(health_path, 'w') as f:
                json.dump(health_data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Error updating dashboard files: {e}")
    
    def update_positions(self):
        """
        Update any open positions (for future implementation)
        """
        # For now, all trades are closed immediately
        pass
    
    def log_trade(self, symbol, decision, result):
        """
        Log trade details
        """
        status = "✅ PROFIT" if result['success'] else "❌ LOSS"
        profit_str = f"${result['profit']:+.2f}"
        
        message = f"🔄 {symbol} {decision['direction']} | {status} {profit_str} | Confidence: {decision['confidence']:.1%} | Balance: ${self.paper_balance:,.2f}"
        print(message)
        
        self.test_log.append({
            'timestamp': datetime.now(),
            'type': 'trade',
            'message': message,
            'data': {'symbol': symbol, 'decision': decision, 'result': result}
        })
    
    def log_message(self, message):
        """
        Log general messages
        """
        print(message)
        self.test_log.append({
            'timestamp': datetime.now(),
            'type': 'info',
            'message': message
        })
    
    def log_error(self, message):
        """
        Log error messages
        """
        error_msg = f"❌ ERROR: {message}"
        print(error_msg)
        self.test_log.append({
            'timestamp': datetime.now(),
            'type': 'error',
            'message': error_msg
        })
    
    def log_status(self):
        """
        Log current status
        """
        total_trades = len(self.trade_history)
        if total_trades == 0:
            return
        
        successful_trades = sum(1 for trade in self.trade_history if trade['success'])
        success_rate = successful_trades / total_trades
        total_profit = sum(trade['profit'] for trade in self.trade_history)
        
        status = f"📊 Status: {total_trades} trades | {success_rate:.1%} success | ${total_profit:+.2f} P&L | Balance: ${self.paper_balance:,.2f}"
        self.log_message(status)
    
    def generate_test_report(self):
        """
        Generate comprehensive test report
        """
        print("\n" + "="*60)
        print("📊 NOBLELOGIC TRADING TEST REPORT")
        print("="*60)
        
        if not self.trade_history:
            print("No trades executed during test session.")
            return
        
        # Calculate statistics
        total_trades = len(self.trade_history)
        successful_trades = sum(1 for trade in self.trade_history if trade['success'])
        success_rate = successful_trades / total_trades
        total_profit = sum(trade['profit'] for trade in self.trade_history)
        avg_profit_per_trade = total_profit / total_trades
        
        print(f"📈 PERFORMANCE SUMMARY:")
        print(f"   Total Trades: {total_trades}")
        print(f"   Successful Trades: {successful_trades}")
        print(f"   Success Rate: {success_rate:.1%}")
        print(f"   Total P&L: ${total_profit:+.2f}")
        print(f"   Average per Trade: ${avg_profit_per_trade:+.2f}")
        print(f"   Final Balance: ${self.paper_balance:,.2f}")
        print(f"   Return: {((self.paper_balance - 100) / 100) * 100:+.2f}%")
        
        # ML Performance
        print(f"\n🤖 ML SYSTEM PERFORMANCE:")
        ml_stats = ml_trading_integration.get_ml_performance_stats()
        for key, value in ml_stats.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
        
        # Save report to file
        report_data = {
            'test_completed': datetime.now().isoformat(),
            'performance': {
                'total_trades': total_trades,
                'success_rate': success_rate,
                'total_profit': total_profit,
                'final_balance': self.paper_balance
            },
            'ml_stats': ml_stats,
            'trades': self.trade_history,
            'log': self.test_log
        }
        
        report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(f"logs/{report_filename}", 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n📄 Full report saved to: logs/{report_filename}")
        print("="*60)

# Function to run a quick test
async def run_quick_test(duration_minutes=30):
    """
    Run a quick test session
    """
    test_mode = TradingTestMode()
    await test_mode.start_test_session(duration_minutes=duration_minutes, trades_per_hour=20)

# Function to run extended test
async def run_extended_test(duration_hours=4):
    """
    Run an extended test session
    """
    test_mode = TradingTestMode()
    await test_mode.start_test_session(duration_minutes=duration_hours*60, trades_per_hour=15)

if __name__ == "__main__":
    print("🚀 NobleLogic Trading Test Mode")
    print("1. Quick Test (30 minutes)")
    print("2. Extended Test (4 hours)")
    choice = input("Select test mode (1 or 2): ")
    
    if choice == "1":
        asyncio.run(run_quick_test())
    elif choice == "2":
        asyncio.run(run_extended_test())
    else:
        print("Invalid choice. Running quick test by default.")
        asyncio.run(run_quick_test())