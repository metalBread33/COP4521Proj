import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("hackernews_data.db")
cursor = conn.cursor()

# Define the SQL command to create the table
create_table_sql = """
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
cursor.execute(create_table_sql)

# Commit the changes and close the connection
conn.commit()
conn.close()

