import asyncio
import httpx
from faker import Faker
import random
import json
from fastapi import websockets

fake = Faker()
URL = "http://localhost:8080/api"  # change if your API runs elsewhere

NUM_USERS = 50
MIN_TWEETS = 5
MAX_TWEETS = 10
limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
semaphore = asyncio.Semaphore(20)

users = []
tokens = []

# -----------------------
# 1. Register users
# -----------------------
async def register_user(client):
 async with semaphore:

    data = {
        "username": fake.user_name(),
        "password": "Password123!"
    }
    response = await client.post(f"{URL}/auth/register", json=data)
    if response.status_code in(201,200) :
        users.append(data)

async def register_all():
    async with httpx.AsyncClient(limits=limits, timeout=30.0) as client:
        tasks = [register_user(client) for _ in range(NUM_USERS)]
        await asyncio.gather(*tasks)

# -----------------------
# 2. Login users
# -----------------------
async def login_user(client, user):
  async with semaphore:
    data = {"username": user["username"], "password": "Password123!"}
    response = await client.post(f"{URL}/auth/login", data=data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        tokens.append(token)

async def login_all():
    async with httpx.AsyncClient(limits=limits, timeout=30.0) as client:
        tasks = [login_user(client, user) for user in users]
        await asyncio.gather(*tasks)

# -----------------------
# 3. Post tweets
# -----------------------
async def post_tweet(client, token):
  async with semaphore:
    headers = {"Authorization": f"Bearer {token}"}
    data = {"content": fake.sentence()}
    await client.post(f"{URL}/tweet/", headers=headers, json=data)

async def post_all_tweets():
    async with httpx.AsyncClient(limits=limits, timeout=30.0) as client:
        tasks = []
        for token in tokens:
            num_tweets = random.randint(MIN_TWEETS, MAX_TWEETS)
            for _ in range(num_tweets):
                tasks.append(post_tweet(client, token))
        await asyncio.gather(*tasks)
async def follow_user(client, token, target_user_id,target_username):
 async with semaphore:
    headers = {"Authorization": f"Bearer {token}"}
    data = {
            "id": target_user_id,
            "username": target_username
        }

    await client.post(f"{URL}/follow/", headers=headers, json=data)

async def follow_randomly():
    ID_OFFSET = 1  # set to 1 if the first registered user has id=1 (common). Set to 0 if ids start at 0.
    FOLLOW_PER_USER = 5

    async with httpx.AsyncClient(limits=limits, timeout=30.0) as client:
        tasks = []
        total = len(tokens)
        if total == 0:
            return

        for i, token in enumerate(tokens):
            current_id = i + ID_OFFSET
            # build list of candidate target indices (exclude current)
            candidate_indices = [j for j in range(total) if j != i]
            if not candidate_indices:
                continue
            k = min(FOLLOW_PER_USER, len(candidate_indices))
            chosen = random.sample(candidate_indices, k=k)
            for j in chosen:
                target_id = j + ID_OFFSET
                # try to get username from users list if available, otherwise empty
                target_username = users[j].get("username") if j < len(users) and isinstance(users[j], dict) else ""
                tasks.append(asyncio.create_task(follow_user(client, token, target_id, target_username)))

        if tasks:
            await asyncio.gather(*tasks)
# ...existing code...
    
        await asyncio.gather(*tasks)
async def open_ws_connection(token, user_index):
    uri = f"ws://localhost:8080/ws/notifications?token={token}"
    async with websockets.connect(uri) as ws:
        print(f"User {user_index} connected to WS")
        try:
            async for message in ws:
                print(f"User {user_index} got: {message}")
        except Exception as e:
            print(f"User {user_index} ws error: {e}")
async def open_some_ws():
    tasks = []
    for i, token in enumerate(tokens[:20]):  # only first 20 for demo
        tasks.append(open_ws_connection(token, i))
    await asyncio.gather(*tasks)
async def get_timeline(client, token):
  async with semaphore:
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(f"{URL}/timeline/", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []
async def check_timelines():
    async with httpx.AsyncClient(limits=limits, timeout=30.0) as client:
        for token in random.sample(tokens, 5):
            timeline = await get_timeline(client, token)
            print("Timeline:", timeline[:3])  # preview first 3 tweets


# -----------------------
# 4. Run everything
# -----------------------
async def main():
    print("Registering users...")
    await register_all()

    print("Logging in users...")
    await login_all()

    print("Posting tweets...")
    await post_all_tweets()

    print("Making users follow each other...")
    await follow_randomly()

    # print("Opening websocket connections...")
    # asyncio.create_task(open_some_ws())  # don’t block

    print("Checking random timelines...")
    await check_timelines()

    with open("tokens.json", "w") as f:
        json.dump(tokens, f)

    # Optional: save tokens for later load testing
    with open("tokens.json", "w") as f:
        json.dump(tokens, f)
    print("Tokens saved to tokens.json")

if __name__ == "__main__":
    asyncio.run(main())
