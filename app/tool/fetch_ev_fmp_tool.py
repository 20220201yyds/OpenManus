from app.tool.base import BaseTool
from typing import Dict
import requests
from app.config import fmp_api_key
import json

class FetchEnterpriseValueFMP(BaseTool):
    """
    Fetches enterprise value and related financial metrics from Financial Modeling Prep (FMP) API.
    """

    name: str = "fetch_ev_fmp"
    description: str = "Fetch enterprise value and related metrics (debt, market cap, cash, etc.) from FMP API for a given stock ticker."
    parameters: dict = {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "The stock ticker symbol (e.g., AAPL, MSFT)"
            }
        },
        "required": ["ticker"],
    }

    async def execute(self, ticker: str) -> Dict:
        print(ticker)
        try:
            url = f"https://financialmodelingprep.com/api/v3/enterprise-value/{ticker}?limit=5&apikey={fmp_api_key}"
            response = requests.get(url)

            if response.status_code != 200:
                return {
                    "observation": f"Failed to fetch data from FMP API: {response.status_code}",
                    "success": False
                }

            data = response.json()
            print(data)
            if not isinstance(data, list):
                return {
                    "observation": "Unexpected response format from FMP (not a list).",
                    "success": False
                }

            ev_list = data[:5]  # Get recent 5

            structured = {
                entry.get("date", f"Year {i}"): {
                    "Stock Price": entry.get("stockPrice"),
                    "Shares": entry.get("numberOfShares"),
                    "Market Cap": entry.get("marketCapitalization"),
                    "Total Debt": entry.get("totalDebt"),
                    "Cash": entry.get("cashAndCashEquivalents"),
                    "Enterprise Value": entry.get("enterpriseValue")
                }
                for i, entry in enumerate(ev_list)
            }
            with open("workspace/income_data.json", "w") as f:
                json.dump(structured, f)
            return {
                "observation": structured,
                "success": True
            }

        except Exception as e:
            return {
                "observation": str(e),
                "success": False
            }