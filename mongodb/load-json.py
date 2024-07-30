import json
import pymongo
from pymongo import MongoClient
import sys

client = MongoClient('mongodb://localhost:{}'.format(sys.argv[1]))

# Open data base in MongoDB server
db = client["291db"]

# Open tweet_info collection in database
infoCollection = db["tweet_info"]

# Delete any existing documents in collection
infoCollection.delete_many({})

tweets = []

# Load JSON file data to be inserted in collection into array
# Change "json/10.json" to a variable
with open(sys.argv[2], "r") as file:
    for line in file:
        try:
            data = json.loads(line)
            tweets.append(data)
        except json.JSONDecodeError as e:
            print(f"Error deconfing JSON: {e}")
            continue

# Enter tweets in batches of 1000
for i in range(0, len(tweets), 1000):
    batch = tweets[i:i + 1000]
    infoCollection.insert_many(batch)

# Create indexes with case-insensitive collation
infoCollection.create_index([("content", "text")])
infoCollection.create_index([("displayname", "text"), ("location", "text")], collation={'locale': 'en', 'strength': 2})
infoCollection.create_index([("retweetCount", pymongo.DESCENDING)], collation={'locale': 'en', 'strength': 2})
infoCollection.create_index([("likeCount", pymongo.DESCENDING)], collation={'locale': 'en', 'strength': 2})
infoCollection.create_index([("quoteCount", pymongo.DESCENDING)], collation={'locale': 'en', 'strength': 2})
infoCollection.create_index([("followersCount", pymongo.DESCENDING)], collation={'locale': 'en', 'strength': 2})
