import spotipy
from spotipy.oauth2 import SpotifyOAuth
from stt import recognize_from_microphone
import sys
from spacy_parsing import parse_voice_command

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="here paste your spotify developer client_id",
                                               client_secret="here paste your spotify developer client_search",
                                               redirect_uri="http://127.0.0.1:8000/callback", #change if needed
                                               scope="user-read-playback-state,user-modify-playback-state"))


# doc = nlp_en(recognize_from_microphone())
# print(f"Testowy tekst: '{doc.text}'")
# for ent in doc.ents:
#     print(ent.text, ent.start_char, ent.end_char, ent.label_)

def search_for_track(search_data):
    entites= search_data.get("entities")
    song_title = entites.get("song_title")
    artist_name = entites.get("artist_name")
    querry_str_parts = []
    if song_title:
        querry_str_parts.append(f'track:"{song_title}"') 
    if artist_name:  
        querry_str_parts.append(f'artist:"{artist_name}"')
    
    search_query_final = " ".join(querry_str_parts)
    print(search_query_final)

    try:
        results = sp.search(q=search_query_final, limit=1, type='track')
        track_info = results['tracks']['items'][0]
    except IndexError:
        print("Couldn't match the track to the artist name, searching only with song title...")
        results = sp.search(song_title, limit=1, type='track')
        track_info = results['tracks']['items'][0]
        return track_info 
    except Exception as ex:
        print(ex)   
    return track_info


def speech_search_spotify():
    try:
        search_data = parse_voice_command(*recognize_from_microphone())
    except Exception as ex:
        print(f"Something went wrong... {ex}")
        
    if search_data["intent"] == "PlaySong":

        track_to_play = []
        track_to_play.append(search_for_track(search_data)['uri'])

        sp.start_playback(uris=track_to_play)

    elif search_data["intent"] == "AddToQueue":
        sp.add_to_queue(search_for_track(search_data)['uri'])
    elif search_data["intent"] == "NextSong":
        sp.next_track()
    elif search_data["intent"] == "PreviousSong":
        sp.previous_track()
    else:
        print("what is your intent")



# elif search_data["intent"] == "SearchArtist":
#         results = sp.search(q=str_parts[1], limit=1, type='artist')
#         artist_info = results['artists']['items'][0]
        
#         print(f"\nZnaleziono artystę:")
#         print(f"  Nazwa: {artist_info['name']}")
#         print(f"  Spotify URI: {artist_info['uri']}") # POPRAWKA TUTAJ (lub 'id' jeśli potrzebujesz tylko ID)
#         print(f"  ID: {artist_info['id']}")
#         if artist_info['genres']:
#             print(f"Gatunki: {', '.join(artist_info['genres'])}")
#             print(f"Popularność: {artist_info['popularity']}")
#         if artist_info['images']: # Sprawdź, czy są dostępne obrazki
#             print(f" Obrazek (URL): {artist_info['images'][0]['url']}") 

#         artist_uri_list = [artist_info['uri']]




