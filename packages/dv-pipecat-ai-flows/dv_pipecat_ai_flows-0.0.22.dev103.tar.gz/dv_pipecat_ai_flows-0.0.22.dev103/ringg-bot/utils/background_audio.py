import os
from typing import Dict, Optional

from loguru import logger

from pipecat.audio.mixers.soundfile_mixer import SoundfileMixer


class BackgroundAudioManager:
    """Manages background audio for the ringg-chatbot to make conversations more realistic.

    This class handles the configuration and management of background audio files
    that are mixed with the bot's speech to simulate real-world conversation environments.
    """

    # DEFAULT AUDIOS
    DEFAULT_AUDIOS = [
        {
            "audio_id": "office_ambience",
            "file_name": "office_ambience_8k_mono.wav",
            "volume": 1,
            "mixing": True,
            "loop": True,
        },
    ]

    def __init__(self, assets_dir: str = "assets/background"):
        """Initialize the background audio manager.

        Args:
            assets_dir: Directory containing background audio files
        """
        self.assets_dir = assets_dir
        self._validate_assets_directory()

    def _validate_assets_directory(self):
        """Validate that the assets directory exists and contains audio files."""
        if not os.path.exists(self.assets_dir):
            logger.warning(f"Background audio assets directory {self.assets_dir} does not exist")
            return

        audio_files = [
            f
            for f in os.listdir(self.assets_dir)
            if f.lower().endswith((".mp3", ".wav", ".flac", ".ogg"))
        ]

        if not audio_files:
            logger.warning(f"No audio files found in {self.assets_dir}")
        else:
            logger.info(f"Found {len(audio_files)} background audio files: {audio_files}")

    def create_mixer_from_audio_config(self, audio_config) -> Optional[SoundfileMixer]:
        """Create a SoundfileMixer instance from an audio config.

        Args:
            audio_config: BackgroundAudioConfig object with audio configuration

        Returns:
            Configured SoundfileMixer instance or None if audio ID is invalid
        """
        original_audio = self._get_audio_info(audio_config.audio_id)

        if not original_audio:
            logger.error(f"Audio ID '{audio_config.audio_id}' not found in mapping")
            return None

        # Use the default values from the original audio configuration
        # Since BackgroundAudioConfig only has audio_id, use original audio defaults
        volume = original_audio["volume"]
        mixing = original_audio["mixing"]
        loop = original_audio["loop"]

        audio_config_dict = {
            "audio_id": audio_config.audio_id,
            "file_path": original_audio["file_path"],
            "volume": volume,
            "mixing": mixing,
            "loop": loop,
        }

        # Create sound files mapping for the mixer
        sound_files = {audio_config_dict["audio_id"]: audio_config_dict["file_path"]}

        logger.info(
            f"Creating background audio mixer with audio ID '{audio_config_dict['audio_id']}' at volume {audio_config_dict['volume']}"
        )

        return SoundfileMixer(
            sound_files=sound_files,
            default_sound=audio_config_dict["audio_id"],
            volume=audio_config_dict["volume"],
            mixing=audio_config_dict["mixing"],
            loop=audio_config_dict["loop"],
        )

    def _get_audio_info(self, audio_id: str | None) -> Optional[Dict]:
        """Get information about a specific audio ID.

        Args:
            audio_id: The audio ID to get info for

        Returns:
            Dictionary with audio information or None if not found
        """
        if audio_id is None:
            return None

        audio_config = next(
            (audio for audio in self.DEFAULT_AUDIOS if audio["audio_id"] == audio_id), None
        )

        if not audio_config:
            return None

        audio_config = audio_config.copy()

        filename = audio_config["file_name"]
        file_path = os.path.join(self.assets_dir, filename)

        if not os.path.exists(file_path):
            logger.warning(f"Audio file not found: {file_path}")
            return None

        audio_config["file_path"] = file_path

        return audio_config


# Default background audio manager instance
background_audio_manager = BackgroundAudioManager()
