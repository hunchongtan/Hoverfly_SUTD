import requests
import csv
import time

# Reddit API needs this
headers = {'User-agent': 'Mozilla/5.0'}
after = None

# Subreddit Name
subreddit = "virtualreality"

# Search query
search_query = "pico 4"

# Define a list to store comments
comments_list = []

# Function to extract comments recursively
def extract_comments(subreddit, post_id):
    comments_url = f"https://www.reddit.com/{subreddit}/comments/{post_id}/.json"
    r = requests.get(comments_url, headers=headers)
    if r.status_code == 200:
        comments_data = r.json()

        # Check if comments are available
        if '1' in comments_data and 'data' in comments_data['1']:
            for comment in comments_data['1']['data']['children']:  # Comments start from index 1
                comment_data = comment['data']
                comments_list.append([comment_data['id'], comment_data['body']])  # Store comment id and body
                if comment_data.get('replies'):  # If there are replies, recursively extract them
                    extract_comments(subreddit, comment_data['id'])
        else:
            print(f"No comments found for post {post_id}")

    else:
        print(f"Failed to retrieve comments for post {post_id}. Status code: {r.status_code}")

# No. of rows
num_rows = 0

# Search for posts related to Pico 4
search_url = f"https://www.reddit.com/r/{subreddit}/search.json?q={search_query}&type=link"
r = requests.get(search_url, headers=headers)
if r.status_code == 200:
    search_results = r.json()
    for post in search_results['data']['children']:
        post_data = post['data']
        post_id = post_data['id']
        extract_comments(subreddit, post_id)

        num_rows += 1
        print(str(num_rows) + " posts processed.")
        time.sleep(4)  # sleep for 2 seconds to avoid hitting Reddit's rate limit

else:
    print(f"Failed to retrieve search results. Status code: {r.status_code}")

# Save comments to a CSV file
csv_file_path = 'comments.csv'
with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Comment ID', 'Comment Body'])  # Write header
    writer.writerows(comments_list)  # Write comments

print("Comments saved to comments.csv")
