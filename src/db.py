import sqlite3

def create_tables():
    conn = sqlite3.connect('src/sna.db')
    cur = conn.cursor() #object used to execute sql queries on db

    #Song Table
    #track_id, track_name, album, duration(ms), is_explicit(boolean), is_playable(in mkt)
    #acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo, valence
    cur.execute('DROP TABLE IF EXISTS songs')
    song_creation_query = """
        CREATE TABLE songs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            album TEXT
            durationMS INTEGER,
            is_explicit INTEGER,
            is_playable INTEGER,
            acousticness REAL,
            danceability REAL,
            energy REAL,
            instrumentalness REAL,
            key INTEGER,
            liveness REAL,
            loudness REAL,
            mode INTEGER,
            speechiness REAL,
            tempo REAL,
            valence REAL
        );
    """
    cur.execute(song_creation_query)

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
    conn.close()



def main():
    create_tables()

if __name__ == '__main__':
    main()