import os
import sqlite3
import feedparser
import requests
import json
from datetime import datetime

DB_FILE = "wikipedia.sqlite"
FEED_URL = 'https://en.wikipedia.org/w/index.php?title=Special:NewPages&feed=rss'
COORD_URL_BASE = 'https://en.wikipedia.org/w/api.php?action=query&prop=coordinates&format=json&titles='

def init_db():
    if not os.path.exists(DB_FILE):
        print("Initialising database...")
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            
            cursor.execute(""" 
                CREATE TABLE "pages" (
                "id"    TEXT NOT NULL UNIQUE,
                "title" TEXT NOT NULL,
                "longitude" REAL,
                "latitude"  REAL,
                "posted"    INTEGER NOT NULL DEFAULT 0,
                "loaded" timestamp,
                PRIMARY KEY("id"))
            """)

            conn.commit()

def is_in_db(cursor, page_id):
    res = cursor.execute("SELECT id FROM pages WHERE id = ?", (page_id, ))
    return not(res.fetchone() is None)

def add_to_db(cursor, id):
    print(f"Adding {id}")
    url = f"{COORD_URL_BASE}{id}"
    headers = {'User-Agent': 'Wiki-Aerialbot/0.1 (https://github.com/squaregoldfish/wiki_aerialbot; squaregoldfish@mastodon.social)'}
    response = requests.get(url, headers=headers)
    page_data = json.loads(response.content)
    page = next(iter(page_data["query"]["pages"].values()))

    title = page["title"]

    longitude = None
    latitude = None

    if "coordinates" in page:
        coords = page["coordinates"][0]
        if coords["globe"] == "earth":
            longitude = float(coords["lon"])
            latitude = float(coords["lat"])

    cursor.execute("INSERT INTO pages (id, title, longitude, latitude, posted, loaded) VALUES (?, ?, ?, ?, ?, ?)",
        (id, title, longitude, latitude, False, datetime.now()))


def main():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Download and parse new pages
        feed = feedparser.parse(FEED_URL)

        # Extract page IDs
        ids = [entry.id.split("/wiki/",1)[1] for entry in feed.entries]

        for id in ids:
            if not is_in_db(cursor, id):
                add_to_db(cursor, id)

        conn.commit()




if __name__ == "__main__":
    init_db()
    main()

