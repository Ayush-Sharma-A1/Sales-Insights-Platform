"""
Audio transcription services using Whisper and Vosk engines.
Handles audio file processing and speech-to-text conversion.
"""

import os
import tempfile
import wave
from typing import Optional

import streamlit as st

from config.settings import config
from src.utils.logger import Logger

log = Logger.get_logger(__name__)

# Optional imports
try:
    import whisper
except ImportError:
    whisper = None

try:
    from vosk import Model as VoskModel, KaldiRecognizer
except ImportError:
    VoskModel = None
    KaldiRecognizer = None


class TranscriptionService:
    """Handles audio transcription from multiple engines"""
    
    @staticmethod
    @st.cache_resource(show_spinner=False)
    def load_whisper_model(model_size: str = "base"):
        """
        Load Whisper model from OpenAI.
        
        Args:
            model_size: Model size (tiny, base, small, medium)
            
        Returns:
            Loaded Whisper model
            
        Raises:
            RuntimeError: If Whisper not installed or invalid model size
        """
        if whisper is None:
            raise RuntimeError(
                "Whisper not installed. Install with: "
                "pip install openai-whisper && ensure ffmpeg is available"
            )
        
        valid_sizes = ["tiny", "base", "small", "medium"]
        if model_size not in valid_sizes:
            raise ValueError(f"Invalid model size. Choose from: {valid_sizes}")
        
        log.info(f"Loading Whisper model: {model_size}")
        return whisper.load_model(model_size)
    
    @staticmethod
    @st.cache_resource(show_spinner=False)
    def load_vosk_model(model_dir: str):
        """
        Load Vosk model for offline speech recognition.
        
        Args:
            model_dir: Path to unzipped Vosk model
            
        Returns:
            Loaded Vosk model
            
        Raises:
            RuntimeError: If Vosk not installed or invalid directory
        """
        if not model_dir or not os.path.isdir(model_dir):
            raise RuntimeError("Valid Vosk model directory not provided.")
        
        if VoskModel is None:
            raise RuntimeError("Vosk not installed. Install with: pip install vosk")
        
        log.info(f"Loading Vosk model from: {model_dir}")
        return VoskModel(model_dir)
    
    @staticmethod
    def transcribe_whisper(audio_bytes: bytes, model, filename: str) -> str:
        """
        Transcribe audio using OpenAI Whisper.
        
        Args:
            audio_bytes: Audio file bytes
            model: Loaded Whisper model
            filename: Original filename
            
        Returns:
            Transcribed text
        """
        with tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=os.path.splitext(filename)[1] or ".wav"
        ) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            path = tmp.name
        
        try:
            log.info(f"Transcribing with Whisper: {filename}")
            result = model.transcribe(path)
            text = result.get("text", "").strip()
            log.info(f"Transcription complete: {len(text)} characters")
            return text
        except Exception as e:
            log.error(f"Whisper transcription failed: {e}")
            raise
        finally:
            try:
                os.remove(path)
            except Exception:
                pass
    
    @staticmethod
    def transcribe_vosk(audio_bytes: bytes, model, filename: str) -> str:
        """
        Transcribe audio using Vosk (offline).
        
        Args:
            audio_bytes: Audio file bytes (WAV PCM 16k mono expected)
            model: Loaded Vosk model
            filename: Original filename
            
        Returns:
            Transcribed text
        """
        if KaldiRecognizer is None:
            return "[Vosk] Library not available. Install vosk."
        
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(filename)[1] or ".wav"
        ) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            path = tmp.name
        
        try:
            if not path.lower().endswith('.wav'):
                return (
                    "[Vosk] Please upload WAV PCM audio (16kHz mono) "
                    "or use Whisper for auto-conversion."
                )
            
            log.info(f"Transcribing with Vosk: {filename}")
            wf = wave.open(path, "rb")
            
            # Validate WAV format
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
                return "[Vosk] WAV must be mono 16-bit PCM. Convert or use Whisper."
            
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)
            
            text_pieces = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    res = rec.Result()
                    text_pieces.append(res)
            
            final = rec.FinalResult()
            text_pieces.append(final)
            text = " ".join(text_pieces)
            
            log.info(f"Vosk transcription complete: {len(text)} characters")
            return text
            
        except Exception as e:
            log.error(f"Vosk transcription failed: {e}")
            return f"[Vosk Error] {e}"
        finally:
            try:
                os.remove(path)
            except Exception:
                pass
