# Spotify Playlist Organizer

## Goal
The goal of this project is simple, I want to be able to take my playlists which hhave gotten long and mixed up and re-organize them. I have playlists hundreds of songs long and want to have it so they are re-combined based on tempo, vibe, and genre. 

## Resources
- ReccoBeats API: https://reccobeats.com/docs/apis/get-track-audio-features
- LastFM API: https://www.last.fm/user/sbull67 

## Song Data
- Acousticness: (0.0, 1.0)
- Danceability: (0.0, 1.0)
- Energy: (0.0, 1.0)
- Instrumentalness: (0.0, 1.0)
- Key: 
{
    -1 -> None,
    0 -> C,
    1 -> C#/Df,
    2 -> D,
    3 -> D#/Ef,
    4 -> E,
    5 -> F,
    6 -> F#/Gf,
    7 -> G,
    8 -> G#/Af,
    9 -> A,
    10 -> A#/Bf,
    11 -> B
}
- Liveness: (0.0, 1.0)
- Loudness: (-60db, 0db)
- Mode:
{
    0 -> Minor,
    1 -> Major
}
- Speechiness: (0.0, 1.0)
- Tempo: (0BPM, 250BPM)
- Valence: (0.0, 1.0)


## TODO
- Data Harvesting Layer
- Playlist Analysis Layer
- Generaization + Webhosting (Deferred for Now)