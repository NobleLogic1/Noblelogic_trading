"""
Real-Time Data Fetching Engine for NobleLogic Trading System

Features:
- WebSocket connections for real-time market data
- Data quality validation and anomaly detection
- Multi-exchange data aggregation and synchronization
- Automatic failover and connection management
- Data caching and optimization
"""

import asyncio
import websockets
import json
import time
import threading
import queue
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
import numpy as np
import hashlib
import hmac
import base64
import requests
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Exchange(Enum):
    BINANCE_US = "binance_us"
    COINBASE_PRO = "coinbase_pro"
    KRAKEN = "kraken"
    KUCOIN = "kucoin"

class DataQuality(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"

@dataclass
class MarketData:
    """Standardized market data structure"""
    symbol: str
    exchange: str
    timestamp: float
    price: float
    volume: float
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    bid_volume: Optional[float] = None
    ask_volume: Optional[float] = None
    trade_id: Optional[str] = None
    data_quality: DataQuality = DataQuality.GOOD
    latency_ms: Optional[float] = None
    received_at: Optional[float] = None

@dataclass
class DataQualityMetrics:
    """Metrics for data quality assessment"""
    exchange: str
    symbol: str
    total_messages: int = 0
    valid_messages: int = 0
    invalid_messages: int = 0
    duplicate_messages: int = 0
    stale_messages: int = 0
    avg_latency_ms: float = 0.0
    last_update: Optional[float] = None
    data_freshness_score: float = 1.0  # 1.0 = perfectly fresh, 0.0 = very stale

class WebSocketConnection:
    """Manages WebSocket connection for a single exchange"""

    def __init__(self, exchange: Exchange, api_key: str = None, api_secret: str = None):
        self.exchange = exchange
        self.api_key = api_key
        self.api_secret = api_secret
        self.ws_url = self._get_ws_url()
        self.websocket = None
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 1.0
        self.heartbeat_interval = 30.0
        self.last_heartbeat = time.time()
        self.subscribed_symbols = set()
        self.message_queue = asyncio.Queue()
        self.callbacks: Dict[str, Callable] = {}

    def _get_ws_url(self) -> str:
        """Get WebSocket URL for the exchange"""
        urls = {
            Exchange.BINANCE_US: "wss://stream.binance.us:9443/ws/",
            Exchange.COINBASE_PRO: "wss://ws-feed.pro.coinbase.com",
            Exchange.KRAKEN: "wss://ws.kraken.com",
            Exchange.KUCOIN: "wss://ws-api.kucoin.com"
        }
        return urls.get(self.exchange, "")

    async def connect(self) -> bool:
        """Establish WebSocket connection"""
        try:
            logger.info(f"Connecting to {self.exchange.value} WebSocket...")

            # Prepare connection parameters
            connect_kwargs = {
                "ping_interval": 20.0,
                "ping_timeout": 10.0
            }

            # Add authentication headers if available and required
            auth_headers = self._get_auth_headers()
            if auth_headers:
                # For websockets library, we need to handle auth differently
                # Some exchanges require auth in the initial message instead
                pass

            self.websocket = await websockets.connect(
                self.ws_url,
                **connect_kwargs
            )
            self.is_connected = True
            self.reconnect_attempts = 0
            logger.info(f"✅ Connected to {self.exchange.value}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to {self.exchange.value}: {e}")
            self.is_connected = False
            return False

    async def disconnect(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        self.is_connected = False
        logger.info(f"Disconnected from {self.exchange.value}")

    async def subscribe(self, symbols: List[str], channels: List[str] = None):
        """Subscribe to market data streams"""
        if not self.is_connected:
            return False

        if channels is None:
            channels = ["ticker", "trades"]

        subscription_message = self._create_subscription_message(symbols, channels)

        try:
            await self.websocket.send(json.dumps(subscription_message))
            self.subscribed_symbols.update(symbols)
            logger.info(f"Subscribed to {symbols} on {self.exchange.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe on {self.exchange.value}: {e}")
            return False

    async def unsubscribe(self, symbols: List[str]):
        """Unsubscribe from market data streams"""
        if not self.is_connected:
            return False

        unsubscription_message = self._create_unsubscription_message(symbols)

        try:
            await self.websocket.send(json.dumps(unsubscription_message))
            self.subscribed_symbols.difference_update(symbols)
            logger.info(f"Unsubscribed from {symbols} on {self.exchange.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to unsubscribe on {self.exchange.value}: {e}")
            return False

    def _create_subscription_message(self, symbols: List[str], channels: List[str]) -> Dict:
        """Create subscription message for the exchange"""
        if self.exchange == Exchange.BINANCE_US:
            streams = []
            for symbol in symbols:
                for channel in channels:
                    if channel == "ticker":
                        streams.append(f"{symbol.lower()}@ticker")
                    elif channel == "trades":
                        streams.append(f"{symbol.lower()}@trade")
            return {"method": "SUBSCRIBE", "params": streams, "id": 1}

        elif self.exchange == Exchange.COINBASE_PRO:
            return {
                "type": "subscribe",
                "product_ids": symbols,
                "channels": channels
            }

        elif self.exchange == Exchange.KRAKEN:
            pairs = [symbol.replace("/", "").lower() for symbol in symbols]

            # Kraken requires authentication for private feeds, but ticker is public
            subscription = {"name": "ticker"}

            # Add authentication if API keys are provided
            if self.api_key and self.api_secret:
                timestamp = str(int(time.time() * 1000))
                message = timestamp + "websocket_login"
                signature = hmac.new(
                    base64.b64decode(self.api_secret),
                    message.encode(),
                    hashlib.sha512
                ).digest()
                signature_b64 = base64.b64encode(signature).decode()

                return {
                    "event": "subscribe",
                    "pair": pairs,
                    "subscription": subscription,
                    "reqid": 1
                }
            else:
                # Public subscription without auth
                return {
                    "event": "subscribe",
                    "pair": pairs,
                    "subscription": subscription
                }

        return {}

    def _create_unsubscription_message(self, symbols: List[str]) -> Dict:
        """Create unsubscription message for the exchange"""
        if self.exchange == Exchange.BINANCE_US:
            streams = [f"{symbol.lower()}@ticker" for symbol in symbols]
            return {"method": "UNSUBSCRIBE", "params": streams, "id": 1}

        elif self.exchange == Exchange.COINBASE_PRO:
            return {
                "type": "unsubscribe",
                "product_ids": symbols,
                "channels": ["ticker", "matches"]
            }

        return {}

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers if required"""
        if not self.api_key or not self.api_secret:
            return {}

        # Implement exchange-specific authentication
        if self.exchange == Exchange.KRAKEN:
            # Kraken WebSocket authentication - send in subscription message instead
            return {}

        return {}

    async def listen(self):
        """Listen for incoming messages"""
        while self.is_connected and self.websocket:
            try:
                message = await self.websocket.recv()
                data = json.loads(message)

                # Process the message
                processed_data = self._process_message(data)
                if processed_data:
                    await self.message_queue.put(processed_data)

                # Check for callbacks
                if 'type' in data and data['type'] in self.callbacks:
                    await self.callbacks[data['type']](data)

            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"Connection closed for {self.exchange.value}")
                self.is_connected = False
                break
            except Exception as e:
                logger.error(f"Error processing message from {self.exchange.value}: {e}")

    def _process_message(self, data: Dict) -> Optional[MarketData]:
        """Process incoming WebSocket message into standardized format"""
        try:
            if self.exchange == Exchange.BINANCE_US:
                return self._process_binance_message(data)
            elif self.exchange == Exchange.COINBASE_PRO:
                return self._process_coinbase_message(data)
            elif self.exchange == Exchange.KRAKEN:
                return self._process_kraken_message(data)
            else:
                return None
        except Exception as e:
            logger.error(f"Error processing {self.exchange.value} message: {e}")
            return None

    def _process_binance_message(self, data: Dict) -> Optional[MarketData]:
        """Process Binance WebSocket message"""
        if 'stream' in data and data['data']:
            stream_data = data['data']

            if stream_data.get('e') == '24hrTicker':
                # 24hr ticker update
                return MarketData(
                    symbol=stream_data['s'],
                    exchange=self.exchange.value,
                    timestamp=stream_data['E'] / 1000,  # Convert to seconds
                    price=float(stream_data['c']),  # Last price
                    volume=float(stream_data['v']),  # Volume
                    bid_price=float(stream_data.get('b', 0)),
                    ask_price=float(stream_data.get('a', 0)),
                    received_at=time.time()
                )
            elif stream_data.get('e') == 'trade':
                # Individual trade
                return MarketData(
                    symbol=stream_data['s'],
                    exchange=self.exchange.value,
                    timestamp=stream_data['T'] / 1000,
                    price=float(stream_data['p']),
                    volume=float(stream_data['q']),
                    trade_id=str(stream_data['t']),
                    received_at=time.time()
                )

        return None

    def _process_coinbase_message(self, data: Dict) -> Optional[MarketData]:
        """Process Coinbase Pro WebSocket message"""
        if data.get('type') == 'ticker':
            return MarketData(
                symbol=data['product_id'],
                exchange=self.exchange.value,
                timestamp=time.time(),
                price=float(data['price']),
                volume=float(data.get('volume_24h', 0)),
                bid_price=float(data.get('best_bid', 0)),
                ask_price=float(data.get('best_ask', 0)),
                received_at=time.time()
            )
        elif data.get('type') == 'match':
            return MarketData(
                symbol=data['product_id'],
                exchange=self.exchange.value,
                timestamp=time.time(),
                price=float(data['price']),
                volume=float(data['size']),
                trade_id=data['trade_id'],
                received_at=time.time()
            )

        return None

    def _process_kraken_message(self, data: Dict) -> Optional[MarketData]:
        """Process Kraken WebSocket message"""
        if isinstance(data, list) and len(data) >= 4:
            channel_name = data[2]
            if channel_name == 'ticker':
                ticker_data = data[1]
                symbol = data[3] if len(data) > 3 else 'unknown'

                return MarketData(
                    symbol=symbol,
                    exchange=self.exchange.value,
                    timestamp=time.time(),
                    price=float(ticker_data['c'][0]),  # Close price
                    volume=float(ticker_data['v'][1]),  # Volume
                    bid_price=float(ticker_data['b'][0]),
                    ask_price=float(ticker_data['a'][0]),
                    received_at=time.time()
                )

        return None

class DataQualityValidator:
    """Validates data quality and detects anomalies"""

    def __init__(self):
        self.metrics: Dict[str, DataQualityMetrics] = {}
        self.price_history: Dict[str, List[Tuple[float, float]]] = {}  # symbol -> [(timestamp, price)]
        self.max_history_size = 1000
        self.stale_threshold_seconds = 30.0
        self.anomaly_threshold_std = 3.0  # 3 standard deviations

    def validate_data(self, data: MarketData) -> Tuple[bool, DataQuality, str]:
        """
        Validate market data quality

        Returns:
            Tuple of (is_valid, quality_score, reason)
        """
        symbol_key = f"{data.exchange}:{data.symbol}"

        # Initialize metrics if needed
        if symbol_key not in self.metrics:
            self.metrics[symbol_key] = DataQualityMetrics(data.exchange, data.symbol)

        metrics = self.metrics[symbol_key]
        metrics.total_messages += 1

        # Check for basic validity
        if not self._is_basic_valid(data):
            metrics.invalid_messages += 1
            return False, DataQuality.INVALID, "Basic validation failed"

        # Check for duplicates
        if self._is_duplicate(data):
            metrics.duplicate_messages += 1
            return False, DataQuality.POOR, "Duplicate message"

        # Check for staleness
        if self._is_stale(data):
            metrics.stale_messages += 1
            return False, DataQuality.POOR, "Stale data"

        # Check for anomalies
        if self._is_anomalous(data):
            return False, DataQuality.POOR, "Price anomaly detected"

        # Update metrics
        metrics.valid_messages += 1
        metrics.last_update = data.timestamp
        self._update_price_history(data)

        # Calculate data freshness
        metrics.data_freshness_score = self._calculate_freshness_score(data)

        # Determine quality score
        quality = self._calculate_quality_score(metrics)

        return True, quality, "Valid data"

    def _is_basic_valid(self, data: MarketData) -> bool:
        """Check basic data validity"""
        if data.price <= 0 or data.volume < 0:
            return False
        if data.bid_price and data.ask_price and data.bid_price >= data.ask_price:
            return False
        if data.timestamp <= 0 or data.timestamp > time.time() + 60:  # Allow 1 minute future
            return False
        return True

    def _is_duplicate(self, data: MarketData) -> bool:
        """Check for duplicate messages"""
        # Simple duplicate detection based on trade ID
        if data.trade_id:
            # In a real implementation, you'd maintain a set of recent trade IDs
            pass
        return False

    def _is_stale(self, data: MarketData) -> bool:
        """Check if data is stale"""
        if data.received_at and time.time() - data.received_at > self.stale_threshold_seconds:
            return True
        return False

    def _is_anomalous(self, data: MarketData) -> bool:
        """Detect price anomalies"""
        symbol_key = f"{data.exchange}:{data.symbol}"

        if symbol_key not in self.price_history or len(self.price_history[symbol_key]) < 10:
            return False

        prices = [p for _, p in self.price_history[symbol_key][-50:]]  # Last 50 prices
        if not prices:
            return False

        mean_price = np.mean(prices)
        std_price = np.std(prices)

        if std_price == 0:
            return False

        z_score = abs(data.price - mean_price) / std_price
        return z_score > self.anomaly_threshold_std

    def _update_price_history(self, data: MarketData):
        """Update price history for anomaly detection"""
        symbol_key = f"{data.exchange}:{data.symbol}"

        if symbol_key not in self.price_history:
            self.price_history[symbol_key] = []

        self.price_history[symbol_key].append((data.timestamp, data.price))

        # Limit history size
        if len(self.price_history[symbol_key]) > self.max_history_size:
            self.price_history[symbol_key] = self.price_history[symbol_key][-self.max_history_size:]

    def _calculate_freshness_score(self, data: MarketData) -> float:
        """Calculate data freshness score (0.0 to 1.0)"""
        if not data.received_at:
            return 0.5

        age_seconds = time.time() - data.received_at
        if age_seconds <= 1.0:
            return 1.0
        elif age_seconds <= 5.0:
            return 0.8
        elif age_seconds <= 10.0:
            return 0.6
        elif age_seconds <= 30.0:
            return 0.4
        else:
            return 0.2

    def _calculate_quality_score(self, metrics: DataQualityMetrics) -> DataQuality:
        """Calculate overall data quality score"""
        if metrics.total_messages == 0:
            return DataQuality.FAIR

        validity_rate = metrics.valid_messages / metrics.total_messages
        freshness_score = metrics.data_freshness_score

        combined_score = (validity_rate + freshness_score) / 2

        if combined_score >= 0.95:
            return DataQuality.EXCELLENT
        elif combined_score >= 0.85:
            return DataQuality.GOOD
        elif combined_score >= 0.70:
            return DataQuality.FAIR
        else:
            return DataQuality.POOR

    def get_quality_report(self, symbol: str = None, exchange: str = None) -> Dict[str, Any]:
        """Get data quality report"""
        if symbol and exchange:
            key = f"{exchange}:{symbol}"
            return asdict(self.metrics.get(key, DataQualityMetrics(exchange, symbol)))
        elif symbol:
            # Return metrics for all exchanges for this symbol
            return {k: asdict(v) for k, v in self.metrics.items() if k.endswith(f":{symbol}")}
        elif exchange:
            # Return metrics for all symbols on this exchange
            return {k: asdict(v) for k, v in self.metrics.items() if k.startswith(f"{exchange}:")}
        else:
            # Return all metrics
            return {k: asdict(v) for k, v in self.metrics.items()}

class MultiExchangeAggregator:
    """Aggregates and synchronizes data from multiple exchanges"""

    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.data_validator = DataQualityValidator()
        self.aggregated_data: Dict[str, MarketData] = {}  # symbol -> best available data
        self.exchange_data: Dict[str, Dict[str, MarketData]] = {}  # exchange -> symbol -> data
        self.subscribed_symbols: set = set()
        self.data_callbacks: List[Callable] = []
        self.is_running = False

    def add_exchange(self, exchange: Exchange, api_key: str = None, api_secret: str = None):
        """Add an exchange connection"""
        connection = WebSocketConnection(exchange, api_key, api_secret)
        self.connections[exchange.value] = connection
        self.exchange_data[exchange.value] = {}
        logger.info(f"Added {exchange.value} exchange")

    def remove_exchange(self, exchange: Exchange):
        """Remove an exchange connection"""
        if exchange.value in self.connections:
            asyncio.create_task(self.connections[exchange.value].disconnect())
            del self.connections[exchange.value]
            del self.exchange_data[exchange.value]
            logger.info(f"Removed {exchange.value} exchange")

    async def start(self):
        """Start all exchange connections"""
        self.is_running = True

        # Start all connections
        connection_tasks = []
        for connection in self.connections.values():
            task = asyncio.create_task(self._manage_connection(connection))
            connection_tasks.append(task)

        # Start data processing
        processing_task = asyncio.create_task(self._process_data())

        # Wait for all tasks
        await asyncio.gather(*connection_tasks, processing_task)

    async def stop(self):
        """Stop all exchange connections"""
        self.is_running = False

        # Disconnect all connections
        disconnect_tasks = []
        for connection in self.connections.values():
            disconnect_tasks.append(connection.disconnect())

        await asyncio.gather(*disconnect_tasks)

    async def subscribe_symbols(self, symbols: List[str]):
        """Subscribe to symbols across all exchanges"""
        self.subscribed_symbols.update(symbols)

        subscribe_tasks = []
        for connection in self.connections.values():
            # Filter symbols that this exchange supports
            supported_symbols = self._filter_supported_symbols(connection.exchange, symbols)
            if supported_symbols:
                subscribe_tasks.append(connection.subscribe(supported_symbols))

        await asyncio.gather(*subscribe_tasks)

    def _filter_supported_symbols(self, exchange: Exchange, symbols: List[str]) -> List[str]:
        """Filter symbols that are supported by the exchange"""
        # In a real implementation, you'd check against exchange's supported symbols
        # For now, return all symbols
        return symbols

    async def _manage_connection(self, connection: WebSocketConnection):
        """Manage a single exchange connection with reconnection logic"""
        while self.is_running:
            try:
                # Connect
                if not await connection.connect():
                    logger.warning(f"Failed to connect to {connection.exchange.value}, will retry...")
                    await asyncio.sleep(connection.reconnect_delay)
                    connection.reconnect_attempts += 1
                    if connection.reconnect_attempts >= connection.max_reconnect_attempts:
                        logger.error(f"Max reconnection attempts reached for {connection.exchange.value}")
                        # Don't break - just keep the connection object for potential future reconnection
                        await asyncio.sleep(300.0)  # Wait 5 minutes before trying again
                        connection.reconnect_attempts = 0
                        continue
                    continue

                # Subscribe to symbols
                if self.subscribed_symbols:
                    supported_symbols = self._filter_supported_symbols(
                        connection.exchange, list(self.subscribed_symbols)
                    )
                    if supported_symbols:
                        await connection.subscribe(supported_symbols)

                # Listen for messages
                await connection.listen()

            except Exception as e:
                logger.error(f"Connection error for {connection.exchange.value}: {e}")
                connection.is_connected = False

            # Reconnection delay
            await asyncio.sleep(connection.reconnect_delay)
            connection.reconnect_delay = min(connection.reconnect_delay * 2, 60.0)  # Exponential backoff

    async def _process_data(self):
        """Process incoming data from all exchanges"""
        while self.is_running:
            try:
                # Collect data from all connections
                data_items = []

                for connection in self.connections.values():
                    try:
                        # Non-blocking get with timeout
                        data = await asyncio.wait_for(connection.message_queue.get(), timeout=0.1)
                        data_items.append(data)
                    except asyncio.TimeoutError:
                        continue

                # Process each data item
                for data in data_items:
                    await self._process_market_data(data)

                # Small delay to prevent busy waiting
                await asyncio.sleep(0.01)

            except Exception as e:
                logger.error(f"Error in data processing: {e}")
                await asyncio.sleep(1.0)

    async def _process_market_data(self, data: MarketData):
        """Process individual market data item"""
        # Validate data quality
        is_valid, quality, reason = self.data_validator.validate_data(data)
        data.data_quality = quality

        if not is_valid:
            logger.warning(f"Invalid data from {data.exchange}:{data.symbol}: {reason}")
            return

        # Store by exchange
        exchange_key = data.exchange
        symbol_key = data.symbol

        if exchange_key not in self.exchange_data:
            self.exchange_data[exchange_key] = {}
        self.exchange_data[exchange_key][symbol_key] = data

        # Update aggregated data (use data from best quality exchange)
        await self._update_aggregated_data(symbol_key)

        # Notify callbacks
        for callback in self.data_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Error in data callback: {e}")

    async def _update_aggregated_data(self, symbol: str):
        """Update aggregated data for a symbol using best available data"""
        available_data = []

        # Collect data from all exchanges for this symbol
        for exchange_data in self.exchange_data.values():
            if symbol in exchange_data:
                available_data.append(exchange_data[symbol])

        if not available_data:
            return

        # Select best data based on quality and recency
        best_data = self._select_best_data(available_data)
        self.aggregated_data[symbol] = best_data

    def _select_best_data(self, data_list: List[MarketData]) -> MarketData:
        """Select the best data from multiple sources"""
        if len(data_list) == 1:
            return data_list[0]

        # Score each data item
        scored_data = []
        for data in data_list:
            score = 0

            # Quality score
            quality_scores = {
                DataQuality.EXCELLENT: 4,
                DataQuality.GOOD: 3,
                DataQuality.FAIR: 2,
                DataQuality.POOR: 1,
                DataQuality.INVALID: 0
            }
            score += quality_scores.get(data.data_quality, 0)

            # Recency score (prefer fresher data)
            if data.received_at:
                age_seconds = time.time() - data.received_at
                if age_seconds <= 1.0:
                    score += 3
                elif age_seconds <= 5.0:
                    score += 2
                elif age_seconds <= 10.0:
                    score += 1

            scored_data.append((score, data))

        # Return data with highest score
        scored_data.sort(key=lambda x: x[0], reverse=True)
        return scored_data[0][1]

    def add_data_callback(self, callback: Callable):
        """Add a callback for new data"""
        self.data_callbacks.append(callback)

    def get_aggregated_data(self, symbol: str) -> Optional[MarketData]:
        """Get aggregated data for a symbol"""
        data = self.aggregated_data.get(symbol)
        if data:
            return data

        # Fallback: try to get data from any connected exchange
        for exchange_data in self.exchange_data.values():
            if symbol in exchange_data:
                return exchange_data[symbol]

        # Last resort: create synthetic data from REST API
        return self._create_fallback_data(symbol)

    def _create_fallback_data(self, symbol: str) -> Optional[MarketData]:
        """Create fallback market data from REST API when WebSocket fails"""
        try:
            # Try to get price from REST API
            price = self._get_rest_price(symbol)
            if price > 0:
                return MarketData(
                    symbol=symbol,
                    exchange="fallback_rest",
                    timestamp=time.time(),
                    price=price,
                    volume=0.0,  # Volume not available from basic REST
                    data_quality=DataQuality.FAIR,  # Lower quality for fallback data
                    received_at=time.time()
                )
        except Exception as e:
            logger.warning(f"Failed to create fallback data for {symbol}: {e}")

        return None

    def get_exchange_data(self, symbol: str, exchange: str) -> Optional[MarketData]:
        """Get data for a specific symbol and exchange"""
        if exchange in self.exchange_data and symbol in self.exchange_data[exchange]:
            return self.exchange_data[exchange][symbol]
        return None

    def get_all_data(self) -> Dict[str, MarketData]:
        """Get all aggregated data"""
        return self.aggregated_data.copy()

    def get_quality_report(self) -> Dict[str, Any]:
        """Get data quality report"""
        return self.data_validator.get_quality_report()

    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Get current prices for multiple symbols (compatibility method)

        Returns aggregated prices from real-time data
        """
        prices = {}
        for symbol in symbols:
            data = self.get_aggregated_data(symbol)
            if data:
                prices[symbol] = data.price
            else:
                # Fallback to REST API if no real-time data available
                prices[symbol] = self._get_rest_price(symbol)
        return prices

    def get_24h_stats(self, symbol: str) -> Dict[str, float]:
        """
        Get 24-hour statistics for a symbol (compatibility method)

        Returns basic stats from real-time data
        """
        data = self.get_aggregated_data(symbol)
        if data:
            # Return basic stats (in a real implementation, you'd aggregate 24h data)
            return {
                'price': data.price,
                'volume': data.volume,
                'bid_price': data.bid_price or data.price,
                'ask_price': data.ask_price or data.price,
                'exchange': data.exchange
            }
        else:
            # Fallback to REST API
            return self._get_rest_24h_stats(symbol)

    def get_kline_data(self, symbol: str, timeframe: str, limit: int = 100) -> List[List]:
        """
        Get kline/candlestick data (compatibility method)

        Note: Real-time data fetcher focuses on current data.
        For historical klines, consider using a separate historical data fetcher.
        """
        # This is a simplified implementation
        # In production, you'd want a proper historical data source
        logger.warning(f"Kline data requested for {symbol} - using simplified implementation")

        data = self.get_aggregated_data(symbol)
        if data:
            # Return a single "candle" with current data
            current_time = int(time.time() * 1000)
            return [[
                current_time,  # Open time
                data.price,    # Open
                data.price,    # High
                data.price,    # Low
                data.price,    # Close
                data.volume,   # Volume
                current_time,  # Close time
                0,             # Quote asset volume
                1,             # Number of trades
                0,             # Taker buy base asset volume
                0,             # Taker buy quote asset volume
                0              # Unused field
            ]]
        else:
            return []

    def _get_rest_price(self, symbol: str) -> float:
        """Fallback REST API price fetch"""
        try:
            # Simple fallback using requests
            import requests
            binance_symbol = symbol.replace('/', '')

            url = f"https://api.binance.us/api/v3/ticker/price"
            params = {"symbol": binance_symbol}

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()
            return float(data['price'])

        except Exception as e:
            logger.error(f"REST fallback failed for {symbol}: {e}")
            return 0.0

    def _get_rest_24h_stats(self, symbol: str) -> Dict[str, float]:
        """Fallback REST API 24h stats fetch"""
        try:
            import requests
            binance_symbol = symbol.replace('/', '')

            url = f"https://api.binance.us/api/v3/ticker/24hr"
            params = {"symbol": binance_symbol}

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()
            return {
                'price': float(data['lastPrice']),
                'volume': float(data['volume']),
                'bid_price': float(data.get('bidPrice', data['lastPrice'])),
                'ask_price': float(data.get('askPrice', data['lastPrice'])),
                'exchange': 'binance_us_fallback'
            }

        except Exception as e:
            logger.error(f"REST 24h stats fallback failed for {symbol}: {e}")
            return {
                'price': 0.0,
                'volume': 0.0,
                'bid_price': 0.0,
                'ask_price': 0.0,
                'exchange': 'error'
            }

# Global instance
data_aggregator = MultiExchangeAggregator()

# Initialize with exchanges that don't require API keys
# Users can add authenticated exchanges as needed
data_aggregator.add_exchange(Exchange.BINANCE_US)  # Public API, no keys required
# data_aggregator.add_exchange(Exchange.COINBASE_PRO)  # Requires API keys
# data_aggregator.add_exchange(Exchange.KRAKEN)  # Optional, requires API keys