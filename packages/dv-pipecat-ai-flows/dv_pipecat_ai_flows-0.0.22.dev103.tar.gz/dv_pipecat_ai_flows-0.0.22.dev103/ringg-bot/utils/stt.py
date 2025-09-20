from typing import List, Optional

from deepgram import LiveOptions  # noqa: D100
from env_config import api_config
from speechmatics.rt import OperatingPoint

from pipecat.services.azure.stt import AzureSTTService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.elevenlabs.stt import ElevenlabsSTTService

# Import Gladia config models needed
from pipecat.services.gladia.config import GladiaInputParams, LanguageConfig
from pipecat.services.gladia.stt import GladiaSTTService, language_to_gladia_language
from pipecat.services.google.stt import GoogleSTTService
# from pipecat.services.hamsa.stt import HamsaSTTService

from pipecat.services.speechmatics.stt import AdditionalVocabEntry, SpeechmaticsSTTService
from pipecat.transcriptions.language import Language


# Add vocab parameter with type hint and default value
def initialize_stt_service(
    stt_provider: str,
    language: str,
    stt_model: Optional[str],
    additional_languages: List[str],
    logger,
    record_locally=False,
    vocab: Optional[List[str]] = None,
):
    """Initializes a speech-to-text (STT) service based on the specified provider.

    This function supports multiple STT providers like Deepgram, Google, Azure, Gladia,
    Speechmatics, ElevenLabs, and Hamsa.

    Provider-specific notes:
    * Deepgram: Nova-3 vs Nova-2 models with vocabulary routing
      - English  → nova-phonecall
      - Hindi    → nova-2
      - nova-3 → keyterms (no boost values)
      - nova-2/phonecall → keywords (word:boost)
    * ElevenLabs: Batch processing with Scribe v1 model, supports 99 languages
    * Other providers: Various real-time streaming capabilities
    """
    if stt_provider == "deepgram":
        dg_lang = "hi" if any(l in additional_languages for l in ("hi", "hi-IN")) else language
        model = stt_model or ("nova-2-phonecall" if dg_lang.startswith("en") else "nova-2")

        def _clean_vocab(words: Optional[List[str]]) -> List[str]:
            return [w.strip() for w in words or [] if isinstance(w, str) and w.strip()]

        keywords: List[str] = []
        keyterms: List[str] = []
        base_fillers_hi = ["हाँ", "हाँ जी"]
        base_fillers_en = ["ha", "haan"]

        is_nova3 = model.startswith("nova-3")

        if dg_lang.startswith("hi"):
            fillers = base_fillers_hi
        else:
            fillers = base_fillers_en
        if is_nova3:
            # KEYTERMS (no boosts)
            if dg_lang[:2] in (
                "hi",
                "nl",
                "ru",
                "pt",
                "es",
                "de",
                "fr",
                "ja",
                "it",
            ):
                dg_lang = "multi"
            keyterms.extend(fillers)
            keyterms.extend(_clean_vocab(vocab))
            keyterms = keyterms[:100]
            addons = {"keyterms": keyterms} if keyterms else None
            kw_args = {}
        else:
            # KEYWORDS (needs boost)
            keywords.extend(f"{w}:1.5" for w in fillers)
            keywords.extend(f"{w}:1.1" for w in _clean_vocab(vocab))
            keywords = keywords[:100]
            addons = None
            kw_args = {"keywords": keywords} if keywords else {}
        logger.info(
            f"Deepgram model={model}, lang={dg_lang}, "
            f"{'keyterms' if is_nova3 else 'keywords'}={keyterms or keywords}"
        )

        live_options = LiveOptions(
            model=model,
            language=dg_lang,
            encoding="linear16",
            channels=1,
            interim_results=True,
            smart_format=False,
            numerals=False,
            punctuate=True,
            profanity_filter=True,
            vad_events=False,
            **kw_args,  # ← keywords only for nova-2 / phonecall
        )
        stt = DeepgramSTTService(
            api_key=api_config.DEEPGRAM_API_KEY,
            live_options=live_options,
            audio_passthrough=record_locally,
            addons=addons,  # ← keyterms only for nova-3
        )
    elif stt_provider == "google":
        logger.debug("Google STT initilaising")
        languages = list({Language(language), Language.EN_IN})
        # list of languages you want to support; adjust if needed
        stt = GoogleSTTService(
            params=GoogleSTTService.InputParams(
                languages=languages, enable_automatic_punctuation=False, model="latest_short"
            ),
            credentials_path="creds.json",  # your service account JSON file,
            location="us",
            audio_passthrough=record_locally,
            # metrics=SentryMetrics(),
        )
        logger.debug("Google STT initiaised")
    elif stt_provider == "azure":
        logger.debug(
            f"Initializing Azure STT. Received language parameter: '{language}' (type: {type(language)})"
        )  # ADDED LOG
        # Explicitly check the condition and log the result
        # is_telugu = language == "te-IN"
        additional_langs = [Language(add_lang) for add_lang in additional_languages]
        # Note: Azure STT requires different handling (Phrase Lists) - see notes below.
        stt = AzureSTTService(
            api_key=api_config.AZURE_SPEECH_API_KEY,
            region=api_config.AZURE_SPEECH_REGION,
            language=Language(language),
            additional_languages=additional_langs,
            audio_passthrough=record_locally,
            vocab=vocab,  # Pass vocab via kwargs
            # metrics=SentryMetrics(),
        )
    elif stt_provider == "gladia":
        languages = [Language(language)]
        for l in additional_languages:
            languages.append(Language(l))

        params = GladiaInputParams(
            language_config=LanguageConfig(languages=languages),
            code_switching=True if len(languages) > 1 else False,
        )

        stt = GladiaSTTService(
            api_key=api_config.GLADIA_API_KEY,
            region="us-west",
            params=params,  # Pass the configured params object
            audio_passthrough=record_locally,
            vocab=vocab,  # Pass vocab via kwargs
            # metrics=SentryMetrics(),
        )
    elif stt_provider == "speechmatics":

        def _clean_vocab(words: Optional[List[str]]) -> List[str]:
            return [w.strip() for w in words or [] if isinstance(w, str) and w.strip()]

        # Base filler words for better recognition (like Deepgram)
        base_fillers_hi = ["हाँ", "हाँ जी"]
        base_fillers_en = ["ha", "haan", "yes", "okay"]

        # Select fillers based on language
        if language.startswith("hi"):
            fillers = base_fillers_hi
        else:
            fillers = base_fillers_en

        # Build additional vocabulary entries
        additional_vocab_entries = []
        # TODO: There's a bug in pipecat where if you dont set the sounds_like, it sends an empty array and Speechmatics throws an error
        # # Add filler words
        # for word in fillers:
        #     additional_vocab_entries.append(AdditionalVocabEntry(content=word))

        # # Add user-provided vocabulary
        # for word in _clean_vocab(vocab):
        #     additional_vocab_entries.append(AdditionalVocabEntry(content=word))

        # # Limit vocabulary size (Speechmatics has performance penalties with large lists)
        # additional_vocab_entries = additional_vocab_entries[:50]  # Conservative limit

        params = SpeechmaticsSTTService.InputParams(
            language="en_ta" if language.startswith("ta") else Language(language),
            enable_diarization=False,  # Disabled as requested
            end_of_utterance_silence_trigger=0.5,  # Set to 0.6 as requested
            enable_partials=True,
            operating_point=OperatingPoint.STANDARD,
            additional_vocab=additional_vocab_entries,  # Use processed vocabulary
        )

        logger.info(f"Speechmatics vocab={[entry.content for entry in additional_vocab_entries]}")

        stt = SpeechmaticsSTTService(
            api_key=api_config.SPEECHMATICS_API_KEY,
            params=params,
            audio_passthrough=record_locally,
            # metrics=SentryMetrics(),
        )
    elif stt_provider == "elevenlabs":
        logger.debug("Initializing ElevenLabs STT")

        # ElevenLabs STT uses batch processing with VAD-based segmentation
        # Map language string to pipecat Language enum
        try:
            pipecat_language = Language(language)
        except ValueError:
            logger.warning(f"Unknown language '{language}', defaulting to English")
            pipecat_language = Language.EN

        logger.info(f"ElevenLabs STT language={pipecat_language}")

        stt = ElevenlabsSTTService(
            api_key=api_config.ELEVENLABS_API_KEY,
            model_id="scribe_v1",
            language=pipecat_language,
            tag_audio_events=False,  # Disable audio event tagging for telephony
            diarize=False,  # Speaker diarization disabled for telephony
            # Note: ElevenLabs STT doesn't support custom vocabulary like Deepgram
            # Audio passthrough is handled by SegmentedSTTService
        )
        logger.debug("ElevenLabs STT initialized")
    elif stt_provider == "hamsa":
        logger.debug("Initializing Hamsa STT")

        # # Hamsa supports Arabic and English
        # hamsa_language = Language(language)

        # # EOS threshold can be configured (0.0-1.0, default 0.3)
        # eos_threshold = 0.3

        # logger.info(f"Hamsa STT language={hamsa_language}, eos_threshold={eos_threshold}")

        # stt = HamsaSTTService(
        #     api_key=api_config.HAMSA_API_KEY,
        #     language=hamsa_language,
        #     eos_threshold=eos_threshold,
        #     audio_passthrough=record_locally,
        #     # metrics=SentryMetrics(),
        # )
        # logger.debug("Hamsa STT initialized")

    return stt
