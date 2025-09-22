# Online Boutique AI Assistant MCP Server

[![PyPI version](https://badge.fury.io/py/ai-boutique-assit-mcp.svg)](https://badge.fury.io/py/ai-boutique-assit-mcp)
[![Python](https://img.shields.io/pypi/pyversions/ai-boutique-assit-mcp.svg)](https://pypi.org/project/ai-boutique-assit-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/ai-boutique-assit-mcp)](https://pepy.tech/project/ai-boutique-assit-mcp)

**Model Context Protocol (MCP) Server for Online Boutique AI Assistant**

Expose microservices through the standardized Model Context Protocol, enabling any MCP client to access complete e-commerce functionality.

📦 **[Available on PyPI](https://pypi.org/project/ai-boutique-assit-mcp/)**

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Available Functions](#available-functions)
6. [Configuration](#configuration)
7. [Development](#development)
8. [Requirements](#requirements)
9. [Use Cases](#use-cases)
10. [Contributing](#contributing)
11. [License](#license)

## Features

- **Complete E-commerce**: 18 microservice functions for products, cart, checkout, payments, shipping
- **Standard MCP Protocol**: Works with any MCP client (Claude, ChatGPT, custom tools)
- **Google ADK Integration**: Built using Google Agent Development Kit patterns
- **Dynamic Configuration**: Environment variable based configuration
- **Production Ready**: Comprehensive logging and error handling

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   MCP Client    │────│  MCP Server      │────│  Microservices      │
│ (Any LLM/Agent) │    │ (This Package)   │    │ (Online Boutique)   │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

## Installation

Install from PyPI:

```bash
pip install ai-boutique-assit-mcp
```

Or install from source:

```bash
git clone https://github.com/arjunprabhulal/ai-boutique-assit-mcp.git
cd ai-boutique-assit-mcp
pip install -e .
```

## Usage

### 1. Start MCP Server

```bash
# Standalone HTTP server
botiq-mcp-server --port 8080
```

### 2. Connect with ADK Agent

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, SseConnectionParams

agent = Agent(
    name="boutique_assistant",
    model="gemini-2.0-flash",
    instruction="You are a helpful e-commerce assistant.",
    tools=[
        McpToolset(
            connection_params=SseConnectionParams(
                url="http://localhost:8080/mcp"
            )
        )
    ]
)
```

## Available Functions

The MCP server exposes 18 e-commerce functions:

### Products & Catalog
- `list_products()` - Browse all products
- `search_products(query)` - Search product catalog  
- `get_product(product_id)` - Get product details
- `get_product_with_image(product_id)` - Product with image
- `filter_products_by_price(max_price_usd)` - Price filtering

### Shopping Cart
- `add_item_to_cart(user_id, product_id, quantity)` - Add to cart
- `get_cart(user_id)` - View cart contents
- `empty_cart(user_id)` - Clear cart

### Checkout & Orders
- `place_order(user_id, currency, address, email, credit_card)` - Complete purchase
- `initiate_checkout()` - Start checkout process

### Shipping & Logistics
- `get_shipping_quote(address, items)` - Calculate shipping
- `ship_order(address, items)` - Arrange shipping

### Payment & Currency
- `charge_card(amount, credit_card)` - Process payment
- `get_supported_currencies()` - Available currencies
- `convert_currency(from_amount, to_currency)` - Currency conversion

### Communication
- `send_order_confirmation(email, order)` - Email confirmations

### Marketing
- `get_ads(context_keys)` - Promotional content
- `list_recommendations(user_id, product_ids)` - Product suggestions

## Configuration

### Environment Variables

Override microservice endpoints:

```bash
export PRODUCT_CATALOG_SERVICE="localhost:3550"
export CART_SERVICE="localhost:7070"
export RECOMMENDATION_SERVICE="localhost:8080"
export SHIPPING_SERVICE="localhost:50052"
export CURRENCY_SERVICE="localhost:7000"
export PAYMENT_SERVICE="localhost:50051"
export EMAIL_SERVICE="localhost:5000"
export CHECKOUT_SERVICE="localhost:5050"
export AD_SERVICE="localhost:9555"
```


## Development

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/arjunprabhulal/ai-boutique-assit-mcp.git
cd ai-boutique-assit-mcp

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start MCP server
python -m ai_boutique_assit_mcp.mcp_server --port 8081

# 4. Test with ADK
adk run ai_boutique_assit_mcp
```

### Build and Publish

```bash
# Build package
python -m build

# Publish to PyPI
python -m twine upload dist/*
```

## Requirements

- **Python**: 3.9 or higher
- **Google ADK**: For MCP integration
- **gRPC**: For microservice communication
- **Target microservices**: Compatible gRPC services

## Use Cases

- **AI Agents**: Connect any LLM to e-commerce microservices
- **API Gateway**: Unified access to distributed services  
- **Testing**: Mock or test e-commerce workflows
- **Integration**: Standard protocol for microservice access
- **Multi-platform**: Use from Python, Node.js, any MCP client

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

**Repository**: [https://github.com/arjunprabhulal/ai-boutique-assit-mcp](https://github.com/arjunprabhulal/ai-boutique-assit-mcp)

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details.

