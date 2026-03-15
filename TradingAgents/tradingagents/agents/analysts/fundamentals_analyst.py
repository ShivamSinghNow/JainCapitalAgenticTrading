from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_fundamentals_analyst(llm, toolkit):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_fundamentals_openai,
                # Data validation (Phase 1)
                toolkit.cross_validate_prices,
                # On-chain & fundamental metrics (Phase 2)
                toolkit.get_coingecko_market_metrics,
                toolkit.get_coingecko_developer_activity,
                toolkit.get_bitcoin_network_metrics,
                toolkit.get_bitcoin_mining_metrics,
            ]
        else:
            tools = [
                toolkit.get_finnhub_company_insider_sentiment,
                toolkit.get_finnhub_company_insider_transactions,
                toolkit.get_simfin_balance_sheet,
                toolkit.get_simfin_cashflow,
                toolkit.get_simfin_income_stmt,
                # Data validation (Phase 1)
                toolkit.cross_validate_prices,
                # On-chain & fundamental metrics (Phase 2)
                toolkit.get_coingecko_market_metrics,
                toolkit.get_coingecko_developer_activity,
                toolkit.get_bitcoin_network_metrics,
                toolkit.get_bitcoin_mining_metrics,
            ]

        system_message = (
            "You are a researcher tasked with analyzing fundamental information about an asset (stock or cryptocurrency)."
            "\n\nFor CRYPTO assets (e.g., BTC-USD, BTCUSDT, ETH-USD):"
            "\n- Traditional fundamental analysis (balance sheets, income statements) doesn't apply to crypto"
            "\n- **Phase 2 On-Chain Tools (NEW)**: Use these crypto-specific fundamental analysis tools:"
            "\n  - `get_coingecko_market_metrics()`: Market cap, supply metrics, volume, ATH/ATL, price changes"
            "\n  - `get_coingecko_developer_activity()`: GitHub commits, contributors, code changes (last 4 weeks)"
            "\n  - `get_bitcoin_network_metrics()`: Hash rate, difficulty, mempool, transactions (BTC only)"
            "\n  - `get_bitcoin_mining_metrics()`: Mining profitability, block production, fees (BTC only)"
            "\n- Use `cross_validate_prices()` to ensure data quality across different sources (e.g., YFinance vs Binance)"
            "\n- Crypto fundamentals = on-chain metrics + market cap + development activity + network health"
            "\n- For market cap analysis: Compare circulating vs max supply, check if supply is inflationary/deflationary"
            "\n- For dev activity: Active development (>100 commits/month) = bullish, dormant repos = bearish"
            "\n- For network health: Rising hash rate = growing security, low mempool = fast confirmations"
            "\n\nFor STOCK assets:"
            "\n- Use traditional fundamental analysis tools: balance sheets, income statements, cash flow, insider transactions"
            "\n- Analyze: financial health, growth trajectory, profitability, debt levels, insider confidence"
            "\n- Use `cross_validate_prices()` to verify data quality"
            "\n\nMake sure to include as much detail as possible. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions."
            + " Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read.",
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. The company we want to look at is {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
