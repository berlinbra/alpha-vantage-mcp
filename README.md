# Alpha Vantage MCP Server
[![Trust Score](https://archestra.ai/mcp-catalog/api/badge/quality/berlinbra/alpha-vantage-mcp)](https://archestra.ai/mcp-catalog/berlinbra__alpha-vantage-mcp)
[![smithery badge](https://smithery.ai/badge/@berlinbra/alpha-vantage-mcp)](https://smithery.ai/server/@berlinbra/alpha-vantage-mcp)

A Model Context Protocol (MCP) server that provides real-time access to financial market data through the free [Alpha Vantage API](https://www.alphavantage.co/documentation/). This server implements a standardized interface for retrieving stock quotes and company information.

<a href="https://glama.ai/mcp/servers/0wues5td08"><img width="380" height="200" src="https://glama.ai/mcp/servers/0wues5td08/badge" alt="AlphaVantage-MCP MCP server" /></a>

# Features

- Real-time stock quotes with price, volume, and change data
- Detailed company information including sector, industry, and market cap
- Real-time cryptocurrency exchange rates with bid/ask prices
- Daily, weekly, and monthly cryptocurrency time series data
- Real-time options chain data with Greeks and implied volatility
- Historical options chain data with advanced filtering and sorting
- Comprehensive ETF profile data with holdings, sector allocation, and key metrics
- Upcoming earnings calendar with customizable time horizons
- Historical earnings data with annual and quarterly reports
- Built-in error handling and rate limit management

## Installation

### Using Claude Desktop

#### Installing via Docker

- Clone the repository and build a local image to be utilized by your Claude desktop client

```sh
cd alpha-vantage-mcp
docker build -t mcp/alpha-vantage .
```

- Change your `claude_desktop_config.json` to match the following, replacing `REPLACE_API_KEY` with your actual key:

 > `claude_desktop_config.json` path
 >
 > - On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
 > - On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "alphavantage": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "-e",
        "ALPHA_VANTAGE_API_KEY",
        "mcp/alpha-vantage"
      ],
      "env": {
        "ALPHA_VANTAGE_API_KEY": "REPLACE_API_KEY"
      }
    }
  }
}
```

#### Installing via Smithery

To install Alpha Vantage MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@berlinbra/alpha-vantage-mcp):

```bash
npx -y @smithery/cli install @berlinbra/alpha-vantage-mcp --client claude
```

<summary> <h3> Development/Unpublished Servers Configuration <h3> </summary>

<details>

```json
{
 "mcpServers": {
  "alpha-vantage-mcp": {
   "args": [
    "--directory",
    "/Users/{INSERT_USER}/YOUR/PATH/TO/alpha-vantage-mcp",
    "run",
    "alpha-vantage-mcp"
   ],
   "command": "uv",
   "env": {
    "ALPHA_VANTAGE_API_KEY": "<insert api key>"
   }
  }
 }
}
```
        
</details>

#### Install packages

```
uv install -e .
```

#### Running

After connecting Claude client with the MCP tool via json file and installing the packages, Claude should see the server's mcp tools:

You can run the sever yourself via:
In alpha-vantage-mcp repo: 
```
uv run src/alpha_vantage_mcp/server.py
```

with inspector
```
* npx @modelcontextprotocol/inspector uv --directory /Users/{INSERT_USER}/YOUR/PATH/TO/alpha-vantage-mcp run src/alpha_vantage_mcp/server.py `
```

## Available Tools

The server implements twelve tools:
- `get-stock-quote`: Get the latest stock quote for a specific company
- `get-company-info`: Get stock-related information for a specific company
- `get-crypto-exchange-rate`: Get current cryptocurrency exchange rates
- `get-time-series`: Get historical daily price data for a stock
- `get-realtime-options`: Get real-time options chain data with Greeks and implied volatility
- `get-historical-options`: Get historical options chain data with advanced filtering and sorting capabilities
- `get-etf-profile`: Get comprehensive ETF profile information including holdings and sector allocation
- `get-crypto-daily`: Get daily time series data for a cryptocurrency
- `get-crypto-weekly`: Get weekly time series data for a cryptocurrency
- `get-crypto-monthly`: Get monthly time series data for a cryptocurrency
- `get-earnings-calendar`: Get upcoming earnings calendar data for companies
- `get-historical-earnings`: Get historical earnings data for a specific company

### get-stock-quote

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Stock symbol (e.g., AAPL, MSFT)"
    }
}
```

**Example Response:**
```
Stock quote for AAPL:

Price: $198.50
Change: $2.50 (+1.25%)
Volume: 58942301
High: $199.62
Low: $197.20
```

### get-company-info

Retrieves detailed company information for a given symbol.

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Stock symbol (e.g., AAPL, MSFT)"
    }
}
```

**Example Response:**
```
Company information for AAPL:

Name: Apple Inc
Sector: Technology
Industry: Consumer Electronics
Market Cap: $3000000000000
Description: Apple Inc. designs, manufactures, and markets smartphones...
Exchange: NASDAQ
Currency: USD
```

### get-crypto-exchange-rate

Retrieves real-time cryptocurrency exchange rates with additional market data.

**Input Schema:**
```json
{
    "crypto_symbol": {
        "type": "string",
        "description": "Cryptocurrency symbol (e.g., BTC, ETH)"
    },
    "market": {
        "type": "string",
        "description": "Market currency (e.g., USD, EUR)",
        "default": "USD"
    }
}
```

**Example Response:**
```
Cryptocurrency exchange rate for BTC/USD:

From: Bitcoin (BTC)
To: United States Dollar (USD)
Exchange Rate: 43521.45000
Last Updated: 2024-12-17 19:45:00 UTC
Bid Price: 43521.00000
Ask Price: 43522.00000
```

### get-time-series

Retrieves daily time series (OHLCV) data with optional date filtering.

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Stock symbol (e.g., AAPL, MSFT)"
    },
    "outputsize": {
        "type": "string",
        "description": "compact (latest 100 data points) or full (up to 20 years of data). When start_date or end_date is specified, defaults to 'full'",
        "default": "compact"
    },
    "start_date": {
        "type": "string",
        "description": "Optional: Start date in YYYY-MM-DD format for filtering results",
        "pattern": "^20[0-9]{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])$"
    },
    "end_date": {
        "type": "string",
        "description": "Optional: End date in YYYY-MM-DD format for filtering results",
        "pattern": "^20[0-9]{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])$"
    },
    "limit": {
        "type": "integer",
        "description": "Optional: Number of data points to return when no date filtering is applied (default: 5)",
        "default": 5,
        "minimum": 1
    }
}
```
**Example Response (Recent Data):**
```
Time Series Data for AAPL (Last Refreshed: 2024-12-17 16:00:00):
(Showing 5 most recent data points)

Date: 2024-12-16
Open: $195.09
High: $197.68
Low: $194.83
Close: $197.57
Volume: 55,751,011
---
Date: 2024-12-13
Open: $194.50
High: $196.25
Low: $193.80
Close: $195.12
Volume: 48,320,567
---
```

**Example Response (Date Range Filtering):**
```
Time Series Data for AAPL (Last Refreshed: 2024-12-17 16:00:00):
Date Range: 2024-12-01 to 2024-12-07 (5 data points)

Date: 2024-12-06
Open: $191.25
High: $193.80
Low: $190.55
Close: $192.90
Volume: 52,145,890
---
Date: 2024-12-05
Open: $189.75
High: $192.40
Low: $188.90
Close: $191.30
Volume: 47,892,345
---
```

### get-realtime-options

Retrieves real-time options chain data for a stock with optional Greeks calculation and contract filtering.

**⚠️ PREMIUM SUBSCRIPTION REQUIRED**: This endpoint requires Alpha Vantage Premium with either the 600 requests/minute or 1200 requests/minute plan. The standard 75 requests/minute plan and free accounts will receive placeholder/demo data instead of real market data. For most use cases, consider using `get-historical-options` which works with all API key tiers.

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Stock symbol (e.g., AAPL, MSFT)"
    },
    "require_greeks": {
        "type": "boolean",
        "description": "Optional: Enable Greeks and implied volatility calculation (default: false)",
        "default": false
    },
    "contract": {
        "type": "string",
        "description": "Optional: Specific options contract ID to retrieve"
    },
    "datatype": {
        "type": "string",
        "description": "Optional: Response format (json or csv, default: json)",
        "enum": ["json", "csv"],
        "default": "json"
    }
}
```

**Example Response:**
```
Realtime Options Data for AAPL
Last Updated: 2025-01-21 16:00:00

=== Expiration: 2025-01-24 ===

Strike: $220.0 (CALL)
Last: $5.25
Bid: $5.10
Ask: $5.30
Volume: 1250
Open Interest: 8420
IV: 0.28
Delta: 0.65
Gamma: 0.02
Theta: -0.15
Vega: 0.45
Rho: 0.12
---

Strike: $220.0 (PUT)
Last: $1.85
Bid: $1.80
Ask: $1.90
Volume: 820
Open Interest: 5240
IV: 0.25
Delta: -0.35
Gamma: 0.02
Theta: -0.12
Vega: 0.42
Rho: -0.08
---
```

**Note**: The above example shows real market data which is only available with Alpha Vantage Premium 600+ requests/minute plans. Users with free accounts or 75 requests/minute plans will see placeholder data (symbols like "XXYYZZ", dates like "2099-99-99") and should use `get-historical-options` instead.

### get-historical-options

Retrieves historical options chain data with advanced filtering and sorting capabilities to find specific contracts.

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Stock symbol (e.g., AAPL, MSFT)"
    },
    "date": {
        "type": "string",
        "description": "Optional: Trading date in YYYY-MM-DD format (defaults to previous trading day, must be after 2008-01-01)",
        "pattern": "^20[0-9]{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])$"
    },
    "expiry_date": {
        "type": "string",
        "description": "Optional: Filter by expiration date in YYYY-MM-DD format",
        "pattern": "^20[0-9]{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])$"
    },
    "min_strike": {
        "type": "number",
        "description": "Optional: Minimum strike price filter (e.g., 100.00)",
        "minimum": 0
    },
    "max_strike": {
        "type": "number",
        "description": "Optional: Maximum strike price filter (e.g., 200.00)",
        "minimum": 0
    },
    "contract_id": {
        "type": "string",
        "description": "Optional: Filter by specific contract ID (e.g., MSTR260116C00000500)"
    },
    "contract_type": {
        "type": "string",
        "description": "Optional: Filter by contract type (call or put)",
        "enum": ["call", "put", "C", "P"]
    },
    "limit": {
        "type": "integer",
        "description": "Optional: Number of contracts to return after filtering (default: 10, use -1 for all contracts)",
        "default": 10,
        "minimum": -1
    },
    "sort_by": {
        "type": "string",
        "description": "Optional: Field to sort by",
        "enum": ["strike", "expiration", "volume", "open_interest", "implied_volatility", "delta", "gamma", "theta", "vega", "rho", "last", "bid", "ask"],
        "default": "strike"
    },
    "sort_order": {
        "type": "string",
        "description": "Optional: Sort order",
        "enum": ["asc", "desc"],
        "default": "asc"
    }
}
```

**Example Response (Basic):**
```
Historical Options Data for AAPL (2024-02-20):
Status: success
Found 156 contracts, sorted by: strike (asc)

Contract Details:
Contract ID: AAPL240315C00190000
Expiration: 2024-03-15
Strike: $190.00
Type: call
Last: $8.45
Bid: $8.40
Ask: $8.50
Volume: 1245
Open Interest: 4567
Implied Volatility: 0.25
Greeks:
  Delta: 0.65
  Gamma: 0.04
  Theta: -0.15
  Vega: 0.30
  Rho: 0.25
---
```

**Example Response (Filtered):**
```
Historical Options Data for MSTR (2024-02-20):
Status: success
Filters: Expiry: 2026-01-16, Strike: min $400 - max $600, Type: call
Found 3 contracts, sorted by: strike (asc)

Contract Details:
Contract ID: MSTR260116C00000500
Expiration: 2026-01-16
Strike: $500.00
Type: call
Last: $125.30
Bid: $124.50
Ask: $126.10
Volume: 89
Open Interest: 1234
---
```

### get-etf-profile

Retrieves comprehensive ETF profile information including basic metrics, sector allocation, and top holdings.

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "ETF symbol (e.g., QQQ, SPY, VTI)"
    }
}
```

**Example Response:**
```
ETF profile for QQQ:

ETF Profile

Basic Information:
Net Assets: $352,700,000,000
Net Expense Ratio: 0.200%
Portfolio Turnover: 8.0%
Dividend Yield: 0.50%
Inception Date: 1999-03-10
Leveraged: NO

Sector Allocation:
INFORMATION TECHNOLOGY: 51.9%
COMMUNICATION SERVICES: 15.4%
CONSUMER DISCRETIONARY: 12.2%
CONSUMER STAPLES: 4.8%
HEALTHCARE: 4.5%
INDUSTRIALS: 4.4%
UTILITIES: 1.4%
MATERIALS: 1.3%
ENERGY: 0.5%
FINANCIALS: 0.4%

Top Holdings:
 1. NVDA - NVIDIA CORP: 9.80%
 2. MSFT - MICROSOFT CORP: 8.85%
 3. AAPL - APPLE INC: 7.35%
 4. AMZN - AMAZON.COM INC: 5.65%
 5. AVGO - BROADCOM INC: 5.14%
 6. META - META PLATFORMS INC CLASS A: 3.63%
 7. NFLX - NETFLIX INC: 3.10%
 8. TSLA - TESLA INC: 2.66%
 9. GOOGL - ALPHABET INC CLASS A: 2.49%
10. COST - COSTCO WHOLESALE CORP: 2.49%

... and 92 more holdings

Total Holdings: 102
```

### get-crypto-daily

Retrieves daily time series data for a cryptocurrency.

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Cryptocurrency symbol (e.g., BTC, ETH)"
    },
    "market": {
        "type": "string",
        "description": "Market currency (e.g., USD, EUR)",
        "default": "USD"
    }
}
```

**Example Response:**
```
Daily cryptocurrency time series for SOL in USD:

Daily Time Series for Solana (SOL)
Market: United States Dollar (USD)
Last Refreshed: 2025-04-17 00:00:00 UTC

Date: 2025-04-17
Open: 131.31000000 USD
High: 131.67000000 USD
Low: 130.74000000 USD
Close: 131.15000000 USD
Volume: 39652.22195178
---
Date: 2025-04-16
Open: 126.10000000 USD
High: 133.91000000 USD
Low: 123.46000000 USD
Close: 131.32000000 USD
Volume: 1764240.04195810
---
```

### get-crypto-weekly

Retrieves weekly time series data for a cryptocurrency.

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Cryptocurrency symbol (e.g., BTC, ETH)"
    },
    "market": {
        "type": "string",
        "description": "Market currency (e.g., USD, EUR)",
        "default": "USD"
    }
}
```

**Example Response:**
```
Weekly cryptocurrency time series for SOL in USD:

Weekly Time Series for Solana (SOL)
Market: United States Dollar (USD)
Last Refreshed: 2025-04-17 00:00:00 UTC

Date: 2025-04-17
Open: 128.32000000 USD
High: 136.00000000 USD
Low: 123.46000000 USD
Close: 131.15000000 USD
Volume: 4823091.05667581
---
Date: 2025-04-13
Open: 105.81000000 USD
High: 134.11000000 USD
Low: 95.16000000 USD
Close: 128.32000000 USD
Volume: 18015328.38860037
---
```

### get-crypto-monthly

Retrieves monthly time series data for a cryptocurrency.

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Cryptocurrency symbol (e.g., BTC, ETH)"
    },
    "market": {
        "type": "string",
        "description": "Market currency (e.g., USD, EUR)",
        "default": "USD"
    }
}
```

**Example Response:**
```
Monthly cryptocurrency time series for SOL in USD:

Monthly Time Series for Solana (SOL)
Market: United States Dollar (USD)
Last Refreshed: 2025-04-17 00:00:00 UTC

Date: 2025-04-17
Open: 124.51000000 USD
High: 136.18000000 USD
Low: 95.16000000 USD
Close: 131.15000000 USD
Volume: 34268628.85976021
---
Date: 2025-03-31
Open: 148.09000000 USD
High: 180.00000000 USD
Low: 112.00000000 USD
Close: 124.54000000 USD
Volume: 42360395.75443056
---
```

### get-earnings-calendar

Retrieves upcoming earnings calendar data for companies with customizable time horizons and sorting capabilities.

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Optional: Stock symbol to filter earnings for a specific company (e.g., AAPL, MSFT, IBM)"
    },
    "horizon": {
        "type": "string",
        "description": "Optional: Time horizon for earnings data (3month, 6month, or 12month)",
        "enum": ["3month", "6month", "12month"],
        "default": "12month"
    },
    "limit": {
        "type": "integer",
        "description": "Optional: Number of earnings entries to return (default: 100)",
        "default": 100,
        "minimum": 1
    },
    "sort_by": {
        "type": "string",
        "description": "Optional: Field to sort by",
        "enum": ["reportDate", "symbol", "name", "fiscalDateEnding", "estimate"],
        "default": "reportDate"
    },
    "sort_order": {
        "type": "string",
        "description": "Optional: Sort order",
        "enum": ["asc", "desc"],
        "default": "desc"
    }
}
```

**Example Response (Default - Latest First):**
```
Earnings calendar (12month):

Upcoming Earnings Calendar (Sorted by reportDate desc):

Company: NVDA - NVIDIA Corp
Report Date: 2025-08-15
Fiscal Date End: 2025-07-31
Estimate: $4.25 USD
---
Company: AAPL - Apple Inc
Report Date: 2025-07-30
Fiscal Date End: 2025-06-30
Estimate: $1.85 USD
---
Company: MSTR - MicroStrategy Inc
Report Date: 2025-05-08
Fiscal Date End: 2025-03-31
Estimate: $1.30 USD
---
Company: MSTR - MicroStrategy Inc
Report Date: 2025-02-06
Fiscal Date End: 2024-12-31
Estimate: $1.25 USD
---
```

**Example Response (Sorted by Symbol):**
```
Earnings calendar (12month):

Upcoming Earnings Calendar (Sorted by symbol asc):

Company: AAPL - Apple Inc
Report Date: 2025-07-30
Fiscal Date End: 2025-06-30
Estimate: $1.85 USD
---
Company: GOOGL - Alphabet Inc
Report Date: 2025-04-25
Fiscal Date End: 2025-03-31
Estimate: $2.15 USD
---
Company: MSTR - MicroStrategy Inc
Report Date: 2025-02-06
Fiscal Date End: 2024-12-31
Estimate: $1.25 USD
---
```

### get-historical-earnings

Retrieves historical earnings data for a specific company, including both annual and quarterly reports.

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Stock symbol for the company (e.g., AAPL, MSFT, IBM)"
    },
    "limit_annual": {
        "type": "integer",
        "description": "Optional: Number of annual earnings to return (default: 5)",
        "default": 5,
        "minimum": 1
    },
    "limit_quarterly": {
        "type": "integer",
        "description": "Optional: Number of quarterly earnings to return (default: 8)",
        "default": 8,
        "minimum": 1
    }
}
```

**Example Response:**
```
Historical Earnings for MSTR:

=== ANNUAL EARNINGS ===
Fiscal Year End: 2023-12-31
Reported EPS: $5.40
---
Fiscal Year End: 2022-12-31
Reported EPS: $-9.98
---

=== QUARTERLY EARNINGS ===
Fiscal Quarter End: 2024-09-30
Reported Date: 2024-10-30
Reported EPS: $1.10
Estimated EPS: $0.98
Surprise: +$0.12 (+12.24%)
Report Time: post-market
---
Fiscal Quarter End: 2024-06-30
Reported Date: 2024-08-01
Reported EPS: $1.05
Estimated EPS: $0.92
Surprise: +$0.13 (+14.13%)
Report Time: post-market
---
```

## Error Handling

The server includes comprehensive error handling for various scenarios:

- Rate limit exceeded
- Invalid API key
- Network connectivity issues
- Timeout handling
- Malformed responses

Error messages are returned in a clear, human-readable format.

## Prerequisites

- Python 3.12 or higher
- httpx
- mcp

## Contributors

- [berlinbra](https://github.com/berlinbra)
- [zzulanas](https://github.com/zzulanas)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License
This MCP server is licensed under the MIT License. 
This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
