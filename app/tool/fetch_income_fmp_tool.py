from app.tool.base import BaseTool
from typing import Dict
import requests
from app.config import fmp_api_key
import json

class FetchIncomeStatementFMP(BaseTool):
    """
    Fetch the last 5 years of income statement data from FMP API, and compute financial ratios.
    """

    name: str = "fetch_income_statement_fmp"
    description: str = "Fetches and computes the last 5 years of income statement data (revenue, SG&A, net income, operating income, margins, etc.) from FMP API."
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
        try:
            url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?limit=5&apikey={fmp_api_key}"
            response = requests.get(url)

            if response.status_code != 200:
                return {
                    "observation": f"FMP API error: {response.status_code}",
                    "success": False
                }

            data = response.json()
            summary = {}

            for entry in data:
                date = entry.get("date", "unknown")
                revenue = entry.get("revenue") or 0
                sga = entry.get("sellingGeneralAndAdministrativeExpenses") or 0
                net_income = entry.get("netIncome") or 0
                operating_income = entry.get("operatingIncome") or 0

                # margin 计算（避免除以0）
                def safe_div(n, d):
                    return round(n / d, 4) if d else None

                summary[date] = {
                    "Revenue": revenue,
                    "Operating Expenses": entry.get("operatingExpenses", "N/A"),
                    "R&D": entry.get("researchAndDevelopmentExpenses", "N/A"),
                    "SG&A": sga,
                    "Operating Income": operating_income,
                    "Net Income": net_income,
                    "SG&A Margin": safe_div(sga, revenue),
                    "Operating Margin": safe_div(operating_income, revenue),
                    "Net Margin": safe_div(net_income, revenue),
                }

            with open("workspace/ev_data.json", "w") as f:
                json.dump(summary, f)

            return {
                "observation": summary,
                "success": True
            }

        except Exception as e:
            return {
                "observation": str(e),
                "success": False
            }