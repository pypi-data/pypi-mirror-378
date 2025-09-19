<h1 style="font-size: 3em; text-align: center">Spotipyio</h1>
<p style="font-size: medium; font-weight: bold; text-align: center">A FREE async Python wrapper to the Spotify API</p>

# ⚙️ Before Start
In case you haven't already registered a Spotify API app, please go first to the 
[Spotify developers page](https://developer.spotify.com/documentation/web-api/tutorials/getting-started#create-an-app) 
and create one. You must possess the following credentials before start:
* Client ID
* Client secret
* Redirect URI

Do you have your credentials? Great, let's start cooking 👨‍🍳

# 💾 Installation
### Pip
```bash 
pip install spotipyio
```

### Pipenv
```bash 
pipenv install spotipyio
```

### Poetry
```bash 
poetry add spotipyio
```

# 🚀 Getting Started
## 🐣 Sending your first request
Here is a simple function that fetches tracks information and prints it

```python
import asyncio
from spotipyio import SpotifyClient
from typing import List


async def fetch_tracks_info(tracks_ids: List[str]):
    async with SpotifyClient() as client:  # Assuming you set your credentials as env variables
        tracks = await client.tracks.info.run(tracks_ids)        
        print(tracks)


if __name__ == "__main__":
    ids = ["0ntQJM78wzOLVeCUAW7Y45", "5FVd6KXrgO9B3JPmC8OPst"]  # Sex On Fire, Do I Wanna Know?
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_tracks_info(ids))
```

## 🦶 Walkthrough
Let's walk through this example one line by another.

### Env Setup
First, we must ensure our [client credentials](#-before-start) are accessible to our code. The easiest way to do so is by simply 
configuring them as environment variables:

| Credential    | Env Variable          |
|---------------|-----------------------|
| Client ID     | SPOTIPY_CLIENT_ID     |
| Client secret | SPOTIPY_CLIENT_SECRET |
| Redirect URI  | SPOTIPY_REDIRECT_URI  |

### SpotifyClient
Once our environment is configured, we can create our `SpotifyClient`. The `SpotifyClient` object is the single object 
you need to use to execute your business logic. Once created, you will not have to use any other object to send requests. 
In the above example, we are using it to fetch tracks information. The easiest way to instantiate it 
([but not the only](#session-management)) is as an async context manager, as done here.

### Run
Our request is then sent using the `run` method. All objects within the `SpotifyClient` send requests using this method, 
ensuring a standardized way to execute each object's main functionality. Pay attention we are feeding the `run` method 
not a single track id but a list of ids. This is one of the greatest benefits the package is offering to the user. 
If you're familiar with the Spotify API you might already know it doesn't offer this kind of functionality, but only 
a single track endpoint or several_tracks endpoint limited to maximum 50 tracks ids. The `tracks.info.run` method - as 
well as other similar methods for other types of data - can receive any number of tracks ids. It automatically takes 
care of optimizing your requests by splitting it to 50 ids chunks and parallelizing them.

## 🔐 Sending your second (authorized) request
In our first request, we didn't configure which 
[OAuth flow](https://developer.spotify.com/documentation/web-api/concepts/authorization) to use. In this case, the 
[Client Credentials](https://developer.spotify.com/documentation/web-api/tutorials/client-credentials-flow) flow is 
chosen by default, which is suitable for endpoints that don't hold private information, such as tracks' and artists' 
information. But how can we send authorized requests to engage with endpoint that require such authorization, such as 
[current user's profile](https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile)? 
Let's see an example:

```python
import asyncio

from spotipyio import SpotifySession, SpotifyClient
from spotipyio.auth import ClientCredentials, SpotifyGrantType


async def get_current_user_profile(access_code: str):
    credentials = ClientCredentials(
        grant_type=SpotifyGrantType.AUTHORIZATION_CODE,
        access_code=access_code
    )
    
    async with SpotifySession(credentials=credentials) as session:
        async with SpotifyClient(session=session) as client:
            profile = await client.current_user.profile.run()
    
    print(profile)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_current_user_profile("<your-access-code>"))
```
Let's drill into the differences between this example and the previous:
1. First, our method now expects an `access_code` argument. An access code is mandatory - you will not be able to 
proceed without creating one first. Read more about authorization codes and how to get them in the 
[official documentation](https://developer.spotify.com/documentation/web-api/tutorials/code-flow), or simply fetch one 
to start with using the [access code fetcher](#access-code-fetcher) tool this package provides.
2. Secondly, We can no longer use the default `SpotifyClient` configuration, so we have to create one ourselves. 
Initially, we have to create a custom `ClientCredentials` object and provide it with the relevant grant type 
(authorization code) and with the access_code we fetched.
3. Then, we create a new `SpotifySession` using the credentials we just created. Pay attention that similar to the 
`SpotifyClient` class, a `SpotifySession` is also created using an async context manager.
4. Finally, we instantiate our `SpotifyClient` using the session. Now, we're good to use it on any endpoint, authorized 
or not.

# 🥽 Deep Dive
## SpotifyClient
<details>
<summary style="font-size: large; font-weight: bold">💿 Albums</summary>
<h3>ℹ️ Info</h3>

**Description**

Get Spotify catalog information for multiple albums identified by their Spotify IDs.

**Example**
```python
from spotipyio import SpotifyClient
import asyncio

async def fetch_albums_info():
    async with SpotifyClient() as client:
        albums_ids = ["4LH4d3cOWNNsVw41Gqt2kv", "0E4xv5gPjykrwBgBZzI8XG"]  # The Dark Side of the Moon, Back to Black
        albums_info = await client.albums.info.run(albums_ids)        

    print(albums_info)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_albums_info())
```

[**Reference**](https://developer.spotify.com/documentation/web-api/reference/get-multiple-artists)
</details>

<details>
<summary style="font-size: large; font-weight: bold">👨‍🎤 Artists</summary>
<h3>ℹ️ Info</h3>

**Description**

Get Spotify catalog information for several artists based on their Spotify IDs.

**Example**
```python
from spotipyio import SpotifyClient
import asyncio

async def fetch_artists_info(spotify_client: SpotifyClient):
    artists_ids = ["6l3HvQ5sa6mXTsMTB19rO5", "1vyhD5VmyZ7KMfW5gqLgo5"]  # J Cole, J Balvin
    artists_info = await spotify_client.artists.info.run(artists_ids)
    
    print(artists_info)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_artists_info())
```

[**Reference**](https://developer.spotify.com/documentation/web-api/reference/get-multiple-artists)

<h3>🔝 Top Tracks</h3>

**Description**

Get Spotify catalog information about an artist's top tracks.

**Example**
```python
from spotipyio import SpotifyClient
import asyncio

async def fetch_artists_top_tracks():
    async with SpotifyClient() as client:
        artists_ids = ["6ra4GIOgCZQZMOaUECftGN", "1Mxqyy3pSjf8kZZL4QVxS0"]  # Frank Zappa, Frank Sinatra
        artists_top_tracks = await client.artists.top_tracks.run(artists_ids)
    
    print(artists_top_tracks)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_artists_top_tracks())
```

[**Reference**](https://developer.spotify.com/documentation/web-api/reference/get-an-artists-top-tracks)

</details>

<details>
<summary style="font-size: large; font-weight: bold">👨‍💻 Current User</summary>
<h3>🔝️ Top Items</h3>

**Description**

Get the current user's top artists or tracks based on calculated affinity.

**Example**
```python
from spotipyio import SpotifySession, SpotifyClient
from spotipyio.auth import ClientCredentials, SpotifyGrantType
from spotipyio.models import ItemsType, TimeRange
import asyncio

async def fetch_current_user_top_artists(access_code: str):
    credentials = ClientCredentials(
        grant_type=SpotifyGrantType.AUTHORIZATION_CODE,
        access_code=access_code
    )
    
    async with SpotifySession(credentials=credentials) as session:
        async with SpotifyClient(session=session) as client:
            top_items = await client.current_user.top_items.run(
                items_type=ItemsType.ARTISTS,
                time_range=TimeRange.SHORT_TERM
            )
            
    print(top_items)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_current_user_top_artists("<your-access-code>"))
```

<h3>👤️ Profile</h3>

**Description**

Get detailed profile information about the current user.

**Example**

```python
import asyncio

from spotipyio import SpotifySession, SpotifyClient
from spotipyio.auth import ClientCredentials, SpotifyGrantType


async def fetch_current_user_profile(access_code: str):
    credentials = ClientCredentials(
        grant_type=SpotifyGrantType.AUTHORIZATION_CODE,
        access_code=access_code
    )

    async with SpotifySession(credentials=credentials) as session:
        async with SpotifyClient(session=session) as client:
            profile = await client.current_user.profile.run()

    print(profile)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_current_user_profile("<your-access-code>"))
```

[**Reference**](https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile)
</details>

<details>
<summary style="font-size: large; font-weight: bold">📻 Playlists</summary>
<h3>➕ Add Items</h3>

**Description**

Add one or more items to a user's playlist.

**Example**

```python
import asyncio

from spotipyio import SpotifySession, SpotifyClient
from spotipyio.auth import ClientCredentials, SpotifyGrantType

async def add_playlist_items(access_code: str, playlist_id: str):
    credentials = ClientCredentials(
        grant_type=SpotifyGrantType.AUTHORIZATION_CODE,
        access_code=access_code
    )
    uris = [
        "spotify:track:3Um9toULmYFGCpvaIPFw7l", # What's Going On
        "spotify:track:7tqhbajSfrz2F7E1Z75ASX"  # Ain't No Mountain High Enough
    ]

    async with SpotifySession(credentials=credentials) as session:
        async with SpotifyClient(session=session) as client:
            response = await client.playlists.add_items.run(
                playlist_id=playlist_id,
                uris=uris
            )

    print(response)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(add_playlist_items("<your-access-code>", "<your-playlist-id>"))
```

[**Reference**](https://developer.spotify.com/documentation/web-api/reference/add-tracks-to-playlist)

<h3>✨ Create Playlist</h3>

**Description**

Create a playlist for a Spotify user.

**Example**

```python
import asyncio

from spotipyio import SpotifySession, SpotifyClient
from spotipyio.auth import ClientCredentials, SpotifyGrantType
from spotipyio.models import PlaylistCreationRequest

async def create_marvin_gay_hits_playlist(access_code: str, user_id: str):
    credentials = ClientCredentials(
        grant_type=SpotifyGrantType.AUTHORIZATION_CODE,
        access_code=access_code
    )
    playlist_request = PlaylistCreationRequest(
        user_id=user_id,
        name="Marvin’s Magic",
        description="A soulful mix of Marvin Gaye’s timeless tracks",
        public=True
    )

    async with SpotifySession(credentials=credentials) as session:
        async with SpotifyClient(session=session) as client:
            response = await client.playlists.create.run(playlist_request)

    print(response)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_marvin_gay_hits_playlist("<your-access-code>", "<your-user-id>"))
```

[**Reference**](https://developer.spotify.com/documentation/web-api/reference/create-playlist)

<h3>ℹ️ Info</h3>

**Description**

Get playlists owned by Spotify users.

**Example**

```python
from spotipyio import SpotifyClient
import asyncio


async def fetch_playlists_info():
    async with SpotifyClient() as client:
        playlists_ids = [
            "37i9dQZF1DX70TzPK5buVf",  # Funk Outta Here
            "37i9dQZF1EFGVVd09MO7iM",  # Written by Pharrell Williams
        ]
        playlists_info = await client.playlists.info.run(playlists_ids)        

    print(playlists_info)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_playlists_info())
```

[**Reference**](https://developer.spotify.com/documentation/web-api/reference/get-playlist)

<h3>➖ Remove Items</h3>

**Description**

Remove one or more items from a user's playlist.

**Example**

```python
import asyncio

from spotipyio import SpotifySession, SpotifyClient
from spotipyio.auth import ClientCredentials, SpotifyGrantType


async def remove_playlist_items(access_code: str, playlist_id: str, snapshot_id: str):
    credentials = ClientCredentials(
        grant_type=SpotifyGrantType.AUTHORIZATION_CODE,
        access_code=access_code
    )
    uris = [
        "spotify:track:1z6WtY7X4HQJvzxC4UgkSf",  # Love on Top
        "spotify:track:6dOtVTDdiauQNBQEDOtlAB"  # Birds of a Feather
    ]

    async with SpotifySession(credentials=credentials) as session:
        async with SpotifyClient(session=session) as client:
            response = await client.playlists.remove_items.run(
                playlist_id=playlist_id,
                uris=uris,
                snapshot_id=snapshot_id
            )

    print(response)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        remove_playlist_items(
            access_code="<your-access-code>",
            playlist_id="<your-playlist-id>",
            snapshot_id="<playlist-snapshot-id>"  # Not sure what's the snapshot id?, fetch it using the info method
        )
    )
```

[**Reference**](https://developer.spotify.com/documentation/web-api/reference/remove-tracks-playlist)

<h3>↕️ Reorder Items</h3>

**Description**

Reorder one or more items from a user's playlist.

**Example**

```python
import asyncio

from spotipyio import SpotifySession, SpotifyClient
from spotipyio.auth import ClientCredentials, SpotifyGrantType
from spotipyio.models import PlaylistReorderRequest


async def reorder_first_item_to_last(access_code: str, playlist_id: str, snapshot_id: str):
    credentials = ClientCredentials(
        grant_type=SpotifyGrantType.AUTHORIZATION_CODE,
        access_code=access_code
    )
    request = PlaylistReorderRequest(
        playlist_id=playlist_id,
        range_start=0,
        insert_before=10,  # Assuming the playlist consists of 10 items
        snapshot_id=snapshot_id,
        range_length=1
    )

    async with SpotifySession(credentials=credentials) as session:
        async with SpotifyClient(session=session) as client:
            response = await client.playlists.reorder_items.run(request)

    print(response)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        reorder_first_item_to_last(
            access_code="<your-access-code>",
            playlist_id="<your-playlist-id>",
            snapshot_id="<playlist-snapshot-id>"  # Not sure what's the snapshot id?, fetch it using the info method
        )
    )
```

[**Reference**](https://developer.spotify.com/documentation/web-api/reference/reorder-or-replace-playlists-tracks)

<h3>🔄️ Replace Items</h3>

**Description**

Replace one or more items from a user's playlist with other provided items.

**Example**

```python
import asyncio

from spotipyio import SpotifySession, SpotifyClient
from spotipyio.auth import ClientCredentials, SpotifyGrantType


async def replace_all_playlist_items_by_uptown_funk(access_code: str, playlist_id: str):
    credentials = ClientCredentials(
        grant_type=SpotifyGrantType.AUTHORIZATION_CODE,
        access_code=access_code
    )

    async with SpotifySession(credentials=credentials) as session:
        async with SpotifyClient(session=session) as client:
            response = await client.playlists.replace_items.run(
                playlist_id=playlist_id,
                uris=["spotify:track:32OlwWuMpZ6b0aN2RZOeMS"]  # Uptown Funk
            )

    print(response)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        replace_all_playlist_items_by_uptown_funk(
            access_code="<your-access-code>",
            playlist_id="<your-playlist-id>",
        )
    )
```

[**Reference**](https://developer.spotify.com/documentation/web-api/reference/reorder-or-replace-playlists-tracks)

<h3>🖼️️ Update Cover</h3>

**Description**

Replace the image used to represent a specific playlist.

**Example**

```python
import asyncio

from spotipyio import SpotifySession, SpotifyClient
from spotipyio.auth import ClientCredentials, SpotifyGrantType


async def update_playlist_cover(access_code: str, playlist_id: str, image_path: str):
    credentials = ClientCredentials(
        grant_type=SpotifyGrantType.AUTHORIZATION_CODE,
        access_code=access_code
    )
    with open(image_path, "rb") as f:
        image = f.read()
        
    async with SpotifySession(credentials=credentials) as session:
        async with SpotifyClient(session=session) as client:
            response = await client.playlists.update_cover.run(
                playlist_id=playlist_id,
                image=image
            )

    print(response)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        update_playlist_cover(
            access_code="<your-access-code>",
            playlist_id="<your-playlist-id>",
            image_path="<path/to/your/image.jpeg>"  # Should be a JPEG image
        )
    )
```

[**Reference**](https://developer.spotify.com/documentation/web-api/reference/upload-custom-playlist-cover)

</details>

<details>
<summary style="font-size: large; font-weight: bold">🔎 Search</summary>

**Description**

Get Spotify catalog information about albums, artists, playlists, tracks, shows, episodes or audiobooks that match a 
keyword string.

**Example**

```python
import asyncio

from spotipyio import SpotifyClient
from spotipyio.models import SearchItem, SearchItemMetadata, SearchItemFilters, SpotifySearchType


async def search_bob_dylan_bootlegs():
    search_item = SearchItem(
        text="Bootleg",
        filters=SearchItemFilters(
            artist="Bob Dylan"
        ),
        metadata=SearchItemMetadata(
            search_types=[SpotifySearchType.ALBUM]
        )
    )

    async with SpotifyClient() as client:
        search_results = await client.search.search_item.run([search_item])

    print(search_results)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search_bob_dylan_bootlegs())
```

[**Reference**](https://developer.spotify.com/documentation/web-api/reference/search)
</details>

<details>
<summary style="font-size: large; font-weight: bold">🎷 Tracks</summary>
<h3>ℹ️ Info</h3>

**Description**

Get Spotify catalog information for multiple tracks based on their Spotify IDs.

**Example**

```python
import asyncio
from spotipyio import SpotifyClient
from typing import List


async def fetch_tracks_info(tracks_ids: List[str]):
    async with SpotifyClient() as client:
        tracks = await client.tracks.info.run(tracks_ids)        
        print(tracks)


if __name__ == "__main__":
    ids = ["2MuWTIM3b0YEAskbeeFE1i", "7xVpkVkd1klTzLJEysIR7z"]  # Master Of Puppets, Masters Of War
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_tracks_info(ids))
```

[**Reference**](https://developer.spotify.com/documentation/web-api/reference/get-several-tracks)

<h3>🔊️ Audio Features</h3>

**Description**

Get Spotify catalog information for multiple tracks based on their Spotify IDs.

**Example**

```python
import asyncio
from spotipyio import SpotifyClient


async def fetch_tracks_audio_features():
    tracks_ids = ["5W3cjX2J3tjhG8zb6u0qHn", "6Sy9BUbgFse0n0LPA5lwy5"]  # Harder Better Faster Stronger, Sandstorm

    async with SpotifyClient() as client:
        tracks = await client.tracks.audio_features.run(tracks_ids)        

    print(tracks)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_tracks_audio_features())
```

[**Reference**](https://developer.spotify.com/documentation/web-api/reference/get-several-audio-features)
</details>

<details>
<summary style="font-size: large; font-weight: bold">👥 Users</summary>

<h3>🔀 Users' Playlists</h3>
**Description**

Get a list of the playlists owned or followed by Spotify users.

**Example**

```python
import asyncio
from spotipyio import SpotifyClient


async def fetch_users_playlists():
    users = ["billboard.com", "pitchfork"]

    async with SpotifyClient() as client:
        users_playlists = await client.users.playlists.run(users)        

    print(users_playlists)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_users_playlists())
```

[**Reference**](https://developer.spotify.com/documentation/web-api/reference/get-list-users-playlists)
</details>

# 🧪 Testing
Testing is central to software development, but when it comes to external APIs like Spotify's it can be tricky 
to test our code without sending any actual request. To this end, spotipy introduces `SpotifyTestClient`. This object 
is designed to help you test components that use the `SpotifyClient` seamlessly, without having to mock or patch 
anything, or familiarize yourself with the internals of `SpotifyClient`. 

## Installation
To avoid adding dev dependencies to our production code, the test client sits under a dedicated `testing` module, which 
requirements' are optional. To install these extra requirements, execute the relevant command.

### Pip
```bash 
pip install spotipyio[testing]
```

### Pipenv
```bash 
pipenv install spotipyio[testing]
```

### Poetry
```bash 
poetry add spotipyio[testing]
```

#### A notice about versions management
As the test client it is designed only for testing, you should include it in only in your dev dependencies. 
On a poetry based project, for example, your `pyproject.toml` file should look somewhat like this:

```toml
[tool.poetry.dependencies]
spotipyio = { version = ">=1,<2" }

[tool.poetry.group.dev.dependencies]
spotipyio = { version = "*", extras = ["testing"] }
```

**Pay attention**: the version is pinned only in the dependencies section. The dev dependencies section should not pin 
a version, to avoid conflicts between two sections.

## Testing your first component
Imagine having a simple function that should fetch a playlist from Spotify and return a list of the 
playlist's tracks names. This function should look something like this:
```python
from typing import List
from spotipyio import SpotifyClient

async def get_playlist_tracks(spotify_client: SpotifyClient, playlist_id: str) -> List[str]:
    playlist = await spotify_client.playlists.info.run_single(playlist_id)
    items = playlist["tracks"]["items"]
    
    return [item["track"]["name"] for item in items]
```

Now, Let's test it:
```python
import pytest

from spotipyio.testing import SpotifyTestClient


@pytest.fixture
async def test_client() -> SpotifyTestClient:
    async with SpotifyTestClient() as client:
        yield client


async def test_get_playlist_tracks(test_client: SpotifyTestClient):
    # Arrange
    spotify_client = test_client.create_client()
    playlist_id = "readme-example"
    test_client.playlists.info.expect_success(playlist_id)

    # Act
    actual = await get_playlist_tracks(spotify_client, playlist_id)

    # Assert
    assert isinstance(actual, list)
```

What do we have here? Let's break it down step by step
1. First, we import `SpotifyTestClient` from the previously mentioned `spotipyio.testing` module. Notice that if you 
didn't install the package including the `testing` extra you will encounter an `ImportError` at this stage.
2. We create a fixture of `SpotifyTestClient`. Notice we use a `yield` statement instead of `return`, to keep 
the fixture context alive until teardown
3. We use the test client to instantiate a `SpotifyClient` instance. This is done using a simple `create_client` 
method, which sets up a client that shares the exact same settings as the test client.
4. Finally, we make sure our playlist request will be successful by calling `test_client.playlists.info.expect_success`.
This makes sure our request to the specific playlist id we're providing will be answered with a 200 status code.

## Testing Deep Dive
<details>
<summary style="font-size: large; font-weight: bold">🐾 SpotifyTestClient blueprint</summary>
In case you've noticed, the test client has the exact same blueprint as `SpotifyClient`. In our example, the tested 
function calls `spotify_client.playlists.info.run`, and our test calls `test_client.playlists.info.expect_success`. 
This identity is not an accident but lies in the core of the `SpotifyTestClient` blueprint. Every module in 
`SpotifyClient` has an equivalent in `SpotifyTestClient`. This makes testing easier then ever. All you have to do is 
check which methods are used by your production code, and call them during test setup with your test client.

The only difference between the two blueprints is in the 
methods they implement. Whereas `SpotifyClient` methods implements the `run` method, `SpotifyTestClient` methods 
implement the `expect_success` and `expect_failure` methods.
</details>

<details>
<summary style="font-size: large; font-weight: bold">📥 Setting the response json</summary>
This test, of course, is not very good. Mainly, it only validates the return value is a list, but it doesn't **really** 
check the actual value returned by the `get_platlist_tracks` function. To check this functionality, let's provide it 
an actual response json we expect. Here's a revised version:

```python
async def test_get_playlist_tracks_successful_response(test_client: SpotifyTestClient):
    # Arrange
    expected = ["Bohemian Raphsody", "The Blacker The Berry", "Take Five", "Jhonny B. Goode"]
    response_items = [{"track": {"name": name}} for name in expected]
    response_json = {"tracks": {"items": response_items}}
    spotify_client = test_client.create_client()
    playlist_id = "readme-example"
    test_client.playlists.info.expect_success(playlist_id, [response_json])

    # Act
    actual = await get_playlist_tracks(spotify_client, playlist_id)
    
    # Assert
    assert actual == expected
```

We've added our arrange block three lines where we define our expected value, than use it to create a mock playlist 
json that will be returned from the API. Than, we provide the test client with this response json, making sure that 
when a request to fetch the `readme-example` playlist will be received, this will be the exact json that will be 
returned. Notice that now our assertion is much stronger - we expect the actual value to be equal to our expectation.
</details>

<details>
<summary style="font-size: large; font-weight: bold">⚠️ Testing failures</summary>
Up until now we've been focusing only on testing successful scenarios. But what about exception handling? Handling 
exceptions is absolutely a must when it comes to work with external APIs like Spotify's. How should we test it? Let's 
start by wrapping our function with a simple `try-except` block

```python
from typing import List
from aiohttp import ClientResponseError
from spotipyio import SpotifyClient

async def get_playlist_tracks(spotify_client: SpotifyClient, playlist_id: str) -> List[str]:
    try:
        playlist = await spotify_client.playlists.info.run_single(playlist_id)
        items = playlist["tracks"]["items"]
        
        return [item["track"]["name"] for item in items]
    
    except ClientResponseError:
        print("Failed to fetch playlist. Retuning empty list instead")
        return []
```

Now, our function will simply print and return an empty list in cases it fails to fetch the API, instead of raising an 
exception that will fail our entire application. But how will we test it? Let's add another test to our suite.

```python
async def test_get_playlist_tracks_failed_response(test_client: SpotifyTestClient):
    # Arrange
    spotify_client = test_client.create_client()
    playlist_id = "readme-example"
    test_client.playlists.info.expect_failure(playlist_id)

    # Act
    actual = await get_playlist_tracks(spotify_client, playlist_id)
    
    # Assert
    assert actual == []
```

The only difference here is the usage of `test_client.playlists.info.expect_failure` instead of `expect_success`. This 
method instructs the test client to response with a failed status code.

Here again, we may also provide it with a specific response. Let's complicate our example by adding different 
behavior to different exceptions. A typical use case would be to backoff in case we receive a 429 (too many requests) 
status code. Here is a naive implementation:

```python
from typing import List
from aiohttp import ClientResponseError
from spotipyio import SpotifyClient
from asyncio import sleep

async def get_playlist_tracks(spotify_client: SpotifyClient, playlist_id: str, retries_left: int = 1) -> List[str]:
    try:
        playlist = await spotify_client.playlists.info.run_single(playlist_id)
        items = playlist["tracks"]["items"]

        return [item["track"]["name"] for item in items]

    except ClientResponseError as e:
        if e.status == 429 and retries_left > 0:
            await sleep(1)
            return await get_playlist_tracks(spotify_client, playlist_id, retries_left - 1)

        print("Failed to fetch playlist. Retuning empty list instead")
        return []
```

How might we test this? By providing our test client a specific status code. This final example will incorporate all 
use cases we saw by now. We will have to call the test client twice: first to set it to return a custom 429 response, 
then to return a successful response. This test will now look like this:

```python
async def test_get_playlist_tracks_first_fail_than_success(test_client: SpotifyTestClient):
    # Arrange
    spotify_client = test_client.create_client()
    playlist_id = "readme-example"
    test_client.playlists.info.expect_failure(playlist_id, status=429)
    expected = ["The Fool on the Hill", "Relax (Take It Easy)", "The Real Slim Shady"]
    response_items = [{"track": {"name": name}} for name in expected]
    response_json = {"tracks": {"items": response_items}}
    playlist_id = "readme-example"
    test_client.playlists.info.expect_success(playlist_id, [response_json])

    # Act
    actual = await get_playlist_tracks(spotify_client, playlist_id)
    
    # Assert
    assert actual == expected
```

**Please notice**: The test client expects ordered expectations. Here we first set a failed response 
expectation, then only a successful response. If we will first call the `expect_success` method, our code will simply 
not reach the except block.
</details>
