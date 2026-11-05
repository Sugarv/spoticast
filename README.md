# Spoticast

## Send Spotify's now playing track to Shoutcast / Icecast server(s) and/or TuneIn Radio AIR API

A simple Python script that sends Spotify's now playing track to one or more of the following:
- a Shoutcast server 
- an Icecast server
- TuneIn Radio AIR API.

Uses [spotipy](https://github.com/spotipy-dev/spotipy) to retrieve song info from Spotify.

### Configuration

1. Create a web app at the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. In your app's settings, add `http://localhost` as a **Redirect URI**.
3. Copy `config-sample.txt` to `config.txt` and fill in your values:

#### Spotify section `[spotify]`
| Key | Value |
|---|---|
| `client_id` | Your app's Client ID (from the [Dashboard](https://developer.spotify.com/dashboard)) |
| `client_secret` | Your app's Client Secret |
| `redirect_uri` | `http://localhost` (must match the Redirect URI in your app settings) |
| `interval` | Polling interval in seconds (default: 10) |

#### Shoutcast section `[shoutcast]` *(optional)*
| Key | Value |
|---|---|
| `server` | Shoutcast server hostname (without `http://`) |
| `port` | Shoutcast server port |
| `admin_pass` | Shoutcast admin password |

#### Icecast section `[icecast]` *(optional)*
| Key | Value |
|---|---|
| `server` | Icecast server hostname (without `http://`) |
| `port` | Icecast server port |
| `mount_point` | Mount point (e.g. `/live`) |
| `admin_pass` | Icecast admin password |

#### TuneIn section `[air_api]` *(optional)*
| Key | Value |
|---|---|
| `partner_id` | TuneIn Partner ID |
| `partner_key` | TuneIn Partner Key |
| `station_id` | TuneIn Station ID |

4. Run the script: `python main.py`

### First-time Spotify authentication

The first time you run the script, your browser will open the Spotify login page.

1. **Log in** to Spotify and click **Agree** to grant access.
2. You will be redirected to a URL like:
   ```
   http://localhost/?code=AQD...very_long_code...
   ```
3. The page will show an error — **that's expected** (nothing is running on localhost).
4. **Copy the entire URL** from your browser's address bar.
5. **Paste it** into the terminal when prompted with `Enter the URL you were redirected to:`.

After this, a `.cache` file is created and you won't need to authenticate again unless the token expires or the `.cache` file is deleted.
