"""
Crypto News Utilities - FREE Crypto-Native News Sources

This module provides access to crypto news using completely free APIs:
- CryptoPanic API (3000 requests/day free tier)
- CryptoCompare News API (100k calls/month free tier)
- RSS Feed Aggregation (CoinDesk, Cointelegraph, Bitcoin Magazine, Decrypt)
- CoinGecko Events API (no authentication required)

All functions use FREE tiers - minimal setup required!
"""

from typing import Annotated, List, Dict, Optional
import requests
import feedparser
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from .config import get_config
from .utils import retry_on_failure


# ===== CRYPTOPANIC NEWS FUNCTIONS =====

def get_cryptopanic_news(
    ticker: Annotated[str, "Cryptocurrency ticker (e.g., 'BTC', 'ETH', 'SOL')"],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "Number of days to look back"] = 7,
    filter_by: Annotated[str, "Filter: 'rising', 'hot', 'bullish', 'bearish', 'important', or 'all'"] = "all",
) -> str:
    """
    Get crypto news - uses RSS feeds as primary source (CryptoPanic API blocked by Cloudflare).

    This function now uses RSS feed aggregation as the primary/fallback source since
    CryptoPanic API has Cloudflare protection that blocks automated requests.

    RSS Sources (100% reliable, no API key needed):
    - CoinDesk: https://www.coindesk.com/arc/outboundfeeds/rss/
    - Cointelegraph: https://cointelegraph.com/rss
    - Bitcoin Magazine: https://bitcoinmagazine.com/.rss/full/
    - Decrypt: https://decrypt.co/feed

    Args:
        ticker: Crypto ticker (BTC, ETH, SOL, etc.) - used for documentation only
        curr_date: Current date
        look_back_days: Days to look back
        filter_by: Filter criteria (not used with RSS fallback)

    Returns:
        Formatted string with crypto news from RSS feeds
    """
    config = get_config()
    api_key = config.get('api_keys', {}).get('cryptopanic', '')

    # Try CryptoPanic API first if API key is configured
    if api_key:
        # CryptoPanic API v1 endpoint
        url = "https://cryptopanic.com/api/v1/posts/"

        # Normalize ticker
        currencies = ticker.upper()

        params = {
            "auth_token": api_key,
            "currencies": currencies,
        }

        # Add filter if specified
        if filter_by != "all" and filter_by in ["rising", "hot", "bullish", "bearish", "important"]:
            params["filter"] = filter_by

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            results = data.get('results', [])

            if results:
                # Filter by date
                start_date = datetime.strptime(curr_date, "%Y-%m-%d")
                before = start_date - relativedelta(days=look_back_days)

                result_str = f"## CryptoPanic News for {ticker} (from {before.strftime('%Y-%m-%d')} to {curr_date}):\n\n"

                news_count = 0
                sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}

                for article in results:
                    published_at = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))

                    # Check if within date range
                    if published_at.replace(tzinfo=None) < before or published_at.replace(tzinfo=None) > start_date:
                        continue

                    title = article.get('title', 'No title')
                    url_link = article.get('url', '')
                    source = article.get('source', {}).get('title', 'Unknown')

                    # Get sentiment/votes
                    votes = article.get('votes', {})
                    positive = votes.get('positive', 0)
                    negative = votes.get('negative', 0)
                    important = votes.get('important', 0)
                    liked = votes.get('liked', 0)
                    disliked = votes.get('disliked', 0)

                    # Determine overall sentiment
                    if positive > negative:
                        sentiment = "POSITIVE 🟢"
                        sentiment_counts["positive"] += 1
                    elif negative > positive:
                        sentiment = "NEGATIVE 🔴"
                        sentiment_counts["negative"] += 1
                    else:
                        sentiment = "NEUTRAL ⚪"
                        sentiment_counts["neutral"] += 1

                    # Format article
                    result_str += f"### {title}\n"
                    result_str += f"**Source**: {source} | **Date**: {published_at.strftime('%Y-%m-%d %H:%M UTC')}\n"
                    result_str += f"**Sentiment**: {sentiment}"

                    if important > 0:
                        result_str += f" | **IMPORTANT** ({important} votes)"

                    result_str += f"\n**Engagement**: +{positive}/-{negative}"

                    if liked > 0 or disliked > 0:
                        result_str += f" | Liked: {liked}, Disliked: {disliked}"

                    result_str += f"\n[Read more]({url_link})\n\n"

                    news_count += 1

                    # Limit to 20 articles
                    if news_count >= 20:
                        break

                # Summary statistics
                if news_count > 0:
                    result_str += f"### Summary:\n"
                    result_str += f"- **Total Articles**: {news_count}\n"
                    result_str += f"- **Positive Sentiment**: {sentiment_counts['positive']} ({sentiment_counts['positive']/news_count*100:.0f}%)\n"
                    result_str += f"- **Negative Sentiment**: {sentiment_counts['negative']} ({sentiment_counts['negative']/news_count*100:.0f}%)\n"
                    result_str += f"- **Neutral Sentiment**: {sentiment_counts['neutral']} ({sentiment_counts['neutral']/news_count*100:.0f}%)\n"

                    # Overall sentiment
                    if sentiment_counts['positive'] > sentiment_counts['negative'] * 1.5:
                        overall = "BULLISH - Predominantly positive news coverage"
                    elif sentiment_counts['negative'] > sentiment_counts['positive'] * 1.5:
                        overall = "BEARISH - Predominantly negative news coverage"
                    else:
                        overall = "MIXED - Balanced positive and negative coverage"

                    result_str += f"\n**Overall News Sentiment**: {overall}\n"

                    return result_str

        except Exception as e:
            # CryptoPanic failed, fall through to RSS fallback
            pass

    # Fallback to RSS feeds (primary source now due to Cloudflare blocking)
    # Note: RSS feeds don't support ticker filtering, so we get general crypto news
    print(f"⚠️  CryptoPanic API unavailable (Cloudflare protection). Using RSS feeds as alternative...")

    rss_result = get_rss_crypto_news(curr_date, look_back_days, max_articles_per_source=10)

    # Add a note about the source
    prefix = f"## Crypto News from RSS Feeds (CryptoPanic unavailable)\n"
    prefix += f"**Note**: CryptoPanic API blocked by Cloudflare. Using reliable RSS sources instead.\n\n"

    return prefix + rss_result


# ===== CRYPTOCOMPARE NEWS FUNCTIONS =====

@retry_on_failure(max_retries=3, delay=2)
def get_cryptocompare_news(
    categories: Annotated[str, "News categories: 'BTC', 'ETH', 'trading', 'regulation', etc."] = "",
    limit: Annotated[int, "Number of articles to fetch"] = 20,
) -> str:
    """
    Get crypto news from CryptoCompare.

    CryptoCompare provides:
    - Real-time crypto news from major publications
    - Category filtering
    - Source filtering

    NOTE: Requires free API key from https://min-api.cryptocompare.com
    Free tier: 100,000 calls/month (plenty for this use case)

    Args:
        categories: Comma-separated categories (e.g., 'BTC,ETH,trading')
        limit: Number of articles

    Returns:
        Formatted string with crypto news
    """
    config = get_config()
    api_key = config.get('api_keys', {}).get('cryptocompare', '')

    if not api_key:
        return "CryptoCompare API key not configured. Get free key at https://min-api.cryptocompare.com and add to config."

    url = "https://min-api.cryptocompare.com/data/v2/news/"

    params = {"lang": "EN"}

    if categories:
        params["categories"] = categories.upper()

    headers = {"Authorization": f"Apikey {api_key}"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        articles = data.get('Data', [])

        if not articles:
            return f"No CryptoCompare news found for categories: {categories}"

        # Limit articles
        articles = articles[:limit]

        result_str = f"## CryptoCompare Crypto News"
        if categories:
            result_str += f" (Categories: {categories})"
        result_str += ":\n\n"

        for article in articles:
            title = article.get('title', 'No title')
            body = article.get('body', '')[:300]  # First 300 chars
            published = article.get('published_on', 0)
            source = article.get('source', 'Unknown')
            url_link = article.get('url', '')
            categories_list = article.get('categories', '').split('|')

            # Format timestamp
            dt = datetime.fromtimestamp(published)

            result_str += f"### {title}\n"
            result_str += f"**Source**: {source} | **Date**: {dt.strftime('%Y-%m-%d %H:%M UTC')}\n"
            result_str += f"**Categories**: {', '.join(categories_list[:5])}\n"  # First 5 categories
            result_str += f"{body}...\n"
            result_str += f"[Read more]({url_link})\n\n"

        return result_str

    except requests.exceptions.RequestException as e:
        return f"Error fetching CryptoCompare news: {str(e)}"
    except Exception as e:
        return f"Error processing CryptoCompare data: {str(e)}"


# ===== RSS FEED AGGREGATION =====

@retry_on_failure(max_retries=3, delay=2)
def get_rss_crypto_news(
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "Number of days to look back"] = 7,
    max_articles_per_source: Annotated[int, "Max articles per source"] = 10,
) -> str:
    """
    Aggregate crypto news from RSS feeds (100% FREE, no API keys).

    RSS Sources:
    - CoinDesk: https://www.coindesk.com/arc/outboundfeeds/rss/
    - Cointelegraph: https://cointelegraph.com/rss
    - Bitcoin Magazine: https://bitcoinmagazine.com/.rss/full/
    - Decrypt: https://decrypt.co/feed

    Requires: feedparser library (pip install feedparser)

    Args:
        curr_date: Current date
        look_back_days: Days to look back
        max_articles_per_source: Max articles per RSS source

    Returns:
        Formatted string with aggregated crypto news
    """
    rss_feeds = {
        "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "Cointelegraph": "https://cointelegraph.com/rss",
        "Bitcoin Magazine": "https://bitcoinmagazine.com/.rss/full/",
        "Decrypt": "https://decrypt.co/feed",
    }

    # Calculate date range
    start_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date - timedelta(days=look_back_days)

    result_str = f"## Crypto News from Major Publications (from {before.strftime('%Y-%m-%d')} to {curr_date}):\n\n"

    all_articles = []

    for source_name, feed_url in rss_feeds.items():
        try:
            feed = feedparser.parse(feed_url)

            article_count = 0

            for entry in feed.entries:
                # Parse published date
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_dt = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_dt = datetime(*entry.updated_parsed[:6])
                else:
                    # Skip if no date
                    continue

                # Check if within date range
                if published_dt < before or published_dt > start_date:
                    continue

                title = entry.get('title', 'No title')
                link = entry.get('link', '')
                summary = entry.get('summary', '')[:300] if 'summary' in entry else ''

                all_articles.append({
                    'source': source_name,
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'published': published_dt,
                })

                article_count += 1

                if article_count >= max_articles_per_source:
                    break

        except Exception as e:
            result_str += f"**{source_name}**: Error fetching RSS feed - {str(e)[:50]}\n\n"

    # Sort all articles by date (most recent first)
    all_articles.sort(key=lambda x: x['published'], reverse=True)

    if not all_articles:
        return f"No RSS news articles found for the specified date range."

    # Format articles
    for article in all_articles[:30]:  # Limit to 30 total articles
        result_str += f"### {article['title']}\n"
        result_str += f"**Source**: {article['source']} | **Date**: {article['published'].strftime('%Y-%m-%d %H:%M')}\n"

        if article['summary']:
            result_str += f"{article['summary']}...\n"

        result_str += f"[Read more]({article['link']})\n\n"

    result_str += f"\n**Total Articles**: {len(all_articles[:30])}\n"
    result_str += f"**Sources**: {', '.join(rss_feeds.keys())}\n"

    return result_str


# ===== COINGECKO EVENTS =====

@retry_on_failure(max_retries=3, delay=2)
def get_coingecko_events(
    coin_id: Annotated[str, "CoinGecko coin ID (e.g., 'bitcoin', 'ethereum', 'solana')"] = "",
    upcoming_only: Annotated[bool, "Only show upcoming events"] = True,
) -> str:
    """
    Get crypto events from CoinGecko (100% FREE, no API key required).

    Events include:
    - Hard forks
    - Airdrops
    - Token unlocks
    - Partnerships
    - Conferences
    - Mainnet launches

    Args:
        coin_id: CoinGecko coin ID (leave empty for all)
        upcoming_only: Filter to upcoming events only

    Returns:
        Formatted string with crypto events
    """
    url = "https://api.coingecko.com/api/v3/events"

    params = {}

    if coin_id:
        # Get coin data first to validate
        params_coin = {"ids": coin_id}

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        events = data.get('data', [])

        if not events:
            return f"No events found on CoinGecko"

        result_str = f"## Upcoming Crypto Events"
        if coin_id:
            result_str += f" for {coin_id.capitalize()}"
        result_str += ":\n\n"

        event_count = 0
        now = datetime.now()

        for event in events:
            title = event.get('title', 'No title')
            description = event.get('description', '')[:200]
            event_type = event.get('type', 'Unknown')
            start_date = event.get('start_date', '')
            end_date = event.get('end_date', '')
            website = event.get('website', '')

            # Parse dates
            try:
                if start_date:
                    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))

                    # Skip past events if upcoming_only
                    if upcoming_only and start_dt.replace(tzinfo=None) < now:
                        continue

                    result_str += f"### {title}\n"
                    result_str += f"**Type**: {event_type}\n"
                    result_str += f"**Date**: {start_dt.strftime('%Y-%m-%d')}"

                    if end_date:
                        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                        result_str += f" to {end_dt.strftime('%Y-%m-%d')}"

                    result_str += "\n"

                    if description:
                        result_str += f"{description}...\n"

                    if website:
                        result_str += f"[More info]({website})\n"

                    result_str += "\n"

                    event_count += 1

                    # Limit to 15 events
                    if event_count >= 15:
                        break

            except Exception:
                continue

        if event_count == 0:
            return f"No upcoming events found"

        result_str += f"**Total Upcoming Events**: {event_count}\n"

        return result_str

    except requests.exceptions.RequestException as e:
        return f"Error fetching CoinGecko events: {str(e)}"
    except Exception as e:
        return f"Error processing CoinGecko events data: {str(e)}"


# ===== HELPER FUNCTIONS =====

def normalize_ticker_for_cryptopanic(ticker: str) -> str:
    """
    Normalize ticker for CryptoPanic API.

    Examples:
        'BTC-USD' -> 'BTC'
        'BTCUSDT' -> 'BTC'
        'Bitcoin' -> 'BTC'
    """
    ticker = ticker.upper()

    # Remove common suffixes
    ticker = ticker.replace('USDT', '').replace('USD', '').replace('BUSD', '')
    ticker = ticker.replace('-', '').replace('/', '').replace('_', '')

    # Common mappings
    mappings = {
        'BITCOIN': 'BTC',
        'ETHEREUM': 'ETH',
        'RIPPLE': 'XRP',
        'CARDANO': 'ADA',
        'SOLANA': 'SOL',
        'POLKADOT': 'DOT',
        'DOGECOIN': 'DOGE',
    }

    return mappings.get(ticker, ticker)


def get_coingecko_coin_id(ticker: str) -> str:
    """
    Convert ticker to CoinGecko coin ID.

    Examples:
        'BTC' -> 'bitcoin'
        'ETH' -> 'ethereum'
        'SOL' -> 'solana'
    """
    ticker = ticker.upper().replace('USDT', '').replace('USD', '')

    mappings = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'SOL': 'solana',
        'ADA': 'cardano',
        'DOT': 'polkadot',
        'LINK': 'chainlink',
        'MATIC': 'polygon',
        'AVAX': 'avalanche',
        'UNI': 'uniswap',
        'AAVE': 'aave',
    }

    return mappings.get(ticker, ticker.lower())
