# Zlogger Python Client

A simple and efficient Python client for the Zlogger logging service.

## Installation

```bash
pip install zlogger-client
```

## Quick Start

```python
from zlogger import ZloggerClient

# Initialize client
logger = ZloggerClient(
    endpoint="https://zlogger.ch/api/logs",
    api_key="your-api-key",
    app_name="my-app"
)

# Send logs
logger.info("Application started", {"version": "1.0.4"})
logger.warn("High memory usage", {"memory": "90%"})
logger.error("Database connection failed", {"db": "primary"})
logger.debug("Processing user request", {"user_id": 123})
```

## API

### ZloggerClient(endpoint, api_key, app_name)

Creates a new Zlogger client instance.

**Parameters:**
- `endpoint` (str): Zlogger API endpoint URL
- `api_key` (str): Your Zlogger API key
- `app_name` (str): Name of your application

### Logging Methods

All logging methods accept:
- `message` (str): The log message
- `context` (dict, optional): Additional context data

**Available methods:**
- `logger.debug(message, context=None)`
- `logger.info(message, context=None)`
- `logger.warn(message, context=None)`
- `logger.error(message, context=None)`

## Example with Context

```python
logger.error("Payment failed", {
    "transaction_id": "txn_123",
    "amount": 99.99,
    "currency": "USD",
    "error_code": "INSUFFICIENT_FUNDS"
})
```

## License

MIT License