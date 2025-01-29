import threading
import time
from flask import Flask, render_template, request, jsonify, url_for
from pymongo import MongoClient
import os
from getSkeets import updateSkeets

app = Flask(__name__)

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")  # Store this in your .env file

client = MongoClient(MONGO_URI)
print(f"Connected to MongoDB: {client}")
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
    return render_template('pictures.html')

@app.route('/get_tweets')
def get_tweets():
    tweets = load_tweets()
    print(f"Retrieved {len(tweets)} tweets")
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

@app.route('/pictures')
def pictures():
    return render_template('pictures.html')

# Add a new route for paginated images
@app.route('/get_paginated_images')
def get_paginated_images():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 12))

    tweets = load_tweets()
    tweets_with_images = [t for t in tweets if t.get('image_url')]

    total_images = len(tweets_with_images)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_images = tweets_with_images[start_index:end_index]

    return jsonify({
        'images': paginated_images,
        'total_images': total_images,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_images + page_size - 1) // page_size
    })
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)