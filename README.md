# Spoticast

## Send Spotify's now playing track to Shoutcast server

A simple Python script that sends Spotify's now playing track to a Shoutcast server.
It uses [spotipy](https://github.com/spotipy-dev/spotipy) to retrieve song info from Spotify.

### Configuration
1. First, create a web app at Spotify, [here](https://developer.spotify.com/dashboard). *(Use http://localhost as a redirect uri)*.
2. Create a config.txt file on the script folder, by copying the config-sample.txt and modifying the values below:

- client_id = YOUR_APP_CLIENT_ID (see [here](https://developer.spotify.com/dashboard))
- client_secret = YOUR_SECRET_KEY
- redirect_uri = REDIRECT_URL (with http/https)
- server = YOUR_SERVER_NAME (without http/https)
- port = YOUR_SERVER_PORT
- admin_pass = YOUR_SHOUTCAST_ADMIN_PASS



