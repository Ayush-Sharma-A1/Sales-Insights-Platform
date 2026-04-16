"""
Configuration settings for Sentiment & Sales Insights application.
Manages all environment variables and application configurations.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class AppConfig:
    """Application configuration management"""
    
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    MODELS_DIR: Path = PROJECT_ROOT / "src" / "models"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    
    # Streamlit config
    PAGE_TITLE: str = "Sentiment & Sales Insights Platform"
    PAGE_LAYOUT: str = "wide"
    INITIAL_SIDEBAR_STATE: str = "expanded"
    
    # Audio Processing
    ASR_ENGINE: str = "whisper"  # Options: whisper, vosk
    WHISPER_MODEL_SIZE: str = "base"  # tiny, base, small, medium
    VOSK_MODEL_DIR: Optional[str] = None
    
    # Sentiment Analysis
    USE_PRETRAINED_SENTIMENT: bool = False
    PRETRAINED_MODEL: str = "distilbert-base-uncased-finetuned-sst-2-english"
    SKLEARN_TEST_SIZE: float = 0.2
    SKLEARN_MAX_ITER: int = 200
    
    # TF-IDF Config
    TFIDF_NGRAM_RANGE: tuple = (1, 2)
    TFIDF_MIN_DF: int = 2
    TFIDF_MAX_FEATURES: int = 50000
    
    # Feature Extraction
    TOP_KEYWORDS_COUNT: int = 20
    MAX_TEXT_LENGTH: int = 4096
    
    # Thresholds
    NEGATIVE_SENTIMENT_THRESHOLD: float = 0.35
    NEGATIVE_RATIO_ALERT: float = 0.40
    
    # File uploads
    ALLOWED_AUDIO_FORMATS: tuple = ("mp3", "wav", "m4a", "aac", "flac")
    ALLOWED_CSV_FORMATS: tuple = ("csv",)
    MAX_FILE_SIZE_MB: int = 500
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Cache settings
    STREAMLIT_CACHE_TTL: int = 3600  # seconds
    
    # Environment
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENV: str = os.getenv("ENV", "development")

    def __post_init__(self):
        """Create necessary directories"""
        self.LOGS_DIR.mkdir(exist_ok=True)
        self.DATA_DIR.mkdir(exist_ok=True)

# Global config instance
config = AppConfig()
