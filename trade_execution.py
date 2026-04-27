"""
Advanced Trade Execution Engine for NobleLogic Trading System

Features:
- Slippage protection with dynamic limits
- Smart order routing across multiple exchanges
- TWAP/VWAP algorithms for large position execution
- Order management and monitoring
- Execution quality metrics
"""

import asyncio
import time
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import json
import os
from dataclasses import dataclass, asdict
from enum import Enum

# Import audit logging
from audit_logger import audit_logger, log_trade_execution, log_error, log_performance_metric, AuditEvent

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TWAP = "twap"
    VWAP = "vwap"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

@dataclass
class Order:
    """Represents a trading order"""
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "GTC"  # Good Till Cancelled
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    average_fill_price: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None
    slippage_protection: bool = True
    max_slippage_percent: float = 0.5  # 0.5% max slippage
    exchange: str = "binance_us"
    execution_strategy: str = "standard"

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class ExecutionMetrics:
    """Tracks execution quality metrics"""
    order_id: str
    total_slippage: float = 0.0
    execution_time_ms: float = 0.0
    price_improvement: float = 0.0
    market_impact: float = 0.0
    fill_rate: float = 0.0
    vwap_deviation: float = 0.0
    realized_spread: float = 0.0

class SlippageProtection:
    """
    Advanced slippage protection system with dynamic limits
    """

    def __init__(self):
        self.market_volatility = {}
        self.order_book_depth = {}
        self.historical_slippage = []
        self.max_history = 1000

    def calculate_dynamic_slippage_limit(self, symbol: str, order_size: float,
                                       market_data: Dict[str, Any]) -> float:
        """
        Calculate dynamic slippage limit based on market conditions

        Args:
            symbol: Trading symbol
            order_size: Order size in base currency
            market_data: Current market data

        Returns:
            Maximum allowed slippage percentage
        """
        # Base slippage limit
        base_limit = 0.5  # 0.5%

        # Adjust for volatility
        volatility = market_data.get('volatility', 0.02)
        volatility_multiplier = min(3.0, max(0.5, volatility * 50))  # 0.5x to 3x

        # Adjust for order size relative to market volume
        avg_volume = market_data.get('avg_volume_24h', 1000000)
        size_ratio = order_size / avg_volume
        size_multiplier = min(5.0, max(1.0, size_ratio * 10))  # 1x to 5x

        # Adjust for market regime
        market_regime = market_data.get('market_regime', 'SIDEWAYS')
        regime_multipliers = {
            'SIDEWAYS': 1.0,
            'BULL': 1.2,
            'BEAR': 1.2,
            'VOLATILE': 2.0,
            'PANIC': 3.0,
            'EUPHORIA': 2.5
        }
        regime_multiplier = regime_multipliers.get(market_regime, 1.0)

        # Adjust for time of day (higher slippage during news events)
        hour = datetime.now().hour
        time_multiplier = 1.0
        if 13 <= hour <= 15:  # Market open hours
            time_multiplier = 1.5
        elif hour in [8, 9, 16, 17]:  # Potential news hours
            time_multiplier = 2.0

        # Calculate final limit
        dynamic_limit = base_limit * volatility_multiplier * size_multiplier * regime_multiplier * time_multiplier

        # Cap at reasonable maximum
        return min(dynamic_limit, 5.0)  # Max 5% slippage

    def validate_slippage(self, order: Order, execution_price: float,
                         market_price: float) -> Tuple[bool, float]:
        """
        Validate if execution price is within slippage limits

        Args:
            order: Order object
            execution_price: Price at which order was executed
            market_price: Reference market price

        Returns:
            Tuple of (is_valid, slippage_percent)
        """
        if not order.slippage_protection:
            return True, 0.0

        # Calculate slippage
        if order.side == OrderSide.BUY:
            slippage_percent = ((execution_price - market_price) / market_price) * 100
        else:  # SELL
            slippage_percent = ((market_price - execution_price) / market_price) * 100

        slippage_percent = abs(slippage_percent)

        # Check against limit
        max_allowed = order.max_slippage_percent
        is_valid = slippage_percent <= max_allowed

        # Record for historical analysis
        self.historical_slippage.append({
            'timestamp': time.time(),
            'symbol': order.symbol,
            'slippage_percent': slippage_percent,
            'order_size': order.quantity,
            'market_regime': 'UNKNOWN'  # Would be populated from market data
        })

        # Limit history size
        if len(self.historical_slippage) > self.max_history:
            self.historical_slippage = self.historical_slippage[-self.max_history:]

        return is_valid, slippage_percent

class SmartOrderRouter:
    """
    Intelligent order routing across multiple exchanges and order types
    """

    def __init__(self):
        self.exchanges = {
            'binance_us': {
                'fee_maker': 0.001,  # 0.1%
                'fee_taker': 0.001,
                'liquidity_score': 0.9,
                'latency_ms': 50,
                'supported_symbols': ['BTC/USD', 'ETH/USD', 'ADA/USD']
            },
            'coinbase_pro': {
                'fee_maker': 0.005,  # 0.5%
                'fee_taker': 0.005,
                'liquidity_score': 0.8,
                'latency_ms': 75,
                'supported_symbols': ['BTC/USD', 'ETH/USD']
            },
            'kraken': {
                'fee_maker': 0.0016,  # 0.16%
                'fee_taker': 0.0026,  # 0.26%
                'liquidity_score': 0.7,
                'latency_ms': 100,
                'supported_symbols': ['BTC/USD', 'ETH/USD', 'ADA/USD', 'SOL/USD']
            }
        }

        self.routing_history = []

    def select_best_exchange(self, symbol: str, order_type: OrderType,
                           order_size: float, urgency: str = 'normal') -> str:
        """
        Select the best exchange for order execution

        Args:
            symbol: Trading symbol
            order_type: Type of order
            order_size: Order size
            urgency: 'low', 'normal', 'high'

        Returns:
            Best exchange name
        """
        candidates = []

        for exchange_name, exchange_info in self.exchanges.items():
            if symbol not in exchange_info['supported_symbols']:
                continue

            # Calculate routing score
            score = self._calculate_routing_score(
                exchange_info, order_type, order_size, urgency
            )
            candidates.append((exchange_name, score))

        if not candidates:
            return 'binance_us'  # Default fallback

        # Return exchange with highest score
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    def _calculate_routing_score(self, exchange_info: Dict, order_type: OrderType,
                               order_size: float, urgency: str) -> float:
        """Calculate routing score for an exchange"""
        score = 0.0

        # Liquidity score (0-1, higher is better)
        score += exchange_info['liquidity_score'] * 40

        # Fee score (lower fees = higher score)
        avg_fee = (exchange_info['fee_maker'] + exchange_info['fee_taker']) / 2
        fee_score = max(0, 1.0 - avg_fee * 100)  # Convert to 0-1 scale
        score += fee_score * 30

        # Latency score (lower latency = higher score)
        latency_score = max(0, 1.0 - (exchange_info['latency_ms'] / 200))  # Normalize to 200ms baseline
        score += latency_score * 20

        # Urgency adjustment
        urgency_multipliers = {'low': 0.8, 'normal': 1.0, 'high': 1.2}
        score *= urgency_multipliers.get(urgency, 1.0)

        # Order type adjustment
        if order_type == OrderType.MARKET:
            # For market orders, prioritize speed and liquidity
            score *= 1.1
        elif order_type in [OrderType.TWAP, OrderType.VWAP]:
            # For algorithmic orders, prioritize fees and stability
            score *= 0.9

        return score

    def get_exchange_info(self, exchange: str) -> Dict[str, Any]:
        """Get information about a specific exchange"""
        return self.exchanges.get(exchange, {})

class TWAPVWAPEngine:
    """
    Time-Weighted Average Price (TWAP) and Volume-Weighted Average Price (VWAP) execution
    """

    def __init__(self):
        self.active_orders = {}
        self.execution_schedules = {}
        self.market_data_cache = {}

    async def execute_twap_order(self, order: Order, duration_minutes: int = 60,
                               slices: int = 12) -> Dict[str, Any]:
        """
        Execute order using Time-Weighted Average Price strategy

        Args:
            order: Order to execute
            duration_minutes: Total execution time
            slices: Number of time slices

        Returns:
            Execution results
        """
        order_id = order.order_id
        self.active_orders[order_id] = order

        # Calculate execution schedule
        total_quantity = order.quantity
        slice_quantity = total_quantity / slices
        slice_interval = (duration_minutes * 60) / slices  # seconds between slices

        execution_results = {
            'order_id': order_id,
            'strategy': 'TWAP',
            'total_slices': slices,
            'slice_interval_seconds': slice_interval,
            'executed_slices': 0,
            'total_executed_quantity': 0.0,
            'total_executed_value': 0.0,
            'average_price': 0.0,
            'start_time': datetime.now(),
            'end_time': None,
            'status': 'running'
        }

        print(f"[TWAP] Starting TWAP execution for {order.symbol} - {slices} slices over {duration_minutes} minutes")

        for slice_num in range(slices):
            # Wait for next slice
            if slice_num > 0:
                await asyncio.sleep(slice_interval)

            # Execute slice
            slice_result = await self._execute_slice(order, slice_quantity, slice_num + 1)
            execution_results['executed_slices'] += 1
            execution_results['total_executed_quantity'] += slice_result['executed_quantity']
            execution_results['total_executed_value'] += slice_result['executed_value']

            # Update average price
            if execution_results['total_executed_quantity'] > 0:
                execution_results['average_price'] = (
                    execution_results['total_executed_value'] / execution_results['total_executed_quantity']
                )

            print(f"[TWAP] Slice {slice_num + 1}/{slices} executed: "
                  f"{slice_result['executed_quantity']:.4f} @ ${slice_result['average_price']:.2f}")

        execution_results['end_time'] = datetime.now()
        execution_results['status'] = 'completed'

        # Calculate final metrics
        execution_results['execution_time_minutes'] = (
            (execution_results['end_time'] - execution_results['start_time']).total_seconds() / 60
        )
        execution_results['completion_rate'] = (
            execution_results['total_executed_quantity'] / total_quantity
        )

        print(f"[TWAP] TWAP execution completed for {order.symbol}")
        print(f"[TWAP] Average execution price: ${execution_results['average_price']:.2f}")
        print(f"[TWAP] Total executed: {execution_results['total_executed_quantity']:.4f}/{total_quantity:.4f}")

        return execution_results

    async def execute_vwap_order(self, order: Order, duration_minutes: int = 60) -> Dict[str, Any]:
        """
        Execute order using Volume-Weighted Average Price strategy

        Args:
            order: Order to execute
            duration_minutes: Total execution time

        Returns:
            Execution results
        """
        order_id = order.order_id
        self.active_orders[order_id] = order

        execution_results = {
            'order_id': order_id,
            'strategy': 'VWAP',
            'total_executed_quantity': 0.0,
            'total_executed_value': 0.0,
            'average_price': 0.0,
            'vwap_target': 0.0,
            'vwap_deviation': 0.0,
            'start_time': datetime.now(),
            'end_time': None,
            'status': 'running'
        }

        print(f"[VWAP] Starting VWAP execution for {order.symbol} over {duration_minutes} minutes")

        # Calculate target VWAP (simplified - would use historical volume profile)
        target_vwap = await self._calculate_target_vwap(order.symbol, duration_minutes)
        execution_results['vwap_target'] = target_vwap

        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        total_quantity = order.quantity

        while time.time() < end_time and execution_results['total_executed_quantity'] < total_quantity:
            # Calculate remaining time and quantity
            remaining_time = end_time - time.time()
            remaining_quantity = total_quantity - execution_results['total_executed_quantity']

            if remaining_time <= 0:
                break

            # Calculate volume participation rate (simplified)
            participation_rate = await self._calculate_volume_participation(
                order.symbol, remaining_quantity, remaining_time
            )

            # Execute portion based on participation rate
            slice_quantity = min(remaining_quantity, participation_rate)

            if slice_quantity > 0.001:  # Minimum order size
                slice_result = await self._execute_slice(order, slice_quantity, 0)
                execution_results['total_executed_quantity'] += slice_result['executed_quantity']
                execution_results['total_executed_value'] += slice_result['executed_value']

                # Update average price
                if execution_results['total_executed_quantity'] > 0:
                    execution_results['average_price'] = (
                        execution_results['total_executed_value'] / execution_results['total_executed_quantity']
                    )

                print(f"[VWAP] Executed slice: {slice_result['executed_quantity']:.4f} @ ${slice_result['average_price']:.2f}")

            # Wait before next execution
            await asyncio.sleep(30)  # Check every 30 seconds

        execution_results['end_time'] = datetime.now()
        execution_results['status'] = 'completed'

        # Calculate VWAP deviation
        if execution_results['average_price'] > 0 and target_vwap > 0:
            execution_results['vwap_deviation'] = (
                (execution_results['average_price'] - target_vwap) / target_vwap
            ) * 100

        print(f"[VWAP] VWAP execution completed for {order.symbol}")
        print(f"[VWAP] Average execution price: ${execution_results['average_price']:.2f}")
        print(f"[VWAP] Target VWAP: ${target_vwap:.2f}")
        print(f"[VWAP] VWAP deviation: {execution_results['vwap_deviation']:.2f}%")

        return execution_results

    async def _execute_slice(self, order: Order, quantity: float, slice_num: int) -> Dict[str, Any]:
        """Execute a single slice of an order"""
        # Simulate execution with some randomness
        execution_price = order.price or 45000  # Default price if not specified

        # Add some price variation (±0.5%)
        price_variation = random.uniform(-0.005, 0.005)
        actual_price = execution_price * (1 + price_variation)

        # Simulate partial fills (90-100% fill rate)
        fill_rate = random.uniform(0.9, 1.0)
        executed_quantity = quantity * fill_rate
        executed_value = executed_quantity * actual_price

        return {
            'executed_quantity': executed_quantity,
            'average_price': actual_price,
            'executed_value': executed_value,
            'fill_rate': fill_rate,
            'slice_number': slice_num
        }

    async def _calculate_target_vwap(self, symbol: str, duration_minutes: int) -> float:
        """Calculate target VWAP for the execution period"""
        # Simplified VWAP calculation - would use historical data
        base_price = 45000  # Would get from market data
        return base_price * random.uniform(0.98, 1.02)  # ±2% variation

    async def _calculate_volume_participation(self, symbol: str,
                                            remaining_quantity: float,
                                            remaining_time_seconds: float) -> float:
        """Calculate how much volume to participate in"""
        # Simplified - would use real-time volume data
        base_volume_rate = 1000  # units per minute
        participation_rate = base_volume_rate * (remaining_time_seconds / 60)
        return min(remaining_quantity, participation_rate * random.uniform(0.05, 0.15))

class AdvancedTradeExecution:
    """
    Main trade execution engine combining all features
    """

    def __init__(self):
        self.slippage_protection = SlippageProtection()
        self.order_router = SmartOrderRouter()
        self.twap_vwap_engine = TWAPVWAPEngine()

        self.active_orders = {}
        self.order_history = []
        self.execution_metrics = {}

        print("[TRADE EXECUTION] Advanced Trade Execution Engine initialized")

    async def execute_order(self, order: Order, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an order with all advanced features

        Args:
            order: Order to execute
            market_data: Current market data

        Returns:
            Execution results
        """
        start_time = time.time()
        order_id = order.order_id

        # Audit: Log order execution start
        audit_logger.log_system_event(
            AuditEvent.USER_ACTION,
            f"Starting order execution: {order.side.value.upper()} {order.quantity} {order.symbol}",
            component="trade_execution",
            metadata={
                'order_id': order_id,
                'symbol': order.symbol,
                'side': order.side.value,
                'quantity': order.quantity,
                'order_type': order.order_type.value,
                'execution_strategy': order.execution_strategy,
                'exchange': getattr(order, 'exchange', None)
            }
        )

        print(f"[EXECUTION] Executing {order.side.value.upper()} order for {order.symbol} "
              f"({order.quantity} units) via {order.execution_strategy}")

        # Select best exchange if not specified
        if not hasattr(order, 'exchange') or not order.exchange:
            order.exchange = self.order_router.select_best_exchange(
                order.symbol, order.order_type, order.quantity
            )

        # Store order
        self.active_orders[order_id] = order

        execution_result = None

        try:
            # Route based on order type and strategy
            if order.order_type == OrderType.TWAP:
                execution_result = await self.twap_vwap_engine.execute_twap_order(order)
            elif order.order_type == OrderType.VWAP:
                execution_result = await self.twap_vwap_engine.execute_vwap_order(order)
            else:
                # Standard execution
                execution_result = await self._execute_standard_order(order, market_data)

            # Calculate execution metrics
            execution_time = (time.time() - start_time) * 1000  # ms
            metrics = self._calculate_execution_metrics(order, execution_result, market_data)
            metrics.execution_time_ms = execution_time
            self.execution_metrics[order_id] = metrics

            # Update order status
            order.status = OrderStatus.FILLED
            order.filled_quantity = execution_result.get('total_executed_quantity', 0)
            order.average_fill_price = execution_result.get('average_price', 0)
            order.updated_at = datetime.now()

            # Audit: Log successful execution
            audit_logger.log_trade_execution(
                symbol=order.symbol,
                side=order.side.value,
                quantity=order.filled_quantity,
                price=order.average_fill_price,
                order_type=order.order_type.value,
                strategy=order.execution_strategy,
                user_id="system",
                session_id="trading_session"
            )

            print(f"[EXECUTION] Order {order_id} completed successfully")
            print(f"[EXECUTION] Executed: {order.filled_quantity:.4f} @ ${order.average_fill_price:.2f}")

        except Exception as e:
            # Audit: Log execution failure
            audit_logger.log_error(
                error_message=str(e),
                error_type=type(e).__name__,
                component="trade_execution",
                user_id="system",
                session_id="trading_session"
            )

            print(f"[EXECUTION] Error executing order {order_id}: {e}")
            order.status = OrderStatus.REJECTED
            execution_result = {'error': str(e), 'status': 'failed'}

        # Store in history
        self.order_history.append({
            'order': asdict(order),
            'execution_result': execution_result,
            'timestamp': datetime.now().isoformat()
        })

        return execution_result

    async def _execute_standard_order(self, order: Order, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a standard market or limit order"""
        # Get current market price
        market_price = market_data.get('price', 45000)

        # Apply slippage protection
        max_slippage = self.slippage_protection.calculate_dynamic_slippage_limit(
            order.symbol, order.quantity, market_data
        )

        # Calculate execution price with slippage
        slippage_factor = random.uniform(-max_slippage/100, max_slippage/100)
        execution_price = market_price * (1 + slippage_factor)

        # Validate slippage
        is_valid, slippage_percent = self.slippage_protection.validate_slippage(
            order, execution_price, market_price
        )

        if not is_valid:
            # Audit: Log slippage protection trigger
            audit_logger.log_error(
                error_message=f"Slippage protection triggered: {slippage_percent:.2f}% > {max_slippage:.2f}%",
                error_type="SlippageProtectionError",
                component="slippage_protection",
                user_id="system",
                session_id="trading_session"
            )
            raise Exception(f"Slippage protection triggered: {slippage_percent:.2f}% > {max_slippage:.2f}%")

        # Simulate execution
        fill_rate = random.uniform(0.95, 1.0)  # 95-100% fill rate
        executed_quantity = order.quantity * fill_rate

        execution_result = {
            'order_id': order.order_id,
            'executed_quantity': executed_quantity,
            'average_price': execution_price,
            'total_executed_value': executed_quantity * execution_price,
            'slippage_percent': slippage_percent,
            'fill_rate': fill_rate,
            'exchange': order.exchange,
            'execution_time_ms': random.uniform(50, 200)
        }

        # Audit: Log standard order execution details
        audit_logger.log_trade_execution(
            symbol=order.symbol,
            side=order.side.value,
            quantity=executed_quantity,
            price=execution_price,
            order_type="standard",
            strategy="market",
            user_id="system",
            session_id="trading_session"
        )

        return execution_result

    def _calculate_execution_metrics(self, order: Order, execution_result: Dict,
                                   market_data: Dict) -> ExecutionMetrics:
        """Calculate execution quality metrics"""
        metrics = ExecutionMetrics(order_id=order.order_id)

        if 'average_price' in execution_result:
            market_price = market_data.get('price', execution_result['average_price'])
            executed_price = execution_result['average_price']

            # Price improvement (positive = better than market)
            if order.side == OrderSide.BUY:
                metrics.price_improvement = (market_price - executed_price) / market_price * 100
            else:
                metrics.price_improvement = (executed_price - market_price) / market_price * 100

        if 'slippage_percent' in execution_result:
            metrics.total_slippage = execution_result['slippage_percent']

        if 'fill_rate' in execution_result:
            metrics.fill_rate = execution_result['fill_rate']

        return metrics

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if not self.order_history:
            return {"message": "No orders executed yet"}

        total_orders = len(self.order_history)
        successful_orders = sum(1 for h in self.order_history
                              if h['execution_result'].get('status') != 'failed')

        total_value = sum(h['execution_result'].get('total_executed_value', 0)
                         for h in self.order_history if h['execution_result'].get('status') != 'failed')

        avg_slippage = np.mean([h['execution_result'].get('slippage_percent', 0)
                               for h in self.order_history if h['execution_result'].get('slippage_percent', 0) > 0])

        stats = {
            "total_orders": total_orders,
            "successful_orders": successful_orders,
            "success_rate": successful_orders / total_orders if total_orders > 0 else 0,
            "total_value_executed": total_value,
            "average_slippage_percent": avg_slippage if not np.isnan(avg_slippage) else 0,
            "orders_by_type": self._get_orders_by_type(),
            "orders_by_exchange": self._get_orders_by_exchange()
        }

        # Audit: Log performance metrics
        audit_logger.log_performance_metric(
            metric_name="execution_success_rate",
            value=stats["success_rate"],
            component="trade_execution",
            user_id="system",
            session_id="trading_session",
            metadata={
                'total_orders': total_orders,
                'successful_orders': successful_orders,
                'total_value_executed': total_value,
                'average_slippage': stats["average_slippage_percent"]
            }
        )

        return stats

    def _get_orders_by_type(self) -> Dict[str, int]:
        """Get order count by type"""
        type_counts = {}
        for history in self.order_history:
            order_type = history['order']['order_type']
            type_counts[order_type] = type_counts.get(order_type, 0) + 1
        return type_counts

    def _get_orders_by_exchange(self) -> Dict[str, int]:
        """Get order count by exchange"""
        exchange_counts = {}
        for history in self.order_history:
            exchange = history['order'].get('exchange', 'unknown')
            exchange_counts[exchange] = exchange_counts.get(exchange, 0) + 1
        return exchange_counts

# Global instance
trade_execution_engine = AdvancedTradeExecution()