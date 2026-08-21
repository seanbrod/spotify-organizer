## data.py
-get spotify playlists and tracks (DONE)
-get tracks audio features (DONE)
    - https://medium.com/@soundnet717/spotify-audio-analysis-has-been-deprecated-what-now-4808aadccfcb (Not Enough Bandwidth)
    - https://reccobeats.com/docs/apis/get-track-audio-features (https://www.reddit.com/r/spotifyapi/comments/1hcafvg/audio_features_alternative/) (CHOSEN APPROACH)
    - https://www.kaggle.com/datasets/rodolfofigueroa/spotify-12m-songs 
    - https://medium.com/@musicae.io/spotify-audio-analysis-was-deprecated-heres-the-best-spotify-api-alternative-for-developers-585750724f48 
-persist store tracks metadata + audio features - SQLite3
-reorganize playlists in spotify based on analysis results

## process.py
-load data into pandas
-normalize features
-choose organization/clustiering analysis strategy
-reorganize playlists + refine
