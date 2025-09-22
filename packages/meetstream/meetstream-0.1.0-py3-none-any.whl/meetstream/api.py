import requests
import json
from typing import Optional, Dict, Any, List

class MeetstreamAPI:
    def __init__(self, base_url: str = "https://api.meetstream.ai", api_key: Optional[str] = None):
        """
        Initialize the Meetstream API client.
        
        Args:
            base_url: The base URL for the API (defaults to production)
            api_key: Your API authentication token
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Token {self.api_key}"
            })
    
    def set_api_key(self, api_key: str):
        """Set or update the API key for authentication."""
        self.api_key = api_key
        self.session.headers.update({
            "Authorization": f"Token {self.api_key}"
        })
    
    def create_bot(
        self,
        meeting_link: str,
        bot_name: str,
        video_required: bool = False,
        audio_required: bool = False,
        bot_message: Optional[str] = None,
        bot_image_url: Optional[str] = None,
        socket_connection_url: Optional[str] = None,
        live_audio_required: Optional[Dict[str, str]] = None,
        live_transcription_required: Optional[Dict[str, str]] = None,
        transcription: Optional[Dict[str, Any]] = None,
        custom_attributes: Optional[Dict[str, Any]] = None,
        join_at: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new bot to join a meeting.
        
        Args:
            meeting_link: The URL of the meeting to join
            bot_name: Name of the bot
            video_required: Whether video recording is required
            audio_required: Whether audio recording is required
            bot_message: Initial message from the bot
            bot_image_url: URL of the bot's profile image
            socket_connection_url: WebSocket URL for real-time communication
            live_audio_required: Configuration for live audio streaming
            live_transcription_required: Configuration for live transcription
            transcription: Transcription service configuration
            custom_attributes: Additional custom attributes
            join_at: Scheduled join time (ISO 8601 format)
            callback_url: URL for webhook callbacks
            
        Returns:
            Response from the API including bot_id and transcript_id
        """
        url = f"{self.base_url}/api/v1/bots/create_bot"
        
        payload = {
            "meeting_link": meeting_link,
            "bot_name": bot_name,
            "video_required": video_required,
            "audio_required": audio_required
        }
        
        # Add optional fields if provided
        if bot_message is not None:
            payload["bot_message"] = bot_message
        if bot_image_url is not None:
            payload["bot_image_url"] = bot_image_url
        if socket_connection_url is not None:
            payload["socket_connection_url"] = socket_connection_url
        if live_audio_required is not None:
            payload["live_audio_required"] = live_audio_required
        if live_transcription_required is not None:
            payload["live_transcription_required"] = live_transcription_required
        if transcription is not None:
            payload["transcription"] = transcription
        if custom_attributes is not None:
            payload["custom_attributes"] = custom_attributes
        if join_at is not None:
            payload["join_at"] = join_at
        if callback_url is not None:
            payload["callback_url"] = callback_url
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def get_bot_status(self, bot_id: str) -> Dict[str, Any]:
        """
        Get the status of a bot.
        
        Args:
            bot_id: The ID of the bot
            
        Returns:
            Status information about the bot
        """
        url = f"{self.base_url}/api/v1/bots/{bot_id}/status"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def get_bot_details(self, bot_id: str) -> Dict[str, Any]:
        """
        Get details about a bot.
        
        Args:
            bot_id: The ID of the bot
            
        Returns:
            Detailed information about the bot
        """
        url = f"{self.base_url}/api/v1/bots/{bot_id}/detail"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def get_bot_audio(self, bot_id: str) -> requests.Response:
        """
        Get audio recorded by the bot.
        
        Args:
            bot_id: The ID of the bot
            
        Returns:
            Response object containing audio data
        """
        url = f"{self.base_url}/api/v1/bots/{bot_id}/get_audio"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response
    
    def get_bot_video(self, bot_id: str) -> requests.Response:
        """
        Get video recorded by the bot.
        
        Args:
            bot_id: The ID of the bot
            
        Returns:
            Response object containing video data
        """
        url = f"{self.base_url}/api/v1/bots/{bot_id}/get_video"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response
    
    def get_transcript(self, transcript_id: str, raw: bool = False) -> Dict[str, Any]:
        """
        Get the transcript for a meeting.
        
        Args:
            transcript_id: The ID of the transcript
            raw: Whether to return raw transcript data
            
        Returns:
            Transcript data
        """
        url = f"{self.base_url}/api/v1/transcript/{transcript_id}/get_transcript"
        
        params = {}
        if raw:
            params["raw"] = "True"
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def remove_bot(self, bot_id: str) -> Dict[str, Any]:
        """
        Remove a bot from a meeting.
        
        Args:
            bot_id: The ID of the bot to remove
            
        Returns:
            Response indicating success or failure
        """
        url = f"{self.base_url}/api/v1/bots/{bot_id}/remove_bot"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def get_speaker_timeline(self, bot_id: str) -> Dict[str, Any]:
        """
        Get the speaker timeline for a meeting.
        
        Args:
            bot_id: The ID of the bot
            
        Returns:
            Speaker timeline data
        """
        url = f"{self.base_url}/api/v1/bots/{bot_id}/get_speaker_timeline"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def get_chats(self, bot_id: str) -> Dict[str, Any]:
        """
        Get chat messages from a meeting.
        
        Args:
            bot_id: The ID of the bot
            
        Returns:
            Chat message data
        """
        url = f"{self.base_url}/api/v1/bots/{bot_id}/get_chats"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def get_screenshots(self, bot_id: str) -> Dict[str, Any]:
        """
        Get screenshots taken during a meeting.
        
        Args:
            bot_id: The ID of the bot
            
        Returns:
            Screenshot data
        """
        url = f"{self.base_url}/api/v1/bots/{bot_id}/get_screenshots"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def get_participants(self, bot_id: str) -> Dict[str, Any]:
        """
        Get participants from a meeting.
        
        Args:
            bot_id: The ID of the bot
            
        Returns:
            Participant data
        """
        url = f"{self.base_url}/api/v1/bots/{bot_id}/get_participants"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()

    
    def create_calendar(
        self,
        google_client_id: str,
        google_client_secret: str,
        google_refresh_token: str
    ) -> Dict[str, Any]:
        """
        Create a calendar integration using Google OAuth credentials.
        
        Args:
            google_client_id: Google client ID
            google_client_secret: Google client secret
            google_refresh_token: Google refresh token
            
        Returns:
            Response from the API with calendar details
        """
        url = f"{self.base_url}/api/v1/calendar/create_calendar"
        
        payload = {
            "google_client_id": google_client_id,
            "google_client_secret": google_client_secret,
            "google_refresh_token": google_refresh_token
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()


# Example usage
if __name__ == "__main__":
    # Initialize the client
    api = MeetstreamAPI(api_key="your_api_key_here")
    
    # Create a bot
    bot_data = api.create_bot(
        meeting_link="https://meet.google.com/xsw-bery-nwc",
        bot_name="Meetstream's Agent",
        bot_message="Hey Everyone 👋",
        bot_image_url="https://images.pexels.com/photos/1458916/pexels-photo-1458916.jpeg",
        custom_attributes={
            "tag": "Maddy",
            "sample": "testing"
        }
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
    
    # Remove bot when done
    removal_result = api.remove_bot(bot_id)
    print("Bot removal:", removal_result)
