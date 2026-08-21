import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()
DB_PATH=os.getenv('DB_PATH')

#this func initalizes the database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor() #object used to execute sql queries on db
    cur.execute('PRAGMA foreign_keys = ON;')

    #Artist Table
    #artist_id, artist_name, artist_genre
    cur.execute('DROP TABLE IF EXISTS artists')
    song_creation_query = """
        CREATE TABLE artists (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            genre TEXT
        );
    """
    cur.execute(song_creation_query)

    #Song Table
    #track_id, track_name, album, playlist_name(personal pl name), playlist_id(personal pl id), duration(ms), is_explicit(boolean), is_playable(in mkt), primary_artist_id
    #acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo, valence
    cur.execute('DROP TABLE IF EXISTS songs')
    song_creation_query = """
        CREATE TABLE songs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            album TEXT
            playlist_name TEXT,
            playlist_id TEXT,
            duration_ms INTEGER,
            is_explicit INTEGER,
            is_playable INTEGER,
            primary_artist_id TEXT,
            acousticness REAL,
            danceability REAL,
            energy REAL,
            instrumentalness REAL,
            "key" INTEGER,
            liveness REAL,
            loudness REAL,
            mode INTEGER,
            speechiness REAL,
            tempo REAL,
            valence REAL,
            FOREIGN KEY (primary_artist_id) REFERENCES artists(id) ON DELETE SET NULL
        );
    """
    cur.execute(song_creation_query)
    conn.commit()
    conn.close()

#this func will create the organized query into the songs table
def song_query(sd):
    id = list(sd.keys())[0]
    query = f"""
        INSERT INTO songs VALUES (
        {id},
        {sd[id]['name']},
        {sd[id]['album']},
        {sd[id]['playlist_name']},
        {sd[id]['playlist_id']},
        {sd[id]['duration']},
        {sd[id]['is_explicit']},
        {sd[id]['is_playable']},
        {sd[id]['artist_id']},
        {sd[id]['acousticness']},
        {sd[id]['danceability']},
        {sd[id]['energy']},
        {sd[id]['instrumentalness']},
        {sd[id]['key']},
        {sd[id]['liveness']},
        {sd[id]['loudness']},
        {sd[id]['mode']},
        {sd[id]['speechiness']},
        {sd[id]['tempo']},
        {sd[id]['valence']},
        );
    """
    return query
     
#this func will create the organized query into the artists table
def artist_query(ad):
    id = list(ad.keys())[0]
    query = f"""
        INSERT INTO artists VALUES (
        {ad[id]['artist_id']},
        {ad[id]['artist_name']},
        {ad[id]['artist_genres']},
        );
    """
    return query

#this func will take in a track and insert it into the db
def insert_track(cur, conn, data):
    song_insert_query = song_query(data)
    try:
        cur.execute(song_insert_query)
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()

    artist_insert_query = artist_query(data)
    try:
        cur.execute(artist_insert_query)
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()

#this func will take in all songs in a playlist and insert them into sqlite db
def ingest_data(data):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor() #object used to execute sql queries on db

    for track in data:
        insert_track(cur, conn, track)

    conn.commit()
    conn.close()

def main():
    print('hi')
    #init_db()

if __name__ == '__main__':
    main()