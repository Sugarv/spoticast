from spotipy.oauth2 import SpotifyOAuth
import spotipy
import requests
import configparser
import requests.exceptions
import urllib3.exceptions
import urllib.parse
import datetime
import threading


# Function to update the currently playing song info
def update_song():
    # Reschedule the function to run after a delay
    threading.Timer(spotify_interval, update_song).start()

    # call spotipy's current_playback & catch exceptions
    try:
        current_track = sp.current_playback()
        r_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp_seconds = current_track['timestamp'] / 1000.0
        # Convert timestamp to a datetime object
        converted_timestamp = datetime.datetime.utcfromtimestamp(timestamp_seconds).strftime('%Y-%m-%d %H:%M:%S')
        print(f'{r_timestamp}: Called Spotify API. Reply timestamp: {converted_timestamp}')
    except spotipy.SpotifyException as err:
        r_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{r_timestamp}: Spotipy Error: {str(err)}')
        return
    except urllib3.exceptions.ProtocolError as err:
        r_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{r_timestamp}: ProtocolError: {str(err)}')
        return
    except Exception as err:
        r_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{r_timestamp}: An unexpected error occurred: {str(err)}')
        return

    if current_track is not None:
        track_name_repl = current_track['item']['name']
        artist_name_repl = current_track['item']['artists'][0]['name']
        # Properly encode the parameters
        track_name = urllib.parse.quote(track_name_repl)
        artist_name = urllib.parse.quote(artist_name_repl)
        song_info = f'{artist_name} {track_name}'

        global last_song_info
        if song_info != last_song_info:
            # Only update if the song has changed
            last_song_info = song_info
            print(f'New song playing: {artist_name_repl} - {track_name_repl}')

            # Construct the URL for updating the song info on the Shoutcast server
            shoutcast_url = f'http://{shoutcast_server}:{shoutcast_port}/admin.cgi?pass={admin_pass}&mode=updinfo&song={song_info}'

            try:
                # Send the HTTP GET request to update the song info
                response = requests.get(shoutcast_url)

                if response.status_code == 200:
                    r_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f'{r_timestamp}: Successfully updated song info on Shoutcast server: {song_info}')
                else:
                    r_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f'{r_timestamp}: Failed to update song info on Shoutcast server. HTTP Status Code: {response.status_code}')
            except requests.exceptions.RequestException as e:
                r_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f'{r_timestamp}: Failed to send data to Shoutcast server : {str(e)}')
            except urllib3.exceptions.ProtocolError as e:
                r_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f'{r_timestamp}: ProtocolError: {str(e)}')

            # Construct the URL for updating the song info on the TuneIn Air API
            air_api_url = f'http://air.radiotime.com/Playing.ashx?partnerId={partner_id}&partnerKey={partner_key}&id={station_id}&title={track_name}&artist={artist_name}'

            try:
                # Send the HTTP GET request to update the song info
                response = requests.get(air_api_url)

                if response.status_code == 200:
                    r_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f'{r_timestamp}: Successfully updated song info on TuneIn Air API: {song_info}')
                else:
                    r_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f'{r_timestamp}: Failed to update song info on TuneIn Air API. HTTP Status Code: {response.status_code}')
            except requests.exceptions.RequestException as e:
                r_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f'{r_timestamp}: Failed to send data to TuneIn Air API: {str(e)}')
            except urllib3.exceptions.ProtocolError as e:
                r_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f'{r_timestamp}: ProtocolError: {str(e)}')


# Initialize app
# Read Spotify API credentials, Shoutcast server & AIR API details from config.txt
config = configparser.ConfigParser()
try:
    config.read('config.txt')

    spotify_config = config['spotify']
    client_id = spotify_config.get('client_id')
    client_secret = spotify_config.get('client_secret')
    redirect_uri = spotify_config.get('redirect_uri')

    shoutcast_config = config['shoutcast']
    shoutcast_server = shoutcast_config.get('server')
    shoutcast_port = shoutcast_config.get('port')
    admin_pass = shoutcast_config.get('admin_pass')

    # Read AIR API details from config.txt
    air_config = config['air_api']
    partner_id = air_config.get('partner_id')
    partner_key = air_config.get('partner_key')
    station_id = air_config.get('station_id')

except (configparser.NoSectionError, KeyError) as e:
    print(f'Error reading configuration data: {str(e)}')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f'{timestamp}: Configuration error...')
    exit(1)

# Initialize Spotipy with OAuth2 authentication
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope="user-read-playback-state user-read-currently-playing"))
except spotipy.oauth2.SpotifyOauthError as e:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f'{timestamp}: Spotipy Error: {str(e)}')
    exit(1)


spotify_interval = 10.0

# Initialize last_song_info
last_song_info = ""

# Initial run
update_song()
