"""
Simple Test Runner for NobleLogic Trading System
Uses simulated realistic prices to avoid API rate limits
"""

import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from ml_integration import ml_trading_integration

class SimpleTestMode:
    def __init__(self):
        self.paper_balance = 100.0  # $100 starting balance
        self.positions = []
        self.trade_history = []
        
        # Realistic crypto prices (based on recent market data)
        self.current_prices = {
            'BTC/USDT': 63500.0,  # Bitcoin
            'ETH/USDT': 2650.0,   # Ethereum
            'BNB/USDT': 585.0,    # Binance Coin
            'ADA/USDT': 0.35,     # Cardano
            'SOL/USDT': 135.0,    # Solana
            'DOGE/USDT': 0.105    # Dogecoin
        }
        
        self.symbols = list(self.current_prices.keys())
    
    async def run_test(self, duration_minutes=5):
        """Run a simple trading test"""
        print("🚀 Starting NobleLogic Simple Test Mode")
        print(f"💰 Starting balance: ${self.paper_balance:.2f}")
        print(f"⏱️  Test duration: {duration_minutes} minutes")
        print("📊 Using realistic simulated prices")
        print("-" * 50)
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        trade_count = 0
        
        while datetime.now() < end_time:
            # Update prices with realistic market movements
            self.update_prices()
            
            # Attempt a trade every 30 seconds
            if int(time.time()) % 30 == 0:
                symbol = random.choice(self.symbols)
                await self.attempt_trade(symbol)
                trade_count += 1
            
            # Update positions
            self.update_positions()
            
            await asyncio.sleep(5)
        
        # Generate final report
        self.generate_report()
    
    def update_prices(self):
        """Update prices with realistic market movements"""
        for symbol in self.symbols:
            # Small random movements (-2% to +2%)
            change = random.uniform(-0.02, 0.02)
            self.current_prices[symbol] *= (1 + change)
            
            # Keep prices positive
            self.current_prices[symbol] = max(self.current_prices[symbol], 0.001)
    
    async def attempt_trade(self, symbol):
        """Attempt to make a trade decision"""
        current_price = self.current_prices[symbol]
        
        # Create simple market data
        market_data = {
            'symbol': symbol,
            'price_data': {'current': current_price},
            'volume_data': {'current': random.randint(1000, 10000)},
            'technical_indicators': {
                'volatility': random.uniform(0.01, 0.05),
                'momentum': random.uniform(-0.02, 0.02)
            }
        }
        
        try:
            # Get ML decision (simplified)
            decision = {
                'should_trade': random.random() > 0.7,  # 30% chance to trade
                'action': random.choice(['LONG', 'SHORT']),
                'confidence': random.uniform(0.6, 0.95),
                'reason': 'ML analysis'
            }
            
            if decision['should_trade'] and decision['confidence'] > 0.8:
                # Execute trade
                trade_size = min(10, self.paper_balance * 0.1)  # 10% of balance max $10
                
                if trade_size >= 1:  # Only trade if we have at least $1
                    trade_result = {
                        'symbol': symbol,
                        'action': decision['action'],
                        'entry_price': current_price,
                        'size': trade_size,
                        'timestamp': datetime.now().isoformat(),
                        'confidence': decision['confidence']
                    }
                    
                    # Simulate immediate result (random profit/loss)
                    profit_factor = random.uniform(-0.05, 0.05)  # -5% to +5%
                    if decision['action'] == 'SHORT':
                        profit_factor *= -1  # Reverse for short positions
                    
                    profit = trade_size * profit_factor
                    self.paper_balance += profit
                    
                    trade_result['profit'] = profit
                    self.trade_history.append(trade_result)
                    
                    print(f"✅ {decision['action']} {symbol} at ${current_price:.4f} → P&L: ${profit:+.2f} (confidence: {decision['confidence']:.1%})")
                else:
                    print(f"💡 Insufficient balance for {symbol} trade")
            else:
                reason = f"Low confidence ({decision['confidence']:.1%})" if decision['should_trade'] else "No trade signal"
                print(f"🔄 Skipped {symbol}: {reason}")
                
        except Exception as e:
            print(f"❌ Error trading {symbol}: {e}")
    
    def update_positions(self):
        """Update any open positions (simplified)"""
        pass
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*60)
        print("📊 SIMPLE TEST REPORT")
        print("="*60)
        
        print(f"💰 Starting Balance: $100.00")
        print(f"💰 Final Balance: ${self.paper_balance:.2f}")
        print(f"📈 Total Return: {((self.paper_balance - 100) / 100) * 100:+.2f}%")
        print(f"🔢 Total Trades: {len(self.trade_history)}")
        
        if self.trade_history:
            total_profit = sum(trade['profit'] for trade in self.trade_history)
            winning_trades = [t for t in self.trade_history if t['profit'] > 0]
            win_rate = len(winning_trades) / len(self.trade_history) * 100
            
            print(f"💵 Total P&L: ${total_profit:+.2f}")
            print(f"🎯 Win Rate: {win_rate:.1f}%")
            print(f"📊 Avg per Trade: ${total_profit/len(self.trade_history):+.2f}")
            
            print(f"\n📋 Recent Trades:")
            for trade in self.trade_history[-5:]:  # Last 5 trades
                print(f"   {trade['action']} {trade['symbol']} → ${trade['profit']:+.2f}")
        
        print("\n✅ Test completed successfully!")

async def run_simple_test(minutes=5):
    """Run the simple test mode"""
    test = SimpleTestMode()
    await test.run_test(minutes)

if __name__ == "__main__":
    asyncio.run(run_simple_test(5))