# 📊 Sentiment & Sales Insights Platform

A professional-grade application for audio transcription, sentiment analysis, and business intelligence. Perfect for analyzing customer/student feedback at scale.

**Version:** 1.0.0  
**Status:** Production Ready  
**License:** MIT

---

## ✨ Features

### 🎙️ **Audio Processing**
- **Whisper Integration**: State-of-the-art speech recognition (online)
- **Vosk Support**: Offline speech recognition for privacy-focused deployments
- **Multi-format Support**: MP3, WAV, M4A, AAC, FLAC
- **Batch Processing**: Handle multiple audio files simultaneously
- **Error Handling**: Graceful fallbacks for unsupported formats

### 🧠 **Sentiment Analysis**
- **Custom Model Training**: TF-IDF + LogisticRegression on your labeled data
- **Pretrained Models**: DistilBERT for zero-shot sentiment prediction
- **Flexible**: Automatically switches between custom and pretrained models
- **Explainable**: Keyword extraction and confidence scores
- **Multi-class**: Supports positive, neutral, and negative classifications

### 📈 **Advanced Analytics**
- **Real-time Dashboard**: Interactive Plotly visualizations
- **Sentiment Trends**: Monthly/temporal analysis
- **Dimensional Breakdown**: Sentiment by location, tech stack, year, etc.
- **Keyword Extraction**: TF-IDF based topic identification
- **Statistical Insights**: Distribution, ratios, and anomaly detection

### 💡 **Intelligent Recommendations**
- **Data-Driven**: Rules based on sentiment patterns and keyword analysis
- **Actionable**: Specific recommendations for each identified issue
- **Contextual**: Tailored advice for different tech stacks and locations
- **Scalable**: Adapts recommendations based on data volume

### 💾 **Data Management**
- **Flexible CSV Import**: Auto-detects and maps column names
- **Data Integration**: Seamlessly merge CRM logs with transcripts
- **Export Options**: Download processed data as CSV or summary as JSON
- **Data Validation**: Built-in error checking and reporting

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- FFmpeg (for Whisper) - [Install Guide](https://ffmpeg.org/download.html)
- 4GB+ RAM recommended
- GPU optional (for faster inference)

### Installation

1. **Clone or download the project**
   ```bash
   cd sentiment_insights
   ```

2. **Create virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify FFmpeg installation** (Windows)
   ```powershell
   # Modify the path in config/settings.py if FFmpeg is not in system PATH
   # Or ensure it's added to your system environment variables
   ```

### Running the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📊 How to Use

### Step 1: Upload Data
- **Option A**: Upload CSV with CRM logs (student names, remarks, dates, etc.)
- **Option B**: Upload audio files (call recordings)
- **Option C**: Upload both for merged analysis

### Step 2: Configure (Optional)
- Map CSV columns to standard names if they differ
- Select ASR engine (Whisper for accuracy, Vosk for offline)
- Choose sentiment model (custom if labels provided, else pretrained)

### Step 3: Process
The app automatically:
1. Loads and validates data
2. Transcribes audio (if provided)
3. Merges CRM logs with transcripts
4. Analyzes sentiment
5. Generates visualizations
6. Creates recommendations

### Step 4: Explore & Export
- View interactive dashboards
- Read AI-generated recommendations
- Download results as CSV or JSON

---

## 🏗️ Project Structure

```
sentiment_insights/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── config/
│   ├── __init__.py
│   └── settings.py                 # Configuration management
│
├── src/
│   ├── __init__.py
│   ├── models/                     # ML model definitions (extendable)
│   │   └── __init__.py
│   ├── services/                   # Business logic & services
│   │   ├── __init__.py
│   │   ├── transcription.py        # Audio → Text (Whisper/Vosk)
│   │   ├── sentiment_analysis.py   # Text → Sentiment
│   │   └── analytics.py            # Data → Insights
│   └── utils/                      # Utility functions
│       ├── __init__.py
│       ├── logger.py               # Logging configuration
│       └── data_processor.py       # Data loading & processing
│
├── data/                           # Data storage
│   ├── raw/                        # Raw inputs (auto-created)
│   └── processed/                  # Processed outputs (auto-created)
│
└── tests/                          # Unit tests (extendable)
    └── __init__.py
```

---

## 🔧 Configuration

Edit `config/settings.py` to customize:

```python
# Audio Processing
WHISPER_MODEL_SIZE = "base"  # tiny, base, small, medium
ASR_ENGINE = "whisper"       # or "vosk"

# Sentiment Analysis
USE_PRETRAINED_SENTIMENT = False
PRETRAINED_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"

# Thresholds
NEGATIVE_SENTIMENT_THRESHOLD = 0.35
NEGATIVE_RATIO_ALERT = 0.40

# Feature Extraction
TOP_KEYWORDS_COUNT = 20
TFIDF_MAX_FEATURES = 50000
```

---

## 📋 CSV Format

**Required Columns (flexible mapping):**
- `student_name`: Student or customer identifier
- `remarks`: Text notes or feedback
- `location`: Geographic location (Noida, Lucknow, etc.)
- `tech_stack`: Product/program category
- `year`: Academic or cohort year
- `date`: When the interaction occurred

**Optional Columns:**
- `call_id`: Identifier to link with audio files
- `label`: Sentiment label for training (`positive`, `neutral`, `negative`)

**Example CSV:**
```csv
student_name,year,tech_stack,location,remarks,call_id,date,label
John Doe,2023,Python,Noida,Great course content,call_001,2024-01-15,positive
Jane Smith,2023,MERN,Lucknow,Fee is too high,call_002,2024-01-16,negative
```

---

## 🎯 Use Cases

### Educational Institutions
- Analyze student feedback on courses
- Identify pain points (fees, timing, support)
- Track satisfaction trends
- Personalized recommendations per cohort

### Sales & Customer Success
- Analyze call center recordings
- Identify objections (price, timing, features)
- Track customer sentiment over time
- Generate coaching recommendations

### Product Management
- Gather feature feedback
- Identify improvement areas
- Benchmark against competitors
- Prioritize development roadmap

### HR & Recruitment
- Analyze candidate interview feedback
- Improve hiring processes
- Identify interview training needs

---

## 🔬 Technical Details

### Sentiment Analysis Models

**Custom Model (Recommended for labeled data)**
- **Vectorizer**: TF-IDF with bigrams
- **Classifier**: LogisticRegression
- **Accuracy**: Depends on labeled data quality
- **Training**: Automatic 80-20 train-test split

**Pretrained Model**
- **Model**: DistilBERT (HuggingFace)
- **Accuracy**: ~91% on benchmark datasets
- **Speed**: Fast inference (CPU-friendly)
- **No Training Required**: Works with zero labels

### TF-IDF Configuration
```python
TfidfVectorizer(
    ngram_range=(1, 2),      # Unigrams + Bigrams
    min_df=2,                 # Appear in ≥2 documents
    max_features=50000        # Keep top 50k features
)
```

### Performance Notes
- **Memory**: ~2GB for small datasets (<10K records)
- **Speed**: ~1-5 minutes for 100 audio files (base Whisper)
- **GPU**: Automatically detects and uses if available

---

## 📊 Sample Recommendations

The system generates contextual recommendations:

```
⚠️ HIGH NEGATIVITY: 45% negative sentiment detected. Consider immediate quality review and student support interventions.

📍 Lucknow: 60% negative sentiment. Action: Review local counselors, improve center infrastructure, or create location-specific support programs.

💻 Python: 50% negative. Action: show job outcomes with real case studies and projects.

💰 FEE CONCERNS: Offer flexible payment plans, scholarships, limited-time discounts, or EMI options.

⏰ TIMING ISSUES: Add evening/weekend batches and flexible scheduling. Consider hybrid and async learning options.
```

---

## 🧪 Testing

Basic test structure (extend as needed):

```bash
pytest tests/ -v --cov=src
```

---

## 🐛 Troubleshooting

### Whisper model not downloading
```bash
# Manually cache the model
python -c "import whisper; whisper.load_model('base')"
```

### FFmpeg not found
```bash
# Windows: Add FFmpeg to PATH or set in settings.py
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

# Linux: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
```

### Out of memory errors
- Use smaller Whisper model (`tiny` instead of `medium`)
- Process fewer files at a time
- Use Vosk instead (works offline, lower memory)

### Slow inference
- Use GPU: Install CUDA-enabled PyTorch
- Use smaller model (`distilbert` is already optimized)
- Enable Streamlit caching (default: enabled)

---

## 📈 Roadmap

**Planned Features:**
- [ ] Database support (PostgreSQL, MongoDB)
- [ ] REST API with FastAPI
- [ ] Model fine-tuning UI
- [ ] Advanced time series forecasting
- [ ] Multi-language support
- [ ] Custom NER for entity extraction
- [ ] Integration with CRM systems (Salesforce, HubSpot)
- [ ] Slack/Teams webhook integration
- [ ] Real-time streaming analysis

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - see LICENSE file for details

---

## 👤 Author

Built as a comprehensive sentiment analysis platform for educational and business use.

---

## 🙏 Acknowledgments

- **Whisper**: OpenAI's speech recognition model
- **Transformers**: HuggingFace NLP library
- **Streamlit**: Interactive web app framework
- **Scikit-learn**: ML algorithms and preprocessing

---

## 📞 Support

For issues, questions, or suggestions:
1. Check existing GitHub issues
2. Review FAQ section in documentation
3. Contact: [your-email@example.com]

---

## 🎓 Educational Value

This project demonstrates:
- **Software Architecture**: Modular design with separation of concerns
- **ML Pipelines**: End-to-end ML workflow
- **Data Processing**: ETL and data integration
- **API Design**: Service-oriented architecture
- **Error Handling**: Graceful degradation and logging
- **UI/UX**: Interactive dashboards and user experience
- **Production Practices**: Configuration management, logging, caching

**Perfect for college projects, portfolios, and production deployment!**

---

**Last Updated**: March 2026  
**Version**: 1.0.0 (Stable)
