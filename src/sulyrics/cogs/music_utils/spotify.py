import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import dotenv
import os
import re

dotenv.load_dotenv()

class sulyrics_spotify():
    def __init__(self):
        self.id = os.getenv("spotipy_client_id")
        self.secret = os.getenv("spotipy_client_secret")
        self.client_credentials_manager = SpotifyClientCredentials(client_id=self.id, client_secret=self.secret)
        self.sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)

    async def get_query_from_spotify(self, query):
        result = self.sp.track(query)
        lavalink_query = f'ytsearch:{result["artists"][0]["name"]} {result["name"]}'

        return lavalink_query
