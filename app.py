import threading
import time
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import os
from getSkeets import updateSkeets

app = Flask(__name__)

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")  # Store this in your .env file

client = MongoClient(MONGO_URI)
db = client.get_database("tweets_db")  # Replace with your database name
collection = db.get_collection("tweets")  # Replace with your collection name

def load_tweets():
    """Fetch all tweets from MongoDB."""
    return list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's default _id field

def save_tweets(tweet):
    """Update or insert a tweet into MongoDB."""
    collection.update_one({"id": tweet["id"]}, {"$set": tweet}, upsert=True)

def scheduled_task():
    """Runs updateSkeets every hour."""
    while True:
        updateSkeets()
        print("Updating skeets...")
        time.sleep(3600)  # Sleep for 1 hour

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_tweets')
def get_tweets():
    tweets = load_tweets()
    filter_type = request.args.get('filter', 'all')

    if filter_type == 'uncategorized':
        filtered_tweets = [t for t in tweets if not t.get('category')]
    elif filter_type == 'categorized':
        filtered_tweets = [t for t in tweets if t.get('category')]
    else:
        filtered_tweets = tweets

    return jsonify(filtered_tweets)

@app.route('/categorize', methods=['POST'])
def categorize():
    tweet_id = float(request.form.get('tweet-id'))
    category = request.form.get('category')
    longitude = request.form.get('longitude')
    latitude = request.form.get('latitude')

    update_data = {
        "category": category,
        "longitude": float(longitude) if longitude else None,
        "latitude": float(latitude) if latitude else None,
    }

    result = collection.update_one({"id": tweet_id}, {"$set": update_data})

    if result.matched_count > 0:
        return jsonify(success=True)
    else:
        return jsonify(success=False), 404

if __name__ == '__main__':
    task_thread = threading.Thread(target=scheduled_task, daemon=True)
    task_thread.start()

    app.run(debug=True,port=80)