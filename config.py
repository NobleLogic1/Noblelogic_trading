"""
Configuration as Code for NobleLogic Trading System
Centralized configuration management using Python dataclasses
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path


def load_api_keys_from_file(file_path: str = "config/secure/APIkeys.txt") -> Dict[str, str]:
    """
    Securely load API keys from a protected file location.

    Args:
        file_path: Path to the API keys file (default: config/secure/APIkeys.txt)

    Returns:
        Dictionary containing API key information organized by exchange
    """
    keys = {}
    current_section = None

    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Check for section headers (lines ending with ':')
                if line.endswith(':') and not line.startswith(' '):
                    current_section = line[:-1].strip()  # Remove the colon
                    keys[current_section] = {}
                # Check for key-value pairs (contain ':' and are indented or follow a section)
                elif ':' in line and current_section:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key, value = parts
                        keys[current_section][key.strip()] = value.strip()

        return keys

    except FileNotFoundError:
        print(f"Warning: API keys file not found at {file_path}")
        return {}
    except Exception as e:
        print(f"Error loading API keys: {e}")
        return {}


@dataclass
class SecurityConfig:
    """Security-related configuration"""
    encryption_key: str = field(default_factory=lambda: os.getenv('ENCRYPTION_KEY', ''))
    api_rate_limit: int = field(default_factory=lambda: int(os.getenv('API_RATE_LIMIT', '10')))
    max_requests_per_minute: int = field(default_factory=lambda: int(os.getenv('MAX_REQUEST_PER_MINUTE', '30')))
    security_level: str = field(default_factory=lambda: os.getenv('SECURITY_LEVEL', 'high'))
    enable_encryption: bool = True
    session_timeout: int = 3600  # 1 hour


@dataclass
class APIConfig:
    """External API configuration"""
    binance_us_api_key: str = field(default_factory=lambda: os.getenv('BINANCE_US_API_KEY', ''))
    binance_us_secret_key: str = field(default_factory=lambda: os.getenv('BINANCE_US_SECRET_KEY', ''))
    binance_us_ip_whitelist: str = field(default_factory=lambda: os.getenv('BINANCE_US_IP_WHITELIST', ''))
    binance_us_base_url: str = "https://api.binance.us"
    binance_us_testnet: bool = False

    # Rate limiting
    api_call_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class TradingConfig:
    """Trading parameters and risk management"""
    initial_capital: float = field(default_factory=lambda: float(os.getenv('INITIAL_CAPITAL', '100')))
    target_daily_profit: float = field(default_factory=lambda: float(os.getenv('TARGET_DAILY_PROFIT', '500')))
    max_daily_loss: float = field(default_factory=lambda: float(os.getenv('MAX_DAILY_LOSS', '25')))
    risk_per_trade: float = field(default_factory=lambda: float(os.getenv('RISK_PER_TRADE', '0.02')))

    # Position sizing
    max_position_size: float = 0.1  # 10% of capital
    min_position_size: float = 0.001  # 0.1% of capital

    # Trading hours (UTC)
    trading_start_hour: int = 14  # 2 PM UTC (9 AM EST)
    trading_end_hour: int = 21    # 9 PM UTC (4 PM EST)

    # Symbols to trade
    enabled_symbols: List[str] = field(default_factory=lambda: ['BTCUSDT', 'ETHUSDT', 'ADAUSDT'])

    # Risk management
    max_open_positions: int = 3
    max_consecutive_losses: int = 3
    profit_taking_threshold: float = 0.05  # 5% profit target
    stop_loss_threshold: float = 0.02     # 2% stop loss


@dataclass
class MLConfig:
    """Machine Learning configuration"""
    model_version: str = "v1.0"
    gpu_acceleration: bool = True
    mixed_precision: bool = False
    batch_size: int = 32
    learning_rate: float = 0.001
    epochs: int = 100

    # Model paths
    model_save_path: str = "models"
    checkpoint_frequency: int = 10

    # Feature engineering
    sequence_length: int = 60  # 60 minutes of data
    prediction_horizon: int = 5  # 5-minute predictions

    # Performance monitoring
    enable_performance_tracking: bool = True
    log_predictions: bool = True


@dataclass
class SystemConfig:
    """System and infrastructure configuration"""
    environment: str = field(default_factory=lambda: os.getenv('ENVIRONMENT', 'development'))
    debug_mode: bool = field(default_factory=lambda: os.getenv('DEBUG', 'false').lower() == 'true')
    log_level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))

    # Server configuration
    host: str = field(default_factory=lambda: os.getenv('HOST', '0.0.0.0'))
    port: int = field(default_factory=lambda: int(os.getenv('PORT', '5000')))
    workers: int = field(default_factory=lambda: int(os.getenv('WORKERS', '4')))

    # Database configuration
    database_url: str = field(default_factory=lambda: os.getenv('DATABASE_URL', 'sqlite:///trading.db'))

    # File paths
    data_directory: str = "data"
    logs_directory: str = "logs"
    models_directory: str = "models"

    # Performance
    enable_caching: bool = True
    cache_ttl: int = 300  # 5 minutes


@dataclass
class AppConfig:
    """Main application configuration"""
    security: SecurityConfig = field(default_factory=SecurityConfig)
    api: APIConfig = field(default_factory=APIConfig)
    trading: TradingConfig = field(default_factory=TradingConfig)
    ml: MLConfig = field(default_factory=MLConfig)
    system: SystemConfig = field(default_factory=SystemConfig)

    # Application metadata
    version: str = "1.0.0"
    name: str = "NobleLogic Trading System"

    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate_configuration()

    def _validate_configuration(self):
        """Validate configuration values"""
        if self.trading.risk_per_trade > 0.1:
            raise ValueError("Risk per trade cannot exceed 10%")

        if self.trading.max_daily_loss > self.trading.initial_capital * 0.5:
            raise ValueError("Max daily loss cannot exceed 50% of initial capital")

        if not self.api.binance_us_api_key and self.system.environment == 'production':
            raise ValueError("Binance API key required for production environment")

    @classmethod
    def from_env_file(cls, env_file: str = ".env") -> 'AppConfig':
        """Load configuration from environment file"""
        if os.path.exists(env_file):
            from dotenv import load_dotenv
            load_dotenv(env_file)
        return cls()

    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'AppConfig':
        """Create configuration from dictionary"""
        # This would require more complex parsing for nested dataclasses
        # For now, return default config
        return cls()

    def to_dict(self) -> Dict:
        """Convert configuration to dictionary"""
        # This would require custom serialization for dataclasses
        return {}

    def save_to_env_file(self, env_file: str = ".env"):
        """Save configuration to environment file"""
        env_content = f"""# NobleLogic Trading System Configuration
# Generated on {__import__('datetime').datetime.now().isoformat()}

# Security Configuration
ENCRYPTION_KEY={self.security.encryption_key}
API_RATE_LIMIT={self.security.api_rate_limit}
MAX_REQUEST_PER_MINUTE={self.security.max_requests_per_minute}
SECURITY_LEVEL={self.security.security_level}

# API Configuration
BINANCE_US_API_KEY={self.api.binance_us_api_key}
BINANCE_US_SECRET_KEY={self.api.binance_us_secret_key}
BINANCE_US_IP_WHITELIST={self.api.binance_us_ip_whitelist}

# Trading Configuration
INITIAL_CAPITAL={self.trading.initial_capital}
TARGET_DAILY_PROFIT={self.trading.target_daily_profit}
MAX_DAILY_LOSS={self.trading.max_daily_loss}
RISK_PER_TRADE={self.trading.risk_per_trade}

# System Configuration
ENVIRONMENT={self.system.environment}
DEBUG={str(self.system.debug_mode).lower()}
LOG_LEVEL={self.system.log_level}
HOST={self.system.host}
PORT={self.system.port}
WORKERS={self.system.workers}
"""
        with open(env_file, 'w') as f:
            f.write(env_content)


# Global configuration instance
config = AppConfig.from_env_file()


def get_config() -> AppConfig:
    """Get the global configuration instance"""
    return config


def reload_config() -> AppConfig:
    """Reload configuration from environment"""
    global config
    config = AppConfig.from_env_file()
    return config