from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_social_media_analyst(llm, toolkit):
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_stock_news_openai,
                # Phase 2: Social sentiment & community metrics
                toolkit.get_coingecko_community_stats,
                toolkit.get_cryptocompare_social_stats,
                toolkit.get_reddit_crypto_sentiment,
                toolkit.get_github_dev_activity,
            ]
        else:
            tools = [
                toolkit.get_reddit_stock_info,
                # Phase 2: Social sentiment & community metrics
                toolkit.get_coingecko_community_stats,
                toolkit.get_cryptocompare_social_stats,
                toolkit.get_reddit_crypto_sentiment,
                toolkit.get_github_dev_activity,
            ]

        system_message = (
            "You are a social media and community sentiment analyst tasked with analyzing social media activity, community engagement, and public sentiment."
            "\n\n**Phase 2 Social Sentiment Tools (NEW)**: For CRYPTO assets, use these specialized tools:"
            "\n- `get_coingecko_community_stats()`: Twitter, Reddit, Telegram followers & engagement rates"
            "\n- `get_cryptocompare_social_stats()`: Multi-platform social metrics (Twitter, Reddit, GitHub)"
            "\n- `get_reddit_crypto_sentiment()`: Analyze crypto subreddit posts & sentiment (r/cryptocurrency, r/bitcoin, etc.)"
            "\n- `get_github_dev_activity()`: Track development momentum via GitHub commits & contributors"
            "\n\n**How to interpret:**"
            "\n- High Twitter/Reddit growth = increasing awareness & potential price catalyst"
            "\n- High engagement rate (>5% Reddit) = very active community (bullish)"
            "\n- Rising GitHub activity = active development (bullish for long-term)"
            "\n- Low/declining social metrics = fading interest (bearish)"
            "\n- Reddit upvote ratio >85% = bullish sentiment, <70% = bearish sentiment"
            "\n\n**Analysis approach:**"
            "\n1. Check community size (Twitter followers, Reddit subscribers)"
            "\n2. Check engagement quality (Reddit active users, upvote ratios)"
            "\n3. Check development activity (GitHub commits, contributors)"
            "\n4. Synthesize: Is community growing? Is engagement high? Is development active?"
            "\n\nFor traditional STOCKS, use standard news/social tools. Try to look at all sources possible from social media to sentiment to news. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions."
            + """ Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read.""",
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
                    "For your reference, the current date is {current_date}. The current company we want to analyze is {ticker}",
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
            "sentiment_report": report,
        }

    return social_media_analyst_node
