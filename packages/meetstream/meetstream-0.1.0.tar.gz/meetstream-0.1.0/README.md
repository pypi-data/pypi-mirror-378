
# Unofficial MeetstreamAPI Python Client

The `MeetstreamAPI` class is a lightweight Python client for interacting with the [Meetstream.ai](https://meetstream.ai) API.  
It allows you to create and manage meeting bots, retrieve transcripts, media, chat messages, participants, and more.

---

## Table of Contents
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [API Reference](#api-reference)
  - [create\_bot](#create_bot-→-dict)
  - [get\_bot\_status](#get_bot_statusbot_id-str--dict)
  - [get\_bot\_details](#get_bot_detailsbot_id-str--dict)
  - [get\_bot\_audio](#get_bot_audiobot_id-str--requestsresponse)
  - [get\_bot\_video](#get_bot_videobot_id-str--requestsresponse)
  - [get\_transcript](#get_transcripttranscript_id-str-raw-bool--false--dict)
  - [remove\_bot](#remove_botbot_id-str--dict)
  - [get\_speaker\_timeline](#get_speaker_timelinebot_id-str--dict)
  - [get\_chats](#get_chatsbot_id-str--dict)
  - [get\_screenshots](#get_screenshotsbot_id-str--dict)
  - [get\_participants](#get_participantsbot_id-str--dict)
- [Error Handling](#error-handling)
- [Example Workflow](#example-workflow)

---

## Installation

```bash
pip install requests
````

(Only `requests` is required.)

---

## Getting Started

```python
from meetstream import MeetstreamAPI  # if you save the class in meetstream.py

# Initialize client with your API key
api = MeetstreamAPI(api_key="your_api_key_here")

# Create a new meeting bot
bot_data = api.create_bot(
    meeting_link="https://meet.google.com/abc-defg-hij",
    bot_name="Meeting Assistant",
    bot_message="Hello, team 👋",
    custom_attributes={"project": "Alpha"}
)

print("Bot created:", bot_data)

bot_id = bot_data["bot_id"]
transcript_id = bot_data["transcript_id"]

# Get bot status
status = api.get_bot_status(bot_id)
print("Bot status:", status)

# Get transcript
transcript = api.get_transcript(transcript_id)
print("Transcript:", transcript)

# Remove the bot when done
result = api.remove_bot(bot_id)
print("Bot removed:", result)
```

---

## Authentication

All requests require an API key.
You can pass it when initializing the client:

```python
api = MeetstreamAPI(api_key="your_api_key")
```

Or set it later:

```python
api.set_api_key("your_api_key")
```

The key is automatically included in all requests via the `Authorization` header.

---

## API Reference

### `create_bot(...) → dict`

Create a new bot and join a meeting.

**Parameters:**

* `meeting_link` *(str, required)* — The meeting URL.
* `bot_name` *(str, required)* — Bot display name.
* `video_required` *(bool, default=False)* — Enable video recording.
* `audio_required` *(bool, default=False)* — Enable audio recording.
* `bot_message` *(str, optional)* — Initial chat message from the bot.
* `bot_image_url` *(str, optional)* — Profile image URL.
* `socket_connection_url` *(str, optional)* — WebSocket endpoint for live updates.
* `live_audio_required` *(dict, optional)* — Config for live audio streaming.
* `live_transcription_required` *(dict, optional)* — Config for live transcription.
* `transcription` *(dict, optional)* — Transcription service settings.
* `custom_attributes` *(dict, optional)* — Any extra metadata you want to store.
* `join_at` *(str, optional)* — Scheduled join time (ISO 8601).
* `callback_url` *(str, optional)* — Webhook callback URL.

**Returns:**
JSON response with `bot_id` and `transcript_id`.

---

### `get_bot_status(bot_id: str) → dict`

Get current status of a bot.

**Parameters:**

* `bot_id` *(str)* — Bot identifier.

**Returns:**
Status info (online/offline, recording status, etc.).

---

### `get_bot_details(bot_id: str) → dict`

Retrieve detailed information about a bot.

---

### `get_bot_audio(bot_id: str) → requests.Response`

Download audio recorded by the bot.
Use `.content` to save the binary data:

```python
audio = api.get_bot_audio(bot_id)
with open("meeting_audio.mp3", "wb") as f:
    f.write(audio.content)
```

---

### `get_bot_video(bot_id: str) → requests.Response`

Download video recorded by the bot.
Similar to audio, use `.content` to save.

---

### `get_transcript(transcript_id: str, raw: bool = False) → dict`

Get meeting transcript.

**Parameters:**

* `transcript_id` *(str)* — Transcript identifier.
* `raw` *(bool, default=False)* — If `True`, returns unprocessed transcript data.

---

### `remove_bot(bot_id: str) → dict`

Remove a bot from a meeting.

---

### `get_speaker_timeline(bot_id: str) → dict`

Retrieve speaker timeline (who spoke when).

---

### `get_chats(bot_id: str) → dict`

Retrieve chat messages captured by the bot.

---

### `get_screenshots(bot_id: str) → dict`

Retrieve screenshots taken during the meeting.

---

### `get_participants(bot_id: str) → dict`

Retrieve participant list for a meeting.

---

## Error Handling

All methods raise `requests.exceptions.HTTPError` if the API returns an error.
Wrap calls in try/except to handle failures:

```python
try:
    status = api.get_bot_status("invalid_bot_id")
except requests.exceptions.HTTPError as e:
    print("API error:", e.response.json())
```

---

## Example Workflow

1. **Create bot** → Get `bot_id` and `transcript_id`.
2. **Monitor status** → Poll `get_bot_status()`.
3. **Fetch data** → Get transcript, audio, video, chats, screenshots.
4. **Remove bot** → Call `remove_bot()` once meeting is done.

