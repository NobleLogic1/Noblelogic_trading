"""
Real-Time Data Fetching Demo

Demonstrates WebSocket connections, data quality validation, and multi-exchange aggregation
"""

import asyncio
import time
import json
from datetime import datetime
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_time_data_fetcher import data_aggregator, MarketData, Exchange

class DataDemo:
    """Demo class for real-time data fetching"""

    def __init__(self):
        self.received_data = []
        self.start_time = None

    async def data_callback(self, data: MarketData):
        """Callback for receiving market data"""
        self.received_data.append(data)
        timestamp = datetime.fromtimestamp(data.timestamp).strftime('%H:%M:%S.%f')[:-3]

        print(f"📊 {data.exchange.upper():12} | {data.symbol:10} | "
              f"${data.price:>12.2f} | {data.volume:>10.2f} | "
              f"{data.data_quality.value:>8} | {timestamp}")

    async def run_demo(self, duration_seconds: int = 30):
        """Run the data fetching demo"""
        print("🚀 NobleLogic Real-Time Data Fetching Demo")
        print("=" * 60)
        print("Note: This demo works with or without API keys.")
        print("WebSocket connections may fail, but REST fallback will provide data.")
        print()
        print("Exchange      | Symbol     | Price       | Volume    | Quality  | Time")
        print("-" * 60)

        # Add data callback
        data_aggregator.add_data_callback(self.data_callback)

        # Subscribe to popular trading pairs
        symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
        print(f"📡 Subscribing to symbols: {symbols}")

        await data_aggregator.subscribe_symbols(symbols)

        # Start data aggregator
        self.start_time = time.time()
        aggregator_task = asyncio.create_task(data_aggregator.start())

        try:
            # Run for specified duration
            await asyncio.sleep(duration_seconds)

        except KeyboardInterrupt:
            print("\n🛑 Demo interrupted by user")

        finally:
            # Stop aggregator
            print("🛑 Stopping data aggregator...")
            await data_aggregator.stop()
            aggregator_task.cancel()

            try:
                await aggregator_task
            except asyncio.CancelledError:
                pass

        # Show summary
        await self.show_summary()

    async def show_summary(self):
        """Show demo summary"""
        print("\n" + "=" * 60)
        print("📊 Demo Summary")

        total_messages = len(self.received_data)
        duration = time.time() - self.start_time if self.start_time else 0

        print(f"Duration: {duration:.1f} seconds")
        print(f"Total messages received: {total_messages}")
        print(".1f")

        if self.received_data:
            # Group by exchange
            exchange_counts = {}
            symbol_counts = {}
            quality_counts = {}

            for data in self.received_data:
                exchange_counts[data.exchange] = exchange_counts.get(data.exchange, 0) + 1
                symbol_counts[data.symbol] = symbol_counts.get(data.symbol, 0) + 1
                quality_counts[data.data_quality.value] = quality_counts.get(data.data_quality.value, 0) + 1

            print("\n📈 Messages by Exchange:")
            for exchange, count in exchange_counts.items():
                print(f"  {exchange.upper()}: {count}")

            print("\n📈 Messages by Symbol:")
            for symbol, count in symbol_counts.items():
                print(f"  {symbol}: {count}")

            print("\n📈 Data Quality Distribution:")
            for quality, count in quality_counts.items():
                percentage = (count / total_messages) * 100
                print(".1f")

        else:
            print("\n📈 No real-time data received during demo period")
            print("   This is normal if WebSocket connections failed.")
            print("   The system will use REST API fallback for price data.")

            # Show fallback data availability
            print("\n📈 Fallback Data Check:")
            for symbol in ["BTC/USDT", "ETH/USDT", "BNB/USDT"]:
                fallback_data = data_aggregator.get_aggregated_data(symbol)
                if fallback_data:
                    print(f"  {symbol}: ${fallback_data.price:.2f} (via {fallback_data.exchange})")
                else:
                    print(f"  {symbol}: No data available")

        # Show data quality report
        print("\n📋 Data Quality Report:")
        quality_report = data_aggregator.get_quality_report()
        if quality_report:
            for key, metrics in quality_report.items():
                print(f"  {key}: {metrics['valid_messages']}/{metrics['total_messages']} valid "
                      f"({metrics['data_freshness_score']:.2f} freshness)")
        else:
            print("  No quality metrics available (no data processed)")

        print("\n✅ Demo completed successfully!")

async def main():
    """Main demo function"""
    demo = DataDemo()

    # Run demo for 30 seconds
    await demo.run_demo(duration_seconds=30)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        sys.exit(1)