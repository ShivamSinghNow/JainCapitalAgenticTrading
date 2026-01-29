"""
Test API Keys Loading from .env

This script verifies that API keys are being loaded correctly from the .env file.
"""

print("=" * 80)
print("🔑 Testing API Keys from .env")
print("=" * 80)
print()

# Test loading config
print("Loading configuration...")
from TradingAgents.tradingagents.dataflows.config import get_config

config = get_config()
api_keys = config.get('api_keys', {})

print("\n✅ Configuration loaded successfully!\n")
print("API Keys Status:")
print("-" * 80)

keys_to_check = [
    ("CryptoPanic", "cryptopanic"),
    ("CryptoCompare/CoinDesk", "cryptocompare"),
    ("GitHub", "github_token"),
    ("Etherscan", "etherscan"),
    ("Reddit Client ID", "reddit_client_id"),
    ("Reddit Client Secret", "reddit_client_secret"),
]

configured_count = 0
for name, key in keys_to_check:
    value = api_keys.get(key, "")
    if value and value.strip():
        # Show only first/last 4 chars for security
        if len(value) > 8:
            masked = f"{value[:4]}...{value[-4:]}"
        else:
            masked = "***"
        print(f"✅ {name:25} : Configured ({masked})")
        configured_count += 1
    else:
        print(f"❌ {name:25} : Not configured")

print()
print(f"Total configured: {configured_count}/{len(keys_to_check)}")
print()

if configured_count > 0:
    print("🎉 Great! API keys are being loaded from .env file")
else:
    print("⚠️  No API keys found. Make sure .env file exists in the project root.")

print("=" * 80)
