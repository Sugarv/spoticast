import tkinter as tk
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import requests
import configparser
import webbrowser

# Function to update the song info on the Shoutcast server
def update_song_info():
    global is_sending
    if not is_sending:
        is_sending = True
        begin_stop_button.config(text="Stop Sending")
        update_song()
    else:
        is_sending = False
        begin_stop_button.config(text="Begin Sending")

# Function to update the currently playing song info
def update_song():
    current_track = sp.current_playback()
    if current_track is not None:
        track_name = current_track['item']['name']
        artist_name = current_track['item']['artists'][0]['name']
        song_info = f'{artist_name} - {track_name}'
        song_label.config(text=song_info)

        global last_song_info
        if is_sending and song_info != last_song_info:
            # Only update if the song has changed
            last_song_info = song_info
            # Construct the URL for updating the song info on the Shoutcast server
            shoutcast_url = f'http://{shoutcast_server}:{shoutcast_port}/admin.cgi?pass={admin_pass}&mode=updinfo&song={song_info}'

            # Send the HTTP GET request to update the song info
            response = requests.get(shoutcast_url)

            if response.status_code == 200:
                print(f'Successfully updated song info on Shoutcast server: {song_info}')
                error_label.config(text="")
            else:
                print(f'Failed to update song info on Shoutcast server. HTTP Status Code: {response.status_code}')
                error_label.config(text="Shoutcast Server Error")

    if is_sending:
        root.after(10000, update_song)  # Update song info every 10 seconds while sending is active
        root.after(10000, check_shoutcast)  # Check Shoutcast server status every 10 seconds

# Function to check the Shoutcast server status
def check_shoutcast():
    try:
        response = requests.head(f'http://{shoutcast_server}:{shoutcast_port}/admin.cgi')
        if response.status_code != 200:
            error_label.config(text="Shoutcast Server OK")
            root.after(10000, check_shoutcast)  # Retry after 10 seconds
        else:
            error_label.config(text="")
    except requests.ConnectionError:
        error_label.config(text="Shoutcast Server Error")
        root.after(10000, check_shoutcast)  # Retry after 10 seconds

# Function to open the GitHub repository link
def open_github_link():
    webbrowser.open("https://github.com/Sugarv/spoticast")

# Function to exit the application
def exit_app():
    root.destroy()

# Read Spotify API credentials and Shoutcast server details from config.txt
config = configparser.ConfigParser()
config.read('config.txt')

spotify_config = config['spotify']
client_id = spotify_config['client_id']
client_secret = spotify_config['client_secret']
redirect_uri = spotify_config['redirect_uri']

shoutcast_config = config['shoutcast']
shoutcast_server = shoutcast_config['server']
shoutcast_port = shoutcast_config['port']
admin_pass = shoutcast_config['admin_pass']

# Initialize Spotipy with OAuth2 authentication
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope="user-read-playback-state user-read-currently-playing"))
except spotipy.oauth2.SpotifyOauthError as e:
    error_label.config(text="Spotify Connection Error")
    sp = None

is_sending = False  # Flag to indicate if sending is active

# Create the tkinter GUI
root = tk.Tk()
root.title("Spotify to Shoutcast")

# Set the window dimensions
window_width = 250
window_height = 200
root.geometry(f"{window_width}x{window_height}")

song_label = tk.Label(root, text="", font=("Helvetica", 12))
song_label.pack(pady=20)

begin_stop_button = tk.Button(root, text="Begin Sending", command=update_song_info)
begin_stop_button.pack(pady=10)

error_label = tk.Label(root, text="", fg="blue")
error_label.pack()

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
