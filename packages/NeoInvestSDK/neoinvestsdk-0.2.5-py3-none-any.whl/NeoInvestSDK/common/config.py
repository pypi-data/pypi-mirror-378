"""
Configuration module for NeoInvestSDK
"""

import sys
from pathlib import Path
from typing import Dict, Optional

from loguru import logger
from pydantic import BaseModel, Field


class LogConfig(BaseModel):
    """Logging configuration"""

    destination: str = Field(default="stdout", description="Log destination")
    level: str = Field(default="INFO", description="Log level")
    format: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        description="Log format",
    )
    rotation: Optional[str] = Field(default="10 MB", description="Log rotation size")
    retention: Optional[str] = Field(default="30 days", description="Log retention period")
    compression: Optional[str] = Field(default="zip", description="Log compression format")
    serialize: bool = Field(default=False, description="Serialize logs to JSON")
    backtrace: bool = Field(default=True, description="Enable backtrace")
    diagnose: bool = Field(default=True, description="Enable diagnose")
    enqueue: bool = Field(default=True, description="Enable enqueue")
    colorize: bool = Field(default=True, description="Colorize console output")
    log_file: Optional[Path] = Field(default=None, description="Log file path")


class APIEndpointsConfig(BaseModel):
    """API endpoints configuration"""

    base_url: str = Field(default="https://neopro-uat.vpbanks.com.vn/neo-api", description="Base URL for API")
    stock_stream_url: str = Field(
        default="wss://stockstream-uat-krx.vpbanks.com.vn/broker",
        description="StockStream WebSocket URL",
    )
    trading_stream_url: str = Field(
        default="wss://neopro-uat.vpbanks.com.vn/trading-stream/realtime",
        description="TradingStream WebSocket URL",
    )
    auth_base_url: str = Field(default="https://external-uat-krx.vpbanks.com.vn", description="Base URL for Authentication service")
    api_public_prefix: str = Field(default="", description="Public API prefix")
    trading_prefix: str = Field(default="/trading", description="Trading API prefix")
    accounts_prefix: str = Field(default="/accounts", description="Accounts API prefix")
    asset_prefix: str = Field(default="/portfolio", description="Asset API prefix")
    market_data_prefix: str = Field(default="/market", description="Market Data API prefix")
    stock_data_prefix: str = Field(default="/stock", description="Stock Data API prefix")


class HttpClientConfig(BaseModel):
    """HTTP client configuration"""

    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    trust_env: bool = Field(default=False, description="Trust environment variables")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")
    proxy: Optional[str] = Field(default=None, description="Proxy URL")
    verify: bool = Field(default=True, description="Verify SSL certificate")
    headers: Dict[str, str] = Field(default_factory=dict, description="Additional headers")


class AuthConfig(BaseModel):
    """Authentication configuration"""

    username: str = Field(default="", description="Username")
    password: str = Field(default="", description="Password")
    pin: str = Field(default="", description="PIN")


class SDKConfig(BaseModel):
    """Main SDK configuration"""

    api_endpoints: APIEndpointsConfig = Field(default_factory=APIEndpointsConfig)

    http_client_config: HttpClientConfig = Field(default_factory=HttpClientConfig)

    auth_config: AuthConfig = Field(default_factory=AuthConfig)

    schema_cache_dir: Path = Field(default=Path(".neopro_schemas"), description="Directory to cache schemas")

    # Logging Configuration
    log_config: LogConfig = Field(default_factory=LogConfig)

    def setup_logging(self) -> None:
        """Setup logging configuration"""
        # Remove default logger
        logger.remove()
        sink: object

        logger.info(f"Setting up logging with config: {self.log_config}")

        if self.log_config.destination == "stdout":
            sink = sys.stdout
        elif self.log_config.destination == "stderr":
            sink = sys.stderr
        elif self.log_config.destination == "file":
            log_file = Path(self.log_config.log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            sink = str(log_file)
        else:
            sink = sys.stderr

        if self.log_config.destination == "file":
            logger.add(
                self.log_config.log_file,
                level=self.log_config.level,
                format=self.log_config.format,
                rotation=self.log_config.rotation,
                retention=self.log_config.retention,
                compression=self.log_config.compression,
                serialize=self.log_config.serialize,
                backtrace=self.log_config.backtrace,
                diagnose=self.log_config.diagnose,
                enqueue=self.log_config.enqueue,
            )
        else:
            logger.add(
                sink,
                level=self.log_config.level,
                format=self.log_config.format,
                colorize=self.log_config.colorize,
                backtrace=self.log_config.backtrace,
                diagnose=self.log_config.diagnose,
                enqueue=self.log_config.enqueue,
            )

    def set_log_level(self, level: str) -> None:
        """Change log level at runtime"""
        self.log_config.level = level
        self.setup_logging()
        logger.info(f"Log level changed to {level}")
