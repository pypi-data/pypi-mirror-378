# FiveTwenty

A comprehensive, production-ready Python client for the OANDA REST v20.

## Features

- **Async-first** with sync wrapper
- **Type-safe** with full mypy strict compliance and 75+ comprehensive models
- **Minimal dependencies** (only httpx + pydantic)
- **Production ready** with retries, rate limiting, and comprehensive error handling
- **Reliable streaming** with configurable reconnection policies and heartbeat monitoring
- **Financial precision** with Decimal calculations and proper OANDA field aliases
- **Complete API coverage** with 100% endpoint implementation (all 7 endpoint groups)
- **Extensive testing** with 427 comprehensive tests and roundtrip validation

## Quick Start

### Installation

```bash
# Note: Package not yet published to PyPI - install from source
git clone https://github.com/NimbleOx/fivetwenty.git
cd fivetwenty
uv pip install -e .
```

### Async Usage (Recommended)

```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient, Environment

async def main():
    async with AsyncClient(
        token="your-token-here",
        environment=Environment.PRACTICE
    ) as client:
        
        # Get accounts
        accounts = await client.accounts.list()
        account_id = accounts[0].id
        
        # Create a market order
        order = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=1000,
            stop_loss=Decimal("1.0900"),
            take_profit=Decimal("1.1100"),
        )
        print(f"Order created: {order.last_transaction_id}")
        
        # Stream prices for 30 seconds
        import time
        end_time = time.time() + 30
        
        async for price in client.pricing.stream(account_id, ["EUR_USD"]):
            if hasattr(price, 'instrument'):  # It's a price update
                spread = price.spread
                print(f"{price.instrument}: {price.closeout_bid}/{price.closeout_ask} (spread: {spread})")
            
            if time.time() > end_time:
                break

if __name__ == "__main__":
    asyncio.run(main())
```

### Sync Usage

```python
from decimal import Decimal
from fivetwenty import Client, Environment

with Client(token="your-token-here", environment=Environment.PRACTICE) as client:
    # Get accounts
    accounts = client.accounts.list()
    account_id = accounts[0].id
    
    # Create a market order  
    order = client.orders.post_market_order(
        account_id=account_id,
        instrument="EUR_USD", 
        units=1000,
        stop_loss=Decimal("1.0900")
    )
    
    # Stream prices (blocking iterator)
    count = 0
    for price in client.pricing.stream_iter(account_id, ["EUR_USD"]):
        if hasattr(price, 'instrument'):
            print(f"{price.instrument}: {price.closeout_bid}/{price.closeout_ask}")
        
        count += 1
        if count > 10:
            break  # Stop after 10 updates
```

## Configuration

### Environment Variables

- `FIVETWENTY_OANDA_TOKEN`: Your API token
- `FIVETWENTY_USER_AGENT_EXTRA`: Additional user agent info

### Advanced Configuration

```python
from fivetwenty import AsyncClient, Environment
import httpx

client = AsyncClient(
    token="your-token",
    environment=Environment.LIVE,  # Use live trading
    timeout=60.0,  # 60 second timeout
    max_retries=5,  # Retry failed requests
    
    # Custom HTTP client with proxy
    transport=httpx.AsyncClient(
        proxies="http://proxy.example.com:8080",
        verify="/path/to/ca-bundle.crt"
    ),
    
    # Custom logging
    logger=your_logger,
)
```

## Error Handling

```python
from fivetwenty import VeeTwentyError, StreamStall

try:
    order = await client.orders.post_market_order(...)
except VeeTwentyError as e:
    print(f"API Error: {e}")
    print(f"Status: {e.status}")
    print(f"Code: {e.code}")  
    print(f"Request ID: {e.request_id}")
    
    if e.retryable:
        # Can retry this operation
        pass

try:
    async for price in client.pricing.stream(...):
        process(price)
except StreamStall:
    # Reconnect and try again
    pass
```

## Architecture Highlights

### Production-Ready Features
- **Smart retries** with exponential backoff and jitter
- **Rate limiting respect** honoring server `Retry-After` headers
- **Write-safe retries** - only retry POST/PUT/PATCH/DELETE with idempotency keys
- **Stall detection** using monotonic time for reliable stream monitoring
- **Token hygiene** - never logs sensitive authentication data

### Financial Precision
- **Decimal precision** for all monetary calculations (never float)
- **OANDA API compatibility** with proper camelCase field aliases
- **String serialization** of Decimals to prevent floating-point errors
- **Roundtrip validation** ensuring data integrity with OANDA's API format

### Developer Experience
- **Type safety** with full mypy strict compliance and `py.typed` marker
- **Comprehensive models** - 75+ Pydantic models covering the entire OANDA API
- **Intuitive API** - everything hangs off `client.accounts`, `client.orders`, `client.pricing`
- **Context managers** for automatic resource cleanup
- **Rich error messages** with request IDs and actionable information
- **VS Code ready** with included development environment configuration

## Project Structure

```
fivetwenty/
├── __init__.py          # Clean public API
├── client.py            # AsyncClient & Client implementations
├── exceptions.py        # Error handling with VeeTwentyError
├── models.py            # 75+ comprehensive OANDA API models
├── endpoints/           # Complete endpoint implementations
│   ├── accounts.py      # Account operations & configuration
│   ├── orders.py        # Complete order management
│   ├── pricing.py       # Pricing, streaming & candles
│   ├── trades.py        # Trade management
│   ├── positions.py     # Position operations
│   └── transactions.py  # Transaction history & streaming
└── _internal/           # Internal utilities
    ├── environment.py   # Environment enum
    └── utils.py         # Helper functions
```

## Requirements

- Python 3.10+
- httpx >= 0.25.0
- pydantic >= 2.5.0

## API Coverage

### ✅ Complete OANDA v20 REST API Implementation (100%)

- **Account Management**: Complete account operations, configuration updates, and change polling
- **Order Operations**: Full order lifecycle - create, list, get, cancel, replace, and client extensions
- **Trade Management**: Complete trade operations - list, get, close, modify, and dependent orders
- **Position Management**: Full position operations - list, get, close by instrument
- **Pricing & Streaming**: Real-time pricing, reliable streaming, and historical candles
- **Transaction History**: Complete audit trail, streaming, and incremental updates

**All 7 endpoint groups implemented with 268 comprehensive tests!**

## Development

This project uses **uv** for dependency management, **poethepoet** for task running, and **ruff** for formatting/linting:

```bash
# Quick setup (poethepoet)
poe setup              # Complete project setup for new developers
poe dev                # Fast development checks (format, typecheck, test)
poe check              # Run format, lint, typecheck, and tests

# Testing
poe test               # Run all tests
poe test-cov           # Run tests with coverage

# Code quality
poe quality-core       # Run format, lint, and typecheck (core files only)
poe format             # Format code
poe lint-fix           # Fix linting issues

# Documentation
poe docs-serve         # Serve docs locally
poe docs-build         # Build documentation

# Or use uv directly
uv sync                # Install dependencies
uv run pytest         # Run tests
uv run ruff format .   # Format code
uv run mypy fivetwenty/     # Type checking
```

See [CLAUDE.md](CLAUDE.md) for detailed development guidance and [TODO.md](TODO.md) for planned features.

## 📚 Documentation

This project features comprehensive documentation organized using the **Diátaxis framework** - a systematic approach that organizes content by user needs.

### Documentation Structure

|                   | **PRACTICAL USE**                | **THEORETICAL KNOWLEDGE**      |
|-------------------|-----------------------------------|---------------------------------|
| **LEARNING-ORIENTED** | 📚 **TUTORIALS**<br>(Learning by doing) | 📖 **EXPLANATION**<br>(Understanding) |
| **PROBLEM-ORIENTED**  | 🛠️ **HOW-TO GUIDES**<br>(Solving problems) | 📋 **REFERENCE**<br>(Information lookup) |

### Working with Documentation

```bash
# Install documentation dependencies
uv pip install -e .[docs]

# Serve documentation locally (available at http://localhost:8000)
uv run mkdocs serve

# Build documentation for production
uv run mkdocs build

# Or use poe tasks
uv run poe docs-serve   # Serve locally
uv run poe docs-build   # Build for production
```

The documentation includes tutorials, how-to guides, API reference, and conceptual explanations. Visit the documentation site for complete details.

## License

MIT License - see LICENSE file for details.