#this file if for harvesting data and interacting with the Spotify Web API

import requests
import os
import sys
import urllib
import base64
from dotenv import load_dotenv

#----------------------------------------------API ACCESS FUNCTIONS----------------------------------------------
load_dotenv()
CLIENT_ID=os.getenv('CLIENT_ID')
CLIENT_SECRET=os.getenv('CLIENT_SECRET')
REDIRECT_URI=os.getenv('REDIRECT_URI')
REFRESH_TOKEN=os.getenv('REFRESH_TOKEN')
SOUNDNET_TOKEN=os.getenv('SOUNDNET_TOKEN')
LASTFM_TOKEN=os.getenv('LASTFM_TOKEN')

#this func gets a public access token (limit 1hr)
def get_public_token() -> str:
    access_url="https://accounts.spotify.com/api/token"
    access_obj = {'grant_type':'client_credentials','client_id':CLIENT_ID,'client_secret':CLIENT_SECRET}

    try:
        r = requests.post(access_url, data= access_obj)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response Body: {r.text}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Network error occurred: {e}")
        sys.exit(1)

    return r.json()['access_token']


#this func gets a private OAuth access token. uses refresh token
def get_refresh_token() -> str:
    access_url='https://accounts.spotify.com/api/token'

    auth_bytes = f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

    headers = {
        'Authorization':f'Basic {auth_base64}',
        'Content-Type':'application/x-www-form-urlencoded'
    }
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN,
    }

    try:
        r = requests.post(access_url, data=payload, headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response Body: {r.text}") # Shows Spotify's detailed error message
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Network error occurred: {e}")
        sys.exit(1)

    return r.json()['access_token']

#----------------------------------------------HELPER FUNCTIONS----------------------------------------------
#this func parses the response for get_playlist_ids and returns the dict[name,id]
def parse_playlist_ids(response, pls) -> dict[str, str]:
    data = response.json()
    pl_set = set(pls)
    names_ids = {}
    for item in data['items']:
        name = item['name']
        if name in pl_set:
            names_ids[name] = item['id']
    return names_ids

#this func will take in a response package full of 50 or under tracks and return a dict[id, name] of tracks
def parse_track_ids(data) -> dict[str, str]:
    ids_names = {}
    for item in data['items']:
        ids_names[item['item']['id']] = item['item']['name']
    return ids_names

#this func finds the total items in a playlist and returns as an int for use in get_playlist_tracks
def get_pl_item_total(url: str, headers) -> int:
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response Body: {r.text}") # Shows Spotify's detailed error message
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Network error occurred: {e}")
        sys.exit(1)
        
    data = r.json()
    return data['total']

#this func queries LastFM API to get top 3 genre tags for an artist given the name
def get_artist_genres(name:str):
    url='https://ws.audioscrobbler.com/2.0/'
    params = {
        'method': 'artist.gettoptags',
        'artist': name,
        'api_key': LASTFM_TOKEN,
        'format': 'json'
    }

    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response Body: {r.text}") # Shows detailed error message
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Network error occurred: {e}")
        sys.exit(1)
    
    tags = r.json().get('toptags', {}).get('tag', [])
    return [t['name'].lower() for t in tags[:3]]

#this func will take in a spotify track object and parse it for desired metadata
#album, duration(ms), is_explicit(boolean), is_playable(in mkt), track_name, track_id, artist_name, artist_id, artist_genre
def parse_track_metadata(data):
    primary_artist = data['album']['artists'][0]
    md = {
        'name': data['name'],
        'id': data['id'],
        'album': data['album']['name'],
        'duration': data['duration_ms'],
        'is_explicit': data['explicit'],
        'is_playable': data['is_playable'],
        'artist_name': primary_artist['name'],
        'artist_id': primary_artist['id'],
        'artist_genres': get_artist_genres(primary_artist['name'])
        }
    return md

#this track will clean and normalize track audio features (really just removes unwanted elements)
def normalize_track_af(data):
    data = data['content'][0]
    data.pop('href')
    data.pop('id')
    data.pop('isrc')
    return data


#----------------------------------------------DATA HARVESTING FUNCTIONS----------------------------------------------
#this func will take in a list of playlist names and return a dict[name, id]
def get_playlist_ids(playlists: list[str]) -> dict[str,str]:
    offset = 0
    limit = 50
    access_url=f'https://api.spotify.com/v1/me/playlists?limit={limit}&offset={offset}'
    access_token=get_refresh_token()

    headers = {
        'Authorization':f'Bearer {access_token}'
    }

    try:
        r = requests.get(access_url, headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response Body: {r.text}") # Shows Spotify's detailed error message
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Network error occurred: {e}")
        sys.exit(1)

    return parse_playlist_ids(r, playlists)

#this func will pull and return all the track ids dict[id, name] of a specific playlist given its playlist id
def get_playlist_tracks(playlist_id: str) -> dict[str,str]:
    mkt = 'US'
    limit = 50
    offset = 0
    fields = 'total,items(item(id,name))'
    access_token=get_refresh_token()
    ids_names = {}
    access_url=f'https://api.spotify.com/v1/playlists/{playlist_id}/items?market={mkt}&fields={fields}&limit={limit}&offset={offset}'

    headers = {
        'Authorization':f'Bearer {access_token}'
    }

    total = get_pl_item_total(access_url, headers)

    while True:
        access_url=f'https://api.spotify.com/v1/playlists/{playlist_id}/items?market={mkt}&fields={fields}&limit={limit}&offset={offset}'
        try:
            r = requests.get(access_url, headers=headers)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            print(f"Response Body: {r.text}") # Shows Spotify's detailed error message
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            sys.exit(1)
        
        data = r.json()
        ids_names |= parse_track_ids(data)
        offset += limit
        total -= limit

        if total < limit:
            break

    return ids_names

#this func will pull and return the track metadata from spotify
def get_track_metadata(id: str):
    mkt='US'
    access_url=f'https://api.spotify.com/v1/tracks/{id}?market={mkt}'
    access_token=get_refresh_token()

    headers = {
        'Authorization':f'Bearer {access_token}'
    }

    try:
        r = requests.get(access_url, headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response Body: {r.text}") # Shows Spotify's detailed error message
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Network error occurred: {e}")
        sys.exit(1)

    return parse_track_metadata(r.json())

#this func will get track audio features from SoundNet RapidAPI
def get_track_audio_features(id: str):
    access_url=f'https://api.reccobeats.com/v1/audio-features?ids={id}'

    headers = {
        'Accept': 'application/json'
    }
    payload = {}
    try:
        r = requests.get(access_url, headers=headers, data=payload)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response Body: {r.text}") # Shows Spotify's detailed error message
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Network error occurred: {e}")
        sys.exit(1)

    return normalize_track_af(r.json())

#this func will take in a track ID and return its audio features + metadata
def get_track_data(id: str):
    t_md = {}
    t_md |= get_track_metadata(id)
    t_id = t_md['id']
    track_data = {
        t_id: t_md
    }
    track_data[t_id] |= get_track_audio_features(id)
    return track_data

#this func will  take in a playlist ID and pull the track data for each track in the playlist
def get_playlist_data(playlist_id: str):
    pl_data = {}
    tracks = get_playlist_tracks(playlist_id)
    for id in tracks.keys():
        pl_data |= get_track_data(id)
    return pl_data

#overally data.py handler:
    #ask and intake playlist names (maybe normalize playlist names?)-spotify api already does this
    #get playlist ids
    #for each playlist id get playlist data
    #save playlist datas to persistent stoarge for analysis
def handler(args):
    pls = get_playlist_ids(args)
    big_data = {}
    for id in pls.values():
        big_data |= get_playlist_data(id)
    return big_data
    
#----------------------------------------------DEPRECIATED FUNCTIONS----------------------------------------------
#this func gets auth code from redirect url
def get_authcode_redirect():
    SCOPE = "playlist-read-private playlist-read-collaborative"
    # Construct the authorization URL
    auth_params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
    }

    auth_url = f'https://accounts.spotify.com/authorize?{urllib.parse.urlencode(auth_params)}'

    print("1. Open this link in your browser:\n")
    print(auth_url)

#this func gets a private OAuth access token
def get_private_token() -> str:
    auth_code = 'code from redirect url'
    access_url='https://accounts.spotify.com/api/token'

    payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    headers = {
        'Content-Type':'application/x-www-form-urlencoded'
    }

    try:
        r = requests.post(access_url, data=payload, headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response Body: {r.text}") # Shows Spotify's detailed error message
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Network error occurred: {e}")
        sys.exit(1)

    data = r.json()
    print(data['refresh_token'])
    return data['access_token']


def main():
    import json
    #pls = ['Workout', 'Beach']
    #data = handler(pls)
    #print(json.dumps(data, indent=4))

    #playlists = get_playlist_ids(pls)
    #for name, id in playlists.items():
    #    print(f'name: {name}, id: {id}\n')
    
    #tracks = get_playlist_tracks(playlists['For the people'])
    #for id, name in tracks.items():
    #    print(f'name: {name}, id: {id}\n')
    

   #print(get_artist_genres('Glass Animals'))
    
    #d = get_track_metadata('2klj0StczYde6WUHBJo5F6')
    #print(d)
    #print(json.dumps(d, indent=4, sort_keys=True))

    #d = get_track_audio_features('2klj0StczYde6WUHBJo5F6')
    #print(json.dumps(d, indent=4, sort_keys=True))

    d = get_track_data('2klj0StczYde6WUHBJo5F6')
    print(json.dumps(d, indent=4))

if __name__=='__main__':
    main()