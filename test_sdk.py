"""Quick test for the ApiTwitter Python SDK."""

import sys
sys.path.insert(0, ".")

from apitwitter import ApiTwitter
from apitwitter.exceptions import ApiTwitterError

API_KEY = input("Enter your API key: ").strip()

client = ApiTwitter(API_KEY)

print("\n--- Test 1: Get user profile ---")
try:
    user = client.get_user("elonmusk")
    print(f"  Name: {user.get('name')}")
    print(f"  Username: {user.get('userName')}")
    print(f"  Followers: {user.get('followers')}")
    print("  [OK] PASSED")
except ApiTwitterError as e:
    print(f"  [FAIL]: [{e.status_code}] {e}")

print("\n--- Test 2: Search tweets ---")
try:
    results = client.search("python", count=3)
    tweets = results.get("tweets", [])
    print(f"  Found {len(tweets)} tweets")
    for t in tweets[:2]:
        text = t.get("text", "")[:80]
        print(f"  - {text.encode('ascii', 'replace').decode()}...")
    print("  [OK] PASSED")
except ApiTwitterError as e:
    print(f"  [FAIL]: [{e.status_code}] {e}")

print("\n--- Test 3: Get user tweets ---")
try:
    result = client.get_user_tweets("elonmusk")
    tweets = result.get("tweets", [])
    print(f"  Got {len(tweets)} tweets")
    if tweets:
        text = tweets[0].get("text", "")[:80]
        print(f"  Latest: {text.encode('ascii', 'replace').decode()}...")
    print("  [OK] PASSED")
except ApiTwitterError as e:
    print(f"  [FAIL]: [{e.status_code}] {e}")

print("\n--- Test 4: Get followers ---")
try:
    result = client.get_followers("elonmusk", count=5)
    followers = result.get("followers", [])
    print(f"  Got {len(followers)} followers")
    print("  [OK] PASSED")
except ApiTwitterError as e:
    print(f"  [FAIL]: [{e.status_code}] {e}")

print("\n--- Test 5: Get user by ID ---")
try:
    user = client.get_user_by_id("44196397")  # Elon Musk
    print(f"  Name: {user.get('name')}")
    print("  [OK] PASSED")
except ApiTwitterError as e:
    print(f"  [FAIL]: [{e.status_code}] {e}")

print("\n--- Test 6: Error handling (invalid user) ---")
try:
    client.get_user("thisisnotarealuser999999")
    print("  [FAIL]: should have raised an error")
except ApiTwitterError as e:
    print(f"  Caught: {e.__class__.__name__}")
    print("  [OK] PASSED")

client.close()
print("\n=== All tests complete ===")
