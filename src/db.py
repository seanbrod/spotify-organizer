import sqlite3

#this func initalizes the database
def init_db():
    conn = sqlite3.connect('data/songs_artists.db')
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

def ingest_data(data):
    return None


def main():
    init_db()

if __name__ == '__main__':
    main()