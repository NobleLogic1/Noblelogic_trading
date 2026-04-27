"""
Test Real-Time Data Fetching Engine

Tests WebSocket connections, data validation, and multi-exchange aggregation
"""

import asyncio
import time
import json
from datetime import datetime
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_time_data_fetcher import (
    MultiExchangeAggregator,
    Exchange,
    MarketData,
    DataQuality,
    DataQualityValidator
)

class DataFetcherTester:
    """Test suite for real-time data fetching functionality"""

    def __init__(self):
        self.aggregator = MultiExchangeAggregator()
        # Add exchanges for testing
        self.aggregator.add_exchange(Exchange.BINANCE_US)
        self.aggregator.add_exchange(Exchange.COINBASE_PRO)
        self.aggregator.add_exchange(Exchange.KRAKEN)
        self.validator = DataQualityValidator()
        self.test_results = []
        self.data_received = []

    def log_test_result(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status} {test_name}"
        if message:
            result += f": {message}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })

    async def test_data_validation(self):
        """Test data quality validation"""
        print("\n🧪 Testing Data Quality Validation...")

        # Test valid data
        valid_data = MarketData(
            symbol="BTC/USDT",
            exchange="binance_us",
            timestamp=time.time(),
            price=50000.0,
            volume=100.0,
            received_at=time.time()
        )

        is_valid, quality, reason = self.validator.validate_data(valid_data)
        self.log_test_result(
            "Valid data validation",
            is_valid and quality in [DataQuality.EXCELLENT, DataQuality.GOOD],
            f"Quality: {quality.value}, Reason: {reason}"
        )

        # Test invalid data (negative price)
        invalid_data = MarketData(
            symbol="BTC/USDT",
            exchange="binance_us",
            timestamp=time.time(),
            price=-100.0,
            volume=100.0,
            received_at=time.time()
        )

        is_valid, quality, reason = self.validator.validate_data(invalid_data)
        self.log_test_result(
            "Invalid data detection",
            not is_valid and quality == DataQuality.INVALID,
            f"Quality: {quality.value}, Reason: {reason}"
        )

        # Test stale data
        stale_data = MarketData(
            symbol="BTC/USDT",
            exchange="binance_us",
            timestamp=time.time() - 60,  # 1 minute old
            price=50000.0,
            volume=100.0,
            received_at=time.time() - 60
        )

        is_valid, quality, reason = self.validator.validate_data(stale_data)
        self.log_test_result(
            "Stale data detection",
            not is_valid and quality == DataQuality.POOR,
            f"Quality: {quality.value}, Reason: {reason}"
        )

    async def test_exchange_connections(self):
        """Test exchange WebSocket connections"""
        print("\n🧪 Testing Exchange Connections...")

        # Test connection establishment (without actually connecting to avoid API limits)
        for exchange in [Exchange.BINANCE_US, Exchange.COINBASE_PRO, Exchange.KRAKEN]:
            connection = self.aggregator.connections[exchange.value]
            has_url = bool(connection.ws_url)
            self.log_test_result(
                f"{exchange.value} WebSocket URL",
                has_url,
                f"URL: {connection.ws_url}"
            )

    async def test_data_aggregation(self):
        """Test multi-exchange data aggregation"""
        print("\n🧪 Testing Data Aggregation...")

        # Create mock data from different exchanges
        mock_data = [
            MarketData(
                symbol="BTC/USDT",
                exchange="binance_us",
                timestamp=time.time(),
                price=50000.0,
                volume=100.0,
                data_quality=DataQuality.EXCELLENT,
                received_at=time.time()
            ),
            MarketData(
                symbol="BTC/USDT",
                exchange="coinbase_pro",
                timestamp=time.time() - 0.5,
                price=50010.0,
                volume=95.0,
                data_quality=DataQuality.GOOD,
                received_at=time.time() - 0.5
            ),
            MarketData(
                symbol="BTC/USDT",
                exchange="kraken",
                timestamp=time.time() - 1.0,
                price=49990.0,
                volume=90.0,
                data_quality=DataQuality.FAIR,
                received_at=time.time() - 1.0
            )
        ]

        # Manually process data to test aggregation
        for data in mock_data:
            await self.aggregator._process_market_data(data)

        # Check aggregated data
        aggregated = self.aggregator.get_aggregated_data("BTC/USDT")
        has_aggregated = aggregated is not None
        self.log_test_result(
            "Data aggregation",
            has_aggregated,
            f"Aggregated price: {aggregated.price if aggregated else 'None'}"
        )

        if aggregated:
            # Should select the highest quality/most recent data
            expected_exchange = "binance_us"  # Highest quality
            correct_selection = aggregated.exchange == expected_exchange
            self.log_test_result(
                "Best data selection",
                correct_selection,
                f"Selected: {aggregated.exchange}, Expected: {expected_exchange}"
            )

    async def test_symbol_subscription(self):
        """Test symbol subscription functionality"""
        print("\n🧪 Testing Symbol Subscription...")

        test_symbols = ["BTC/USDT", "ETH/USDT"]

        # Test subscription tracking
        await self.aggregator.subscribe_symbols(test_symbols)

        subscription_tracked = test_symbols[0] in self.aggregator.subscribed_symbols
        self.log_test_result(
            "Symbol subscription tracking",
            subscription_tracked,
            f"Subscribed symbols: {list(self.aggregator.subscribed_symbols)}"
        )

    async def test_data_callbacks(self):
        """Test data callback functionality"""
        print("\n🧪 Testing Data Callbacks...")

        callback_received = []

        def test_callback(data):
            callback_received.append(data)

        self.aggregator.add_data_callback(test_callback)

        # Send test data
        test_data = MarketData(
            symbol="BTC/USDT",
            exchange="binance_us",
            timestamp=time.time(),
            price=50000.0,
            volume=100.0,
            received_at=time.time()
        )

        await self.aggregator._process_market_data(test_data)

        # Check if callback was called
        callback_called = len(callback_received) > 0
        self.log_test_result(
            "Data callback execution",
            callback_called,
            f"Callbacks received: {len(callback_received)}"
        )

    async def test_quality_reporting(self):
        """Test data quality reporting"""
        print("\n🧪 Testing Quality Reporting...")

        # Add some test data
        test_data = MarketData(
            symbol="BTC/USDT",
            exchange="binance_us",
            timestamp=time.time(),
            price=50000.0,
            volume=100.0,
            received_at=time.time()
        )

        self.validator.validate_data(test_data)

        # Get quality report
        report = self.validator.get_quality_report("BTC/USDT", "binance_us")
        has_report = bool(report)
        self.log_test_result(
            "Quality report generation",
            has_report,
            f"Report keys: {list(report.keys()) if report else 'None'}"
        )

    async def test_connection_management(self):
        """Test connection management and failover"""
        print("\n🧪 Testing Connection Management...")

        # Test adding/removing exchanges
        initial_count = len(self.aggregator.connections)

        # Add a new exchange
        self.aggregator.add_exchange(Exchange.KUCOIN)
        after_add_count = len(self.aggregator.connections)

        add_successful = after_add_count > initial_count
        self.log_test_result(
            "Exchange addition",
            add_successful,
            f"Connections: {initial_count} -> {after_add_count}"
        )

        # Remove exchange
        self.aggregator.remove_exchange(Exchange.KUCOIN)
        after_remove_count = len(self.aggregator.connections)

        remove_successful = after_remove_count < after_add_count
        self.log_test_result(
            "Exchange removal",
            remove_successful,
            f"Connections: {after_add_count} -> {after_remove_count}"
        )

    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Real-Time Data Fetching Tests...")
        print("=" * 50)

        start_time = time.time()

        try:
            await self.test_data_validation()
            await self.test_exchange_connections()
            await self.test_data_aggregation()
            await self.test_symbol_subscription()
            await self.test_data_callbacks()
            await self.test_quality_reporting()
            await self.test_connection_management()

        except Exception as e:
            print(f"❌ Test suite error: {e}")
            self.log_test_result("Test suite execution", False, str(e))

        end_time = time.time()
        duration = end_time - start_time

        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")

        passed_tests = sum(1 for result in self.test_results if result['passed'])
        total_tests = len(self.test_results)

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(".1f")
        print(".2f")

        if passed_tests == total_tests:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed. Check logs above.")

        # Save results to file
        results_file = "test_data_fetching_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed': passed_tests,
                    'failed': total_tests - passed_tests,
                    'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
                    'duration_seconds': duration
                },
                'results': self.test_results,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)

        print(f"\n📄 Detailed results saved to {results_file}")

        return passed_tests == total_tests

async def main():
    """Main test execution"""
    tester = DataFetcherTester()
    success = await tester.run_all_tests()

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())