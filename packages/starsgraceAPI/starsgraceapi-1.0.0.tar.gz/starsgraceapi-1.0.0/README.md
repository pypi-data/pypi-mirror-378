# Fragment API Python Client

A Python client library for interacting with the Fragment API, which provides programmatic access to Telegram Stars, Premium, and TON services.

## Installation

```bash
pip install starsgraceAPI
```

## Usage

```python
from fragment_api import FragmentAPI

# Initialize client
client = FragmentAPI()

# Create authentication session
auth_response = client.create_auth(
    wallet_mnemonic="word1 word2 word3 ...",
    cookies="cookie1=value1; cookie2=value2",
    hash_value="121ff4016366e2a38f"
)

# Check balance
balance = client.get_balance()

# Buy stars
stars_response = client.buy_stars("@username", quantity=50, show_sender=False)

# Gift premium
premium_response = client.gift_premium("@username", months=3, show_sender=False)

# Top up TON
ton_response = client.topup_ton("@username", amount=1, show_sender=False)

# Search users
stars_user = client.get_user_stars("@username")
premium_user = client.get_user_premium("@username")

# Check API health
health = client.health_check()

# Close session
client.close()
```

## Features

- Session management with persistent auth_key
- Support for all Fragment API endpoints
- Error handling for API responses
- Type hints for better code completion
- Clean and intuitive interface

## Requirements

- Python 3.7+
- requests>=2.28.0

## License

MIT License