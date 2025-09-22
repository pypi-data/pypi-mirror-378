#!/usr/bin/env python3
"""
ADK-based Model Context Protocol (MCP) Server for Online Boutique AI Assistant

This server exposes Online Boutique AI Assistant e-commerce functionality through MCP,
using the Google Agent Development Kit (ADK) tools framework.

The MCP server connects directly to the GKE-based microservices using gRPC
and exposes a clean interface for product search, cart management, checkout, etc.

Environment variables:
    PRODUCT_CATALOG_SERVICE: Override endpoint for product catalog service
    CART_SERVICE: Override endpoint for cart service
    RECOMMENDATION_SERVICE: Override endpoint for recommendation service
    SHIPPING_SERVICE: Override endpoint for shipping service
    CURRENCY_SERVICE: Override endpoint for currency service
    PAYMENT_SERVICE: Override endpoint for payment service
    EMAIL_SERVICE: Override endpoint for email service
    CHECKOUT_SERVICE: Override endpoint for checkout service
    AD_SERVICE: Override endpoint for ad service
"""

# Standard library imports
import asyncio
import json
import logging
import os
from typing import Any, Dict, List

# Third-party imports
import grpc
import requests
import uvicorn
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

# MCP Server imports
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.models import InitializationOptions

# Google ADK imports
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

# Local application imports - gRPC protobuf classes
from ai_boutique_assit_mcp.hipstershop_pb2 import (
    Empty, CartItem, AddItemRequest, EmptyCartRequest, GetCartRequest,
    ListRecommendationsRequest, ListRecommendationsResponse,
    GetProductRequest, SearchProductsRequest, SearchProductsResponse, ListProductsResponse, Money,
    Address, GetQuoteRequest, GetQuoteResponse, ShipOrderRequest, ShipOrderResponse,
    GetSupportedCurrenciesResponse, CurrencyConversionRequest,
    CreditCardInfo, ChargeRequest, ChargeResponse,
    OrderItem, OrderResult, SendOrderConfirmationRequest,
    PlaceOrderRequest, PlaceOrderResponse,
    AdRequest, AdResponse, Ad
)

# Local application imports - gRPC service stubs
from ai_boutique_assit_mcp.hipstershop_pb2_grpc import (
    CartServiceStub, RecommendationServiceStub, ProductCatalogServiceStub,
    ShippingServiceStub, CurrencyServiceStub, PaymentServiceStub,
    EmailServiceStub, CheckoutServiceStub, AdServiceStub
)

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# HELPER FUNCTIONS FOR CONVERTING GRPC OBJECTS TO DICTIONARIES
# =============================================================================
# These functions convert protobuf objects to Python dictionaries for JSON response
def _product_to_dict(product):
    """Convert a gRPC product object to a dictionary."""
    # Handle relative image URLs by converting them to absolute URLs
    picture_url = product.picture
    if picture_url and picture_url.startswith('/'):
        picture_url = f"http://34.60.168.18{picture_url}"
    
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "picture": picture_url,
        "price_usd": {
            "currency_code": product.price_usd.currency_code,
            "units": product.price_usd.units,
            "nanos": product.price_usd.nanos
        },
        "categories": list(product.categories)
    }

def _cart_item_to_dict(cart_item):
    return {
        "product_id": cart_item.product_id,
        "quantity": cart_item.quantity,
    }

def _money_to_dict(money):
    return {
        "currency_code": money.currency_code,
        "units": money.units,
        "nanos": money.nanos,
    }

def _address_to_dict(address):
    return {
        "street_address": address.street_address,
        "city": address.city,
        "state": address.state,
        "country": address.country,
        "zip_code": address.zip_code,
    }

def _order_item_to_dict(order_item):
    return {
        "item": _cart_item_to_dict(order_item.item),
        "cost": _money_to_dict(order_item.cost),
    }

def _order_result_to_dict(order_result):
    return {
        "order_id": order_result.order_id,
        "shipping_tracking_id": order_result.shipping_tracking_id,
        "shipping_cost": _money_to_dict(order_result.shipping_cost),
        "shipping_address": _address_to_dict(order_result.shipping_address),
        "items": [_order_item_to_dict(item) for item in order_result.items],
    }

def _ad_to_dict(ad: Ad):
    return {
        "redirect_url": ad.redirect_url,
        "text": ad.text,
    }

# =============================================================================
# SERVICE CLIENT CONNECTION FUNCTIONS
# =============================================================================
# These functions create connections to the various microservices
# Each can be configured via environment variables
def _get_product_catalog_client():
    """Create and return a gRPC client for the product catalog service."""
    endpoint = os.environ.get('PRODUCT_CATALOG_SERVICE', 'productcatalogservice:3550')
    logger.info(f"Product catalog service connecting to: {endpoint}")
    channel = grpc.insecure_channel(endpoint)
    return ProductCatalogServiceStub(channel)

def _get_cart_client():
    endpoint = os.environ.get('CART_SERVICE', 'cartservice:7070')
    logger.info(f"Cart service connecting to: {endpoint}")
    channel = grpc.insecure_channel(endpoint)
    return CartServiceStub(channel)

def _get_recommendation_client():
    channel = grpc.insecure_channel(os.environ.get('RECOMMENDATION_SERVICE', 'recommendationservice:8080'))
    return RecommendationServiceStub(channel)

def _get_shipping_client():
    channel = grpc.insecure_channel(os.environ.get('SHIPPING_SERVICE', 'shippingservice:50051'))
    return ShippingServiceStub(channel)

def _get_currency_client():
    channel = grpc.insecure_channel(os.environ.get('CURRENCY_SERVICE', 'currencyservice:7000'))
    return CurrencyServiceStub(channel)

def _get_payment_client():
    channel = grpc.insecure_channel(os.environ.get('PAYMENT_SERVICE', 'paymentservice:50051'))
    return PaymentServiceStub(channel)

def _get_email_client():
    channel = grpc.insecure_channel(os.environ.get('EMAIL_SERVICE', 'emailservice:5000'))
    return EmailServiceStub(channel)

def _get_checkout_client():
    endpoint = os.environ.get('CHECKOUT_SERVICE', 'checkoutservice:5050')
    logger.info(f"Checkout service connecting to: {endpoint}")
    channel = grpc.insecure_channel(endpoint)
    return CheckoutServiceStub(channel)

def _get_ad_client():
    channel = grpc.insecure_channel(os.environ.get('AD_SERVICE', 'adservice:9555'))
    return AdServiceStub(channel)

# =============================================================================
# MICROSERVICE BUSINESS FUNCTIONS EXPOSED AS ADK TOOLS
# =============================================================================

# E-commerce functions that will be exposed as MCP tools
def add_item_to_cart(user_id: str, product_id: str, quantity: int) -> Dict[str, Any]:
    """Adds an item to the user's cart."""
    try:
        client = _get_cart_client()
        request = AddItemRequest(
            user_id=user_id,
            item=CartItem(product_id=product_id, quantity=quantity)
        )
        client.AddItem(request)
        return {}
    except grpc.RpcError as e:
        return {"error": f"gRPC error: {e.code()} - {e.details()}"}
    except Exception as e:
        return {"error": str(e)}

def get_cart(user_id: str) -> Dict[str, Any]:
    """Retrieves the content of a user's cart."""
    try:
        client = _get_cart_client()
        request = GetCartRequest(user_id=user_id)
        response = client.GetCart(request)
        return {
            "user_id": response.user_id,
            "items": [_cart_item_to_dict(item) for item in response.items]
        }
    except grpc.RpcError as e:
        return {"error": f"gRPC error: {e.code()} - {e.details()}"}
    except Exception as e:
        return {"error": str(e)}

def empty_cart(user_id: str) -> Dict[str, Any]:
    """Empties a user's cart."""
    try:
        client = _get_cart_client()
        request = EmptyCartRequest(user_id=user_id)
        client.EmptyCart(request)
        return {}
    except grpc.RpcError as e:
        return {"error": f"gRPC error: {e.code()} - {e.details()}"}
    except Exception as e:
        return {"error": str(e)}

def initiate_checkout() -> Dict[str, Any]:
    """Initiates the checkout process by returning checkout form data."""
    return {
        "show_checkout": True,
        "message": "Ready to complete your order"
    }

def list_recommendations(user_id: str, product_ids: List[str]) -> Dict[str, Any]:
    """Lists product recommendations for a user based on given product IDs."""
    try:
        client = _get_recommendation_client()
        request = ListRecommendationsRequest(user_id=user_id, product_ids=product_ids)
        response: ListRecommendationsResponse = client.ListRecommendations(request)
        
        recommended_products_details = []
        for prod_id in response.product_ids:
            product_details = get_product(prod_id) # Reuse get_product to fetch full details
            if "error" not in product_details:
                recommended_products_details.append(product_details)
            else:
                logger.warning(f"Could not retrieve details for product {prod_id}: {product_details['error']}")
                
        return {"products": recommended_products_details}
    except grpc.RpcError as e:
        return {"error": f"gRPC error: {e.code()} - {e.details()}"}
    except Exception as e:
        return {"error": str(e)}

def get_shipping_quote(street_address: str, city: str, state: str, country: str, zip_code: int, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Gets a shipping quote for a given address and list of cart items."""
    try:
        client = _get_shipping_client()
        address = Address(
            street_address=street_address, city=city, state=state, country=country, zip_code=zip_code
        )
        cart_items = [CartItem(product_id=item["product_id"], quantity=item["quantity"]) for item in items]
        request = GetQuoteRequest(address=address, items=cart_items)
        response: GetQuoteResponse = client.GetQuote(request)
        return {
            "cost_usd": _money_to_dict(response.cost_usd),
            "shipping_address": _address_to_dict(address)
        }
    except grpc.RpcError as e:
        return {"error": f"gRPC error: {e.code()} - {e.details()}"}
    except Exception as e:
        return {"error": str(e)}

def ship_order(street_address: str, city: str, state: str, country: str, zip_code: int, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Ships an order to a given address and list of cart items."""
    try:
        client = _get_shipping_client()
        address = Address(
            street_address=street_address, city=city, state=state, country=country, zip_code=zip_code
        )
        cart_items = [CartItem(product_id=item["product_id"], quantity=item["quantity"]) for item in items]
        request = ShipOrderRequest(address=address, items=cart_items)
        response: ShipOrderResponse = client.ShipOrder(request)
        return {"tracking_id": response.tracking_id}
    except grpc.RpcError as e:
        return {"error": f"gRPC error: {e.code()} - {e.details()}"}
    except Exception as e:
        return {"error": str(e)}

def get_supported_currencies() -> Dict[str, Any]:
    """Gets a list of supported currency codes."""
    try:
        client = _get_currency_client()
        request = Empty()
        response: GetSupportedCurrenciesResponse = client.GetSupportedCurrencies(request)
        return {"currency_codes": list(response.currency_codes)}
    except grpc.RpcError as e:
        return {"error": f"gRPC error: {e.code()} - {e.details()}"}
    except Exception as e:
        return {"error": str(e)}

def convert_currency(from_currency_code: str, from_units: int, from_nanos: int, to_currency_code: str) -> Dict[str, Any]:
    """Converts an amount from one currency to another."""
    try:
        client = _get_currency_client()
        from_money = Money(currency_code=from_currency_code, units=from_units, nanos=from_nanos)
        request = CurrencyConversionRequest(from_=from_money, to_code=to_currency_code)
        response = client.Convert(request)
        return {"converted_money": _money_to_dict(response)}
    except grpc.RpcError as e:
        return {"error": f"gRPC error: {e.code()} - {e.details()}"}
    except Exception as e:
        return {"error": str(e)}

def charge_card(amount_currency_code: str, amount_units: int, amount_nanos: int, credit_card_number: str, credit_card_cvv: int, credit_card_expiration_year: int, credit_card_expiration_month: int) -> Dict[str, Any]:
    """Charges a credit card for a given amount."""
    try:
        client = _get_payment_client()
        amount = Money(currency_code=amount_currency_code, units=amount_units, nanos=amount_nanos)
        credit_card = CreditCardInfo(
            credit_card_number=credit_card_number,
            credit_card_cvv=credit_card_cvv,
            credit_card_expiration_year=credit_card_expiration_year,
            credit_card_expiration_month=credit_card_expiration_month
        )
        request = ChargeRequest(amount=amount, credit_card=credit_card)
        response: ChargeResponse = client.Charge(request)
        return {"transaction_id": response.transaction_id}
    except grpc.RpcError as e:
        return {"error": f"gRPC error: {e.code()} - {e.details()}"}
    except Exception as e:
        return {"error": str(e)}

def send_order_confirmation(email: str, order_result: Dict[str, Any]) -> Dict[str, Any]:
    """Sends an order confirmation email."""
    try:
        client = _get_email_client()
        order = OrderResult(
            order_id=order_result.get("order_id", ""),
            shipping_tracking_id=order_result.get("shipping_tracking_id", ""),
            shipping_cost=Money(
                currency_code=order_result["shipping_cost"]["currency_code"],
                units=order_result["shipping_cost"]["units"],
                nanos=order_result["shipping_cost"]["nanos"],
            ) if "shipping_cost" in order_result else None,
            shipping_address=Address(
                street_address=order_result["shipping_address"]["street_address"],
                city=order_result["shipping_address"]["city"],
                state=order_result["shipping_address"]["state"],
                country=order_result["shipping_address"]["country"],
                zip_code=order_result["shipping_address"]["zip_code"],
            ) if "shipping_address" in order_result else None,
            items=[
                OrderItem(
                    item=CartItem(
                        product_id=item["item"]["product_id"],
                        quantity=item["item"]["quantity"],
                    ),
                    cost=Money(
                        currency_code=item["cost"]["currency_code"],
                        units=item["cost"]["units"],
                        nanos=item["cost"]["nanos"],
                    )
                ) for item in order_result.get("items", [])
            ]
        )

        request = SendOrderConfirmationRequest(email=email, order=order)
        client.SendOrderConfirmation(request)
        return {}
    except grpc.RpcError as e:
        return {"error": f"gRPC error: {e.code()} - {e.details()}"}
    except Exception as e:
        return {"error": str(e)}

def place_order(user_id: str, user_currency: str, address: Dict[str, Any], email: str, credit_card: Dict[str, Any]) -> Dict[str, Any]:
    """Places an order for a user."""
    try:
        client = _get_checkout_client()
        address_grpc = Address(
            street_address=address["street_address"],
            city=address["city"],
            state=address["state"],
            country=address["country"],
            zip_code=address["zip_code"],
        )
        credit_card_grpc = CreditCardInfo(
            credit_card_number=credit_card["credit_card_number"],
            credit_card_cvv=credit_card["credit_card_cvv"],
            credit_card_expiration_year=credit_card["credit_card_expiration_year"],
            credit_card_expiration_month=credit_card["credit_card_expiration_month"],
        )
        request = PlaceOrderRequest(
            user_id=user_id, user_currency=user_currency, address=address_grpc, email=email, credit_card=credit_card_grpc
        )
        response: PlaceOrderResponse = client.PlaceOrder(request)
        return {"order": _order_result_to_dict(response.order)}
    except grpc.RpcError as e:
        return {"error": f"gRPC error: {e.code()} - {e.details()}"}
    except Exception as e:
        return {"error": str(e)}

def get_ads(context_keys: List[str]) -> Dict[str, Any]:
    """Gets advertisements based on a list of context keywords."""
    try:
        client = _get_ad_client()
        request = AdRequest(context_keys=context_keys)
        response: AdResponse = client.GetAds(request)
        return {"ads": [_ad_to_dict(ad) for ad in response.ads]}
    except grpc.RpcError as e:
        return {"error": f"gRPC error: {e.code()} - {e.details()}"}
    except Exception as e:
        return {"error": str(e)}

def list_products() -> Dict[str, Any]:
    """List all products from the catalog using gRPC."""
    try:
        client = _get_product_catalog_client()
        request = Empty()
        response: ListProductsResponse = client.ListProducts(request)
        products = [_product_to_dict(product) for product in response.products]
        return {
            "products": products,
            "count": len(products)
        }
    except grpc.RpcError as e:
        return {"error": f"gRPC error: {e.code()} - {e.details()}"}
    except Exception as e:
        return {"error": str(e)}

def filter_products_by_price(max_price_usd: float) -> Dict[str, Any]:
    """Filter products by maximum price in USD."""
    try:
        # Get all products first
        all_products_result = list_products()
        if "error" in all_products_result:
            return all_products_result
            
        # Filter products by price
        filtered_products = []
        for product in all_products_result["products"]:
            # Calculate total price: units + (nanos / 1,000,000,000)
            price_info = product.get("price_usd", {})
            units = price_info.get("units", 0)
            nanos = price_info.get("nanos", 0)
            total_price = units + (nanos / 1_000_000_000)
            
            # Include product if under max price
            if total_price <= max_price_usd:
                filtered_products.append(product)
        
        return {
            "products": filtered_products,
            "count": len(filtered_products),
            "filter": f"under ${max_price_usd}"
        }
    except Exception as e:
        return {"error": str(e)}

def get_product(product_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific product using gRPC."""
    try:
        client = _get_product_catalog_client()
        request = GetProductRequest(id=product_id)
        response = client.GetProduct(request)
        return _product_to_dict(response)
    except grpc.RpcError as e:
        return {"error": f"gRPC error: {e.code()} - {e.details()}"}
    except Exception as e:
        return {"error": str(e)}

def search_products(query: str) -> Dict[str, Any]:
    """Enhanced search for products in the catalog using gRPC."""
    try:
        client = _get_product_catalog_client()
        request = SearchProductsRequest(query=query)
        response: SearchProductsResponse = client.SearchProducts(request)
        products = [_product_to_dict(product) for product in response.results]
        
        return {
            "query": query,
            "products": products,
            "count": len(products)
        }
    except grpc.RpcError as e:
        return {"error": f"gRPC error: {e.code()} - {e.details()}"}
    except Exception as e:
        return {"error": str(e)}

def get_product_with_image(product_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific product and download its image."""
    try:
        product_details = get_product(product_id)
        
        if "error" in product_details:
            return product_details
            
        # If product has an image URL, download it
        if product_details.get('picture'):
            try:
                image_url = product_details['picture']
                if image_url.startswith('/'):
                    image_url = f"http://34.118.239.199{image_url}"  # frontend cluster IP
                
                image_response = requests.get(image_url, timeout=10)
                image_response.raise_for_status()
                
                # Get content type
                content_type = image_response.headers.get('content-type', 'image/jpeg')
                product_details['image_downloaded'] = True
                product_details['resolved_image_url'] = image_url
                product_details['image_link'] = image_url
            except Exception as img_error:
                product_details['image_error'] = f"Failed to download image: {str(img_error)}"
                product_details['image_downloaded'] = False
        else:
            product_details['image_downloaded'] = False
            
        return product_details
    except Exception as e:
        return {"error": str(e)}

# =============================================================================
# MCP SERVER CONFIGURATION USING ADK
# =============================================================================

def create_adk_tools():
    """Create ADK FunctionTool instances for all our microservice functions."""
    adk_tools = []
    
    # Get all microservice functions
    functions = {
        'add_item_to_cart': add_item_to_cart,
        'get_cart': get_cart,
        'empty_cart': empty_cart,
        'initiate_checkout': initiate_checkout,
        'list_recommendations': list_recommendations,
        'get_shipping_quote': get_shipping_quote,
        'ship_order': ship_order,
        'get_supported_currencies': get_supported_currencies,
        'convert_currency': convert_currency,
        'charge_card': charge_card,
        'send_order_confirmation': send_order_confirmation,
        'place_order': place_order,
        'get_ads': get_ads,
        'list_products': list_products,
        'filter_products_by_price': filter_products_by_price,
        'get_product': get_product,
        'search_products': search_products,
        'get_product_with_image': get_product_with_image
    }
    
    # Create ADK FunctionTool for each function
    for name, func in functions.items():
        adk_tool = FunctionTool(func)
        adk_tools.append(adk_tool)
    
    return adk_tools

def create_mcp_server():
    """Create and configure the MCP server for Online Boutique AI Assistant."""
    # Create MCP server
    server = Server("online-boutique-mcp-server")
    
    # Get ADK tools and convert them to MCP format
    adk_tools = create_adk_tools()
    
    # Get all microservice functions for direct calling
    microservice_functions = {
        'add_item_to_cart': add_item_to_cart,
        'get_cart': get_cart,
        'empty_cart': empty_cart,
        'initiate_checkout': initiate_checkout,
        'list_recommendations': list_recommendations,
        'get_shipping_quote': get_shipping_quote,
        'ship_order': ship_order,
        'get_supported_currencies': get_supported_currencies,
        'convert_currency': convert_currency,
        'charge_card': charge_card,
        'send_order_confirmation': send_order_confirmation,
        'place_order': place_order,
        'get_ads': get_ads,
        'list_products': list_products,
        'filter_products_by_price': filter_products_by_price,
        'get_product': get_product,
        'search_products': search_products,
        'get_product_with_image': get_product_with_image
    }
    
    @server.list_tools()
    async def handle_list_tools() -> list[mcp_types.Tool]:
        """Handle list_tools requests."""
        mcp_tools = []
        for adk_tool in adk_tools:
            mcp_tool = adk_to_mcp_tool_type(adk_tool)
            mcp_tools.append(mcp_tool)
        return mcp_tools
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
        """Handle call_tool requests."""
        # Find the matching ADK tool
        matching_tool = None
        for adk_tool in adk_tools:
            if adk_tool.name == name:
                matching_tool = adk_tool
                break
        
        if not matching_tool:
            raise ValueError(f"Tool {name} not found")
        
        try:
            # Execute the ADK tool's run_async method like in the working example
            adk_tool_response = await matching_tool.run_async(
                args=arguments,
                tool_context=None,
            )
            logger.info(f"MCP Server: ADK tool '{name}' executed. Response: {adk_tool_response}")
            
            # Format response as JSON string within TextContent
            response_text = json.dumps(adk_tool_response, indent=2)
            return [mcp_types.TextContent(type="text", text=response_text)]
            
        except Exception as e:
            logger.error(f"MCP Server: Error executing ADK tool '{name}': {e}")
            error_text = json.dumps({"error": f"Failed to execute tool '{name}': {str(e)}"})
            return [mcp_types.TextContent(type="text", text=error_text)]
    
    return server

# =============================================================================
# SERVER STARTUP AND CONFIGURATION (ADK Pattern)
# =============================================================================

async def run_http_server(port: int = 8080):
    """Run MCP server via HTTP using built-in server capabilities."""
    server = create_mcp_server()
    
    # Use the server's built-in HTTP capabilities
    from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
    
    session_manager = StreamableHTTPSessionManager(
        app=server,
        stateless=True
    )
    
    async def handle_request(scope: Scope, receive: Receive, send: Send) -> None:
        await session_manager.handle_request(scope, receive, send)
    
    starlette_app = Starlette(
        debug=False,
        routes=[Mount("/mcp", app=handle_request)]
    )
    
    async with session_manager.run():
        logger.info("MCP server started on port %s", port)
        adk_tools = create_adk_tools()
        logger.info("Available functions: %s", ", ".join(tool.name for tool in adk_tools))
        
        config = uvicorn.Config(app=starlette_app, host="0.0.0.0", port=port, log_level="info")
        server_instance = uvicorn.Server(config)
        await server_instance.serve()

async def run_stdio_server():
    """Run MCP server in stdio mode for ADK."""
    server = create_mcp_server()
    
    # Run as stdio server for ADK
    from mcp.server.stdio import stdio_server
    from mcp.server.models import InitializationOptions
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, 
            write_stream,
            InitializationOptions(
                server_name="online-boutique-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

def main():
    """Main entry point for the MCP server."""
    import sys
    logging.basicConfig(level=logging.INFO)
    
    # Check if running as child process (ADK calls it this way)
    if sys.stdin.isatty() == False:
        # Running as child process - use stdio mode
        asyncio.run(run_stdio_server())
    else:
        # Running standalone - use HTTP mode
        port = int(os.getenv('PORT', '8080'))
        asyncio.run(run_http_server(port=port))


if __name__ == "__main__":
    main()
