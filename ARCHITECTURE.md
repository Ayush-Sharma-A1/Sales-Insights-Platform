# System Architecture & Design Documentation

## Overview

The Sentiment & Sales Insights Platform is built on a modular, service-oriented architecture designed for scalability, maintainability, and extensibility.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend (Web UI)                  │
│  - File Upload  - Data Mapping  - Visualizations  - Export      │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼─────────────┐      ┌──────────▼─────────────┐
│   Data Processing   │      │   Configuration Layer  │
│                     │      │                        │
│ - CSV Loading       │      │ - Settings Management  │
│ - Data Validation   │      │ - Environment Config   │
│ - Merging           │      │ - Cache Management     │
└───────┬─────────────┘      └──────────┬─────────────┘
        │                              │
        └──────────────┬───────────────┘
                       │
        ┌──────────────▼──────────────┐
        │   Service Layer             │
        │                             │
        ├─ Transcription Service ─────┤
        │  ├─ Whisper Integration    │
        │  └─ Vosk Integration       │
        │                             │
        ├─ Sentiment Analysis Service ┤
        │  ├─ Custom Model Training  │
        │  └─ Pretrained Pipelines   │
        │                             │
        ├─ Analytics Service ────────┤
        │  ├─ Sentiment Summaries    │
        │  ├─ Keyword Extraction     │
        │  ├─ Dimensional Analysis   │
        │  └─ Recommendations        │
        │                             │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │   Utility Layer             │
        │                             │
        │ - Logging & Monitoring      │
        │ - Error Handling            │
        │ - Data Validation           │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │   External ML Libraries     │
        │                             │
        │ - OpenAI Whisper            │
        │ - HuggingFace Transformers  │
        │ - Scikit-learn              │
        │ - Vosk                      │
        └─────────────────────────────┘
```

## Core Components

### 1. **Web Interface (Streamlit)**
**Purpose**: User-friendly interactive dashboard  
**Responsibilities**:
- File upload and validation
- Column mapping UI
- Real-time configuration
- Dashboard visualization
- Data export

**Key Features**:
- Responsive design
- Progress tracking
- Error messaging
- Caching for performance

### 2. **Configuration Layer** (`config/`)

**File**: `settings.py`

**Features**:
```python
@dataclass
class AppConfig:
    - PROJECT_ROOT: Base project directory
    - DATA_DIR: Storage for data
    - MODELS_DIR: Model artifacts
    - LOGS_DIR: Application logs
    - ASR_ENGINE: Whisper or Vosk selection
    - WHISPER_MODEL_SIZE: Model precision vs. speed tradeoff
    - PRETRAINED_MODEL: Which HF model to use
    - Thresholds: Sentiment detection limits
    - File constraints: Upload size, formats
    - Logging: Level, format, handlers
```

**Design Benefits**:
- Single source of truth for configuration
- Environment-specific overrides via .env
- Type-safe configuration with dataclass
- Auto-creates necessary directories

### 3. **Data Processing Layer** (`src/utils/`)

**Components**:

#### DataProcessor
```
Responsibilities:
├─ CSV Loading (with encoding detection)
├─ Date Parsing (flexible formats)
├─ DataFrame Construction (schema standardization)
├─ Data Merging (CRM + Transcripts)
└─ Keyword Matching (for analysis)
```

**Key Methods**:
- `load_csv()`: Handles multiple encodings
- `parse_date()`: Supports various date formats
- `build_dataframe()`: Creates standard schema
- `merge_transcripts()`: Intelligent joining on call_id

**Design Pattern**: Static utility class for testability

#### Logger
```
Responsibilities:
├─ Centralized logging configuration
├─ File + Console handlers
├─ Log level management
└─ Performance monitoring
```

### 4. **Service Layer** (`src/services/`)

#### Transcription Service
```python
TranscriptionService:
├─ load_whisper_model()         # Load model with caching
├─ load_vosk_model()             # Load offline model
├─ transcribe_whisper()          # Online transcription
└─ transcribe_vosk()             # Offline transcription
```

**Design Pattern**: Factory + Caching
- `@st.cache_resource`: Loads model once, reuses across runs
- Graceful error handling with fallbacks
- Supports multiple audio formats via ffmpeg

#### Sentiment Analysis Service
```python
SentimentAnalyzer:
├─ load_pretrained_pipeline()        # HuggingFace models
├─ train_custom_model()              # TF-IDF + LogisticRegression
├─ predict_sentiment_custom()        # Custom model inference
├─ predict_sentiment_pretrained()    # Pretrained inference
└─ get_model_metrics()               # Classification metrics
```

**ML Pipeline**:
```
Text Input
    │
    ├─→ [Check labels present?]
    │        ├─ Yes → [Train Custom Model]
    │        │           ├─ TF-IDF Vectorization
    │        │           ├─ LogisticRegression
    │        │           └─ 80-20 Train-Test Split
    │        │
    │        └─ No → [Load Pretrained Model]
    │                 └─ DistilBERT
    │
    └─→ [Inference]
         ├─ Get Predictions
         ├─ Get Confidence Scores
         └─ Return Results
```

**Vectorization Config**:
```python
TfidfVectorizer(
    ngram_range=(1, 2),      # Unigrams + Bigrams
    min_df=2,                 # Appear in ≥2 documents
    max_features=50000        # Keep top features
)
```

#### Analytics Service
```python
AnalyticsEngine:
├─ get_sentiment_summary()           # Overall statistics
├─ extract_top_keywords()            # TF-IDF based extraction
├─ analyze_by_dimension()            # Location, Stack, Year
├─ generate_recommendations()        # Rule-based insights
└─ get_monthly_trend()               # Time series analysis
```

**Recommendation System**:
```
Input: Analysis Results
    │
    ├─→ [Overall Sentiment Check]
    │   └─ IF negativity > 40% → Alert
    │
    ├─→ [Dimensional Analysis]
    │   ├─ Location-based → Specific actions
    │   ├─ Tech Stack → Stack-specific tips
    │   └─ Year Level → Cohort recommendations
    │
    ├─→ [Keyword Detection]
    │   ├─ Fee concerns → Payment options
    │   ├─ Timing issues → Schedule flexibility
    │   ├─ Support concerns → Mentorship programs
    │   └─ Career focus → Placement highlights
    │
    └─→ Output: Actionable Recommendations
```

## Data Flow

### Complete Analysis Pipeline

```
Step 1: INPUT
├─ CSV File (CRM data)
└─ Audio Files (Recordings)
    │
Step 2: DATA LOADING
├─ load_csv() → Auto-detect encoding
├─ Column mapping (flexible schema)
└─ Validation & cleaning
    │
Step 3: TRANSCRIPTION
├─ Choose engine (Whisper/Vosk)
├─ Batch process audio files
└─ Generate transcripts
    │
Step 4: DATA INTEGRATION
├─ Merge on call_id
├─ Combine remarks + transcript → combined_text
└─ Parse dates
    │
Step 5: SENTIMENT ANALYSIS
├─ Check for labeled data
├─ If labels available:
│   ├─ Train custom model (80-20 split)
│   └─ Cross-validate performance
├─ If no labels:
│   ├─ Load pretrained model
│   └─ Batch inference
└─ Store predictions + confidence
    │
Step 6: ANALYTICS
├─ Summary statistics
├─ Dimensional breakdown
├─ Keyword extraction (TF-IDF)
├─ Trend analysis (temporal)
└─ Generate recommendations
    │
Step 7: VISUALIZATION
├─ Sentiment distribution (Pie)
├─ Sentiment count (Bar)
├─ By dimension (Bar)
├─ Trends (Line)
└─ Keywords (Bar)
    │
Step 8: EXPORT
└─ Download CSV or JSON
```

## Design Patterns Used

### 1. **Factory Pattern**
```python
# TranscriptionService acts as factory
if asr_engine == "Whisper":
    model = TranscriptionService.load_whisper_model()
else:
    model = TranscriptionService.load_vosk_model()
```

### 2. **Strategy Pattern**
```python
# Sentiment analysis switches strategies
if has_labels:
    strategy = train_custom_model()
else:
    strategy = load_pretrained_pipeline()

predictions = strategy.predict(texts)
```

### 3. **Caching/Memoization**
```python
@st.cache_resource  # Model loaded once per session
def load_whisper_model(model_size):
    return whisper.load_model(model_size)
```

### 4. **Configuration Management**
```python
# Single source of truth
config = AppConfig()  # Global config instance
db.MODEL_SIZE = config.WHISPER_MODEL_SIZE
```

### 5. **Service Locator**
```python
# All services accessible from main app
transcription = TranscriptionService
sentiment = SentimentAnalyzer
analytics = AnalyticsEngine
```

## Database and Storage

### Current Implementation
- **CSV-based**: Direct CSV import/export
- **In-memory**: Processed data stored in pandas DataFrames
- **File-based**: Exports saved to local filesystem

### Future Enhancements
```python
# Proposed database layer
├─ PostgreSQL Integration
│   ├─ Store processed analysis results
│   ├─ Historical tracking
│   └─ Multi-user support
├─ Model Persistence
│   ├─ Save trained models
│   └─ Version control
└─ Audit Logging
    ├─ Track all analyses
    └─ User activity logging
```

## Performance Considerations

### Optimization Strategies

**1. Caching**
```python
@st.cache_resource  # Cache models (expensive)
@st.cache_data      # Cache processed data
```

**2. Batch Processing**
- Process multiple audio files simultaneously
- Vectorized operations with NumPy/Pandas

**3. Model Selection**
- Whisper "base" balances speed/accuracy
- DistilBERT is 40% faster than BERT
- TF-IDF is lightweight compared to deep learning

**4. Memory Management**
- Limit text length to 4096 tokens
- Stream large files
- Cleanup temporary files

### Benchmarks (approximate)

| Operation | Time | Memory |
|-----------|------|--------|
| Load CSV (10K rows) | 0.5s | 50MB |
| Transcribe 1 audio (Whisper, base) | 30-60s | 2GB |
| Train custom model (500 samples) | 2-5s | 100MB |
| Pretrained sentiment (10K texts) | 1-2m | 1GB |
| Generate recommendations | 1s | 10MB |

## Extensibility

### Adding New ASR Engines
```python
# In transcription.py
class TranscriptionService:
    @staticmethod
    def transcribe_google(audio_bytes, api_key):
        # Implement Google Cloud Speech-to-Text
        pass
```

### Adding New Models
```python
# In sentiment_analysis.py
class SentimentAnalyzer:
    @staticmethod
    def load_bert_model():
        # Implement BERT-large for higher accuracy
        pass
```

### Adding Database Support
```python
# New module: src/db/
class DatabaseManager:
    def save_analysis(self, df, metadata):
        # Save to PostgreSQL
        pass
    
    def load_historical_data(self, date_range):
        # Load previous analyses
        pass
```

## Error Handling Strategy

**Layered Approach**:
```
User Input (Validation)
    ↓
Data Loading (Encoding detection, fallback)
    ↓
ASR Pipeline (Graceful degradation)
    ↓
ML Inference (Exception handling)
    ↓
Analytics (Check data sufficiency)
    ↓
Logging (All errors recorded)
    ↓
User Feedback (Clear error messages)
```

## Security Considerations

1. **File Validation**
   - Check file types and sizes
   - Scan for malicious content (optional)

2. **Data Privacy**
   - Use Vosk for offline processing (no cloud)
   - Option to delete processed data

3. **Model Security**
   - Load models from trusted sources
   - Verify model signatures

4. **Access Control** (future)
   - Authentication/Authorization layer
   - Role-based access to results

## Monitoring & Logging

**Log Levels**:
```python
DEBUG    # Detailed execution flow
INFO     # Major milestones (model load, predictions)
WARNING  # Recoverable issues (missing data, encoding)
ERROR    # Unrecoverable problems (failed transcription)
```

**Key Metrics to Track**:
- Model loading times
- Transcription success rates
- Sentiment prediction confidence
- User upload frequency
- Recommendation generation time

## Testing Strategy

**Unit Tests** (`tests/test_core.py`):
- Data processor functions
- Sentiment analysis logic
- Analytics calculations

**Integration Tests** (planned):
- End-to-end pipelines
- Service interactions
- Data flow

**Performance Tests** (planned):
- Large dataset handling
- Model inference speed
- Memory usage

## Deployment Architecture

### Development
```
Local Machine
├─ Streamlit server
├─ Python venv
└─ Local file storage
```

### Production (Recommended)
```
Docker Container
├─ Streamlit app
├─ Nginx reverse proxy
├─ PostgreSQL database
└─ S3 file storage
```

### Scalability
```
Kubernetes Cluster (for enterprise)
├─ Multiple Streamlit replicas (stateless)
├─ Load balancer
├─ Centralized database
└─ Distributed storage (S3, GCS)
```

---

**Document Version**: 1.0  
**Last Updated**: March 2026  
**Architecture**: Modular Service-Oriented  
**Status**: Production Ready
