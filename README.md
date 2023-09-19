# Spoticast

## Send Spotify's now playing track to Shoutcast server and/or TuneIn Radio AIR API

A simple Python script that sends Spotify's now playing track to a Shoutcast server and/or TuneIn Radio AIR API.
It uses [spotipy](https://github.com/spotipy-dev/spotipy) to retrieve song info from Spotify.

### Configuration
1. First, create a web app at Spotify, [here](https://developer.spotify.com/dashboard). *(Use http://localhost as a redirect uri)*.
2. Create a config.txt file on the script folder, by copying the config-sample.txt and modifying the values below:

- client_id = SPOTIFY_APP_CLIENT_ID (see [here](https://developer.spotify.com/dashboard))
- client_secret = SPOTIFY_APP_SECRET_KEY
- redirect_uri = SPOTIFY_APP_REDIRECT_URL (with http/https)
- server = SHOUTCAST_SERVER_NAME (without http/https)
- port = SHOUTCAST_SERVER_PORT
- admin_pass = SHOUTCAST_SERVER_ADMIN_PASS
- partner_id = TUNEIN_PARTNER_ID
- partner_key = TUNEIN_PARTNER_KEY
- station_id = TUNEIN_STATION_ID
