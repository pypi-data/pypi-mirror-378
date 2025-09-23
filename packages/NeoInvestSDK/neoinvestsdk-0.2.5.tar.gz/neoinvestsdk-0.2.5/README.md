# NeoInvestSDK

Modern, async Python SDK for NeoPro Trading Platform with real-time market data streaming, trading operations, and portfolio management.

# Setup

```
python -m venv .venv
.\.venv\Scripts\active
pip install NeoInvestSDK
python examples\01_basic_stock_stream.py
```


# SDK Config PROD

```python
config = SDKConfig(
    log_config=LogConfig(level="DEBUG"),
    api_endpoints=APIEndpointsConfig(
        base_url="https://neoapi.vpbanks.com.vn/neo-api",
        stock_stream_url="wss://neoapi.vpbanks.com.vn/stock-stream/broker",
        trading_stream_url="wss://neoapi.vpbanks.com.vn/trading-stream/broker",
        auth_base_url="https://external.vpbanks.com.vn",
    ),
    auth_config=AuthConfig(
        username="",
        password="",
        pin="",
    ),
)
```