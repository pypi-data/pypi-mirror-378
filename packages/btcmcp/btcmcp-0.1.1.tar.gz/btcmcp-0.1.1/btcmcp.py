from typing import Any
import httpx
import requests
import json
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("btcmcp")

@mcp.tool()
def get_btc_price() -> float | None:
    """Get the current price of Bitcoin from Binance API"""
    try:
        # Binance API endpoint for BTC/USDT price
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        
        # Make the API request
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the JSON response
        data = response.json()
        
        # Extract the price and convert to float
        price = float(data['price'])
        
        return price
        
    except Exception:
        # Handle any errors and return 0.0
        return None

def main():
    """Main entry point for the CLI"""
    mcp.run()

if __name__ == "__main__":
    main()

