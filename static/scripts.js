function categorizeTweet(tweetId, category, longitude, latitude) {
    fetch('/categorize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'tweet-id': tweetId,
            'category': category,
            'longitude': longitude,
            'latitude': latitude
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Tweet categorized successfully!');
        } else {
            alert('Failed to update category.');
        }
    })
    .catch(error => console.error('Error:', error));
}

let tweets = [];
let currentTweetIndex = 0;
let map, marker;

function initMap() {
    map = L.map('map').setView([45.4215, -75.6972], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    map.on('click', function(e) {
        placeMarker(e.latlng);
    });
}

function placeMarker(latlng) {
    if (marker) {
        map.removeLayer(marker);
    }
    marker = L.marker(latlng).addTo(map);
    tweets[currentTweetIndex].latitude = latlng.lat;
    tweets[currentTweetIndex].longitude = latlng.lng;
}

function loadTweets() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    const categoryFilter = document.getElementById('category-filter').value;


    const url = new URL('/get_tweets', window.location.origin);
    if (startDate) url.searchParams.append('start_date', startDate);
    if (endDate) url.searchParams.append('end_date', endDate);
    if (categoryFilter !== 'all') url.searchParams.append('category', categoryFilter);


    // Show loading indicator
    const loadingIndicator = document.getElementById('loading') || document.createElement('div');
    loadingIndicator.id = 'loading';
    loadingIndicator.textContent = 'Loading...';
    document.body.appendChild(loadingIndicator);

    fetch(url)
        .then(response => response.json())
        .then(data => {
            tweets = data;
            currentTweetIndex = 0;
            if (tweets.length > 0) {
                displayTweet();
                updateNavigationButtons();
            } else {
                displayNoTweetsMessage();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            displayErrorMessage();
        })
        .finally(() => {
            // Hide loading indicator
            loadingIndicator.remove();
        });
}

document.getElementById('apply-filters').addEventListener('click', loadTweets);

// Call loadTweets on page load to display initial tweets
document.addEventListener('DOMContentLoaded', loadTweets);

function displayNoTweetsMessage() {
    const tweetContainer = document.getElementById('tweet-container');
    tweetContainer.innerHTML = '<p>No tweets available for the selected filter.</p>';
}

function displayErrorMessage() {
    const tweetContainer = document.getElementById('tweet-container');
    tweetContainer.innerHTML = '<p>An error occurred while loading tweets. Please try again later.</p>';
}

function displayTweet() {
    const tweet = tweets[currentTweetIndex];
    if (tweet) {
        const tweetImage = document.getElementById('tweet-image');
        const tweetDate = document.getElementById('tweet-date');

        tweetImage.src = tweet.image_url || '';
        tweetImage.alt = `Tweet image for ${tweet.date}`;
        tweetImage.onerror = function() {
            this.src = 'path/to/placeholder-image.jpg';
            this.alt = 'Image not available';
        };

        tweetDate.textContent = `Date: ${tweet.date || 'Unknown'}`;

        document.getElementById('tweet-id').value = tweet.id || '';
        document.getElementById('category').value = tweet.category || '';

        if (marker) {
            map.removeLayer(marker);
        }

        if (tweet.latitude && tweet.longitude) {
            const latlng = L.latLng(tweet.latitude, tweet.longitude);
            placeMarker(latlng);
            map.setView(latlng, 13);
        } else {
            map.setView([45.4215, -75.6972], 11);
        }
    } else {
        displayNoTweetsMessage();
    }
}

function updateNavigationButtons() {
    document.getElementById('back-button').disabled = currentTweetIndex === 0;
    document.getElementById('next-button').disabled = currentTweetIndex === tweets.length - 1;
}

document.getElementById('back-button').addEventListener('click', function() {
    if (currentTweetIndex > 0) {
        currentTweetIndex--;
        displayTweet();
        updateNavigationButtons();
    }
});

document.getElementById('next-button').addEventListener('click', function() {
    if (currentTweetIndex < tweets.length - 1) {
        currentTweetIndex++;
        displayTweet();
        updateNavigationButtons();
    }
});

//document.getElementById('filter').addEventListener('change', loadTweets);

document.getElementById('categorization-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const tweet = tweets[currentTweetIndex];
    if (tweet.longitude && tweet.latitude) {
        formData.append('longitude', tweet.longitude);
        formData.append('latitude', tweet.latitude);
    }

    fetch('/categorize', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            tweets[currentTweetIndex].category = formData.get('category');
            if (currentTweetIndex < tweets.length - 1) {
                currentTweetIndex++;
                displayTweet();
                updateNavigationButtons();
            } else {
                alert('All tweets have been categorized!');
            }
        } else {
            alert('Failed to update category.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to update category.');
    });
});

initMap();
loadTweets();