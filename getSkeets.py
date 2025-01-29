from atproto import Client
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

BLSKY_USERNAME = os.getenv("BLSKY_USERNAME")
BLSKY_PASSWORD = os.getenv("BLSKY_PASSWORD")
MONGO_URI = os.getenv("MONGO_URI")  # Store this in your .env file

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client.get_database("tweets_db")  # Change to your database name
collection = db.get_collection("tweets")  # Change to your collection name

def updateSkeets():
    """Fetches new Bluesky posts and stores them in MongoDB."""
    bl_client = Client()
    bl_client.login(BLSKY_USERNAME, BLSKY_PASSWORD)
    
    data = bl_client.get_author_feed(
        actor='did:plc:f6th6vxdusiyht2avm2ejiwd',
        filter='posts_no_replies',
        limit=100,
    )

    feed = data.feed

    for viewpost in feed:
        text = viewpost.post.record.text.lower()
        if 'good morning ottawa' in text and 'bonjour ottawa' in text:
            created = viewpost.post.record.created_at.split('T')[0]
            image_url = viewpost.post.embed.images[0].fullsize if viewpost.post.embed else None

            # Check if the post is already stored in MongoDB
            existing_entry = collection.find_one({"date": created})
            if not existing_entry:
                new_entry = {
                    "date": created,
                    "image_url": image_url,
                    "category": "",
                    "longitude": None,
                    "latitude": None,
                    "id": collection.count_documents({}) + 1  # Incremental ID
                }
                collection.insert_one(new_entry)
                print(f"Added new skeet: {new_entry}")

if __name__ == "__main__":
    updateSkeets()
