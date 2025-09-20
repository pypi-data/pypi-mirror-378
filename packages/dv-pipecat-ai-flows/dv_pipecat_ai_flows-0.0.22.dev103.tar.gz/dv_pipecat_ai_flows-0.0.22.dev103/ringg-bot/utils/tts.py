# -*- coding: utf-8 -*-
# Text formatter + TTS helpers with Arabic Najdi currency handling

import hashlib
import io
import json
import re
import socket
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Callable, Dict, Optional

import numpy as np
import redis.asyncio as redis
from loguru import logger
from num2words import num2words as main_num2words
from num_to_words import num_to_word as indic_num2words
from num_to_words.utils.constants import SUPPORTED_LANGUAGES as NUM2WORDS_SUPPORTED_LANGUAGES
from pipecat.audio.resamplers.soxr_resampler import SOXRAudioResampler
from pipecat.frames.frames import TTSAudioRawFrame, TTSSpeakFrame
from pipecat.services.azure.tts import AzureTTSService
from pipecat.services.cartesia.tts import CartesiaHttpTTSService, CartesiaTTSService
from pipecat.services.deepgram.tts import DeepgramTTSService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.google.tts import (
    GoogleHttpTTSService,
    GoogleTTSService,
    language_to_google_tts_language,
)
from pipecat.services.sarvam.tts import SarvamTTSService
from pipecat.services.tts_service import TTSService
from pipecat.transcriptions.language import Language
from pipecat.transports.network.fastapi_websocket import FastAPIWebsocketTransport
from pipecat.pipeline.task import PipelineTask
from pydub import AudioSegment
from env_config import api_config
# --------------------------
# Language detection helpers
# --------------------------


def is_hindi(text: str) -> bool:
    hindi_chars = re.findall(r"[\u0900-\u097F]+", text)
    hindi_chars_count = sum(len(word) for word in hindi_chars)
    threshold = 0.25
    return hindi_chars_count / len(text) > threshold if text else False


def is_arabic(text: str) -> bool:
    arabic_chars = re.findall(
        r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+",
        text,
    )
    arabic_chars_count = sum(len(word) for word in arabic_chars)
    threshold = 0.25
    return arabic_chars_count / len(text) >= threshold if text else False


# --------------------------
# Localized constants
# --------------------------

CURRENCY_UNITS = {
    "en": {
        "₹": ("rupees", "paisa"),
        "$": ("dollars", "cents"),
        "€": ("euros", "cents"),
        "£": ("pounds", "pence"),
        "د.إ": ("dirhams", "fils"),
        "ر.س": ("riyals", "halalas"),
    },
    "hi": {
        "₹": ("रुपये", "पैसे"),
        "$": ("डॉलर", "सेंट"),
        "€": ("यूरो", "सेंट"),
        "£": ("पाउंड", "पेंस"),
    },
    "ar": {
        "₹": ("روبية", "بيسة"),
        "$": ("دولار", "سنت"),
        "€": ("يورو", "سنت"),
        "£": ("جنيه", "بنس"),
        "د.إ": ("درهم", "فلس"),
        "ر.س": ("ريال", "هلله"),
    },
}

MONTH_NAMES = {
    "en": [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ],
    "hi": [
        "जनवरी",
        "फरवरी",
        "मार्च",
        "अप्रैल",
        "मई",
        "जून",
        "जुलाई",
        "अगस्त",
        "सितंबर",
        "अक्टूबर",
        "नवंबर",
        "दिसंबर",
    ],
    "ar": [
        "يناير",
        "فبراير",
        "مارس",
        "أبريل",
        "مايو",
        "يونيو",
        "يوليو",
        "أغسطس",
        "سبتمبر",
        "أكتوبر",
        "نوفمبر",
        "ديسمبر",
    ],
}

SYMBOL_TRANSLATIONS = {
    "en": {
        "@": "at",
        "#": "hash",
        "%": "percent",
        "&": "and",
        "+": "plus",
        "=": "equals",
        "_": "underscore",
    },
    "hi": {
        "@": "एट",
        "#": "हैश",
        "%": "प्रतिशत",
        "&": "और",
        "+": "जोड़",
        "=": "बराबर",
        "_": "अंडरस्कोर",
    },
    "ar": {
        "@": "في",
        "#": "رقم",
        "%": "بالمائة",
        "&": "و",
        "+": "زائد",
        "=": "يساوي",
        "_": "شرطة سفلية",
    },
}

# --------------------------
# Arabic currency support via num2words + Najdi pass
# --------------------------

SUPPORTED_AR_CURRENCY_CODES = {"SR", "EGP", "KWD", "TND"}
SYMBOL_TO_AR_CODE = {
    "ر.س": "SR",
    "SAR": "SR",
    "$SR": "SR",
    "ج.م": "EGP",
    "EGP": "EGP",
    "د.ك": "KWD",
    "KWD": "KWD",
    "د.ت": "TND",
    "TND": "TND",
}

# Morphological forms for unsupported Arabic currencies (singular, dual, plural, singular_formal)
AR_UNITS_FORMS = {
    "د.إ": ("درهم", "درهمين", "دراهم", "درهم"),
    "$": ("دولار", "دولارين", "دولارات", "دولار"),
    "€": ("يورو", "يورو", "يورو", "يورو"),  # indeclinable in practice
    "£": ("جنيه", "جنيهين", "جنيهات", "جنيه"),
    "₹": ("روبية", "روبيتين", "روبيات", "روبية"),
}
AR_SUB_FORMS = {
    "د.إ": ("فلس", "فلسين", "فلوس", "فلس"),
    "$": ("سنت", "سنتين", "سنتات", "سنت"),
    "€": ("سنت", "سنتين", "سنتات", "سنت"),
    "£": ("بنس", "بنسين", "بنسات", "بنس"),
    "₹": ("بيسة", "بيستين", "بيسات", "بيسة"),  # (kept as-is to match your earlier mapping)
}


def _choose_ar_unit(n: int, forms: tuple[str, str, str, str]) -> str:
    n_mod = n % 100
    if n == 1:
        return forms[0]
    if n == 2:
        return forms[1]
    if 3 <= n_mod <= 10:
        return forms[2]
    return forms[3]


def apply_arabic_dialect(text: str, dialect: str) -> str:
    """
    Apply Arabic dialect-specific transformations to MSA text.

    Args:
        text: MSA Arabic text to transform
        dialect: Dialect name (case-insensitive)

    Returns:
        Dialect-transformed text

    Supported Dialects:
        "najdi": Najdi Saudi dialect transformations
        Future: "hijazi", "gulf", "levantine", etc.
    """
    dialect_lower = dialect.lower() if dialect else ""

    if dialect_lower == "najdi":
        return _najdiize_ar(text)
    # Future: Add more dialects here
    # elif dialect_lower == "hijazi":
    #     return _hijazize_ar(text)
    # elif dialect_lower in ["gulf", "khaleeji"]:
    #     return _gulfize_ar(text)
    # elif dialect_lower in ["levantine", "shami"]:
    #     return _levantinize_ar(text)

    # Unknown dialect - return unchanged
    return text


def _najdiize_ar(text: str) -> str:
    """Convert MSA number text to Najdi pronunciation."""
    # Tens → -ين
    text = (
        text.replace("عشرون", "عشرين")
        .replace("ثلاثون", "ثلاثين")
        .replace("أربعون", "أربعين")
        .replace("خمسون", "خمسين")
        .replace("ستون", "ستين")
        .replace("سبعون", "سبعين")
        .replace("ثمانون", "ثمانين")
        .replace("تسعون", "تسعين")
    )
    # Duals → -ين
    text = (
        text.replace("ريالان", "ريالين")
        .replace("درهمان", "درهمين")
        .replace("جنيهان", "جنيهين")
        .replace("ديناران", "دينارين")
        .replace("هللتان", "هللتين")
        .replace("قرشان", "قرشين")
        .replace("فلسان", "فلسين")
    )
    # Optional colloquial hundreds
    text = text.replace("مائة", "مية").replace("مئتان", "ميتين")
    # Remove bookish tanwīn
    text = (
        text.replace("ريالاً", "ريال")
        .replace("درهماً", "درهم")
        .replace("ديناراً", "دينار")
        .replace("جنيهاً", "جنيه")
        .replace("اً", "")
    )
    return " ".join(text.split())


def my_num2words(
    n,
    lang,
    use_currency: bool = False,
    currency_code: Optional[str] = None,
    dialect: Optional[str] = None,
):
    """Wrapper with Arabic currency (via num2words) + Najdi post-processing."""
    # Arabic currency via num2words public API
    if lang == "ar" and use_currency and currency_code:
        code = currency_code if currency_code in SUPPORTED_AR_CURRENCY_CODES else "SR"
        out = main_num2words(float(n), lang="ar", to="currency", currency=code)
        if dialect:
            out = apply_arabic_dialect(out, dialect)
        return out

    # Arabic decimals → "فاصلة" with smart handling
    if lang == "ar" and (isinstance(n, float) or (isinstance(n, str) and "." in str(n))):
        if isinstance(n, str):
            # String input preserves trailing zeros
            parts = n.split(".")
            integer_part = int(parts[0])
            frac_str = parts[1]
        else:
            # Float input (legacy)
            integer_part = int(n)
            frac_str = str(n).split(".", 1)[1] if "." in str(n) else ""

        # Check if decimal part is all zeros
        if not frac_str or frac_str.strip("0") == "":
            return main_num2words(integer_part, lang="ar")

        int_words = main_num2words(integer_part, lang="ar")

        # Smart handling for 2-digit decimals
        if len(frac_str) == 2:
            if frac_str.endswith("0") and frac_str[0] != "0":
                # .40, .50, .60, .70, .80, .90 → treat as whole tens
                tens_value = int(frac_str[0]) * 10  # 4 -> 40
                frac_words = main_num2words(tens_value, lang="ar")
            elif frac_str[0] == "0":
                # .04, .05, .07 etc. → "zero X"
                frac_words = (
                    f"{main_num2words(0, lang='ar')} {main_num2words(int(frac_str[1]), lang='ar')}"
                )
            else:
                # .34, .56, .78 etc. → treat as whole number (34, 56, 78)
                frac_number = int(frac_str)
                frac_words = main_num2words(frac_number, lang="ar")
        else:
            # For other lengths (.123, .5, etc.) → individual digits
            frac_str = frac_str.rstrip("0")
            if not frac_str:
                return main_num2words(integer_part, lang="ar")
            frac_words = " ".join(main_num2words(int(d), lang="ar") for d in frac_str)

        out = f"{int_words} فاصلة {frac_words}"
        if dialect:
            out = apply_arabic_dialect(out, dialect)
        return out

    if isinstance(n, float) and lang in NUM2WORDS_SUPPORTED_LANGUAGES:
        integer_part = int(n)
        frac_str = str(n).split(".", 1)[1] if "." in str(n) else ""
        if not frac_str or not frac_str.strip("0"):
            return indic_num2words(integer_part, lang=lang).replace(",", "")
        frac_str = frac_str.rstrip("0")
        int_words = indic_num2words(integer_part, lang=lang)
        frac_words = " ".join(indic_num2words(int(d), lang=lang) for d in frac_str)
        decimal_word = "point"
        return f"{int_words} {decimal_word} {frac_words}".replace(",", "")

    # Fallbacks
    if lang == "ar":
        out = main_num2words(n, lang="ar").replace(",", "")
        if dialect:
            out = apply_arabic_dialect(out, dialect)
        return out
    else:
        # Convert float to int for indic_num2words which only accepts integers
        return indic_num2words(int(n), lang=lang).replace(",", "")


# --------------------------
# Formatter
# --------------------------


def format_tts_text(text: str, lang_code: str = "en-IN", dialect: Optional[str] = None) -> str:
    """Format text for TTS with robust number, currency, date/time, and symbol handling.

    Args:
        text: Input text to format
        lang_code: Language code (e.g., "ar-SA", "en-US", "hi-IN")
        dialect: Optional dialect specification (e.g., "najdi", "hijazi", "gulf")
                 If None, uses standard/MSA forms for the language

    Returns:
        Formatted text optimized for TTS pronunciation

    Supported Dialects:
        Arabic: "najdi" - Uses Najdi pronunciation patterns (-ين endings, مية vs مائة, etc.)
        Future: Can be extended for other Arabic dialects or languages
    """
    # Handle empty or whitespace-only text
    if not text or not text.strip():
        return ""
    
    try:
        lang = lang_code[0:2]

        # Handle Arabic using num2words (which supports 'ar') even though it's not in NUM2WORDS_SUPPORTED_LANGUAGES
        if lang == "ar":
            # Arabic is supported by num2words but not indic-num2words
            pass
        elif lang not in NUM2WORDS_SUPPORTED_LANGUAGES:
            return text

        # Language auto-detect for hi/en
        if lang in ["hi", "en"]:
            lang = "hi" if is_hindi(text) else "en"

        symbols = SYMBOL_TRANSLATIONS.get(lang, SYMBOL_TRANSLATIONS["en"])
        month_names = MONTH_NAMES.get(lang, MONTH_NAMES["en"])

        # Normalize dashes
        text = re.sub(r"[―–—]", "-", text)

        # Currency replacement
        def replace_currency(match):
            symbol = match.group(1)
            amount_str = match.group(2).replace(",", "")
            scale = (match.group(3) or "").lower()

            # Compute numeric value with optional scale
            val = Decimal(amount_str)
            if scale == "k":
                val *= 1_000
            elif scale == "m":
                val *= 1_000_000
            elif scale in ("lakh", "lakhs"):
                val *= 100_000
            elif scale in ("crore", "crores"):
                val *= 10_000_000

            # Arabic + supported currencies via num2words(currency)
            if lang == "ar" and symbol in SYMBOL_TO_AR_CODE:
                code = SYMBOL_TO_AR_CODE[symbol]
                return my_num2words(
                    float(val), "ar", use_currency=True, currency_code=code, dialect=dialect
                )

            # Arabic + unsupported currencies → manual morphology + dialect numbers
            if lang == "ar" and symbol in AR_UNITS_FORMS:
                q = val.quantize(Decimal("0.01"))
                int_part = int(q)
                frac_num = int((q - int_part) * 100)

                # integer side
                int_words = my_num2words(int_part, "ar", dialect=dialect)
                unit_word = _choose_ar_unit(
                    int_part if int_part != 0 else 1, AR_UNITS_FORMS[symbol]
                )
                result = f"{int_words} {unit_word}"

                # fractional side
                if frac_num > 0:
                    frac_words = my_num2words(frac_num, "ar", dialect=dialect)
                    sub_unit = _choose_ar_unit(frac_num, AR_SUB_FORMS[symbol])
                    result += f" و {frac_words} {sub_unit}"

                return result

            # Non-Arabic (en/hi etc.)
            units = CURRENCY_UNITS.get(lang, CURRENCY_UNITS["en"]).get(symbol)
            if not units:
                return match.group(0)  # unknown symbol, leave as-is

            q = val.quantize(Decimal("0.01"))
            int_part = int(q)
            frac_num = int((q - int_part) * 100)

            int_words = my_num2words(int_part, lang)
            result = f"{int_words} {units[0]}"
            if frac_num > 0:
                frac_words = my_num2words(frac_num, lang)
                result += f" {frac_words} {units[1]}"
            return result

        # Western currency symbols
        text = re.sub(
            r"(\$|₹|€|£)\s*(\d+(?:[\d,.]*)?)\s*(lakhs?|crores?|k|m)?\b",
            replace_currency,
            text,
        )
        # Arabic currency symbols (SR/EGP/KWD/TND/AED)
        text = re.sub(
            r"(ر\.س|د\.إ|ج\.م|د\.ك|د\.ت)\s*(\d+(?:[\d,.]*)?)\s*(lakhs?|crores?|k|m)?\b",
            replace_currency,
            text,
        )

        # Phone numbers (keep your earlier logic)
        repetition_terms = {"en": ["double", "triple"]}.get(lang, ["double", "triple"])

        def partition_run(count):
            groups = []
            while count > 0:
                if count == 4:
                    groups.extend([2, 2])
                    count = 0
                elif count >= 3:
                    groups.append(3)
                    count -= 3
                elif count == 2:
                    groups.append(2)
                    count -= 2
                else:
                    groups.append(1)
                    count -= 1
            return groups

        def process_phone(number):
            result = []
            i = 0
            while i < len(number):
                current = number[i]
                run_length = 1
                j = i + 1
                if lang == "en":
                    while j < len(number) and number[j] == current:
                        run_length += 1
                        j += 1
                if run_length > 1:
                    for group in partition_run(run_length):
                        digit_word = my_num2words(int(current), lang, dialect=dialect)
                        if group == 2:
                            result.append(f"{repetition_terms[0]} {digit_word}")
                        elif group == 3:
                            result.append(f"{repetition_terms[1]} {digit_word}")
                        else:
                            result.append(digit_word)
                else:
                    result.append(my_num2words(int(current), lang, dialect=dialect))
                i = j
            return " ".join(result)

        text = re.sub(
            r"(\+\d{1,3}[- ]?)?(\d{10})",
            lambda m: process_phone(re.sub(r"\D", "", m.group(2)[-10:]))
            if m.group(1) and m.group(1).startswith("+91")
            else process_phone(re.sub(r"\D", "", m.group(0))),
            text,
        )

        # Symbols (@, #, etc.)
        text = re.sub(r"([@#%&=+_=])", lambda m: f" {symbols[m.group(1)]} ", text)

        # Dates
        current_year = 2025

        def replace_date_yyyy_mm_dd(m):
            y, mo, d = m.group(1), m.group(2), m.group(3)
            day_word = my_num2words(int(d), lang, dialect=dialect)
            year_word = my_num2words(int(y), lang, dialect=dialect)
            if mo.isdigit():
                idx = int(mo)
                month_word = month_names[idx - 1] if 1 <= idx <= 12 else mo
            else:
                month_word = mo
            return (
                f"{day_word} {month_word}"
                if int(y) == current_year
                else f"{day_word} {month_word}, {year_word}"
            )

        text = re.sub(r"\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b", replace_date_yyyy_mm_dd, text)

        def replace_date_extended(m):
            d, mo, y = m.group(1), m.group(2), m.group(4)
            day_word = my_num2words(int(d), lang, dialect=dialect)
            if mo.isdigit():
                idx = int(mo)
                month_word = month_names[idx - 1] if 1 <= idx <= 12 else mo
            else:
                candidate = mo.lower()
                month_word = next(
                    (name for name in month_names if name.lower().startswith(candidate)), mo
                )
            if y:
                full_year = (
                    int(y)
                    if len(y) == 4
                    else (2000 + int(y) if int(y) <= current_year % 100 else 1900 + int(y))
                )
                year_word = my_num2words(full_year, lang, dialect=dialect)
                return (
                    f"{day_word} {month_word}"
                    if full_year == current_year
                    else f"{day_word} {month_word}, {year_word}"
                )
            return f"{day_word} {month_word}"

        text = re.sub(
            r"\b(\d{1,2})[-/](\d{1,2}|[A-Za-z]+)([-/](\d{2,4}))?\b", replace_date_extended, text
        )

        # Time
        text = re.sub(
            r"(\d{1,2}):(\d{2})(?:\s*([AaPp][Mm]))?",
            lambda m: f"{my_num2words(int(m.group(1)) % 12 or 12, lang, dialect=dialect)} "
            f"{'' if int(m.group(2)) == 0 else my_num2words(int(m.group(2)), lang, dialect=dialect)} "
            f"{m.group(3) or ('PM' if int(m.group(1)) >= 12 else 'AM')}",
            text,
        )

        # URLs/emails
        text = re.sub(
            r"\b(https?://\S+|www\.\S+)\b",
            lambda m: " ".join(symbols.get(c, c) for c in m.group().lower()),
            text,
        )
        text = re.sub(
            r"\b(\w+@\w+\.\w+)\b",
            lambda m: " ".join(symbols.get(c, c) for c in m.group().lower()),
            text,
        )

        # Numbers (decimals first so we don't double-convert)
        def replace_decimal(match):
            decimal_str = match.group()
            if lang == "ar":
                # For Arabic, pass the original string to preserve trailing zeros
                return my_num2words(decimal_str, lang, dialect=dialect)
            else:
                # Non-Arabic: use float conversion
                return my_num2words(float(decimal_str), lang, dialect=dialect)

        text = re.sub(r"\b(\d+\.\d+)\b", replace_decimal, text)
        text = re.sub(
            r"\b\d{1,3}(,\d{2,3})+(?!\d)\b",
            lambda m: my_num2words(int(m.group().replace(",", "")), lang, dialect=dialect),
            text,
        )
        text = re.sub(
            r"\b(\d+)(st|nd|rd|th)\b",
            lambda m: my_num2words(int(m.group(1)), lang, dialect=dialect),
            text,
        )
        text = re.sub(
            r"\b(\d{1,})\b", lambda m: my_num2words(int(m.group()), lang, dialect=dialect), text
        )

        return " ".join(text.split())

    except Exception as e:
        # Log the error but return original text to prevent flow breakage
        logger.error(f"Error in format_tts_text: {e}")
        return text


# --------------------------
# TTS service initialization
# --------------------------


def initialize_tts_service(
    tts_provider: str,
    language: str,
    voice: str,
    text_formatter: Optional[Callable[[str, str], str]] = None,
    **kwargs,
) -> TTSService:
    """Initializes and returns a TTSService instance based on the given configuration.

    Args:
        tts_provider: The TTS provider to use (e.g., "azure", "elevenlabs").
        language: The language code (e.g., "en-US").
        voice: The voice ID or name.
        text_formatter: Optional text processing function that takes (text, lang_code) and returns formatted text.
        **kwargs: Additional keyword arguments to pass to the TTSService constructor.

    Returns:
        A configured TTSService instance.
    """
    if tts_provider == "azure":
        try:
            primary_language_enum = Language(language)
        except ValueError:
            logger.warning(f"Invalid primary language code '{language}', defaulting to en-IN.")
            primary_language_enum = Language.EN_IN
            language = "en-IN"

        additional_langs = None
        additional_voices = None

        if language.startswith("te"):
            additional_langs = ["en-IN"]
            additional_voices = {"en-IN": voice}
            logger.info(
                "Primary language is Telugu (te-IN), adding en-IN as additional TTS language."
            )
        # Note: We pass the primary language enum and voice directly.
        # Create InputParams specifically for non-language SSML settings like rate.
        voice_config = kwargs.get("voice_config", {})
        speed_config = (
            voice_config.get("speed")
            if hasattr(voice_config, "get")
            else getattr(voice_config, "speed", None)
        )
        azure_speed = str(speed_config) if speed_config is not None else "1.25"
        input_params = AzureTTSService.InputParams(rate=azure_speed)
        tts = AzureTTSService(
            api_key=kwargs.get("azure_api_key"),
            region=kwargs.get("azure_region"),
            params=input_params,
            language=primary_language_enum,
            voice=voice,
            additional_languages=additional_langs,
            additional_voices=additional_voices,
            text_formatter=text_formatter,
        )
    elif tts_provider == "elevenlabs":
        tts_model = kwargs.get("tts_model", "eleven_turbo_v2_5")
        voice_config = kwargs.get("voice_config", {})
        speed_config = (
            voice_config.get("speed")
            if hasattr(voice_config, "get")
            else getattr(voice_config, "speed", None)
        )
        try:
            elevenlabs_speed = float(speed_config) if speed_config is not None else 1.0
        except ValueError:
            logger.warning(
                f"Invalid speed value '{speed_config}' for ElevenLabs, using default 1.0."
            )
            elevenlabs_speed = 1.0

        input_params = ElevenLabsTTSService.InputParams(
            language=Language(language),
            speed=elevenlabs_speed,
            stability=voice_config.get("stability", None)
            if hasattr(voice_config, "get")
            else getattr(voice_config, "stability", None),
            similarity_boost=voice_config.get("similarity_boost", None)
            if hasattr(voice_config, "get")
            else getattr(voice_config, "similarity_boost", None),
            style=voice_config.get("style", None)
            if hasattr(voice_config, "get")
            else getattr(voice_config, "style", None),
        )
        tts = ElevenLabsTTSService(
            api_key=kwargs.get("elevenlabs_api_key"),
            voice_id=voice,
            params=input_params,
            model=tts_model,
            sample_rate=16000,
            text_formatter=text_formatter,
        )
    elif tts_provider == "google":
        voice_lower = voice.lower()
        is_chirp_or_journey = ("chirp" in voice_lower) or ("journey" in voice_lower)
        voice_config = kwargs.get("voice_config", {})
        speed_val = (
            voice_config.get("speed", "1.0")
            if hasattr(voice_config, "get")
            else getattr(voice_config, "speed", "1.0")
        )
        google_speed = str(speed_val)

        if is_chirp_or_journey:
            voice = f"{str(language_to_google_tts_language(Language(language))).lower()}-{str(voice).lower()}"
            input_params = GoogleTTSService.InputParams(
                language=Language(language), rate=float(google_speed)
            )
            tts = GoogleTTSService(
                credentials_path=kwargs.get("google_credentials_path"),
                voice_id=voice,
                params=input_params,
                text_formatter=text_formatter,
                voice_config=kwargs.get("voice_config", {}),
            )
        else:
            input_params = GoogleHttpTTSService.InputParams(
                language=Language(language), rate=google_speed
            )
            tts = GoogleHttpTTSService(
                credentials_path=kwargs.get("google_credentials_path"),
                voice_id=voice,
                params=input_params,
                text_formatter=text_formatter,
            )
    elif tts_provider == "deepgram":
        tts = DeepgramTTSService(
            api_key=kwargs.get("deepgram_api_key"),
            voice=voice,
            text_formatter=text_formatter,
        )
    elif tts_provider == "cartesia":
        voice_config = kwargs.get("voice_config", {})
        speed_config = (
            voice_config.get("speed")
            if hasattr(voice_config, "get")
            else getattr(voice_config, "speed", None)
        )
        cartesia_speed = str(speed_config) if speed_config is not None else "1.0"
        input_params = CartesiaTTSService.InputParams(
            language=Language(language), speed=cartesia_speed
        )
        tts_model = kwargs.get("tts_model", "sonic")
        if language == "hi":
            tts = CartesiaHttpTTSService(
                api_key=kwargs.get("cartesia_api_key"),
                voice_id=voice,
                params=input_params,
                model=tts_model,
                text_formatter=text_formatter,
            )
        else:
            tts = CartesiaTTSService(
                api_key=kwargs.get("cartesia_api_key"),
                voice_id=voice,
                params=input_params,
                model=tts_model,
                text_formatter=text_formatter,
            )
    elif tts_provider == "sarvam":
        # Sarvam expects base language codes (kn, hi, etc.) not locale-specific ones (kn-IN, hi-IN)
        sarvam_language = language.split("-")[0] if "-" in language else language
        input_params = SarvamTTSService.InputParams(language=Language(sarvam_language))
        tts = SarvamTTSService(
            api_key=api_config.SARVAM_API_KEY,
            params=input_params,
            text_formatter=text_formatter,
            voice_id=voice,
        )
    else:
        raise ValueError(f"Unsupported TTS provider: {tts_provider}")

    return tts


# --------------------------
# TTS cache + playback
# --------------------------


async def say_with_cache(
    task: PipelineTask,
    tts_service,
    redis_client: redis.Redis,
    use_cache: bool,
    text: str,
    transport: Optional[FastAPIWebsocketTransport],
    logger,
):
    key = f"intro_tts_{hashlib.sha256(text.encode()).hexdigest()}"
    if use_cache and redis_client:
        try:
            cached_mp3 = await redis_client.get(key)
            if cached_mp3 and len(cached_mp3) > 4:
                logger.info(f"TTS cache hit for {key}")

                # Decode MP3
                seg = AudioSegment.from_file(io.BytesIO(cached_mp3), format="mp3")
                pcm_int16 = np.array(seg.get_array_of_samples(), dtype=np.int16)

                # Stereo → mono
                if seg.channels > 1:
                    pcm_int16 = pcm_int16.reshape(-1, seg.channels).mean(axis=1).astype(np.int16)

                # Resample to 8kHz if needed
                sample_rate = seg.frame_rate
                if sample_rate != 8_000:
                    resampler = SOXRAudioResampler()
                    pcm_bytes = pcm_int16.tobytes()
                    resampled_bytes = await resampler.resample(pcm_bytes, sample_rate, 8_000)
                    pcm_int16 = np.frombuffer(resampled_bytes, dtype=np.int16)

                # If a transport is provided, stream; otherwise just return
                if transport is not None:
                    block_size = 160  # 20ms @ 8kHz mono
                    for start in range(0, len(pcm_int16), block_size):
                        chunk = pcm_int16[start : start + block_size]
                        if not chunk.size:
                            break
                        frame = TTSAudioRawFrame(
                            audio=chunk.tobytes(), sample_rate=8_000, num_channels=1
                        )
                        await transport.output().send_audio(frame)

                logger.info("Finished cached playback.")
                return True
            else:
                logger.info(f"TTS cache miss for {key}")
        except Exception as e:
            logger.error(f"Redis/decode error for {key}: {e}")

    logger.info("Using live TTS service (via pipeline).")
    if tts_service is not None:
        print("here is the text", text)
        await task.queue_frame(TTSSpeakFrame(text))
    return False


async def cache_tts_mp3(
    redis_client: redis.Redis,
    text: str,
    mp3_bytes: bytes,
    ttl_seconds: int = 10_000,
) -> str:
    key = f"intro_tts_{hashlib.sha256(text.encode()).hexdigest()}"
    try:
        await redis_client.set(name=key, value=mp3_bytes, ex=ttl_seconds)
        logger.info("Cached TTS audio under {} (TTL={} s)".format(key, ttl_seconds))
    except Exception as exc:
        logger.error("Failed to cache TTS audio: {}".format(exc))
    return key


async def put_file_on_redis(redis_client, text: str, filename: str):
    mp3_bytes = Path(filename).read_bytes()
    return await cache_tts_mp3(redis_client, text, mp3_bytes)


async def get_tts_file_from_redis(redis_client: redis.Redis, text: str, output_dir: str = "."):
    """Retrieves MP3 bytes from Redis and saves them to a file."""
    key = f"intro_tts_{hashlib.sha256(text.encode()).hexdigest()}"
    mp3_bytes = await redis_client.get(key)

    if mp3_bytes:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        filename = output_path / f"{key}.mp3"
        try:
            with open(filename, "wb") as f:
                f.write(mp3_bytes)
            print(f"Successfully saved MP3 to: {filename}")
            return str(filename)
        except Exception as e:
            print(f"Error saving MP3 file {filename}: {e}")
            return None
    else:
        print(f"No data found in Redis for key: {key}")
        return None


# --------------------------
# Quick self-test (optional)
# --------------------------

# if __name__ == "__main__":
#     print(
#         format_tts_text(
#             "यह CROCS का cash on delivery order है जिसमें Getaway Printed Strappy Chalk Women Flip-7 है, और order value 5745.00 रुपए है। 50.03 and  50.30",
#             "hi",
#         )
#     )
#     print(format_tts_text("Hello, how are you? ₹5.6 lakhs $500k 500000 "))
#     print(format_tts_text("9986576544, 998657654"))
#     print(format_tts_text("Hello, how are you? 04/08/2026 04-08-2026 2026-08-04", "en"))
#     print(format_tts_text("आप कैसे है  आप कैसे है  आप कैसे है 2026 04/08/2026 ₹10 lakhs ₹10 crores", "hi"))
#     print(format_tts_text("Hello, how are you? 2026", "en"))
#     print(format_tts_text("Hello, how are you? 2026", "te-IN"))
#     print(
#         format_tts_text('إذا في أي أسئلة أو مواضيع حابب تعرف عنها بخصوص "ConVox CCS 4.0."', "ar-AE")
#     )
#     print(format_tts_text("إذا في أي أسئلة أو مواضيع حابب تعرف عنها 2026-08-04 ", "ar-AE"))
#     print(
#         format_tts_text("إذا في أي أسئلة أو مواضيع حابب تعرف عنها 2026-08-04 04-08-2026 ", "ar-AE")
#     )

#     print("=== Najdi vs MSA Comparison ===\n")

#     tests = [
#         ("ر.س 2", "ar-SA"),
#         ("ر.س 20", "ar-SA"),
#         ("ر.س 100", "ar-SA"),
#         ("ر.س 103", "ar-SA"),
#         ("ر.س 250.50", "ar-SA"),
#     ]

#     for amount, locale in tests:
#         msa = format_tts_text(amount, locale, dialect=None)  # Standard/MSA
#         najdi = format_tts_text(amount, locale, dialect="najdi")  # Najdi dialect
#         print(f"{amount}:\n  MSA:   {msa}\n  Najdi: {najdi}\n")

#     print("=== Unsupported (custom) ===\n")
#     for amount, locale in [("د.إ 100", "ar-AE"), ("$200", "ar-SA"), ("د.إ 1.5k", "ar-AE")]:
#         print(f"{amount}: {format_tts_text(amount, locale, dialect='najdi')}")
# print(
#     format_tts_text(
#         "9876.98 ريال،",
#         "ar-SA",
#     )
# )
# Test Arabic decimal pronunciation
# print("=== Arabic Decimal Tests ===")
# print("250.40:", format_tts_text("250.40", "ar-SA", dialect="najdi"))  # Should be "forty"
# print("250.04:", format_tts_text("250.04", "ar-SA", dialect="najdi"))  # Should be "zero four"
# print("250.05:", format_tts_text("250.05", "ar-SA", dialect="najdi"))  # Should be "zero five"
# print("250.50:", format_tts_text("250.50", "ar-SA", dialect="najdi"))  # Should be "fifty"
# print("250.90:", format_tts_text("250.90", "ar-SA", dialect="najdi"))  # Should be "ninety"
# print("250.07:", format_tts_text("250.07", "ar-SA", dialect="najdi"))  # Should be "zero seven"
# print("250.34:", format_tts_text("250.34", "ar-SA", dialect="najdi"))  # Should be "thirty four"
# print("250.56:", format_tts_text("250.56", "ar-SA", dialect="najdi"))  # Should be "fifty six"
# print("250.00:", format_tts_text("250.00", "ar-SA", dialect="najdi"))  # Should ignore decimal part
# print("250.10:", format_tts_text("250.10", "ar-SA", dialect="najdi"))

# # Test direct my_num2words calls
# print("\n=== Direct my_num2words Tests ===")
# print("String '250.34':", format_tts_text("250.34", "ar", dialect="najdi"))
# print("String '250.40':", format_tts_text("250.40", "ar", dialect="najdi"))
# print("String '250.00':", format_tts_text("250.00", "ar", dialect="najdi"))
# print(
#     format_tts_text(
#         "31-07-2025",
#         "ar-SA",
#         dialect="najdi",
#     )
# )
# print(
#     format_tts_text(
#         "31-07-2025",
#         "ar-SA",
#     )
# )
# print(format_tts_text("0,5,0,0,0", "en"))
# print(format_tts_text("Rs. 2026.05 Rs. 2026.50", "en"))
# print(
#     format_tts_text(
#         "ريال 250.05 ريال",
#         "ar-SA",
#         dialect="najdi",
#     )
# )

# print(format_tts_text("Hello, 1.20 how are you? ₹5.6 lakhs $500k 500000 "))
# print(format_tts_text("9986576544, 998657654"))
