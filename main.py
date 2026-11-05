from spotipy.oauth2 import SpotifyOAuth
import spotipy
import requests
import configparser
import requests.exceptions
import urllib3.exceptions
import datetime
import time


def log(message):
    """Print a timestamped log message."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f'{timestamp}: {message}')


def send_update(url, service_name, song_info, params=None, auth=None):
    """Send an HTTP GET request to update song info on a streaming service."""
    try:
        response = requests.get(url, params=params, auth=auth, timeout=10)
        if response.status_code == 200:
            log(f'Successfully updated song info on {service_name}: {song_info}')
        else:
            log(f'Failed to update song info on {service_name}. HTTP Status Code: {response.status_code}')
    except requests.exceptions.RequestException as e:
        log(f'Failed to send data to {service_name}: {e}')
    except urllib3.exceptions.ProtocolError as e:
        log(f'ProtocolError: {e}')


# Function to update the currently playing song info
def update_song():
    # call spotipy's current_playback & catch exceptions
    try:
        current_track = sp.current_playback()
    except spotipy.SpotifyException as err:
        log(f'Spotipy Error: {err}')
        return
    except urllib3.exceptions.ProtocolError as err:
        log(f'ProtocolError: {err}')
        return
    except Exception as err:
        log(f'An unexpected error occurred: {err}')
        return

    if current_track is None or current_track.get('item') is None:
        return

    timestamp_seconds = current_track['timestamp'] / 1000.0
    converted_timestamp = datetime.datetime.fromtimestamp(
        timestamp_seconds, tz=datetime.timezone.utc
    ).strftime('%Y-%m-%d %H:%M:%S')
    log(f'Called Spotify API. Reply timestamp: {converted_timestamp}')

    track_name = current_track['item']['name']
    artist_name = current_track['item']['artists'][0]['name']
    song_info = f'{artist_name} - {track_name}'

    global last_song_info
    if song_info != last_song_info:
        # Only update if the song has changed
        last_song_info = song_info
        print(f'New song playing: {song_info}')

        # Update Shoutcast server if configured
        if shoutcast_server:
            send_update(
                url=f'http://{shoutcast_server}:{shoutcast_port}/admin.cgi',
                service_name='Shoutcast server',
                song_info=song_info,
                params={'pass': admin_pass, 'mode': 'updinfo', 'song': song_info}
            )

        # Update Icecast server if configured
        if icecast_server:
            send_update(
                url=f'http://{icecast_server}:{icecast_port}/admin/metadata',
                service_name='Icecast server',
                song_info=song_info,
                params={'mount': icecast_mount, 'mode': 'updinfo', 'song': song_info},
                auth=('source', icecast_pass)
            )

        # Update TuneIn Air API if configured
        if partner_id:
            send_update(
                url='http://air.radiotime.com/Playing.ashx',
                service_name='TuneIn Air API',
                song_info=song_info,
                params={
                    'partnerId': partner_id,
                    'partnerKey': partner_key,
                    'id': station_id,
                    'title': track_name,
                    'artist': artist_name
                }
            )


# Initialize app
# Read Spotify API credentials, Shoutcast server & AIR API details from config.txt
config = configparser.ConfigParser()
try:
    config.read('config.txt')

    spotify_config = config['spotify']
    client_id = spotify_config.get('client_id')
    client_secret = spotify_config.get('client_secret')
    redirect_uri = spotify_config.get('redirect_uri')

    # Read Shoutcast server details from config.txt (if section exists)
    shoutcast_config = config['shoutcast'] if config.has_section('shoutcast') else {}
    shoutcast_server = shoutcast_config.get('server')
    shoutcast_port = shoutcast_config.get('port')
    admin_pass = shoutcast_config.get('admin_pass')

    # Read Icecast server details from config.txt (if section exists)
    icecast_config = config['icecast'] if config.has_section('icecast') else {}
    icecast_server = icecast_config.get('server')
    icecast_port = icecast_config.get('port')
    icecast_mount = icecast_config.get('mount_point')
    icecast_pass = icecast_config.get('admin_pass')

    # Read AIR API details from config.txt (if section exists)
    air_config = config['air_api'] if config.has_section('air_api') else {}
    partner_id = air_config.get('partner_id')
    partner_key = air_config.get('partner_key')
    station_id = air_config.get('station_id')

    # Read polling interval from config (default: 10 seconds)
    spotify_interval = float(spotify_config.get('interval', '10'))

except (configparser.NoSectionError, KeyError, ValueError) as e:
    print(f'Error reading configuration data: {str(e)}')
    log('Configuration error...')
    exit(1)

# Initialize Spotipy with OAuth2 authentication
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope="user-read-playback-state user-read-currently-playing"))
except spotipy.oauth2.SpotifyOauthError as e:
    log(f'Spotipy Error: {e}')
    exit(1)

# Initialize last_song_info
last_song_info = ""

# Main loop
try:
    while True:
        update_song()
        time.sleep(spotify_interval)
except KeyboardInterrupt:
    print('\nShutting down...')
