# Standard Library Imports
import asyncio
from typing import Union

# Third-Party Imports
from google.cloud import texttospeech_v1

# First-Party Imports
from pipecat.frames.frames import STTUpdateSettingsFrame, TTSUpdateSettingsFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.azure import AzureTTSService
from pipecat.services.google.tts import GoogleTTSService, language_to_google_tts_language
from pipecat.services.tts_service import TTSService
from pipecat.transcriptions.language import Language

# Define language mapping
LANGUAGE_MAP = {
    "english": Language.EN_IN,
    "hindi": Language.HI_IN,
    "telugu": Language.TE_IN,
    "tamil": Language.TA_IN,
    "kannada": Language.KN_IN,
    # Add more mappings as needed
}

# Define switch_language tool
switch_language_tool = {
    "name": "switch_language",
    "description": "Switch to this conversation language when the user asks explicitly asks you to do so.",
    "parameters": {
        "type": "object",
        "properties": {
            "language": {
                "type": "string",
                "description": "The target language name (e.g., 'telugu', 'english', 'hindi', 'tamil', 'kannada').",
            },
        },
        "required": ["language"],
    },
}


async def switch_language_handler(
    function_name: str,
    tool_call_id: str,
    args: dict,
    llm: FrameProcessor,
    tts: Union[TTSService, GoogleTTSService],
    tts_provider: str,
    context,
    result_callback: callable,
    function_call_monitor,
    bot_logger,
):
    language_name = args.get("language", "").lower()
    bot_logger.info(f"Attempting to switch STT language to: {language_name}")
    function_call_monitor.append("called_switch_language")
    language_enum = LANGUAGE_MAP.get(language_name)

    if not language_enum:
        error_message = f"Sorry, I don't support the language '{language_name}' for STT."
        bot_logger.warning(error_message)
        await result_callback({"error": error_message})
        return

    try:
        voice = tts._voice_id

        # Update STT (Upstream)
        stt_update_frame = STTUpdateSettingsFrame(settings={"language": language_enum})
        await llm.push_frame(stt_update_frame, FrameDirection.UPSTREAM)
        bot_logger.info(f"Pushed STTUpdateSettingsFrame for {language_name} upstream")

        # Update TTS (Downstream)
        if tts_provider == "azure":
            tts_update_frame = TTSUpdateSettingsFrame(settings={"language": language_enum})
            await llm.push_frame(tts_update_frame, FrameDirection.DOWNSTREAM)
            bot_logger.info(f"Pushed TTSUpdateSettingsFrame for {language_name} downstream")
            success_message = f"Switched language to {language_name}."
        if tts_provider == "google":
            if "chirp" in voice.lower() and isinstance(tts, GoogleTTSService):
                if tts._voice_config.get("is_clone", False):
                    tts._voice = texttospeech_v1.VoiceSelectionParams(
                        language_code=str(language_to_google_tts_language(language_enum)).lower(),
                        voice_clone=tts._voice_clone_params,
                    )
                    success_message = f"Switched language to {language_name}."
                else:
                    current_language = tts._settings["language"]
                    voice = voice.lower().replace(current_language.lower() + "-", "")
                    voice = f"{str(language_to_google_tts_language(language_enum)).lower()}-{str(voice).lower()}"
                    bot_logger.info(
                        f"chirp voice changing from currnet_voice {current_language}, voice: {voice}, language: {language_enum}"
                    )
                    # print(
                    #     f"chirp voice changing from currnet_voice {current_language}, voice: {voice}, language: {language_enum}"
                    # )
                    tts_update_frame = TTSUpdateSettingsFrame(
                        settings={"language": language_enum, "voice": voice}
                    )

                    await llm.push_frame(tts_update_frame, FrameDirection.DOWNSTREAM)
                    # print(f"Pushed TTSUpdateSettingsFrame for {language_name} downstream")
                    bot_logger.info(f"Pushed TTSUpdateSettingsFrame for {language_name} downstream")
                    success_message = f"Switched language to {language_name}."
            else:
                bot_logger.info(
                    f"Switching language not supported for this TTS provider {tts_provider} and voice {voice}- not chirp"
                )
                success_message = f"Switching language not supported for this TTS provider {tts_provider} and voice {voice}- not chirp"

        else:
            bot_logger.info(
                f"Switching language not supported for this TTS provider {tts_provider}"
            )
            success_message = (
                f"Switching language not supported for this TTS provider {tts_provider}"
            )

        await result_callback({"status": success_message})

    except Exception as e:
        error_message = f"An error occurred while switching language: {e}"
        bot_logger.exception(error_message)
        await result_callback({"error": error_message})
