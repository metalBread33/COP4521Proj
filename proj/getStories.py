#!/usr/bin/python3
import sqlite3
import requests

# Connect to the SQLite database
conn = sqlite3.connect("hackernews_data.db")
cursor = conn.cursor()

# Define the SQL command to insert data into the table, using INSERT OR IGNORE
insert_data_sql = """
INSERT OR IGNORE INTO hackernews_data (id, by, descendants, kids, score, text, time, title, type, url)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

# Define the HackerNews API URL to fetch the latest item IDs
latest_items_url = "https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"

# Make a request to the HackerNews API to get the IDs of the latest items
response = requests.get(latest_items_url)
if response.status_code == 200:
    latest_item_ids = response.json()[:30]  # Fetch data for the latest 30 items

    # Iterate through the latest item IDs and fetch data for each item
    for item_id in latest_item_ids:
        item_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json?print=pretty"
        item_response = requests.get(item_url)
        if item_response.status_code == 200:
            item_data = item_response.json()
            if item_data.get("type") == "story":  # Check if it's a story
                # Extract relevant data from the API response
                data_tuple = (
                    item_data.get("id"),
                    item_data.get("by", ""),
                    item_data.get("descendants", 0),
                    str(item_data.get("kids", [])),
                    item_data.get("score", 0),
                    item_data.get("text", ""),
                    item_data.get("time", 0),
                    item_data.get("title", ""),
                    item_data.get("type", ""),
                    str(item_data.get("url", f"{item_url}"))
                )
                # Insert the data into the SQLite table using INSERT OR IGNORE
                cursor.execute(insert_data_sql, data_tuple)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
else:
    print("Failed to fetch data from the HackerNews API.")
