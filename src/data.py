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

    headers = {
        'Authorization':f'Bearer {access_token}'
    }

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
        
        if data['total'] < limit:
            break

    return ids_names

#TODO: this will pull track metadata and audio features for analysis
def get_track_data():
    return None

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


    pls = ['Type shi', 'Workout']
    playlists = get_playlist_ids(pls)
    for name, id in playlists.items():
        print(f'name: {name}, id: {id}\n')
    
    tracks = get_playlist_tracks(playlists['Workout'])
    for id, name in tracks.items():
        print(f'name: {name}, id: {id}\n')

if __name__=='__main__':
    main()