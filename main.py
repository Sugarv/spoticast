import tkinter as tk
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import requests
import configparser
import webbrowser
import requests.exceptions
import urllib3.exceptions
import urllib.parse
import datetime


# Function to toggle sending to Shoutcast Server
def toggle_shoutcast():
    global send_to_shoutcast
    send_to_shoutcast = not send_to_shoutcast

# Function to toggle sending to TuneIn Air API
def toggle_air_api():
    global send_to_air_api
    send_to_air_api = not send_to_air_api
# Function to update the song info on the Shoutcast server
def update_song_info():
    global is_sending, send_to_shoutcast, send_to_air_api, error_label_air_api, error_label_shoutcast

    # Clear error labels
    error_label_shoutcast.config(text='')
    error_label_air_api.config(text='')

    if not is_sending:
        is_sending = True
        begin_stop_button.config(text="Stop Sending")

        # Disable the checkboxes when sending is enabled
        shoutcast_checkbox.config(state="disabled")
        air_api_checkbox.config(state="disabled")

        update_song()
    else:
        is_sending = False
        begin_stop_button.config(text="Begin Sending")

        # Re-enable the checkboxes when sending is not active
        shoutcast_checkbox.config(state="normal")
        air_api_checkbox.config(state="normal")

# Function to update the currently playing song info
def update_song():
    # call spotipy's current_playback & catch exceptions
    try:
        current_track = sp.current_playback()
    except spotipy.SpotifyException as err:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{timestamp}: Spotipy Error: {str(err)}')
        error_label_shoutcast.config(text="Spotify API Error")
        return
    except urllib3.exceptions.ProtocolError as err:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{timestamp}: ProtocolError: {str(err)}')
        error_label_shoutcast.config(text="Protocol Error")
        return
    except Exception as err:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{timestamp}: An unexpected error occurred: {str(err)}')
        return

    if current_track is not None:
        track_name = current_track['item']['name']
        artist_name = current_track['item']['artists'][0]['name']
        # Properly encode the parameters
        track_name = urllib.parse.quote(track_name)
        artist_name = urllib.parse.quote(artist_name)
        song_info = f'{artist_name} - {track_name}'
        song_label.config(text=song_info)

        global last_song_info
        if is_sending and song_info != last_song_info:
            # Only update if the song has changed
            last_song_info = song_info

            if send_to_shoutcast:
                # Construct the URL for updating the song info on the Shoutcast server
                shoutcast_url = f'http://{shoutcast_server}:{shoutcast_port}/admin.cgi?pass={admin_pass}&mode=updinfo&song={song_info}'

                try:
                    # Send the HTTP GET request to update the song info
                    response = requests.get(shoutcast_url)

                    if response.status_code == 200:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f'{timestamp}: Successfully updated song info on Shoutcast server: {song_info}')
                        error_label_shoutcast.config(text="")
                    else:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f'{timestamp}: Failed to update song info on Shoutcast server. HTTP Status Code: {response.status_code}')
                        error_label_shoutcast.config(text="*** Shoutcast Server Error ***")
                except requests.exceptions.RequestException as e:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f'{timestamp}: Failed to send data to Shoutcast server : {str(e)}')
                    error_label_shoutcast.config(text="*** Shoutcast Server Error ***")
                except urllib3.exceptions.ProtocolError as e:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f'{timestamp}: ProtocolError: {str(e)}')
                    error_label_shoutcast.config(text="*** Protocol Error ***")

            if send_to_air_api:
                # Construct the URL for updating the song info on the TuneIn Air API
                air_api_url = f'http://air.radiotime.com/Playing.ashx?partnerId={partner_id}&partnerKey={partner_key}&id={station_id}&title={track_name}&artist={artist_name}'

                try:
                    # Send the HTTP GET request to update the song info
                    response = requests.get(air_api_url)

                    if response.status_code == 200:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f'{timestamp}: Successfully updated song info on TuneIn Air API: {song_info}')
                        error_label_air_api.config(text="")
                    else:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f'{timestamp}: Failed to update song info on TuneIn Air API. HTTP Status Code: {response.status_code}')
                        error_label_air_api.config(text="*** Air API Error ***")
                except requests.exceptions.RequestException as e:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f'{timestamp}: Failed to send data to TuneIn Air API: {str(e)}')
                    error_label_air_api.config(text="*** Air API Error ***")
                except urllib3.exceptions.ProtocolError as e:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f'{timestamp}: ProtocolError: {str(e)}')
                    error_label_shoutcast.config(text="*** Protocol Error ***")

    if is_sending:
        root.after(spotify_interval, update_song)  # Update song info every 10 seconds while sending is active
        root.after(shoutcast_interval, check_shoutcast)  # Check Shoutcast server status every 10 seconds


# Function to check the Shoutcast server status
def check_shoutcast():
    if send_to_shoutcast:
        try:
            response = requests.head(f'http://{shoutcast_server}:{shoutcast_port}/admin.cgi')
            if response.status_code != 200:
                error_label_shoutcast.config(text="Shoutcast Server OK")
                root.after(shoutcast_interval, check_shoutcast)  # Retry after 10 seconds
            else:
                error_label_shoutcast.config(text="")
        except requests.ConnectionError:
            error_label_shoutcast.config(text="Shoutcast Server Error")
            root.after(shoutcast_interval, check_shoutcast)  # Retry after 10 seconds
    else:
        error_label_shoutcast.config(text="")  # Clear the error label if not sending to Shoutcast

# Function to open the GitHub repository link
def open_github_link():
    webbrowser.open("https://github.com/Sugarv/spoticast")

# Function to exit the application
def exit_app():
    root.destroy()

# Read Spotify API credentials and Shoutcast server details from config.txt
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
    error_label_shoutcast.config(text="Configuration Error")
    sp = None

# Initialize Spotipy with OAuth2 authentication
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope="user-read-playback-state user-read-currently-playing"))
except spotipy.oauth2.SpotifyOauthError as e:
    print(f'Spotipy Error: {str(e)}')
    error_label.config(text="Spotify Connection Error")
    sp = None

is_sending = False  # Flag to indicate if sending is active
send_to_shoutcast = False  # Flag to control sending to Shoutcast
send_to_air_api = False  # Flag to control sending to TuneIn Air API

spotify_interval = 30000
shoutcast_interval = 10000

# Create the tkinter GUI
root = tk.Tk()
root.title("SpotiCast")

# Set the window dimensions
window_width = 250
window_height = 250
root.geometry(f"{window_width}x{window_height}")

song_label = tk.Label(root, text="", font=("Helvetica", 12))
song_label.pack(pady=20)

begin_stop_button = tk.Button(root, text="Begin Sending", command=update_song_info)
begin_stop_button.pack(pady=10)

# Checkboxes to toggle sending methods
shoutcast_checkbox = tk.Checkbutton(root, text="Shoutcast Server", command=toggle_shoutcast)
shoutcast_checkbox.pack()
air_api_checkbox = tk.Checkbutton(root, text="TuneIn Air API", command=toggle_air_api)
air_api_checkbox.pack()

# Create labels for Shoutcast Server and Air API errors
error_label_shoutcast = tk.Label(root, text="", fg="red")
error_label_shoutcast.pack()

error_label_air_api = tk.Label(root, text="", fg="red")
error_label_air_api.pack()

# Create a Text widget for the footer as a hyperlink
footer_text = tk.Text(root, wrap="none", height=1, width=50, cursor="hand2", relief=tk.FLAT, borderwidth=0)
footer_text.tag_configure("hyperlink", foreground="blue", underline=True)
footer_text.insert("1.0", "(c) sugarvag, 2023 - GitHub", "hyperlink")
footer_text.pack(side="bottom")
footer_text.bind("<Button-1>", lambda event: open_github_link())

exit_button = tk.Button(root, text="Exit", command=exit_app, fg='red')
exit_button.pack()

# Initialize last_song_info
last_song_info = ""

root.after(0, update_song)  # Initial call to update_song
root.after(0, check_shoutcast)  # Initial call to check_shoutcast
root.mainloop()
