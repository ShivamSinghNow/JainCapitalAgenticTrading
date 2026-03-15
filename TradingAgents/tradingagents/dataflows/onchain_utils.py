"""
On-Chain Metrics Utilities - FREE On-Chain Data Sources

This module provides access to on-chain and fundamental crypto metrics using FREE APIs:
- CoinGecko API (no API key required for basic endpoints)
- Blockchain.info API (Bitcoin-specific metrics, no key required)
- CoinCap API (no API key required)
- CryptoCompare Social Stats (uses existing API key from Phase 1)

All functions use FREE tiers - minimal setup required!
"""

from typing import Annotated
import requests
from datetime import datetime
from .config import get_config
from .utils import retry_on_failure


# ===== TICKER TO COIN ID MAPPINGS =====

TICKER_TO_COINGECKO = {
    "BTC": "bitcoin",
    "BTCUSDT": "bitcoin",
    "BTC-USD": "bitcoin",
    "ETH": "ethereum",
    "ETHUSDT": "ethereum",
    "ETH-USD": "ethereum",
    "SOL": "solana",
    "SOLUSDT": "solana",
    "SOL-USD": "solana",
    "ADA": "cardano",
    "ADAUSDT": "cardano",
    "ADA-USD": "cardano",
    "DOT": "polkadot",
    "DOTUSDT": "polkadot",
    "DOT-USD": "polkadot",
    "LINK": "chainlink",
    "LINKUSDT": "chainlink",
    "LINK-USD": "chainlink",
    "MATIC": "polygon",
    "MATICUSDT": "polygon",
    "MATIC-USD": "polygon",
    "AVAX": "avalanche-2",
    "AVAXUSDT": "avalanche-2",
    "AVAX-USD": "avalanche-2",
    "UNI": "uniswap",
    "UNIUSDT": "uniswap",
    "UNI-USD": "uniswap",
    "AAVE": "aave",
    "AAVEUSDT": "aave",
    "AAVE-USD": "aave",
    "CRV": "curve-dao-token",
    "CRVUSDT": "curve-dao-token",
    "CRV-USD": "curve-dao-token",
}


def normalize_ticker_to_coingecko(ticker: str) -> str:
    """
    Convert trading ticker to CoinGecko coin ID.

    Examples:
        'BTC-USD' -> 'bitcoin'
        'BTCUSDT' -> 'bitcoin'
        'ETH' -> 'ethereum'
    """
    ticker_upper = ticker.upper().strip()

    # Check direct mapping
    if ticker_upper in TICKER_TO_COINGECKO:
        return TICKER_TO_COINGECKO[ticker_upper]

    # Try removing common suffixes
    for suffix in ['USDT', 'USD', 'BUSD', '-USD', '-USDT']:
        if ticker_upper.endswith(suffix):
            base = ticker_upper.replace(suffix, '')
            if base in TICKER_TO_COINGECKO:
                return TICKER_TO_COINGECKO[base]

    # Default: return lowercase ticker (may or may not work)
    return ticker_upper.lower()


# ===== COINGECKO MARKET METRICS =====

@retry_on_failure(max_retries=3, delay=2)
def get_coingecko_market_metrics(
    coin_id: Annotated[str, "CoinGecko coin ID or ticker (e.g., 'bitcoin', 'BTC-USD')"]
) -> str:
    """
    Get comprehensive market metrics from CoinGecko (100% FREE, no API key required).

    Provides fundamental on-chain market data:
    - Market cap (current and fully diluted)
    - Circulating supply vs total supply
    - Price changes (24h, 7d, 30d, 1y)
    - Trading volume
    - Market cap rank
    - All-time high/low

    Rate limit: 10-30 calls/minute (no authentication needed)

    Args:
        coin_id: CoinGecko coin ID (e.g., 'bitcoin', 'ethereum') or ticker (e.g., 'BTC-USD')

    Returns:
        Formatted string with market metrics and analysis
    """
    # Normalize ticker to CoinGecko ID if needed
    if coin_id.upper() in TICKER_TO_COINGECKO or '-' in coin_id or 'USDT' in coin_id.upper():
        coin_id = normalize_ticker_to_coingecko(coin_id)

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"

    params = {
        'localization': 'false',  # Skip translations to reduce response size
        'tickers': 'false',       # Skip ticker data to reduce response size
        'market_data': 'true',
        'community_data': 'false',
        'developer_data': 'false',
        'sparkline': 'false'
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Extract market data
        market_data = data.get('market_data', {})

        if not market_data:
            return f"No market data available for {coin_id}"

        # Get name and symbol
        name = data.get('name', coin_id)
        symbol = data.get('symbol', '').upper()

        # Build report
        result_str = f"## CoinGecko Market Metrics: {name} ({symbol})\n\n"

        # Current price
        current_price = market_data.get('current_price', {}).get('usd', 0)
        result_str += f"**Current Price**: ${current_price:,.2f}\n\n"

        # Market cap
        market_cap = market_data.get('market_cap', {}).get('usd', 0)
        market_cap_rank = market_data.get('market_cap_rank', 'N/A')
        fully_diluted_valuation = market_data.get('fully_diluted_valuation', {}).get('usd', 0)

        result_str += f"### Market Capitalization:\n"
        result_str += f"- **Current Market Cap**: ${market_cap:,.0f}\n"
        result_str += f"- **Market Cap Rank**: #{market_cap_rank}\n"
        if fully_diluted_valuation:
            result_str += f"- **Fully Diluted Valuation**: ${fully_diluted_valuation:,.0f}\n"
        result_str += "\n"

        # Supply
        circulating_supply = market_data.get('circulating_supply', 0)
        total_supply = market_data.get('total_supply', 0)
        max_supply = market_data.get('max_supply', 0)

        result_str += f"### Supply:\n"
        result_str += f"- **Circulating Supply**: {circulating_supply:,.0f} {symbol}\n"
        if total_supply:
            result_str += f"- **Total Supply**: {total_supply:,.0f} {symbol}\n"
        if max_supply:
            result_str += f"- **Max Supply**: {max_supply:,.0f} {symbol}\n"
            supply_pct = (circulating_supply / max_supply * 100) if max_supply > 0 else 0
            result_str += f"- **% of Max Supply in Circulation**: {supply_pct:.2f}%\n"
        result_str += "\n"

        # Price changes
        price_change_24h = market_data.get('price_change_percentage_24h', 0)
        price_change_7d = market_data.get('price_change_percentage_7d', 0)
        price_change_30d = market_data.get('price_change_percentage_30d', 0)
        price_change_1y = market_data.get('price_change_percentage_1y', 0)

        result_str += f"### Price Changes:\n"
        result_str += f"- **24 Hours**: {price_change_24h:+.2f}%\n"
        result_str += f"- **7 Days**: {price_change_7d:+.2f}%\n"
        result_str += f"- **30 Days**: {price_change_30d:+.2f}%\n"
        result_str += f"- **1 Year**: {price_change_1y:+.2f}%\n"
        result_str += "\n"

        # Volume
        total_volume = market_data.get('total_volume', {}).get('usd', 0)
        volume_to_market_cap = (total_volume / market_cap * 100) if market_cap > 0 else 0

        result_str += f"### Trading Volume:\n"
        result_str += f"- **24h Volume**: ${total_volume:,.0f}\n"
        result_str += f"- **Volume/Market Cap Ratio**: {volume_to_market_cap:.2f}%\n"
        result_str += "\n"

        # All-time high/low
        ath = market_data.get('ath', {}).get('usd', 0)
        ath_date = market_data.get('ath_date', {}).get('usd', '')
        ath_change_pct = market_data.get('ath_change_percentage', {}).get('usd', 0)

        atl = market_data.get('atl', {}).get('usd', 0)
        atl_date = market_data.get('atl_date', {}).get('usd', '')
        atl_change_pct = market_data.get('atl_change_percentage', {}).get('usd', 0)

        result_str += f"### All-Time Records:\n"
        result_str += f"- **All-Time High**: ${ath:,.2f}"
        if ath_date:
            ath_dt = datetime.fromisoformat(ath_date.replace('Z', '+00:00'))
            result_str += f" ({ath_dt.strftime('%Y-%m-%d')})"
        result_str += f"\n- **Distance from ATH**: {ath_change_pct:.2f}%\n"

        result_str += f"- **All-Time Low**: ${atl:,.2f}"
        if atl_date:
            atl_dt = datetime.fromisoformat(atl_date.replace('Z', '+00:00'))
            result_str += f" ({atl_dt.strftime('%Y-%m-%d')})"
        result_str += f"\n- **Distance from ATL**: +{atl_change_pct:.2f}%\n"
        result_str += "\n"

        # Analysis
        result_str += f"### Analysis:\n"

        # Trend analysis
        if price_change_24h > 5:
            result_str += f"- 📈 Strong upward momentum (24h: +{price_change_24h:.2f}%)\n"
        elif price_change_24h < -5:
            result_str += f"- 📉 Significant downward pressure (24h: {price_change_24h:.2f}%)\n"

        # Supply analysis
        if max_supply and supply_pct > 90:
            result_str += f"- ⚠️  High circulating supply ({supply_pct:.1f}% of max) - limited new supply pressure\n"
        elif max_supply and supply_pct < 50:
            result_str += f"- ⚠️  Low circulating supply ({supply_pct:.1f}% of max) - potential dilution risk\n"

        # Volume analysis
        if volume_to_market_cap > 10:
            result_str += f"- 🔥 High trading activity (volume/mcap: {volume_to_market_cap:.1f}%) - strong liquidity\n"
        elif volume_to_market_cap < 1:
            result_str += f"- ⚠️  Low trading activity (volume/mcap: {volume_to_market_cap:.1f}%) - liquidity concerns\n"

        # ATH analysis
        if ath_change_pct > -20:
            result_str += f"- 🎯 Near all-time high ({abs(ath_change_pct):.1f}% below ATH) - potential resistance\n"
        elif ath_change_pct < -80:
            result_str += f"- 💎 Deep discount ({abs(ath_change_pct):.1f}% below ATH) - potential opportunity\n"

        return result_str

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"Coin '{coin_id}' not found on CoinGecko. Try using the full coin ID (e.g., 'bitcoin' instead of 'BTC')"
        elif e.response.status_code == 429:
            return f"Rate limit exceeded for CoinGecko API. Please wait a moment and try again."
        else:
            return f"HTTP error fetching CoinGecko data: {e}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching CoinGecko market metrics: {str(e)}"
    except Exception as e:
        return f"Error processing CoinGecko data: {str(e)}"


# ===== COINGECKO DEVELOPER ACTIVITY =====

@retry_on_failure(max_retries=3, delay=2)
def get_coingecko_developer_activity(
    coin_id: Annotated[str, "CoinGecko coin ID or ticker (e.g., 'bitcoin', 'BTC-USD')"]
) -> str:
    """
    Get developer activity metrics from CoinGecko (100% FREE, no API key required).

    Provides development activity indicators:
    - GitHub commits (last 4 weeks)
    - Code additions and deletions
    - Contributors count
    - Stars, forks, watchers
    - Pull requests merged
    - Issues closed

    Rate limit: 10-30 calls/minute (no authentication needed)

    Args:
        coin_id: CoinGecko coin ID (e.g., 'bitcoin', 'ethereum') or ticker (e.g., 'BTC-USD')

    Returns:
        Formatted string with developer activity metrics and analysis
    """
    # Normalize ticker to CoinGecko ID if needed
    if coin_id.upper() in TICKER_TO_COINGECKO or '-' in coin_id or 'USDT' in coin_id.upper():
        coin_id = normalize_ticker_to_coingecko(coin_id)

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"

    params = {
        'localization': 'false',
        'tickers': 'false',
        'market_data': 'false',
        'community_data': 'false',
        'developer_data': 'true',  # Only fetch developer data
        'sparkline': 'false'
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Extract developer data
        dev_data = data.get('developer_data', {})

        if not dev_data:
            return f"No developer data available for {coin_id}"

        # Get name and symbol
        name = data.get('name', coin_id)
        symbol = data.get('symbol', '').upper()

        # Build report
        result_str = f"## CoinGecko Developer Activity: {name} ({symbol})\n\n"

        # GitHub stats
        forks = dev_data.get('forks', 0)
        stars = dev_data.get('stars', 0)
        subscribers = dev_data.get('subscribers', 0)
        total_issues = dev_data.get('total_issues', 0)
        closed_issues = dev_data.get('closed_issues', 0)
        pull_requests_merged = dev_data.get('pull_requests_merged', 0)
        pull_request_contributors = dev_data.get('pull_request_contributors', 0)

        result_str += f"### GitHub Repository Stats:\n"
        result_str += f"- **Stars**: {stars:,}\n"
        result_str += f"- **Forks**: {forks:,}\n"
        result_str += f"- **Watchers**: {subscribers:,}\n"
        result_str += f"- **Contributors**: {pull_request_contributors:,}\n"
        result_str += "\n"

        # Code activity (last 4 weeks)
        commit_count_4_weeks = dev_data.get('commit_count_4_weeks', 0)
        code_additions_4_weeks = dev_data.get('code_additions_deletions_4_weeks', {}).get('additions', 0)
        code_deletions_4_weeks = dev_data.get('code_additions_deletions_4_weeks', {}).get('deletions', 0)

        result_str += f"### Code Activity (Last 4 Weeks):\n"
        result_str += f"- **Commits**: {commit_count_4_weeks:,}\n"
        result_str += f"- **Lines Added**: +{code_additions_4_weeks:,}\n"
        result_str += f"- **Lines Deleted**: -{code_deletions_4_weeks:,}\n"
        net_lines = code_additions_4_weeks - code_deletions_4_weeks
        result_str += f"- **Net Change**: {net_lines:+,} lines\n"
        result_str += "\n"

        # Issue and PR activity
        result_str += f"### Issue & PR Activity:\n"
        result_str += f"- **Total Issues**: {total_issues:,}\n"
        result_str += f"- **Closed Issues**: {closed_issues:,}\n"
        if total_issues > 0:
            close_rate = (closed_issues / total_issues) * 100
            result_str += f"- **Issue Close Rate**: {close_rate:.1f}%\n"
        result_str += f"- **Pull Requests Merged**: {pull_requests_merged:,}\n"
        result_str += "\n"

        # Analysis
        result_str += f"### Development Activity Analysis:\n"

        # Commit analysis
        if commit_count_4_weeks > 100:
            result_str += f"- 🔥 Very active development ({commit_count_4_weeks} commits/4wks) - strong ongoing work\n"
        elif commit_count_4_weeks > 20:
            result_str += f"- ✅ Active development ({commit_count_4_weeks} commits/4wks) - healthy activity\n"
        elif commit_count_4_weeks > 0:
            result_str += f"- ⚠️  Low development activity ({commit_count_4_weeks} commits/4wks) - minimal updates\n"
        else:
            result_str += f"- 🚫 No recent commits - project may be dormant or complete\n"

        # Code change analysis
        if net_lines > 1000:
            result_str += f"- 📈 Significant code expansion (+{net_lines:,} net lines) - major feature development\n"
        elif net_lines < -1000:
            result_str += f"- 🔧 Major refactoring ({net_lines:,} net lines) - code cleanup/optimization\n"

        # Community engagement
        if stars > 10000:
            result_str += f"- ⭐ Highly popular project ({stars:,} stars) - strong community interest\n"
        elif stars > 1000:
            result_str += f"- ✅ Popular project ({stars:,} stars) - good community support\n"

        # Issue management
        if total_issues > 0:
            close_rate = (closed_issues / total_issues) * 100
            if close_rate > 80:
                result_str += f"- ✅ Excellent issue management ({close_rate:.1f}% closed) - responsive team\n"
            elif close_rate < 50:
                result_str += f"- ⚠️  Many open issues ({close_rate:.1f}% closed) - potential maintenance concerns\n"

        # Contributor analysis
        if pull_request_contributors > 50:
            result_str += f"- 👥 Large contributor base ({pull_request_contributors} contributors) - decentralized development\n"
        elif pull_request_contributors < 5:
            result_str += f"- ⚠️  Small contributor base ({pull_request_contributors} contributors) - centralization risk\n"

        return result_str

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"Coin '{coin_id}' not found on CoinGecko. Try using the full coin ID (e.g., 'bitcoin' instead of 'BTC')"
        elif e.response.status_code == 429:
            return f"Rate limit exceeded for CoinGecko API. Please wait a moment and try again."
        else:
            return f"HTTP error fetching CoinGecko developer data: {e}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching CoinGecko developer activity: {str(e)}"
    except Exception as e:
        return f"Error processing CoinGecko developer data: {str(e)}"


# ===== COINGECKO COMMUNITY STATS =====

@retry_on_failure(max_retries=3, delay=2)
def get_coingecko_community_stats(
    coin_id: Annotated[str, "CoinGecko coin ID or ticker (e.g., 'bitcoin', 'BTC-USD')"]
) -> str:
    """
    Get community and social metrics from CoinGecko (100% FREE, no API key required).

    Provides community engagement metrics:
    - Twitter followers
    - Reddit subscribers and active accounts
    - Telegram channel members
    - Facebook likes
    - Alexa rank (website traffic)
    - Public interest score

    Rate limit: 10-30 calls/minute (no authentication needed)

    Args:
        coin_id: CoinGecko coin ID (e.g., 'bitcoin', 'ethereum') or ticker (e.g., 'BTC-USD')

    Returns:
        Formatted string with community metrics and analysis
    """
    # Normalize ticker to CoinGecko ID if needed
    if coin_id.upper() in TICKER_TO_COINGECKO or '-' in coin_id or 'USDT' in coin_id.upper():
        coin_id = normalize_ticker_to_coingecko(coin_id)

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"

    params = {
        'localization': 'false',
        'tickers': 'false',
        'market_data': 'false',
        'community_data': 'true',  # Only fetch community data
        'developer_data': 'false',
        'sparkline': 'false'
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Extract community data
        community_data = data.get('community_data', {})
        public_interest_stats = data.get('public_interest_stats', {})

        if not community_data and not public_interest_stats:
            return f"No community data available for {coin_id}"

        # Get name and symbol
        name = data.get('name', coin_id)
        symbol = data.get('symbol', '').upper()

        # Build report
        result_str = f"## CoinGecko Community Stats: {name} ({symbol})\n\n"

        # Social media followers (handle None values)
        twitter_followers = community_data.get('twitter_followers') or 0
        reddit_subscribers = community_data.get('reddit_subscribers') or 0
        reddit_average_posts_48h = community_data.get('reddit_average_posts_48h') or 0
        reddit_average_comments_48h = community_data.get('reddit_average_comments_48h') or 0
        reddit_accounts_active_48h = community_data.get('reddit_accounts_active_48h') or 0
        telegram_channel_user_count = community_data.get('telegram_channel_user_count') or 0
        facebook_likes = community_data.get('facebook_likes') or 0

        result_str += f"### Social Media Following:\n"
        if twitter_followers:
            result_str += f"- **Twitter Followers**: {twitter_followers:,}\n"
        if reddit_subscribers:
            result_str += f"- **Reddit Subscribers**: {reddit_subscribers:,}\n"
        if telegram_channel_user_count:
            result_str += f"- **Telegram Members**: {telegram_channel_user_count:,}\n"
        if facebook_likes:
            result_str += f"- **Facebook Likes**: {facebook_likes:,}\n"

        if not any([twitter_followers, reddit_subscribers, telegram_channel_user_count, facebook_likes]):
            result_str += f"- No social media data available\n"
        result_str += "\n"

        # Reddit activity (last 48 hours)
        if reddit_subscribers or reddit_average_posts_48h or reddit_average_comments_48h:
            result_str += f"### Reddit Activity (Last 48h):\n"
            if reddit_average_posts_48h:
                result_str += f"- **Average Posts**: {reddit_average_posts_48h:.1f}\n"
            if reddit_average_comments_48h:
                result_str += f"- **Average Comments**: {reddit_average_comments_48h:.1f}\n"
            if reddit_accounts_active_48h:
                result_str += f"- **Active Accounts**: {reddit_accounts_active_48h:,}\n"
                if reddit_subscribers > 0:
                    engagement_rate = (reddit_accounts_active_48h / reddit_subscribers) * 100
                    result_str += f"- **Engagement Rate**: {engagement_rate:.2f}%\n"
            result_str += "\n"

        # Public interest (handle None values)
        alexa_rank = public_interest_stats.get('alexa_rank') or 0
        bing_matches = public_interest_stats.get('bing_matches') or 0

        if alexa_rank or bing_matches:
            result_str += f"### Public Interest:\n"
            if alexa_rank:
                result_str += f"- **Alexa Rank**: #{alexa_rank:,} (website traffic)\n"
            if bing_matches:
                result_str += f"- **Bing Search Matches**: {bing_matches:,}\n"
            result_str += "\n"

        # Analysis
        result_str += f"### Community Analysis:\n"

        # Twitter analysis
        if twitter_followers > 1000000:
            result_str += f"- 🔥 Massive Twitter following ({twitter_followers:,}) - mainstream recognition\n"
        elif twitter_followers > 100000:
            result_str += f"- ✅ Strong Twitter presence ({twitter_followers:,}) - good visibility\n"
        elif twitter_followers > 0:
            result_str += f"- ⚠️  Small Twitter following ({twitter_followers:,}) - limited reach\n"

        # Reddit analysis
        if reddit_subscribers > 500000:
            result_str += f"- 🔥 Huge Reddit community ({reddit_subscribers:,} subscribers) - strong grassroots support\n"
        elif reddit_subscribers > 50000:
            result_str += f"- ✅ Active Reddit community ({reddit_subscribers:,} subscribers) - engaged users\n"
        elif reddit_subscribers > 0:
            result_str += f"- ⚠️  Small Reddit community ({reddit_subscribers:,} subscribers) - niche following\n"

        # Reddit engagement
        if reddit_subscribers > 0 and reddit_accounts_active_48h:
            engagement_rate = (reddit_accounts_active_48h / reddit_subscribers) * 100
            if engagement_rate > 5:
                result_str += f"- 🔥 High Reddit engagement ({engagement_rate:.1f}%) - very active community\n"
            elif engagement_rate > 1:
                result_str += f"- ✅ Good Reddit engagement ({engagement_rate:.1f}%) - healthy activity\n"
            elif engagement_rate > 0:
                result_str += f"- ⚠️  Low Reddit engagement ({engagement_rate:.1f}%) - passive community\n"

        # Telegram analysis
        if telegram_channel_user_count > 100000:
            result_str += f"- 💬 Large Telegram community ({telegram_channel_user_count:,}) - active discussions\n"
        elif telegram_channel_user_count > 10000:
            result_str += f"- ✅ Active Telegram group ({telegram_channel_user_count:,}) - engaged community\n"

        # Overall community strength
        total_followers = twitter_followers + reddit_subscribers + telegram_channel_user_count + facebook_likes
        if total_followers > 2000000:
            result_str += f"- 🌟 Exceptional community strength ({total_followers:,} total) - major project\n"
        elif total_followers > 500000:
            result_str += f"- ✅ Strong community support ({total_followers:,} total) - established project\n"
        elif total_followers > 0:
            result_str += f"- ⚠️  Growing community ({total_followers:,} total) - early stage\n"

        return result_str

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"Coin '{coin_id}' not found on CoinGecko. Try using the full coin ID (e.g., 'bitcoin' instead of 'BTC')"
        elif e.response.status_code == 429:
            return f"Rate limit exceeded for CoinGecko API. Please wait a moment and try again."
        else:
            return f"HTTP error fetching CoinGecko community data: {e}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching CoinGecko community stats: {str(e)}"
    except Exception as e:
        return f"Error processing CoinGecko community data: {str(e)}"


# ===== BLOCKCHAIN.INFO BITCOIN NETWORK METRICS =====

@retry_on_failure(max_retries=3, delay=2)
def get_bitcoin_network_metrics() -> str:
    """
    Get Bitcoin network metrics from Blockchain.info (100% FREE, no API key required).

    Provides Bitcoin-specific blockchain metrics:
    - Hash rate (network computational power)
    - Difficulty (mining difficulty)
    - Mempool size (unconfirmed transactions)
    - Average block size
    - Transactions per day
    - Average transaction value
    - Average confirmation time

    No rate limits, completely free, no authentication needed.

    Returns:
        Formatted string with Bitcoin network metrics and analysis
    """
    # Blockchain.info stats API
    url = "https://blockchain.info/stats?format=json"

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Build report
        result_str = f"## Bitcoin Network Metrics (Blockchain.info)\n\n"

        # Network hash rate
        hash_rate = data.get('hash_rate', 0)  # in GH/s
        result_str += f"### Network Hash Rate:\n"
        result_str += f"- **Current Hash Rate**: {hash_rate / 1_000_000:.2f} EH/s (Exa-hashes per second)\n"
        result_str += "\n"

        # Mining difficulty
        difficulty = data.get('difficulty', 0)
        result_str += f"### Mining Difficulty:\n"
        result_str += f"- **Current Difficulty**: {difficulty:,.0f}\n"
        result_str += "\n"

        # Mempool and transactions
        mempool_size = data.get('mempool_size', 0)  # bytes
        unconfirmed_count = data.get('n_tx_mempool', 0)
        n_tx = data.get('n_tx', 0)  # transactions in last 24h

        result_str += f"### Transaction Activity:\n"
        result_str += f"- **Mempool Size**: {mempool_size / 1_000_000:.2f} MB\n"
        result_str += f"- **Unconfirmed Transactions**: {unconfirmed_count:,}\n"
        result_str += f"- **Transactions (24h)**: {n_tx:,}\n"
        result_str += "\n"

        # Block stats
        blocks_size = data.get('blocks_size', 0)  # bytes
        n_blocks_mined = data.get('n_blocks_mined', 0)
        minutes_between_blocks = data.get('minutes_between_blocks', 0)

        if n_blocks_mined > 0:
            avg_block_size = blocks_size / n_blocks_mined
        else:
            avg_block_size = 0

        result_str += f"### Block Statistics:\n"
        result_str += f"- **Blocks Mined (24h)**: {n_blocks_mined}\n"
        result_str += f"- **Average Block Size**: {avg_block_size / 1_000_000:.2f} MB\n"
        result_str += f"- **Average Block Time**: {minutes_between_blocks:.1f} minutes\n"
        result_str += "\n"

        # Market and economic metrics
        market_price_usd = data.get('market_price_usd', 0)
        total_btc = data.get('totalbc', 0) / 100_000_000  # Convert from satoshis
        trade_volume_btc = data.get('trade_volume_btc', 0)
        trade_volume_usd = data.get('trade_volume_usd', 0)

        result_str += f"### Economic Metrics:\n"
        result_str += f"- **Market Price**: ${market_price_usd:,.2f}\n"
        result_str += f"- **Total BTC in Circulation**: {total_btc:,.2f} BTC\n"
        result_str += f"- **Trade Volume (24h)**: {trade_volume_btc:,.2f} BTC (${trade_volume_usd:,.0f})\n"
        result_str += "\n"

        # Transaction stats
        total_fees_btc = data.get('total_fees_btc', 0) / 100_000_000  # Convert from satoshis
        estimated_transaction_volume_usd = data.get('estimated_transaction_volume_usd', 0)

        if n_tx > 0:
            avg_tx_value = estimated_transaction_volume_usd / n_tx
        else:
            avg_tx_value = 0

        result_str += f"### Transaction Economics:\n"
        result_str += f"- **Total Fees (24h)**: {total_fees_btc:.2f} BTC\n"
        result_str += f"- **Estimated TX Volume (24h)**: ${estimated_transaction_volume_usd:,.0f}\n"
        result_str += f"- **Average Transaction Value**: ${avg_tx_value:,.2f}\n"
        result_str += "\n"

        # Analysis
        result_str += f"### Network Health Analysis:\n"

        # Hash rate analysis
        if hash_rate > 500_000_000:  # > 500 EH/s
            result_str += f"- 🔥 Extremely high hash rate ({hash_rate / 1_000_000:.0f} EH/s) - network very secure\n"
        elif hash_rate > 300_000_000:  # > 300 EH/s
            result_str += f"- ✅ Strong hash rate ({hash_rate / 1_000_000:.0f} EH/s) - good network security\n"
        elif hash_rate > 0:
            result_str += f"- ⚠️  Hash rate at {hash_rate / 1_000_000:.0f} EH/s\n"

        # Mempool congestion
        if unconfirmed_count > 100000:
            result_str += f"- ⚠️  High mempool congestion ({unconfirmed_count:,} unconfirmed) - expect delays\n"
        elif unconfirmed_count > 50000:
            result_str += f"- ⚠️  Moderate mempool congestion ({unconfirmed_count:,} unconfirmed) - some delays possible\n"
        elif unconfirmed_count > 0:
            result_str += f"- ✅ Low mempool congestion ({unconfirmed_count:,} unconfirmed) - fast confirmations\n"

        # Block time analysis
        if minutes_between_blocks < 9:
            result_str += f"- 🔥 Faster than average block time ({minutes_between_blocks:.1f} min) - high mining activity\n"
        elif minutes_between_blocks > 11:
            result_str += f"- ⚠️  Slower than average block time ({minutes_between_blocks:.1f} min) - lower mining activity\n"
        else:
            result_str += f"- ✅ Normal block time ({minutes_between_blocks:.1f} min) - healthy mining\n"

        # Transaction volume analysis
        if n_tx > 400000:
            result_str += f"- 🔥 Very high transaction activity ({n_tx:,}/day) - strong network usage\n"
        elif n_tx > 250000:
            result_str += f"- ✅ Good transaction activity ({n_tx:,}/day) - healthy usage\n"
        elif n_tx > 0:
            result_str += f"- ⚠️  Transaction activity at {n_tx:,}/day\n"

        return result_str

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return f"Rate limit exceeded for Blockchain.info API. Please wait a moment and try again."
        else:
            return f"HTTP error fetching Blockchain.info data: {e}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching Bitcoin network metrics: {str(e)}"
    except Exception as e:
        return f"Error processing Bitcoin network data: {str(e)}"


# ===== CRYPTO FEAR & GREED INDEX =====

@retry_on_failure(max_retries=3, delay=2)
def get_fear_greed_index() -> str:
    """
    Get Crypto Fear & Greed Index from Alternative.me (100% FREE, no API key required).

    The Fear & Greed Index is a composite sentiment indicator (0-100) based on:
    - Volatility (25%)
    - Market Momentum/Volume (25%)
    - Social Media (15%)
    - Surveys (15%)
    - Dominance (10%)
    - Trends (10%)

    Scale:
    - 0-24: Extreme Fear
    - 25-49: Fear
    - 50-74: Greed
    - 75-100: Extreme Greed

    No rate limits, completely free, no authentication needed.

    Returns:
        Formatted string with Fear & Greed Index and historical data
    """
    # Alternative.me Fear & Greed Index API
    url = "https://api.alternative.me/fng/?limit=30"  # Get last 30 days

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        if 'data' not in data or not data['data']:
            return "No Fear & Greed Index data available"

        # Get current and historical data
        current = data['data'][0]
        historical = data['data']

        current_value = int(current['value'])
        current_classification = current['value_classification']
        timestamp = current['timestamp']

        # Build report
        result_str = f"## Crypto Fear & Greed Index (Alternative.me)\n\n"

        result_str += f"### Current Sentiment:\n"
        result_str += f"- **Index Value**: {current_value}/100\n"
        result_str += f"- **Classification**: {current_classification}\n"
        result_str += f"- **Last Updated**: {datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M')}\n"
        result_str += "\n"

        # Calculate averages
        values = [int(d['value']) for d in historical]
        avg_7d = sum(values[:7]) / min(7, len(values)) if len(values) >= 1 else current_value
        avg_30d = sum(values) / len(values) if len(values) > 0 else current_value

        result_str += f"### Historical Averages:\n"
        result_str += f"- **7-Day Average**: {avg_7d:.1f}/100\n"
        result_str += f"- **30-Day Average**: {avg_30d:.1f}/100\n"
        result_str += "\n"

        # Trend analysis
        if len(historical) >= 7:
            recent_avg = sum(values[:3]) / 3
            week_ago_avg = sum(values[4:7]) / 3
            trend_change = recent_avg - week_ago_avg

            result_str += f"### Trend (Recent vs Week Ago):\n"
            if trend_change > 10:
                result_str += f"- 📈 Sentiment improving significantly (+{trend_change:.1f} points)\n"
            elif trend_change > 5:
                result_str += f"- ↗️  Sentiment improving moderately (+{trend_change:.1f} points)\n"
            elif trend_change < -10:
                result_str += f"- 📉 Sentiment deteriorating significantly ({trend_change:.1f} points)\n"
            elif trend_change < -5:
                result_str += f"- ↘️  Sentiment deteriorating moderately ({trend_change:.1f} points)\n"
            else:
                result_str += f"- ➡️  Sentiment stable ({trend_change:+.1f} points)\n"
            result_str += "\n"

        # Interpretation
        result_str += f"### Analysis & Trading Implications:\n"

        if current_value <= 24:
            result_str += f"- 😱 **Extreme Fear** - Market may be oversold, potential buying opportunity\n"
            result_str += f"- Historically, extreme fear has preceded market bottoms\n"
            result_str += f"- Consider: Value accumulation, DCA strategies\n"
        elif current_value <= 49:
            result_str += f"- 😟 **Fear** - Market sentiment is negative but not extreme\n"
            result_str += f"- May indicate caution or uncertainty among investors\n"
            result_str += f"- Consider: Selective buying on dips\n"
        elif current_value <= 74:
            result_str += f"- 😊 **Greed** - Market sentiment is positive\n"
            result_str += f"- Investors are optimistic but not euphoric\n"
            result_str += f"- Consider: Normal risk management, watch for overheating\n"
        else:  # 75-100
            result_str += f"- 🤑 **Extreme Greed** - Market may be overbought, potential correction ahead\n"
            result_str += f"- Historically, extreme greed has preceded market tops\n"
            result_str += f"- Consider: Profit-taking, risk reduction, tighter stop-losses\n"

        # Contrarian indicator note
        result_str += f"\n**Note**: This is a contrarian indicator - extreme fear often presents buying opportunities, while extreme greed suggests caution.\n"

        return result_str

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return f"Rate limit exceeded for Fear & Greed Index API. Please wait a moment and try again."
        else:
            return f"HTTP error fetching Fear & Greed Index: {e}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching Fear & Greed Index: {str(e)}"
    except Exception as e:
        return f"Error processing Fear & Greed Index data: {str(e)}"


# ===== COINCAP MARKET RANKINGS =====

@retry_on_failure(max_retries=3, delay=2)
def get_coincap_rankings(limit: int = 20) -> str:
    """
    Get cryptocurrency market cap rankings from CoinCap (100% FREE, no API key required).

    Provides top cryptocurrencies by market cap with:
    - Rank, symbol, name
    - Price, market cap, volume
    - 24h change percentage
    - Supply metrics

    No rate limits, completely free, no authentication needed.

    Args:
        limit: Number of top coins to retrieve (default: 20)

    Returns:
        Formatted string with market rankings
    """
    url = "https://api.coincap.io/v2/assets"
    params = {'limit': min(limit, 100)}  # Cap at 100

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if 'data' not in data or not data['data']:
            return "No ranking data available from CoinCap"

        assets = data['data']

        # Build report
        result_str = f"## Cryptocurrency Market Rankings (CoinCap)\n\n"
        result_str += f"### Top {len(assets)} Cryptocurrencies by Market Cap:\n\n"

        for asset in assets[:10]:  # Show top 10 in detail
            rank = asset.get('rank', 'N/A')
            symbol = asset.get('symbol', 'N/A')
            name = asset.get('name', 'N/A')
            price = float(asset.get('priceUsd', 0))
            market_cap = float(asset.get('marketCapUsd', 0))
            volume_24h = float(asset.get('volumeUsd24Hr', 0))
            change_24h = float(asset.get('changePercent24Hr', 0))
            supply = float(asset.get('supply', 0))

            result_str += f"**#{rank} {name} ({symbol})**\n"
            result_str += f"- Price: ${price:,.4f}\n"
            result_str += f"- Market Cap: ${market_cap:,.0f}\n"
            result_str += f"- 24h Volume: ${volume_24h:,.0f}\n"
            result_str += f"- 24h Change: {change_24h:+.2f}%\n"
            result_str += f"- Supply: {supply:,.0f} {symbol}\n"
            result_str += "\n"

        # Summary stats
        total_market_cap = sum(float(a.get('marketCapUsd', 0)) for a in assets)
        avg_change = sum(float(a.get('changePercent24Hr', 0)) for a in assets) / len(assets)

        result_str += f"### Market Summary:\n"
        result_str += f"- **Total Market Cap (Top {len(assets)})**: ${total_market_cap:,.0f}\n"
        result_str += f"- **Average 24h Change**: {avg_change:+.2f}%\n"
        result_str += "\n"

        # Market sentiment
        gainers = sum(1 for a in assets if float(a.get('changePercent24Hr', 0)) > 0)
        losers = len(assets) - gainers

        result_str += f"### Market Breadth:\n"
        result_str += f"- **Gainers**: {gainers}/{len(assets)} ({gainers/len(assets)*100:.1f}%)\n"
        result_str += f"- **Losers**: {losers}/{len(assets)} ({losers/len(assets)*100:.1f}%)\n"
        result_str += "\n"

        if gainers > losers * 1.5:
            result_str += "- 🟢 **Bullish Market**: Majority of coins gaining\n"
        elif losers > gainers * 1.5:
            result_str += "- 🔴 **Bearish Market**: Majority of coins losing\n"
        else:
            result_str += "- ⚪ **Mixed Market**: Balanced gains and losses\n"

        return result_str

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return f"Rate limit exceeded for CoinCap API. Please wait a moment and try again."
        else:
            return f"HTTP error fetching CoinCap rankings: {e}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching CoinCap rankings: {str(e)}"
    except Exception as e:
        return f"Error processing CoinCap data: {str(e)}"


# ===== CRYPTOCOMPARE SOCIAL STATS =====

@retry_on_failure(max_retries=3, delay=2)
def get_cryptocompare_social_stats(
    symbol: Annotated[str, "Cryptocurrency symbol (e.g., 'BTC', 'ETH')"]
) -> str:
    """
    Get social media statistics from CryptoCompare (FREE tier: 100k calls/month).

    Provides social media metrics:
    - Twitter followers, statuses, lists
    - Reddit subscribers, active users
    - Code repository stats
    - Community points

    Requires free API key from CryptoCompare (sign up at min-api.cryptocompare.com).

    Args:
        symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH', 'SOL')

    Returns:
        Formatted string with social statistics
    """
    # Clean symbol
    symbol_clean = symbol.upper().replace('-USD', '').replace('USDT', '').replace('USD', '')

    # Get API key from config
    config = get_config()
    api_key = config.get('cryptocompare_api_key', '')

    # CryptoCompare social stats endpoint
    url = f"https://min-api.cryptocompare.com/data/social/coin/latest"
    params = {'coinId': symbol_clean}
    headers = {}

    if api_key:
        headers['authorization'] = f'Apikey {api_key}'

    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        if 'Data' not in data:
            return f"No social stats available for {symbol_clean} on CryptoCompare"

        social_data = data['Data']

        # Build report
        result_str = f"## CryptoCompare Social Stats: {symbol_clean}\n\n"

        # Twitter stats
        twitter = social_data.get('Twitter', {})
        if twitter:
            result_str += f"### Twitter:\n"
            result_str += f"- **Followers**: {twitter.get('followers', 0):,}\n"
            result_str += f"- **Statuses**: {twitter.get('statuses', 0):,}\n"
            result_str += f"- **Lists**: {twitter.get('lists', 0):,}\n"
            result_str += f"- **Favourites**: {twitter.get('favourites', 0):,}\n"
            result_str += "\n"

        # Reddit stats
        reddit = social_data.get('Reddit', {})
        if reddit:
            result_str += f"### Reddit:\n"
            result_str += f"- **Subscribers**: {reddit.get('subscribers', 0):,}\n"
            result_str += f"- **Active Users**: {reddit.get('active_users', 0):,}\n"
            result_str += f"- **Posts (48h)**: {reddit.get('posts_per_hour', 0) * 48:.0f}\n"
            result_str += f"- **Comments (48h)**: {reddit.get('comments_per_hour', 0) * 48:.0f}\n"
            result_str += "\n"

        # Code repository
        code_repo = social_data.get('CodeRepository', {})
        if code_repo:
            result_str += f"### Code Repository:\n"
            result_str += f"- **Stars**: {code_repo.get('stars', 0):,}\n"
            result_str += f"- **Forks**: {code_repo.get('forks', 0):,}\n"
            result_str += f"- **Watchers**: {code_repo.get('subscribers', 0):,}\n"
            result_str += f"- **Contributors**: {code_repo.get('contributors', 0):,}\n"
            result_str += "\n"

        # General stats
        general = social_data.get('General', {})
        if general:
            result_str += f"### Community:\n"
            result_str += f"- **Community Points**: {general.get('Points', 0):,}\n"
            result_str += "\n"

        return result_str

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return f"CryptoCompare API key required. Sign up for free at min-api.cryptocompare.com"
        elif e.response.status_code == 429:
            return f"Rate limit exceeded for CryptoCompare API. Please wait a moment and try again."
        else:
            return f"HTTP error fetching CryptoCompare social stats: {e}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching CryptoCompare social stats: {str(e)}"
    except Exception as e:
        return f"Error processing CryptoCompare data: {str(e)}"


# ===== GITHUB DEVELOPMENT ACTIVITY =====

# GitHub repo mappings for major cryptocurrencies
GITHUB_REPO_MAP = {
    'BTC': 'bitcoin/bitcoin',
    'ETH': 'ethereum/go-ethereum',
    'SOL': 'solana-labs/solana',
    'ADA': 'input-output-hk/cardano-node',
    'DOT': 'paritytech/polkadot',
    'LINK': 'smartcontractkit/chainlink',
    'MATIC': 'maticnetwork/bor',
    'AVAX': 'ava-labs/avalanchego',
    'UNI': 'Uniswap/v3-core',
    'AAVE': 'aave/aave-v3-core',
}


@retry_on_failure(max_retries=3, delay=2)
def get_github_dev_activity(
    repo: Annotated[str, "GitHub repo (e.g., 'bitcoin/bitcoin') or symbol (e.g., 'BTC')"]
) -> str:
    """
    Get development activity from GitHub (FREE tier: 5k requests/hour).

    Provides repository development metrics:
    - Recent commits (last 4 weeks)
    - Pull requests (open, closed, merged)
    - Issues (open, closed)
    - Contributors

    Optional: GitHub personal access token for higher rate limits.

    Args:
        repo: GitHub repository (owner/repo) or crypto symbol

    Returns:
        Formatted string with development activity
    """
    # Map symbol to repo if needed
    repo_clean = repo.upper().replace('-USD', '').replace('USDT', '')
    if repo_clean in GITHUB_REPO_MAP:
        repo = GITHUB_REPO_MAP[repo_clean]

    # Get API token from config (optional)
    config = get_config()
    github_token = config.get('github_token', '')

    headers = {'Accept': 'application/vnd.github.v3+json'}
    if github_token:
        headers['Authorization'] = f'token {github_token}'

    try:
        # Get repository info
        repo_url = f"https://api.github.com/repos/{repo}"
        repo_response = requests.get(repo_url, headers=headers, timeout=15)
        repo_response.raise_for_status()
        repo_data = repo_response.json()

        # Get recent commits
        commits_url = f"https://api.github.com/repos/{repo}/commits"
        commits_response = requests.get(commits_url, headers=headers, params={'per_page': 100}, timeout=15)
        commits_response.raise_for_status()
        commits = commits_response.json()

        # Count commits in last 4 weeks
        from datetime import datetime, timedelta, timezone
        four_weeks_ago = datetime.now(timezone.utc) - timedelta(weeks=4)
        recent_commits = 0
        for commit in commits:
            commit_date_str = commit.get('commit', {}).get('author', {}).get('date', '')
            if commit_date_str:
                commit_date = datetime.fromisoformat(commit_date_str.replace('Z', '+00:00'))
                if commit_date > four_weeks_ago:
                    recent_commits += 1

        # Build report
        result_str = f"## GitHub Development Activity: {repo}\n\n"

        result_str += f"### Repository Stats:\n"
        result_str += f"- **Stars**: {repo_data.get('stargazers_count', 0):,}\n"
        result_str += f"- **Forks**: {repo_data.get('forks_count', 0):,}\n"
        result_str += f"- **Watchers**: {repo_data.get('watchers_count', 0):,}\n"
        result_str += f"- **Open Issues**: {repo_data.get('open_issues_count', 0):,}\n"
        result_str += "\n"

        result_str += f"### Recent Activity (Last 4 Weeks):\n"
        result_str += f"- **Commits**: {recent_commits:,}\n"
        result_str += "\n"

        # Analysis
        result_str += f"### Analysis:\n"
        if recent_commits > 100:
            result_str += f"- 🔥 Very active development ({recent_commits} commits/4wks)\n"
        elif recent_commits > 20:
            result_str += f"- ✅ Active development ({recent_commits} commits/4wks)\n"
        elif recent_commits > 0:
            result_str += f"- ⚠️  Low activity ({recent_commits} commits/4wks)\n"
        else:
            result_str += f"- 🚫 No recent commits\n"

        if repo_data.get('stargazers_count', 0) > 10000:
            result_str += f"- ⭐ Highly popular project\n"

        return result_str

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"Repository '{repo}' not found on GitHub"
        elif e.response.status_code == 403:
            return f"GitHub API rate limit exceeded. Consider adding a GitHub token to config."
        else:
            return f"HTTP error fetching GitHub data: {e}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching GitHub dev activity: {str(e)}"
    except Exception as e:
        return f"Error processing GitHub data: {str(e)}"


# Note: get_github_repo_stats is similar to get_github_dev_activity but focuses on static repo stats
# For brevity, we'll make it an alias with different focus
get_github_repo_stats = get_github_dev_activity  # Same implementation, different use case


# ===== REDDIT CRYPTO SENTIMENT =====

@retry_on_failure(max_retries=3, delay=2)
def get_reddit_crypto_sentiment(
    subreddit: Annotated[str, "Subreddit name (e.g., 'cryptocurrency', 'bitcoin')"] = "cryptocurrency",
    limit: int = 25
) -> str:
    """
    Get sentiment from crypto subreddits (FREE, Reddit API).

    Analyzes recent posts from crypto subreddits:
    - r/cryptocurrency (general crypto discussion)
    - r/bitcoin (Bitcoin-specific)
    - r/ethereum (Ethereum-specific)
    - r/CryptoMarkets (trading discussion)

    Provides:
    - Top posts and sentiment
    - Discussion topics
    - Community mood

    Requires Reddit API credentials (free OAuth2).

    Args:
        subreddit: Subreddit to analyze (default: 'cryptocurrency')
        limit: Number of posts to analyze (default: 25)

    Returns:
        Formatted string with sentiment analysis
    """
    # Note: This is a simplified version. Full implementation would use PRAW library
    # and Reddit OAuth2 authentication. For now, we'll use Reddit's JSON API (limited)

    url = f"https://www.reddit.com/r/{subreddit}/hot.json"
    headers = {'User-Agent': 'TradingAgents/1.0'}
    params = {'limit': limit}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if 'data' not in data or 'children' not in data['data']:
            return f"No posts found in r/{subreddit}"

        posts = data['data']['children']

        # Build report
        result_str = f"## Reddit Sentiment: r/{subreddit}\n\n"

        result_str += f"### Top Posts:\n"
        for i, post_data in enumerate(posts[:5], 1):
            post = post_data['data']
            title = post.get('title', 'N/A')
            score = post.get('score', 0)
            num_comments = post.get('num_comments', 0)
            upvote_ratio = post.get('upvote_ratio', 0)

            result_str += f"\n**{i}. {title[:80]}{'...' if len(title) > 80 else ''}**\n"
            result_str += f"- Score: {score:,} | Comments: {num_comments:,} | Upvote Ratio: {upvote_ratio:.0%}\n"

        result_str += "\n### Community Metrics:\n"
        avg_score = sum(p['data'].get('score', 0) for p in posts) / len(posts)
        avg_comments = sum(p['data'].get('num_comments', 0) for p in posts) / len(posts)
        avg_upvote_ratio = sum(p['data'].get('upvote_ratio', 0) for p in posts) / len(posts)

        result_str += f"- **Average Score**: {avg_score:.0f}\n"
        result_str += f"- **Average Comments**: {avg_comments:.0f}\n"
        result_str += f"- **Average Upvote Ratio**: {avg_upvote_ratio:.0%}\n"
        result_str += "\n"

        # Sentiment analysis
        result_str += f"### Sentiment:\n"
        if avg_upvote_ratio > 0.85:
            result_str += f"- 🟢 **Positive**: High upvote ratio ({avg_upvote_ratio:.0%}) suggests bullish sentiment\n"
        elif avg_upvote_ratio > 0.70:
            result_str += f"- ⚪ **Neutral**: Moderate upvote ratio ({avg_upvote_ratio:.0%})\n"
        else:
            result_str += f"- 🔴 **Negative**: Low upvote ratio ({avg_upvote_ratio:.0%}) suggests bearish sentiment\n"

        if avg_comments > 50:
            result_str += f"- 💬 **High Engagement**: Averaging {avg_comments:.0f} comments per post\n"

        return result_str

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return f"Rate limit exceeded for Reddit API. Please wait a moment and try again."
        else:
            return f"HTTP error fetching Reddit data: {e}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching Reddit sentiment: {str(e)}"
    except Exception as e:
        return f"Error processing Reddit data: {str(e)}"


# ===== BITCOIN MINING METRICS =====

@retry_on_failure(max_retries=3, delay=2)
def get_bitcoin_mining_metrics() -> str:
    """
    Get Bitcoin mining metrics (100% FREE, no API key required).

    Provides mining-specific data:
    - Hash rate and difficulty
    - Mining profitability estimates
    - Next difficulty adjustment
    - Block rewards and fees

    Uses Blockchain.info API (completely free, no limits).

    Returns:
        Formatted string with mining metrics and analysis
    """
    # Use Blockchain.info for basic mining stats
    stats_url = "https://blockchain.info/stats?format=json"

    try:
        response = requests.get(stats_url, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Build report
        result_str = f"## Bitcoin Mining Metrics\n\n"

        # Hash rate and difficulty
        hash_rate = data.get('hash_rate', 0)  # in GH/s
        difficulty = data.get('difficulty', 0)
        next_retarget = data.get('nextretarget', 0)

        result_str += f"### Network Hashrate & Difficulty:\n"
        result_str += f"- **Network Hash Rate**: {hash_rate / 1_000_000:.2f} EH/s\n"
        result_str += f"- **Current Difficulty**: {difficulty:,.0f}\n"
        result_str += f"- **Next Difficulty Adjustment**: Block {next_retarget:,}\n"
        result_str += "\n"

        # Block and reward stats
        n_blocks_total = data.get('n_blocks_total', 0)
        n_blocks_mined = data.get('n_blocks_mined', 0)  # Last 24h
        minutes_between_blocks = data.get('minutes_between_blocks', 0)

        result_str += f"### Block Production:\n"
        result_str += f"- **Total Blocks Mined**: {n_blocks_total:,}\n"
        result_str += f"- **Blocks (24h)**: {n_blocks_mined}\n"
        result_str += f"- **Average Block Time**: {minutes_between_blocks:.1f} minutes\n"
        result_str += f"- **Target Block Time**: 10.0 minutes\n"

        # Calculate if ahead or behind target
        if minutes_between_blocks > 0:
            time_variance = ((minutes_between_blocks - 10) / 10) * 100
            result_str += f"- **Variance from Target**: {time_variance:+.1f}%\n"
        result_str += "\n"

        # Miner revenue
        total_fees_btc = data.get('total_fees_btc', 0) / 100_000_000  # Convert from satoshis
        market_price_usd = data.get('market_price_usd', 0)

        # Estimate daily miner revenue (subsidy + fees)
        # Current subsidy is 3.125 BTC per block (after 2024 halving)
        blocks_per_day = 144  # Target: 6 blocks/hour * 24 hours
        actual_blocks_per_day = n_blocks_mined if n_blocks_mined > 0 else blocks_per_day
        block_subsidy = 3.125  # BTC per block (post-2024 halving)

        daily_subsidy_btc = actual_blocks_per_day * block_subsidy
        daily_fees_btc = total_fees_btc
        daily_total_btc = daily_subsidy_btc + daily_fees_btc
        daily_total_usd = daily_total_btc * market_price_usd

        result_str += f"### Miner Revenue (24h Estimate):\n"
        result_str += f"- **Block Subsidy**: {daily_subsidy_btc:.2f} BTC (${daily_subsidy_btc * market_price_usd:,.0f})\n"
        result_str += f"- **Transaction Fees**: {daily_fees_btc:.2f} BTC (${daily_fees_btc * market_price_usd:,.0f})\n"
        result_str += f"- **Total Revenue**: {daily_total_btc:.2f} BTC (${daily_total_usd:,.0f})\n"

        # Fee percentage of revenue
        fee_percentage = 0
        if daily_total_btc > 0:
            fee_percentage = (daily_fees_btc / daily_total_btc) * 100
            result_str += f"- **Fees as % of Revenue**: {fee_percentage:.1f}%\n"
        result_str += "\n"

        # Mining economics
        result_str += f"### Mining Economics:\n"
        if hash_rate > 0:
            # Revenue per EH/s per day
            revenue_per_eh = (daily_total_usd / (hash_rate / 1_000_000))
            result_str += f"- **Revenue per EH/s/day**: ${revenue_per_eh:,.2f}\n"

        result_str += f"- **Current BTC Price**: ${market_price_usd:,.2f}\n"
        result_str += "\n"

        # Analysis
        result_str += f"### Mining Analysis:\n"

        # Difficulty trend (based on block time)
        if minutes_between_blocks < 9.5:
            result_str += f"- ⬆️  Faster than target blocks ({minutes_between_blocks:.1f} min) - Difficulty likely to INCREASE\n"
        elif minutes_between_blocks > 10.5:
            result_str += f"- ⬇️  Slower than target blocks ({minutes_between_blocks:.1f} min) - Difficulty likely to DECREASE\n"
        else:
            result_str += f"- ➡️  On-target block time ({minutes_between_blocks:.1f} min) - Difficulty likely to remain stable\n"

        # Hash rate strength
        if hash_rate > 500_000_000:  # > 500 EH/s
            result_str += f"- 🔒 Extremely high network security ({hash_rate / 1_000_000:.0f} EH/s)\n"

        # Fee analysis
        if fee_percentage > 10:
            result_str += f"- 💰 High fee revenue ({fee_percentage:.1f}%) - Network congestion or high demand\n"
        elif fee_percentage < 2:
            result_str += f"- ⚠️  Low fee revenue ({fee_percentage:.1f}%) - Miners heavily reliant on subsidy\n"

        # Profitability indicator
        if daily_total_usd > 50_000_000:  # > $50M daily
            result_str += f"- 💎 High miner revenue (${daily_total_usd/1_000_000:.1f}M/day) - Mining very profitable\n"

        return result_str

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return f"Rate limit exceeded for Blockchain.info API. Please wait a moment and try again."
        else:
            return f"HTTP error fetching Bitcoin mining data: {e}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching Bitcoin mining metrics: {str(e)}"
    except Exception as e:
        return f"Error processing Bitcoin mining data: {str(e)}"
