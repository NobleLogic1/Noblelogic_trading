"""
Test script for advanced trade execution integration
"""

import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from trade_execution import (
    AdvancedTradeExecution, Order, OrderType, OrderSide,
    trade_execution_engine
)

async def test_trade_execution():
    """Test the trade execution system"""
    print("\n===== TESTING ADVANCED TRADE EXECUTION =====\n")

    # Test different order types
    test_orders = [
        {
            'symbol': 'BTC/USDT',
            'side': OrderSide.BUY,
            'order_type': OrderType.MARKET,
            'quantity': 0.01,
            'description': 'Market Buy Order'
        },
        {
            'symbol': 'ETH/USDT',
            'side': OrderSide.SELL,
            'order_type': OrderType.LIMIT,
            'quantity': 0.1,
            'price': 3000,
            'description': 'Limit Sell Order'
        },
        {
            'symbol': 'ADA/USDT',
            'side': OrderSide.BUY,
            'order_type': OrderType.TWAP,
            'quantity': 1000,
            'description': 'TWAP Buy Order (simulated)'
        },
        {
            'symbol': 'SOL/USDT',
            'side': OrderSide.SELL,
            'order_type': OrderType.VWAP,
            'quantity': 50,
            'description': 'VWAP Sell Order (simulated)'
        }
    ]

    # Execute test orders
    for i, order_data in enumerate(test_orders):
        print(f"\n--- Test {i+1}: {order_data['description']} ---")

        # Create order
        order = Order(
            order_id=f"test_order_{i+1}_{int(datetime.now().timestamp())}",
            symbol=order_data['symbol'],
            side=order_data['side'],
            order_type=order_data['order_type'],
            quantity=order_data['quantity'],
            price=order_data.get('price'),
            slippage_protection=True,
            max_slippage_percent=0.5
        )

        # Prepare market data
        market_data = {
            'price': order_data.get('price', 45000),
            'volatility': 0.02,
            'volume': 1000000,
            'market_regime': 'SIDEWAYS',
            'trend_strength': 0.5,
            'trend_direction': 1 if order_data['side'] == OrderSide.BUY else -1,
            'liquidity_score': 0.8,
            'avg_volume_24h': 1000000
        }

        try:
            # Execute order
            result = await trade_execution_engine.execute_order(order, market_data)

            print(f"✅ Order executed successfully")
            print(f"   Order ID: {order.order_id}")
            print(f"   Symbol: {order.symbol}")
            print(f"   Type: {order.order_type.value}")
            print(f"   Side: {order.side.value}")
            print(f"   Quantity: {order.quantity}")

            if 'average_price' in result:
                print(f"   Execution Price: ${result['average_price']:.2f}")
            if 'slippage_percent' in result:
                print(f"   Slippage: {result['slippage_percent']:.2f}%")
            if 'exchange' in result:
                print(f"   Exchange: {result['exchange']}")
            if 'execution_time_ms' in result:
                print(f"   Execution Time: {result['execution_time_ms']:.1f}ms")

            if order.order_type in [OrderType.TWAP, OrderType.VWAP]:
                if 'strategy' in result:
                    print(f"   Strategy: {result['strategy']}")
                if 'average_price' in result and 'vwap_target' in result:
                    print(f"   VWAP Target: ${result['vwap_target']:.2f}")
                    print(f"   VWAP Deviation: {result.get('vwap_deviation', 0):.2f}%")

        except Exception as e:
            print(f"❌ Order execution failed: {e}")

    # Get execution statistics
    print("\n--- Execution Statistics ---")
    stats = trade_execution_engine.get_execution_stats()

    print(f"Total Orders: {stats.get('total_orders', 0)}")
    print(f"Successful Orders: {stats.get('successful_orders', 0)}")
    print(f"Success Rate: {stats.get('success_rate', 0):.1%}")
    print(f"Total Value Executed: ${stats.get('total_value_executed', 0):,.2f}")
    print(f"Average Slippage: {stats.get('average_slippage_percent', 0):.2f}%")

    if 'orders_by_type' in stats:
        print("\nOrders by Type:")
        for order_type, count in stats['orders_by_type'].items():
            print(f"  {order_type}: {count}")

    if 'orders_by_exchange' in stats:
        print("\nOrders by Exchange:")
        for exchange, count in stats['orders_by_exchange'].items():
            print(f"  {exchange}: {count}")

    print("\n===== TRADE EXECUTION TESTING COMPLETE =====\n")

if __name__ == "__main__":
    asyncio.run(test_trade_execution())