from typing import Any
import httpx
import os

ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

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