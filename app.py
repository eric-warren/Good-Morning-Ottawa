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

def load_tweets(start_date=None, end_date=None, category=None):
    """
    Fetch tweets from MongoDB with optional date range and category filters.
    
    :param start_date: Start date for filtering (inclusive)
    :param end_date: End date for filtering (inclusive)
    :param category: Category to filter by
    :return: List of filtered tweets
    """
    query = {}

    # Add date range filter if provided
    if start_date and end_date:
        query['date'] = {'$gte': start_date, '$lte': end_date}
    elif start_date:
        query['date'] = {'$gte': start_date}
    elif end_date:
        query['date'] = {'$lte': end_date}

    # Add category filter if provided
    if category:
        if category == 'uncategorized':
            query['category'] = {'$in': [None, '']}
        elif category == 'categorized':
            query['category'] = {'$nin': [None, '']}
        else:
            query['category'] = category

    # Fetch tweets based on the constructed query
    return list(collection.find(query, {"_id": 0}))  # Exclude MongoDB's default _id field

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
    date = request.args.get('date')
    return render_template('index.html', filter_date=date)

@app.route('/get_tweets')
def get_tweets():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    filter_type = request.args.get('category', 'all')


    category = None
    if filter_type in ['uncategorized', 'categorized']:
        category = filter_type
    elif filter_type != 'all':
        category = filter_type

    tweets = load_tweets(start_date, end_date, category)

    return jsonify(tweets)

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
    tweets = load_tweets()
    tweets_with_images = [t for t in tweets if t.get('image_url')]
    return render_template('pictures.html', tweets=tweets_with_images)

# Add a new route for paginated images
@app.route('/get_paginated_images')
def get_paginated_images():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 12))
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    filter_type = request.args.get('filter', 'all')

    category = None
    if filter_type in ['uncategorized', 'categorized']:
        category = filter_type
    elif filter_type != 'all':
        category = filter_type

    tweets = load_tweets(start_date, end_date, category)
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
    task_thread = threading.Thread(target=scheduled_task, daemon=True)
    task_thread.start()

    app.run(host='0.0.0.0',port=80)