"""This creates the table that the articles are stored in."""
import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
CONNECTION = sqlite3.connect("hackernews_data.db")
CURSOR = CONNECTION.cursor()

# Define the SQL command to create the table
CREATE_QUERY = """
CREATE TABLE IF NOT EXISTS hackernews_data (
    id INTEGER PRIMARY KEY,
    by TEXT,
    descendants INTEGER,
    kids BLOB,
    score INTEGER,
    text TEXT,
    time INTEGER,
    title TEXT,
    type TEXT,
    url TEXT,
    likes INTEGER DEFAULT 0,
    dislikes INTEGER DEFAULT 0
);
"""

# Execute the SQL command to create the table
CURSOR.execute(CREATE_QUERY)

# Commit the changes and close the connection
CONNECTION.commit()
CONNECTION.close()
