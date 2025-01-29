from atproto import Client
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BLSKY_USERNAME = os.getenv("BLSKY_USERNAME")
BLSKY_PASSWORD = os.getenv("BLSKY_PASSWORD")


def updateSkeets():
    client = Client()
    client.login(BLSKY_USERNAME, BLSKY_PASSWORD)
    
    data = client.get_author_feed(
        actor='did:plc:f6th6vxdusiyht2avm2ejiwd',
        filter='posts_no_replies',
        limit=100,
    )

    feed = data.feed
    df = pd.read_json('parsed_tweets.json', dtype={'date': str})

    for viewpost in feed:
        if 'good morning ottawa' in viewpost.post.record.text.lower() and 'bonjour ottawa' in viewpost.post.record.text.lower():
            created = viewpost.post.record.created_at.split('T')[0]
            id = df['id'].max()
            if created not in df['date'].values:
                id += 1
                new_row = {
                    'date': created,
                    'image_url': viewpost.post.embed.images[0].fullsize,
                    'category': '',
                    'longitude': '',
                    'latitude': '',
                    'id': id
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_json('parsed_tweets.json', orient='records', index=False)

if __name__ == "__main__":
    updateSkeets()
