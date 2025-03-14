from typing import Any
import asyncio
import httpx
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import os

ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

if not API_KEY:
    raise ValueError("Missing ALPHA_VANTAGE_API_KEY environment variable")

server = Server("alpha_vantage_finance")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="get-stock-quote",
            description="Get current stock quote information",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT)",
                    },
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-company-info",
            description="Get detailed company information",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT)",
                    },
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-crypto-exchange-rate",
            description="Get current cryptocurrency exchange rate",
            inputSchema={
                "type": "object",
                "properties": {
                    "crypto_symbol": {
                        "type": "string",
                        "description": "Cryptocurrency symbol (e.g., BTC, ETH)",
                    },
                    "market": {
                        "type": "string",
                        "description": "Market currency (e.g., USD, EUR)",
                        "default": "USD"
                    }
                },
                "required": ["crypto_symbol"],
            },
        ),
        types.Tool(
            name="get-time-series",
            description="Get daily time series data for a stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT)",
                    },
                    "outputsize": {
                        "type": "string",
                        "description": "compact (latest 100 data points) or full (up to 20 years of data)",
                        "enum": ["compact", "full"],
                        "default": "compact"
                    }
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-historical-options",
            description="Get historical options chain data for a stock with sorting capabilities",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT)",
                    },
                    "date": {
                        "type": "string",
                        "description": "Optional: Trading date in YYYY-MM-DD format (defaults to previous trading day, must be after 2008-01-01)",
                        "pattern": "^20[0-9]{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])$"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Optional: Number of contracts to return (default: 10, use -1 for all contracts)",
                        "default": 10,
                        "minimum": -1
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "Optional: Field to sort by",
                        "enum": [
                            "strike",
                            "expiration",
                            "volume",
                            "open_interest",
                            "implied_volatility",
                            "delta",
                            "gamma",
                            "theta",
                            "vega",
                            "rho",
                            "last",
                            "bid",
                            "ask"
                        ],
                        "default": "strike"
                    },
                    "sort_order": {
                        "type": "string",
                        "description": "Optional: Sort order",
                        "enum": ["asc", "desc"],
                        "default": "asc"
                    }
                },
                "required": ["symbol"],
            },
        )
    ]

async def make_alpha_request(client: httpx.AsyncClient, function: str, symbol: str, additional_params: dict = None) -> dict[str, Any] | str:
    """Make a request to the Alpha Vantage API with proper error handling."""
    params = {
        "function": function,
        "symbol": symbol,
        "apikey": API_KEY
    }
    if additional_params:
        params.update(additional_params)

    try:
        response = await client.get(
            ALPHA_VANTAGE_BASE,
            params=params,
            timeout=30.0
        )

        # Check for specific error responses
        if response.status_code == 429:
            return f"Rate limit exceeded. Error details: {response.text}"
        elif response.status_code == 403:
            return f"API key invalid or expired. Error details: {response.text}"

        response.raise_for_status()

        data = response.json()

        # Check for Alpha Vantage specific error messages
        if "Error Message" in data:
            return f"Alpha Vantage API error: {data['Error Message']}"
        if "Note" in data and "API call frequency" in data["Note"]:
            return f"Rate limit warning: {data['Note']}"

        return data
    except httpx.TimeoutException:
        return "Request timed out after 30 seconds. The Alpha Vantage API may be experiencing delays."
    except httpx.ConnectError:
        return "Failed to connect to Alpha Vantage API. Please check your internet connection."
    except httpx.HTTPStatusError as e:
        return f"HTTP error occurred: {str(e)} - Response: {e.response.text}"
    except Exception as e:
        return f"Unexpected error occurred: {str(e)}"

def format_quote(quote_data: dict) -> str:
    """Format quote data into a concise string."""
    try:
        global_quote = quote_data.get("Global Quote", {})
        if not global_quote:
            return "No quote data available in the response"

        return (
            f"Price: ${global_quote.get('05. price', 'N/A')}\n"
            f"Change: ${global_quote.get('09. change', 'N/A')} "
            f"({global_quote.get('10. change percent', 'N/A')})\n"
            f"Volume: {global_quote.get('06. volume', 'N/A')}\n"
            f"High: ${global_quote.get('03. high', 'N/A')}\n"
            f"Low: ${global_quote.get('04. low', 'N/A')}\n"
            "---"
        )
    except Exception as e:
        return f"Error formatting quote data: {str(e)}"

def format_company_info(overview_data: dict) -> str:
    """Format company information into a concise string."""
    try:
        if not overview_data:
            return "No company information available in the response"

        return (
            f"Name: {overview_data.get('Name', 'N/A')}\n"
            f"Sector: {overview_data.get('Sector', 'N/A')}\n"
            f"Industry: {overview_data.get('Industry', 'N/A')}\n"
            f"Market Cap: ${overview_data.get('MarketCapitalization', 'N/A')}\n"
            f"Description: {overview_data.get('Description', 'N/A')}\n"
            f"Exchange: {overview_data.get('Exchange', 'N/A')}\n"
            f"Currency: {overview_data.get('Currency', 'N/A')}\n"
            "---"
        )
    except Exception as e:
        return f"Error formatting company data: {str(e)}"

def format_crypto_rate(crypto_data: dict) -> str:
    """Format cryptocurrency exchange rate data into a concise string."""
    try:
        realtime_data = crypto_data.get("Realtime Currency Exchange Rate", {})
        if not realtime_data:
            return "No exchange rate data available in the response"

        return (
            f"From: {realtime_data.get('2. From_Currency Name', 'N/A')} ({realtime_data.get('1. From_Currency Code', 'N/A')})\n"
            f"To: {realtime_data.get('4. To_Currency Name', 'N/A')} ({realtime_data.get('3. To_Currency Code', 'N/A')})\n"
            f"Exchange Rate: {realtime_data.get('5. Exchange Rate', 'N/A')}\n"
            f"Last Updated: {realtime_data.get('6. Last Refreshed', 'N/A')} {realtime_data.get('7. Time Zone', 'N/A')}\n"
            f"Bid Price: {realtime_data.get('8. Bid Price', 'N/A')}\n"
            f"Ask Price: {realtime_data.get('9. Ask Price', 'N/A')}\n"
            "---"
        )
    except Exception as e:
        return f"Error formatting cryptocurrency data: {str(e)}"

def format_time_series(time_series_data: dict) -> str:
    """Format time series data into a concise string."""
    try:
        # Get the daily time series data
        time_series = time_series_data.get("Time Series (Daily)", {})
        if not time_series:
            return "No time series data available in the response"

        # Get metadata
        metadata = time_series_data.get("Meta Data", {})
        symbol = metadata.get("2. Symbol", "Unknown")
        last_refreshed = metadata.get("3. Last Refreshed", "Unknown")

        # Format the most recent 5 days of data
        formatted_data = [
            f"Time Series Data for {symbol} (Last Refreshed: {last_refreshed})\n\n"
        ]

        for date, values in list(time_series.items())[:5]:
            formatted_data.append(
                f"Date: {date}\n"
                f"Open: ${values.get('1. open', 'N/A')}\n"
                f"High: ${values.get('2. high', 'N/A')}\n"
                f"Low: ${values.get('3. low', 'N/A')}\n"
                f"Close: ${values.get('4. close', 'N/A')}\n"
                f"Volume: {values.get('5. volume', 'N/A')}\n"
                "---\n"
            )

        return "\n".join(formatted_data)
    except Exception as e:
        return f"Error formatting time series data: {str(e)}"

def format_historical_options(options_data: dict, limit: int = 10, sort_by: str = "strike", sort_order: str = "asc") -> str:
    """Format historical options chain data into a concise string with sorting."""
    try:
        if "Error Message" in options_data:
            return f"Error: {options_data['Error Message']}"

        options_chain = options_data.get("data", [])

        if not options_chain:
            return "No options data available in the response"

        formatted = [
            f"Historical Options Data:\n",
            f"Status: {options_data.get('message', 'N/A')}\n",
            f"Sorted by: {sort_by} ({sort_order})\n\n"
        ]

        # Convert string values to float for numeric sorting
        def get_sort_key(contract):
            value = contract.get(sort_by, 0)
            try:
                # Remove $ and % signs if present
                if isinstance(value, str):
                    value = value.replace('$', '').replace('%', '')
                return float(value)
            except (ValueError, TypeError):
                return value

        # Sort the options chain
        sorted_chain = sorted(
            options_chain,
            key=get_sort_key,
            reverse=(sort_order == "desc")
        )

        # If limit is -1, show all contracts
        display_contracts = sorted_chain if limit == -1 else sorted_chain[:limit]

        for contract in display_contracts:
            formatted.append(f"Contract Details:\n")
            formatted.append(f"Contract ID: {contract.get('contractID', 'N/A')}\n")
            formatted.append(f"Expiration: {contract.get('expiration', 'N/A')}\n")
            formatted.append(f"Strike: ${contract.get('strike', 'N/A')}\n")
            formatted.append(f"Type: {contract.get('type', 'N/A')}\n")
            formatted.append(f"Last: ${contract.get('last', 'N/A')}\n")
            formatted.append(f"Mark: ${contract.get('mark', 'N/A')}\n")
            formatted.append(f"Bid: ${contract.get('bid', 'N/A')} (Size: {contract.get('bid_size', 'N/A')})\n")
            formatted.append(f"Ask: ${contract.get('ask', 'N/A')} (Size: {contract.get('ask_size', 'N/A')})\n")
            formatted.append(f"Volume: {contract.get('volume', 'N/A')}\n")
            formatted.append(f"Open Interest: {contract.get('open_interest', 'N/A')}\n")
            formatted.append(f"IV: {contract.get('implied_volatility', 'N/A')}\n")
            formatted.append(f"Delta: {contract.get('delta', 'N/A')}\n")
            formatted.append(f"Gamma: {contract.get('gamma', 'N/A')}\n")
            formatted.append(f"Theta: {contract.get('theta', 'N/A')}\n")
            formatted.append(f"Vega: {contract.get('vega', 'N/A')}\n")
            formatted.append(f"Rho: {contract.get('rho', 'N/A')}\n")
            formatted.append("---\n")

        if limit != -1 and len(sorted_chain) > limit:
            formatted.append(f"\n... and {len(sorted_chain) - limit} more contracts")

        return "".join(formatted)
    except Exception as e:
        return f"Error formatting options data: {str(e)}"

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can fetch financial data and notify clients of changes.
    """
    if not arguments:
        return [types.TextContent(type="text", text="Missing arguments for the request")]

    if name == "get-stock-quote":
        symbol = arguments.get("symbol")
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()

        async with httpx.AsyncClient() as client:
            quote_data = await make_alpha_request(
                client,
                "GLOBAL_QUOTE",
                symbol
            )

            if isinstance(quote_data, str):
                return [types.TextContent(type="text", text=f"Error: {quote_data}")]

            formatted_quote = format_quote(quote_data)
            quote_text = f"Stock quote for {symbol}:\n\n{formatted_quote}"

            return [types.TextContent(type="text", text=quote_text)]

    elif name == "get-company-info":
        symbol = arguments.get("symbol")
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()

        async with httpx.AsyncClient() as client:
            company_data = await make_alpha_request(
                client,
                "OVERVIEW",
                symbol
            )

            if isinstance(company_data, str):
                return [types.TextContent(type="text", text=f"Error: {company_data}")]

            formatted_info = format_company_info(company_data)
            info_text = f"Company information for {symbol}:\n\n{formatted_info}"

            return [types.TextContent(type="text", text=info_text)]

    elif name == "get-crypto-exchange-rate":
        crypto_symbol = arguments.get("crypto_symbol")
        if not crypto_symbol:
            return [types.TextContent(type="text", text="Missing crypto_symbol parameter")]

        market = arguments.get("market", "USD")
        crypto_symbol = crypto_symbol.upper()
        market = market.upper()

        async with httpx.AsyncClient() as client:
            crypto_data = await make_alpha_request(
                client,
                "CURRENCY_EXCHANGE_RATE",
                None,
                {
                    "from_currency": crypto_symbol,
                    "to_currency": market
                }
            )

            if isinstance(crypto_data, str):
                return [types.TextContent(type="text", text=f"Error: {crypto_data}")]

            formatted_rate = format_crypto_rate(crypto_data)
            rate_text = f"Cryptocurrency exchange rate for {crypto_symbol}/{market}:\n\n{formatted_rate}"

            return [types.TextContent(type="text", text=rate_text)]

    elif name == "get-time-series":
        symbol = arguments.get("symbol")
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()
        outputsize = arguments.get("outputsize", "compact")

        async with httpx.AsyncClient() as client:
            time_series_data = await make_alpha_request(
                client,
                "TIME_SERIES_DAILY",
                symbol,
                {"outputsize": outputsize}
            )

            if isinstance(time_series_data, str):
                return [types.TextContent(type="text", text=f"Error: {time_series_data}")]

            formatted_series = format_time_series(time_series_data)
            series_text = f"Time series data for {symbol}:\n\n{formatted_series}"

            return [types.TextContent(type="text", text=series_text)]

    elif name == "get-historical-options":
        symbol = arguments.get("symbol")
        date = arguments.get("date")
        limit = arguments.get("limit", 10)
        sort_by = arguments.get("sort_by", "strike")
        sort_order = arguments.get("sort_order", "asc")

        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()

        async with httpx.AsyncClient() as client:
            params = {
                "function": "HISTORICAL_OPTIONS",
                "symbol": symbol
            }
            if date:
                params["date"] = date

            options_data = await make_alpha_request(
                client,
                "HISTORICAL_OPTIONS",
                symbol,
                params
            )

            if isinstance(options_data, str):
                return [types.TextContent(type="text", text=f"Error: {options_data}")]

            formatted_options = format_historical_options(options_data, limit, sort_by, sort_order)
            options_text = f"Historical options data for {symbol}"
            if date:
                options_text += f" on {date}"
            options_text += f":\n\n{formatted_options}"

            return [types.TextContent(type="text", text=options_text)]
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="alpha_vantage_finance",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

# This is needed if you'd like to connect to a custom client
if __name__ == "__main__":
    asyncio.run(main())
