# ApiTwitter Python SDK

Official Python SDK for the [ApiTwitter](https://apitwitter.com) REST API — access Twitter/X data without the official developer portal.

## Installation

```bash
pip install apitwitter
```

## Quick Start

```python
from apitwitter import ApiTwitter

client = ApiTwitter("your-api-key")

# Get user profile (uses server pool — no cookies needed)
user = client.get_user("elonmusk")
print(user["name"], user["followers"])

# Search tweets
results = client.search("python programming", count=10)
for tweet in results["tweets"]:
    print(tweet["text"])

# Get user tweets
tweets = client.get_user_tweets("elonmusk")
for tweet in tweets["tweets"]:
    print(tweet["text"])
```

## Read Operations (Server Pool)

These endpoints use the server-side pool — no cookies or proxy needed:

```python
client = ApiTwitter("your-api-key")

# Users
user = client.get_user("username")
user = client.get_user_by_id("12345")
users = client.get_users_batch(["id1", "id2", "id3"])
followers = client.get_followers("username", count=100)
following = client.get_following("username", count=100)

# Tweets
tweets = client.get_user_tweets("username")
tweets = client.get_tweets(["tweet_id_1", "tweet_id_2"])

# Search
results = client.search("query", product="Top", count=20)
# product options: "Top", "Latest", "People", "Photos", "Videos"
```

## Write Operations (Own Credentials)

Write endpoints require your own Twitter cookies and proxy:

```python
COOKIE = "ct0=...;auth_token=..."
PROXY = "http://user:pass@host:port"

# Post a tweet
client.create_tweet("Hello from ApiTwitter SDK!", COOKIE, PROXY)

# Like / unlike
client.like("tweet_id", COOKIE, PROXY)
client.unlike("tweet_id", COOKIE, PROXY)

# Retweet
client.retweet("tweet_id", COOKIE, PROXY)

# Follow / unfollow
client.follow("user_id", COOKIE, PROXY)
client.unfollow("user_id", COOKIE, PROXY)

# Send DM
client.send_dm("user_id", "Hello!", COOKIE, PROXY)

# Bookmarks
client.add_bookmark("tweet_id", COOKIE, PROXY)
bookmarks = client.get_bookmarks(COOKIE, PROXY)

# Timeline
timeline = client.get_timeline_for_you(COOKIE, PROXY, count=20)
latest = client.get_timeline_latest(COOKIE, PROXY, count=20)
```

## Pagination

```python
# First page
result = client.get_followers("username", count=100)
followers = result["followers"]

# Next page
if result.get("next_cursor"):
    result = client.get_followers("username", count=100, cursor=result["next_cursor"])
    followers.extend(result["followers"])
```

## Error Handling

```python
from apitwitter import ApiTwitter
from apitwitter.exceptions import (
    AuthenticationError,
    InsufficientCreditsError,
    RateLimitError,
    NotFoundError,
)

client = ApiTwitter("your-api-key")

try:
    user = client.get_user("username")
except AuthenticationError:
    print("Invalid API key")
except InsufficientCreditsError:
    print("Top up your balance")
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
except NotFoundError:
    print("User not found")
```

## Lists, Communities, Topics

```python
COOKIE = "ct0=...;auth_token=..."
PROXY = "http://user:pass@host:port"

# Lists
client.create_list("My List", COOKIE, PROXY, description="A list")
client.get_list_tweets("list_id", COOKIE, PROXY)
client.add_list_member("list_id", "user_id", COOKIE, PROXY)

# Communities
communities = client.explore_communities(COOKIE, PROXY)
client.join_community("community_id", COOKIE, PROXY)

# Topics
client.follow_topic("topic_id", COOKIE, PROXY)
```

## Configuration

```python
client = ApiTwitter(
    api_key="your-api-key",
    base_url="https://api.apitwitter.com",  # default
    timeout=30.0,                            # request timeout in seconds
)
```

## Links

- [Documentation](https://docs.apitwitter.com)
- [API Reference](https://docs.apitwitter.com/api-reference)
- [Website](https://apitwitter.com)
- [Get API Key](https://apitwitter.com/dashboard)
- [Telegram Support](https://t.me/ApiTwitter)
