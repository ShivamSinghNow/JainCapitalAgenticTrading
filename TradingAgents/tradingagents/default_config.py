import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": os.path.join(os.getcwd(), "data"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o-mini",
    "quick_think_llm": "gpt-4o-mini",
    "backend_url": "https://api.openai.com/v1",
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Tool settings
    "online_tools": True,
    # API Keys for FREE crypto data sources
    # Get free API keys from:
    # - CryptoPanic: https://cryptopanic.com/developers/api/ (3000 requests/day)
    # - CryptoCompare: https://min-api.cryptocompare.com (100k calls/month)
    # - Reddit: https://www.reddit.com/prefs/apps (OAuth2, completely free)
    # - GitHub: https://github.com/settings/tokens (5000 requests/hour)
    # - Etherscan: https://etherscan.io/myapikey (5 calls/second)
    "api_keys": {
        "cryptopanic": os.getenv("CRYPTOPANIC_API_KEY", ""),  # Free tier: 3000 req/day
        "cryptocompare": os.getenv("CRYPTOCOMPARE_API_KEY", ""),  # Free tier: 100k calls/month
        "reddit_client_id": os.getenv("REDDIT_CLIENT_ID", ""),  # Free OAuth2
        "reddit_client_secret": os.getenv("REDDIT_CLIENT_SECRET", ""),
        "github_token": os.getenv("GITHUB_TOKEN", ""),  # Free: 5000 req/hour
        "etherscan": os.getenv("ETHERSCAN_API_KEY", ""),  # Free tier: 5 calls/second
    },
    # Cache TTL (Time To Live) settings in seconds
    # Adjust based on your trading frequency and data freshness requirements
    "cache_ttl": {
        "price_data": 300,  # 5 minutes - frequent updates for price data
        "exchange_data": 900,  # 15 minutes - funding rates, OI, long/short ratios
        "onchain_data": 21600,  # 6 hours - on-chain metrics change slowly
        "news_data": 3600,  # 1 hour - news updates
        "social_data": 3600,  # 1 hour - social sentiment metrics
        "defi_data": 21600,  # 6 hours - DeFi protocol metrics
        "github_data": 43200,  # 12 hours - development activity
    },
}
