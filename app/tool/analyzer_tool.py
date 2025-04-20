import os
import json
from typing import Dict
from app.tool.base import BaseTool


class FinancialNarrativeGenerator(BaseTool):
    """
    Loads income and valuation data from local files and instructs GPT to generate a financial report.
    """

    name: str = "generate_financial_narrative"
    description: str = "Generates a 5-paragraph financial report using locally cached data. No input required."

    parameters: dict = {}  # No parameters needed

    async def execute(self) -> Dict:
        try:
            workspace_dir = os.path.join(os.getcwd(), "workspace")
            income_path = os.path.join(workspace_dir, "income_data.json")
            ev_path = os.path.join(workspace_dir, "ev_data.json")

            if not os.path.exists(income_path) or not os.path.exists(ev_path):
                return {
                    "observation": "❌ Required data files not found. Make sure to run fetch_income and fetch_ev first.",
                    "success": False
                }

            # ✅ 读取本地缓存的数据
            with open(income_path, "r") as f:
                income_data = json.load(f)

            with open(ev_path, "r") as f:
                ev_data = json.load(f)

            # 📌 固定 instruction prompt
            instruction = (
                "Using the financial data provided below, write a comprehensive financial analysis consisting of the following five sections:\n\n"

                "1. **Tagline**:\n"
                "Write a concise one-sentence summary (no more than 25 words) that captures the company's strategic positioning or investment outlook.\n\n"

                "2. **Company Overview**:\n"
                "Provide a factual overview of the company's core business operations, product/service portfolio, geographic reach, and competitive positioning in the industry. "
                "Do not include financial performance here — keep it operational. Limit to 250 words.\n\n"

                "3. **Investment Update**:\n"
                "Summarize the company’s financial performance over the past five years using actual data (e.g., revenue growth, net income, SG&A margin, operating margin, etc.). "
                "Identify any notable year-over-year trends, inflection points, or reversals. Use specific figures (e.g., 'Revenue rose 5.1% to $391B in 2024'). Keep it under 300 words.\n\n"

                "4. **Valuation**:\n"
                "Analyze the company's current valuation using enterprise value (EV), market capitalization, stock price trends, and profitability metrics. "
                "Include observations about valuation growth, EV/Revenue or EV/EBITDA trends (if data available), and interpret how this reflects investor sentiment. "
                "Support all statements with exact numbers and keep this section under 300 words.\n\n"

                "5. **Risks**:\n"
                "List exactly 3 bullet-point risks. Each risk must be data-driven and based on the financial or operational information available. "
                "Use the following format:\n"
                "- **[Short Title]** — [One to two sentence explanation with relevant figures or trends]\n"
                "- ...\n"
                "- ...\n\n"

                "Please write in clear, formal English with an analytical tone. Do not speculate or generalize. Avoid generic phrases and always support your statements with exact figures provided in the data. "
                "Return plain text only (no HTML or markdown formatting).")

            # 🧠 拼成大 prompt 交给 GPT Planner
            full_prompt = {
                "instruction": instruction,
                "financial_data": {
                    "financial_data": income_data,
                    "valuation_data": ev_data
                }
            }

            return {
                "observation": full_prompt,
                "success": True
            }

        except Exception as e:
            return {
                "observation": f"💥 Error: {str(e)}",
                "success": False
            }