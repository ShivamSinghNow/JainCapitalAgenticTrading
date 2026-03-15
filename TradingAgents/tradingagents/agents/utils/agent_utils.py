from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from typing import List
from typing import Annotated
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import RemoveMessage
from langchain_core.tools import tool
from datetime import date, timedelta, datetime
import functools
import pandas as pd
import os
from dateutil.relativedelta import relativedelta
from langchain_openai import ChatOpenAI
import TradingAgents.tradingagents.dataflows.interface as interface
from TradingAgents.tradingagents.default_config import DEFAULT_CONFIG
from langchain_core.messages import HumanMessage


def create_msg_delete():
    def delete_messages(state):
        """Clear messages and add placeholder for Anthropic compatibility"""
        messages = state["messages"]
        
        # Remove all messages
        removal_operations = [RemoveMessage(id=m.id) for m in messages]
        
        # Add a minimal placeholder message
        placeholder = HumanMessage(content="Continue")
        
        return {"messages": removal_operations + [placeholder]}
    
    return delete_messages


class Toolkit:
    _config = DEFAULT_CONFIG.copy()

    @classmethod
    def update_config(cls, config):
        """Update the class-level configuration."""
        cls._config.update(config)

    @property
    def config(self):
        """Access the configuration."""
        return self._config

    def __init__(self, config=None):
        if config:
            self.update_config(config)

    @staticmethod
    @tool
    def get_reddit_news(
        curr_date: Annotated[str, "Date you want to get news for in yyyy-mm-dd format"],
    ) -> str:
        """
        Retrieve global news from Reddit within a specified time frame.
        Args:
            curr_date (str): Date you want to get news for in yyyy-mm-dd format
        Returns:
            str: A formatted dataframe containing the latest global news from Reddit in the specified time frame.
        """
        
        global_news_result = interface.get_reddit_global_news(curr_date, 7, 5)

        return global_news_result

    @staticmethod
    @tool
    def get_finnhub_news(
        ticker: Annotated[
            str,
            "Search query of a company, e.g. 'AAPL, TSM, etc.",
        ],
        start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
        end_date: Annotated[str, "End date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest news about a given stock from Finnhub within a date range
        Args:
            ticker (str): Ticker of a company. e.g. AAPL, TSM
            start_date (str): Start date in yyyy-mm-dd format
            end_date (str): End date in yyyy-mm-dd format
        Returns:
            str: A formatted dataframe containing news about the company within the date range from start_date to end_date
        """

        end_date_str = end_date

        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        look_back_days = (end_date - start_date).days

        finnhub_news_result = interface.get_finnhub_news(
            ticker, end_date_str, look_back_days
        )

        return finnhub_news_result

    @staticmethod
    @tool
    def get_reddit_stock_info(
        ticker: Annotated[
            str,
            "Ticker of a company. e.g. AAPL, TSM",
        ],
        curr_date: Annotated[str, "Current date you want to get news for"],
    ) -> str:
        """
        Retrieve the latest news about a given stock from Reddit, given the current date.
        Args:
            ticker (str): Ticker of a company. e.g. AAPL, TSM
            curr_date (str): current date in yyyy-mm-dd format to get news for
        Returns:
            str: A formatted dataframe containing the latest news about the company on the given date
        """

        stock_news_results = interface.get_reddit_company_news(ticker, curr_date, 7, 5)

        return stock_news_results

    @staticmethod
    @tool
    def get_YFin_data(
        symbol: Annotated[str, "ticker symbol of the company"],
        start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
        end_date: Annotated[str, "End date in yyyy-mm-dd format"],
    ) -> str:
        """
        Retrieve the stock price data for a given ticker symbol from Yahoo Finance.
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
            start_date (str): Start date in yyyy-mm-dd format
            end_date (str): End date in yyyy-mm-dd format
        Returns:
            str: A formatted dataframe containing the stock price data for the specified ticker symbol in the specified date range.
        """

        result_data = interface.get_YFin_data(symbol, start_date, end_date)

        return result_data

    @staticmethod
    @tool
    def get_YFin_data_online(
        symbol: Annotated[str, "ticker symbol of the company"],
        start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
        end_date: Annotated[str, "End date in yyyy-mm-dd format"],
    ) -> str:
        """
        Retrieve the stock price data for a given ticker symbol from Yahoo Finance.
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
            start_date (str): Start date in yyyy-mm-dd format
            end_date (str): End date in yyyy-mm-dd format
        Returns:
            str: A formatted dataframe containing the stock price data for the specified ticker symbol in the specified date range.
        """

        result_data = interface.get_YFin_data_online(symbol, start_date, end_date)

        return result_data

    @staticmethod
    @tool
    def get_stockstats_indicators_report(
        symbol: Annotated[str, "ticker symbol of the company"],
        indicator: Annotated[
            str, "technical indicator to get the analysis and report of"
        ],
        curr_date: Annotated[
            str, "The current trading date you are trading on, YYYY-mm-dd"
        ],
        look_back_days: Annotated[int, "how many days to look back"] = 30,
    ) -> str:
        """
        Retrieve stock stats indicators for a given ticker symbol and indicator.
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
            indicator (str): Technical indicator to get the analysis and report of
            curr_date (str): The current trading date you are trading on, YYYY-mm-dd
            look_back_days (int): How many days to look back, default is 30
        Returns:
            str: A formatted dataframe containing the stock stats indicators for the specified ticker symbol and indicator.
        """

        result_stockstats = interface.get_stock_stats_indicators_window(
            symbol, indicator, curr_date, look_back_days, False
        )

        return result_stockstats

    @staticmethod
    @tool
    def get_stockstats_indicators_report_online(
        symbol: Annotated[str, "ticker symbol of the company"],
        indicator: Annotated[
            str, "technical indicator to get the analysis and report of"
        ],
        curr_date: Annotated[
            str, "The current trading date you are trading on, YYYY-mm-dd"
        ],
        look_back_days: Annotated[int, "how many days to look back"] = 30,
    ) -> str:
        """
        Retrieve stock stats indicators for a given ticker symbol and indicator.
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
            indicator (str): Technical indicator to get the analysis and report of
            curr_date (str): The current trading date you are trading on, YYYY-mm-dd
            look_back_days (int): How many days to look back, default is 30
        Returns:
            str: A formatted dataframe containing the stock stats indicators for the specified ticker symbol and indicator.
        """

        result_stockstats = interface.get_stock_stats_indicators_window(
            symbol, indicator, curr_date, look_back_days, True
        )

        return result_stockstats

    @staticmethod
    @tool
    def get_finnhub_company_insider_sentiment(
        ticker: Annotated[str, "ticker symbol for the company"],
        curr_date: Annotated[
            str,
            "current date of you are trading at, yyyy-mm-dd",
        ],
    ):
        """
        Retrieve insider sentiment information about a company (retrieved from public SEC information) for the past 30 days
        Args:
            ticker (str): ticker symbol of the company
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
            str: a report of the sentiment in the past 30 days starting at curr_date
        """

        data_sentiment = interface.get_finnhub_company_insider_sentiment(
            ticker, curr_date, 30
        )

        return data_sentiment

    @staticmethod
    @tool
    def get_finnhub_company_insider_transactions(
        ticker: Annotated[str, "ticker symbol"],
        curr_date: Annotated[
            str,
            "current date you are trading at, yyyy-mm-dd",
        ],
    ):
        """
        Retrieve insider transaction information about a company (retrieved from public SEC information) for the past 30 days
        Args:
            ticker (str): ticker symbol of the company
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
            str: a report of the company's insider transactions/trading information in the past 30 days
        """

        data_trans = interface.get_finnhub_company_insider_transactions(
            ticker, curr_date, 30
        )

        return data_trans

    @staticmethod
    @tool
    def get_simfin_balance_sheet(
        ticker: Annotated[str, "ticker symbol"],
        freq: Annotated[
            str,
            "reporting frequency of the company's financial history: annual/quarterly",
        ],
        curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
    ):
        """
        Retrieve the most recent balance sheet of a company
        Args:
            ticker (str): ticker symbol of the company
            freq (str): reporting frequency of the company's financial history: annual / quarterly
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
            str: a report of the company's most recent balance sheet
        """

        data_balance_sheet = interface.get_simfin_balance_sheet(ticker, freq, curr_date)

        return data_balance_sheet

    @staticmethod
    @tool
    def get_simfin_cashflow(
        ticker: Annotated[str, "ticker symbol"],
        freq: Annotated[
            str,
            "reporting frequency of the company's financial history: annual/quarterly",
        ],
        curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
    ):
        """
        Retrieve the most recent cash flow statement of a company
        Args:
            ticker (str): ticker symbol of the company
            freq (str): reporting frequency of the company's financial history: annual / quarterly
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
                str: a report of the company's most recent cash flow statement
        """

        data_cashflow = interface.get_simfin_cashflow(ticker, freq, curr_date)

        return data_cashflow

    @staticmethod
    @tool
    def get_simfin_income_stmt(
        ticker: Annotated[str, "ticker symbol"],
        freq: Annotated[
            str,
            "reporting frequency of the company's financial history: annual/quarterly",
        ],
        curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
    ):
        """
        Retrieve the most recent income statement of a company
        Args:
            ticker (str): ticker symbol of the company
            freq (str): reporting frequency of the company's financial history: annual / quarterly
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
                str: a report of the company's most recent income statement
        """

        data_income_stmt = interface.get_simfin_income_statements(
            ticker, freq, curr_date
        )

        return data_income_stmt

    @staticmethod
    @tool
    def get_google_news(
        query: Annotated[str, "Query to search with"],
        curr_date: Annotated[str, "Curr date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest news from Google News based on a query and date range.
        Args:
            query (str): Query to search with
            curr_date (str): Current date in yyyy-mm-dd format
            look_back_days (int): How many days to look back
        Returns:
            str: A formatted string containing the latest news from Google News based on the query and date range.
        """

        google_news_results = interface.get_google_news(query, curr_date, 7)

        return google_news_results

    @staticmethod
    @tool
    def get_stock_news_openai(
        ticker: Annotated[str, "the company's ticker"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest news about a given stock by using OpenAI's news API.
        Args:
            ticker (str): Ticker of a company. e.g. AAPL, TSM
            curr_date (str): Current date in yyyy-mm-dd format
        Returns:
            str: A formatted string containing the latest news about the company on the given date.
        """

        openai_news_results = interface.get_stock_news_openai(ticker, curr_date)

        return openai_news_results

    @staticmethod
    @tool
    def get_global_news_openai(
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest macroeconomics news on a given date using OpenAI's macroeconomics news API.
        Args:
            curr_date (str): Current date in yyyy-mm-dd format
        Returns:
            str: A formatted string containing the latest macroeconomic news on the given date.
        """

        openai_news_results = interface.get_global_news_openai(curr_date)

        return openai_news_results

    @staticmethod
    @tool
    def get_fundamentals_openai(
        ticker: Annotated[str, "the company's ticker"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest fundamental information about a given stock on a given date by using OpenAI's news API.
        Args:
            ticker (str): Ticker of a company. e.g. AAPL, TSM
            curr_date (str): Current date in yyyy-mm-dd format
        Returns:
            str: A formatted string containing the latest fundamental information about the company on the given date.
        """

        openai_fundamentals_results = interface.get_fundamentals_openai(
            ticker, curr_date
        )

        return openai_fundamentals_results

    # ===== CRYPTO EXCHANGE DATA TOOLS (Phase 1) =====

    @staticmethod
    @tool
    def get_order_book_imbalance(
        symbol: Annotated[str, "Crypto trading pair, e.g. 'BTCUSDT', 'ETHUSDT'"],
        depth: Annotated[int, "Order book depth levels to analyze (default 20)"] = 20,
    ) -> str:
        """
        Analyze order book imbalance for a crypto trading pair from Binance US.

        Provides insights into short-term price pressure by analyzing bid/ask depth.
        High bid volume indicates buying pressure, high ask volume indicates selling pressure.

        Args:
            symbol (str): Crypto trading pair (e.g., 'BTCUSDT', 'ETHUSDT')
            depth (int): Number of order book levels to analyze (default 20)

        Returns:
            str: Formatted report with bid/ask volumes, spread, and imbalance interpretation
        """
        result = interface.get_order_book_imbalance(symbol, depth)
        return result

    @staticmethod
    @tool
    def get_taker_buysell_volume(
        symbol: Annotated[str, "Crypto trading pair, e.g. 'BTCUSDT', 'ETHUSDT'"],
        interval: Annotated[str, "Time interval: '1m', '5m', '15m', '1h', '4h', '1d'"] = "1h",
        limit: Annotated[int, "Number of candles to analyze (default 24)"] = 24,
    ) -> str:
        """
        Analyze taker buy/sell volume ratios to identify aggressive buying vs selling.

        Taker buy volume indicates market orders hitting the ask (bullish).
        Taker sell volume indicates market orders hitting the bid (bearish).
        High taker buy ratio suggests strong buying pressure and potential uptrend.

        Args:
            symbol (str): Crypto trading pair (e.g., 'BTCUSDT', 'ETHUSDT')
            interval (str): Candlestick interval ('1m', '5m', '15m', '1h', '4h', '1d')
            limit (int): Number of recent candles to analyze (default 24)

        Returns:
            str: Formatted report showing buy/sell volume ratios and trend interpretation
        """
        result = interface.get_taker_buysell_volume(symbol, interval, limit)
        return result

    @staticmethod
    @tool
    def get_funding_rate(
        symbol: Annotated[str, "Crypto perpetual pair, e.g. 'BTCUSDT', 'ETHUSDT'"],
        limit: Annotated[int, "Number of historical funding rates to retrieve"] = 10,
    ) -> str:
        """
        Get funding rates for crypto perpetual futures (uses Bybit as Binance US doesn't support futures).

        Funding rates indicate sentiment in perpetual futures markets:
        - Positive rate: Longs pay shorts (bullish sentiment, potential overheating)
        - Negative rate: Shorts pay longs (bearish sentiment, potential oversold)
        - Extreme rates often precede trend reversals

        Args:
            symbol (str): Perpetual futures pair (e.g., 'BTCUSDT', 'ETHUSDT')
            limit (int): Number of historical funding rate periods (default 10)

        Returns:
            str: Formatted report with funding rate history and sentiment interpretation
        """
        result = interface.get_binance_funding_rate(symbol, limit)
        return result

    @staticmethod
    @tool
    def get_open_interest(
        symbol: Annotated[str, "Crypto perpetual pair, e.g. 'BTCUSDT', 'ETHUSDT'"],
    ) -> str:
        """
        Get open interest for crypto perpetual futures (uses Bybit as Binance US doesn't support futures).

        Open interest represents total outstanding futures contracts:
        - Rising OI + rising price = strong uptrend (new money entering longs)
        - Rising OI + falling price = strong downtrend (new money entering shorts)
        - Falling OI = position unwinding, potential trend exhaustion

        Args:
            symbol (str): Perpetual futures pair (e.g., 'BTCUSDT', 'ETHUSDT')

        Returns:
            str: Formatted report with current open interest and trend interpretation
        """
        result = interface.get_binance_open_interest(symbol)
        return result

    # ===== CRYPTO NEWS TOOLS (Phase 1) =====

    @staticmethod
    @tool
    def get_crypto_news_rss(
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
        look_back_days: Annotated[int, "Number of days to look back for news"] = 7,
    ) -> str:
        """
        Get crypto news from major publications via RSS feeds (CoinDesk, Cointelegraph, Bitcoin Magazine, Decrypt).

        100% reliable source requiring no API key. Provides general crypto market news,
        not filtered by specific ticker. Best for overall market sentiment and major events.

        Args:
            curr_date (str): Current date in yyyy-mm-dd format
            look_back_days (int): Days to look back for news articles (default 7)

        Returns:
            str: Formatted news articles from major crypto publications
        """
        result = interface.get_rss_crypto_news(curr_date, look_back_days, max_articles_per_source=10)
        return result

    @staticmethod
    @tool
    def get_crypto_news_cryptopanic(
        ticker: Annotated[str, "Crypto ticker, e.g. 'BTC', 'ETH', 'SOL'"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
        look_back_days: Annotated[int, "Number of days to look back"] = 7,
    ) -> str:
        """
        Get ticker-specific crypto news with automatic RSS fallback (CryptoPanic API often blocked by Cloudflare).

        Attempts to fetch news specific to the crypto ticker. If CryptoPanic API is unavailable,
        automatically falls back to RSS feeds. Provides broader crypto news coverage.

        Args:
            ticker (str): Crypto ticker symbol (e.g., 'BTC', 'ETH', 'SOL')
            curr_date (str): Current date in yyyy-mm-dd format
            look_back_days (int): Days to look back for news (default 7)

        Returns:
            str: Formatted crypto news articles with sentiment (if available from CryptoPanic) or RSS news
        """
        result = interface.get_cryptopanic_news(ticker, curr_date, look_back_days)
        return result

    @staticmethod
    @tool
    def get_crypto_news_cryptocompare(
        categories: Annotated[str, "News categories: 'BTC', 'ETH', 'trading', 'regulation', etc."] = "BTC,ETH",
        limit: Annotated[int, "Number of articles to retrieve"] = 20,
    ) -> str:
        """
        Get categorized crypto news from CryptoCompare API (requires free API key).

        Provides real-time crypto news from major sources with category filtering.
        Useful for getting news related to specific cryptocurrencies or topics.

        Args:
            categories (str): Comma-separated categories (e.g., 'BTC,ETH,trading,regulation')
            limit (int): Number of articles to retrieve (default 20)

        Returns:
            str: Formatted news articles from CryptoCompare with source and date information
        """
        result = interface.get_cryptocompare_news(categories, limit)
        return result

    # ===== DATA VALIDATION TOOLS (Phase 1) =====

    @staticmethod
    @tool
    def cross_validate_prices(
        price1: Annotated[float, "Price from first source"],
        price2: Annotated[float, "Price from second source"],
        source1: Annotated[str, "Name of first data source"],
        source2: Annotated[str, "Name of second data source"],
        symbol: Annotated[str, "Trading symbol being validated"],
        max_diff_pct: Annotated[float, "Maximum acceptable difference percentage"] = 5.0,
    ) -> str:
        """
        Cross-validate price data from two different sources to detect discrepancies.

        Compares prices from different data sources (e.g., YFinance vs Binance) to ensure
        data quality. Large discrepancies may indicate stale data, API errors, or market issues.

        Args:
            price1 (float): Price from first source
            price2 (float): Price from second source
            source1 (str): Name of first data source (e.g., 'YFinance')
            source2 (str): Name of second data source (e.g., 'Binance US')
            symbol (str): Trading symbol (e.g., 'BTC-USD')
            max_diff_pct (float): Maximum acceptable price difference percentage (default 5.0%)

        Returns:
            str: Validation result with warning if prices differ significantly
        """
        is_valid, warning = interface.cross_validate_prices(
            price1, price2, source1, source2, symbol, max_diff_pct
        )

        result = f"Price Validation for {symbol}:\n"
        result += f"  {source1}: ${price1:,.2f}\n"
        result += f"  {source2}: ${price2:,.2f}\n"
        result += f"  Valid: {is_valid}\n"
        if warning:
            result += f"  ⚠️ Warning: {warning}\n"

        return result

    # ===== ON-CHAIN & SOCIAL SENTIMENT TOOLS (Phase 2) =====

    @staticmethod
    @tool
    def get_coingecko_market_metrics(
        ticker: Annotated[str, "Crypto ticker, e.g. 'BTC', 'ETH', 'BTC-USD'"],
    ) -> str:
        """
        Get comprehensive market metrics for a cryptocurrency from CoinGecko.

        Provides fundamental crypto data: market cap, supply, volume, price changes,
        ATH/ATL, and trend analysis. Essential for fundamental crypto analysis.

        Args:
            ticker (str): Crypto ticker (e.g., 'BTC', 'ETH', 'BTC-USD')

        Returns:
            str: Detailed market metrics report with trend analysis
        """
        result = interface.get_coingecko_market_metrics(ticker)
        return result

    @staticmethod
    @tool
    def get_coingecko_developer_activity(
        ticker: Annotated[str, "Crypto ticker, e.g. 'BTC', 'ETH'"],
    ) -> str:
        """
        Get developer activity metrics from CoinGecko.

        Tracks GitHub commits, contributors, code changes, issues/PRs. Strong development
        activity indicates healthy long-term project fundamentals.

        Args:
            ticker (str): Crypto ticker (e.g., 'BTC', 'ETH')

        Returns:
            str: Developer activity report with GitHub stats and analysis
        """
        result = interface.get_coingecko_developer_activity(ticker)
        return result

    @staticmethod
    @tool
    def get_coingecko_community_stats(
        ticker: Annotated[str, "Crypto ticker, e.g. 'BTC', 'ETH'"],
    ) -> str:
        """
        Get community statistics from CoinGecko.

        Tracks Twitter, Reddit, Telegram, Facebook following and engagement.
        High community growth indicates increasing awareness and potential demand.

        Args:
            ticker (str): Crypto ticker (e.g., 'BTC', 'ETH')

        Returns:
            str: Community statistics report with social media metrics
        """
        result = interface.get_coingecko_community_stats(ticker)
        return result

    @staticmethod
    @tool
    def get_bitcoin_network_metrics() -> str:
        """
        Get Bitcoin-specific network metrics from Blockchain.info.

        Provides hash rate, difficulty, mempool size, transaction count, block stats.
        Critical for understanding Bitcoin network health and security.

        Returns:
            str: Bitcoin network metrics report with security and usage analysis
        """
        result = interface.get_bitcoin_network_metrics()
        return result

    @staticmethod
    @tool
    def get_bitcoin_mining_metrics() -> str:
        """
        Get Bitcoin mining profitability and production metrics.

        Tracks mining difficulty, block production, miner revenue, transaction fees.
        Helps assess mining health and network economics.

        Returns:
            str: Bitcoin mining metrics report with profitability analysis
        """
        result = interface.get_bitcoin_mining_metrics()
        return result

    @staticmethod
    @tool
    def get_fear_greed_index() -> str:
        """
        Get crypto Fear & Greed Index from Alternative.me.

        Composite sentiment indicator (0-100) based on volatility, volume, social media,
        surveys, and market dominance. Useful for contrarian trading signals.

        Scale:
        - 0-24: Extreme Fear (potential buying opportunity)
        - 25-49: Fear (caution, selective buying)
        - 50-74: Greed (normal risk management)
        - 75-100: Extreme Greed (potential top, profit-taking)

        Returns:
            str: Fear & Greed Index with 30-day history and trend analysis
        """
        result = interface.get_fear_greed_index()
        return result

    @staticmethod
    @tool
    def get_coincap_rankings(
        limit: Annotated[int, "Number of top coins to retrieve"] = 20,
    ) -> str:
        """
        Get cryptocurrency market cap rankings from CoinCap.

        Shows top cryptocurrencies by market cap with price, volume, and supply data.
        Useful for market breadth analysis (% gaining vs losing).

        Args:
            limit (int): Number of top coins to retrieve (default 20)

        Returns:
            str: Market rankings with price changes and market breadth analysis
        """
        result = interface.get_coincap_rankings(limit)
        return result

    @staticmethod
    @tool
    def get_cryptocompare_social_stats(
        ticker: Annotated[str, "Crypto ticker, e.g. 'BTC', 'ETH'"],
    ) -> str:
        """
        Get social media statistics from CryptoCompare (requires free API key).

        Tracks Twitter, Reddit, GitHub metrics across multiple platforms.
        Provides social sentiment and community engagement trends.

        Args:
            ticker (str): Crypto ticker (e.g., 'BTC', 'ETH')

        Returns:
            str: Social media statistics report (or error if API key not configured)
        """
        result = interface.get_cryptocompare_social_stats(ticker)
        return result

    @staticmethod
    @tool
    def get_reddit_crypto_sentiment(
        subreddit: Annotated[str, "Subreddit name, e.g. 'cryptocurrency', 'bitcoin'"],
        limit: Annotated[int, "Number of posts to analyze"] = 25,
    ) -> str:
        """
        Analyze crypto subreddit sentiment from Reddit.

        Scrapes recent posts from crypto subreddits and analyzes titles for sentiment.
        Useful for gauging community mood and narrative trends.

        Args:
            subreddit (str): Subreddit to analyze (e.g., 'cryptocurrency', 'bitcoin', 'ethereum')
            limit (int): Number of posts to retrieve (default 25)

        Returns:
            str: Sentiment analysis with post titles, scores, and upvote ratios
        """
        result = interface.get_reddit_crypto_sentiment(subreddit, limit)
        return result

    @staticmethod
    @tool
    def get_github_dev_activity(
        ticker: Annotated[str, "Crypto ticker, e.g. 'BTC', 'ETH'"],
    ) -> str:
        """
        Get GitHub development activity for crypto projects (requires free GitHub token).

        Tracks commits, contributors, PRs, issues for the last 30 days.
        High development activity indicates active project maintenance.

        Args:
            ticker (str): Crypto ticker (e.g., 'BTC', 'ETH')

        Returns:
            str: GitHub activity report with commit and contributor metrics
        """
        result = interface.get_github_dev_activity(ticker)
        return result

    @staticmethod
    @tool
    def get_github_repo_stats(
        ticker: Annotated[str, "Crypto ticker, e.g. 'BTC', 'ETH'"],
    ) -> str:
        """
        Get GitHub repository statistics (alias for get_github_dev_activity).

        Provides same data as get_github_dev_activity - stars, forks, commits, contributors.

        Args:
            ticker (str): Crypto ticker (e.g., 'BTC', 'ETH')

        Returns:
            str: GitHub repository statistics report
        """
        result = interface.get_github_repo_stats(ticker)
        return result
