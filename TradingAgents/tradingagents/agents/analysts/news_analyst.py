from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_news_analyst(llm, toolkit):
    def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_global_news_openai,
                toolkit.get_google_news,
                # Crypto news sources (Phase 1)
                toolkit.get_crypto_news_rss,
                toolkit.get_crypto_news_cryptocompare,
                toolkit.get_crypto_news_cryptopanic,
            ]
        else:
            tools = [
                toolkit.get_finnhub_news,
                toolkit.get_reddit_news,
                toolkit.get_google_news,
                # Crypto news sources (Phase 1)
                toolkit.get_crypto_news_rss,
                toolkit.get_crypto_news_cryptocompare,
                toolkit.get_crypto_news_cryptopanic,
            ]

        system_message = (
            "You are a news researcher tasked with analyzing recent news and trends over the past week. Please write a comprehensive report of the current state of the world that is relevant for trading and macroeconomics."
            "\n\nFor CRYPTO assets (e.g., BTC-USD, BTCUSDT, ETH-USD):"
            "\n- Use `get_crypto_news_rss()` for reliable general crypto market news from major publications (CoinDesk, Cointelegraph, Bitcoin Magazine, Decrypt)"
            "\n- Use `get_crypto_news_cryptocompare()` to get categorized crypto news (specify categories like 'BTC,ETH,trading,regulation')"
            "\n- Use `get_crypto_news_cryptopanic()` for ticker-specific crypto news (automatically falls back to RSS if API is blocked)"
            "\n- Focus on: regulatory developments, major partnerships, technological upgrades, market sentiment shifts, whale movements, institutional adoption"
            "\n\nFor STOCK assets:"
            "\n- Use traditional news sources (Finnhub, Google News, Reddit, OpenAI news)"
            "\n- Focus on: earnings, guidance, partnerships, regulatory issues, macroeconomic factors"
            "\n\nDo not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions."
            + """ Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."""
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
                    "For your reference, the current date is {current_date}. We are looking at the company {ticker}",
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
            "news_report": report,
        }

    return news_analyst_node
