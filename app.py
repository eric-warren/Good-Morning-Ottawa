import threading
import time
from flask import Flask, render_template, request, jsonify
import json
from getSkeets import updateSkeets

app = Flask(__name__)

def load_tweets():
    with open('parsed_tweets.json', 'r') as f:
        return json.load(f)

def save_tweets(tweets):
    with open('parsed_tweets.json', 'w') as f:
        json.dump(tweets, f, indent=2)

def scheduled_task():
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
    tweet_id = request.form.get('tweet-id')
    category = request.form.get('category')
    longitude = request.form.get('longitude')
    latitude = request.form.get('latitude')

    tweets = load_tweets()
    tweet_found = False
    for tweet in tweets:
        if tweet['id'] == float(tweet_id):
            tweet['category'] = category
            tweet['longitude'] = float(longitude) if longitude else None
            tweet['latitude'] = float(latitude) if latitude else None
            tweet_found = True
            break

    if tweet_found:
        save_tweets(tweets)
        return jsonify(success=True)
    else:
        return jsonify(success=False), 404

if __name__ == '__main__':
    # Start the scheduled task in a separate thread
    task_thread = threading.Thread(target=scheduled_task)
    task_thread.daemon = True
    task_thread.start()

    app.run(debug=True)

