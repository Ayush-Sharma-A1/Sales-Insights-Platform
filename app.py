"""
Sentiment & Sales Insights Platform
Multi-service application for audio transcription, sentiment analysis, and business intelligence.

This is the main Streamlit application entry point.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

from config.settings import config
from src.utils.logger import Logger
from src.utils.data_processor import DataProcessor
from src.services.transcription import TranscriptionService
from src.services.sentiment_analysis import SentimentAnalyzer
from src.services.analytics import AnalyticsEngine

log = Logger.get_logger(__name__)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title=config.PAGE_TITLE,
    layout=config.PAGE_LAYOUT,
    initial_sidebar_state=config.INITIAL_SIDEBAR_STATE,
    menu_items={
        "About": "Sentiment & Sales Insights Platform\nVersion 1.0.0\nBuilt with Streamlit, Whisper, and Transformers"
    }
)

# Custom CSS for better styling
st.markdown("""
    <style>
        .main-header {
            font-size: 3em;
            color: #1f77b4;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .sub-header {
            font-size: 1.2em;
            color: #555;
            margin-bottom: 20px;
        }
        .metric-card {
            background: #f0f2f6;
            padding: 20px;
            border-radius: 8px;
            margin: 10px 0;
        }
        .warning-box {
            background: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            border-radius: 4px;
            margin: 10px 0;
        }
        .success-box {
            background: #d4edda;
            padding: 15px;
            border-left: 4px solid #28a745;
            border-radius: 4px;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# TITLE & DESCRIPTION
# ============================================================================

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(
        '<div class="main-header">📊 Sentiment & Sales Insights Platform</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="sub-header">Transcribe audio • Analyze sentiment • Generate insights</div>',
        unsafe_allow_html=True
    )

with col2:
    st.info(f"📅 {datetime.now().strftime('%Y-%m-%d')}", icon="ℹ️")

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

st.sidebar.markdown("## ⚙️ Configuration")
st.sidebar.markdown("---")

# ASR Engine selection
asr_engine = st.sidebar.selectbox(
    "🎙️ Audio Engine",
    ["Whisper", "Vosk (Offline)"],
    help="Choose transcription engine: Whisper (online, accurate) or Vosk (offline, faster)"
)

if asr_engine == "Whisper":
    whisper_size = st.sidebar.selectbox(
        "Model Size",
        ["tiny", "base", "small", "medium"],
        index=1,
        help="Smaller = faster, Larger = more accurate"
    )
else:
    vosk_model_dir = st.sidebar.text_input(
        "Vosk Model Path",
        value="",
        help="Path to unzipped Vosk model directory"
    )

st.sidebar.markdown("---")

# Sentiment analysis settings
use_pretrained = st.sidebar.checkbox(
    "🤖 Use Pretrained Model",
    value=False,
    help="Use pretrained model even if custom labels are available"
)

st.sidebar.markdown("---")

# Export settings
save_intermediate = st.sidebar.checkbox(
    "💾 Export Results",
    value=True,
    help="Download processed CSV with predictions"
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 📚 Info")
st.sidebar.caption(f"Config: {config.ENV.upper()}")
st.sidebar.caption(f"Pretrained: {config.PRETRAINED_MODEL}")

log.info(f"App started: ASR={asr_engine}, Pretrained={use_pretrained}")

# ============================================================================
# STEP 1: FILE UPLOAD
# ============================================================================

st.markdown("## Step 1️⃣: Upload Data")
st.markdown("Upload your CRM logs and call recordings")

col_csv, col_audio = st.columns(2)

with col_csv:
    csv_file = st.file_uploader(
        "📄 CSV File",
        type=config.ALLOWED_CSV_FORMATS,
        help="CRM logs with student info, remarks, dates, and optional sentiment labels"
    )

with col_audio:
    audio_files = st.file_uploader(
        "🎵 Audio Files",
        type=config.ALLOWED_AUDIO_FORMATS,
        accept_multiple_files=True,
        help="Call recordings for transcription"
    )

# ============================================================================
# STEP 2: LOAD & MAP DATA
# ============================================================================

df = None
df_transcripts = pd.DataFrame()

if csv_file is not None:
    try:
        with st.spinner("Loading CSV..."):
            df_raw, load_status = DataProcessor.load_csv(csv_file)
        
        st.success(f"✅ CSV loaded: {df_raw.shape[0]} rows × {df_raw.shape[1]} columns")
        
        # Column mapping
        with st.expander("🔧 Map Columns (if different from standard names)", expanded=False):
            cols = ["<none>"] + list(df_raw.columns)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                map_student = st.selectbox("Student Name", cols, 
                    index=cols.index("student_name") if "student_name" in cols else 0)
                map_year = st.selectbox("Year", cols,
                    index=cols.index("year") if "year" in cols else 0)
                map_stack = st.selectbox("Tech Stack", cols,
                    index=cols.index("tech_stack") if "tech_stack" in cols else 0)
            
            with col2:
                map_loc = st.selectbox("Location", cols,
                    index=cols.index("location") if "location" in cols else 0)
                map_remarks = st.selectbox("Remarks/Notes", cols,
                    index=cols.index("remarks") if "remarks" in cols else 0)
                map_callid = st.selectbox("Call ID", cols,
                    index=cols.index("call_id") if "call_id" in cols else 0)
            
            with col3:
                map_date = st.selectbox("Date", cols,
                    index=cols.index("date") if "date" in cols else 0)
                map_label = st.selectbox("Sentiment Label", cols,
                    index=cols.index("label") if "label" in cols else 0)
        
        # Build standardized dataframe
        column_mapping = {
            "student_name": map_student,
            "year": map_year,
            "tech_stack": map_stack,
            "location": map_loc,
            "remarks": map_remarks,
            "call_id": map_callid,
            "date": map_date,
            "label": map_label,
        }
        
        df = DataProcessor.build_dataframe(df_raw, column_mapping)
        
        # Show preview
        with st.expander("👁️ Preview Data", expanded=False):
            st.dataframe(df.head(10), use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ Error loading CSV: {str(e)}")
        log.error(f"CSV loading error: {e}")

# ============================================================================
# STEP 3: TRANSCRIBE AUDIO
# ============================================================================

if audio_files:
    st.markdown("## Step 2️⃣: Transcribe Audio")
    st.markdown(f"Processing {len(audio_files)} audio file(s)...")
    
    try:
        # Load appropriate ASR engine
        model = None
        if asr_engine == "Whisper":
            with st.spinner("🔄 Loading Whisper model..."):
                model = TranscriptionService.load_whisper_model(whisper_size)
        else:
            with st.spinner("🔄 Loading Vosk model..."):
                model = TranscriptionService.load_vosk_model(vosk_model_dir)
        
        # Transcribe files
        transcripts = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, audio_file in enumerate(audio_files):
            status_text.text(f"Processing: {audio_file.name}")
            audio_bytes = audio_file.read()
            
            try:
                if asr_engine == "Whisper":
                    text = TranscriptionService.transcribe_whisper(
                        audio_bytes, model, audio_file.name
                    )
                else:
                    text = TranscriptionService.transcribe_vosk(
                        audio_bytes, model, audio_file.name
                    )
                
                transcripts.append({
                    "call_id": audio_file.name.split(".")[0],
                    "transcript_text": text
                })
                
            except Exception as e:
                st.warning(f"⚠️ Failed to transcribe {audio_file.name}: {str(e)}")
                log.error(f"Transcription error for {audio_file.name}: {e}")
            
            progress_bar.progress((i + 1) / len(audio_files))
        
        status_text.empty()
        progress_bar.empty()
        
        if transcripts:
            st.success(f"✅ Transcribed {len(transcripts)}/{len(audio_files)} files")
            df_transcripts = pd.DataFrame(transcripts)
        else:
            st.error("❌ No files were successfully transcribed")
    
    except Exception as e:
        st.error(f"❌ Transcription failed: {str(e)}")
        log.error(f"ASR pipeline error: {e}")

# ============================================================================
# STEP 4: MERGE DATA
# ============================================================================

if df is not None and (audio_files or not df.empty):
    st.markdown("## Step 3️⃣: Merge Data")
    
    try:
        merged = DataProcessor.merge_transcripts(df, df_transcripts)
        st.success(f"✅ Merged: {merged.shape[0]} records")
        
        with st.expander("👁️ Preview Merged Data", expanded=False):
            st.dataframe(merged.head(10), use_container_width=True)
    except Exception as e:
        st.error(f"❌ Merge failed: {str(e)}")
        log.error(f"Data merge error: {e}")
        merged = None

elif df is not None:
    merged = df

else:
    merged = None

# ============================================================================
# STEP 5: SENTIMENT ANALYSIS
# ============================================================================

if merged is not None and len(merged) > 0:
    st.markdown("## Step 4️⃣: Sentiment Analysis")
    
    try:
        can_train = (
            "label" in merged.columns and
            merged["label"].notna().any() and
            not use_pretrained
        )
        
        with st.spinner("🔄 Running sentiment analysis..."):
            if can_train:
                try:
                    st.info("🎯 Training custom model on provided labels...")
                    
                    vectorizer, clf, report = SentimentAnalyzer.train_custom_model(
                        merged["combined_text"].fillna(""),
                        merged["label"]
                    )
                    
                    predictions, confidence = SentimentAnalyzer.predict_sentiment_custom(
                        merged["combined_text"],
                        vectorizer,
                        clf
                    )
                    
                    merged["sentiment"] = predictions
                    merged["sentiment_score"] = confidence
                    model_used = "Custom TF-IDF+LogisticRegression"
                    
                    # Show report
                    with st.expander("📊 Model Report", expanded=False):
                        st.text(report)
                    
                except Exception as e:
                    st.warning(f"Training failed ({str(e)}), using pretrained...")
                    can_train = False
            
            if not can_train:
                st.info("🤖 Using pretrained HuggingFace model (DistilBERT)...")
                
                nlp = SentimentAnalyzer.load_pretrained_pipeline()
                predictions, scores = SentimentAnalyzer.predict_sentiment_pretrained(
                    merged["combined_text"],
                    nlp
                )
                
                merged["sentiment"] = predictions
                merged["sentiment_score"] = scores
                model_used = "Pretrained DistilBERT"
        
        st.success(f"✅ Sentiment analysis complete ({model_used})")
        
    except Exception as e:
        st.error(f"❌ Sentiment analysis failed: {str(e)}")
        log.error(f"Sentiment analysis error: {e}")
        merged = None

# ============================================================================
# STEP 6: ANALYTICS & INSIGHTS
# ============================================================================

if merged is not None and "sentiment" in merged.columns:
    st.markdown("## Step 5️⃣: Analytics & Insights")
    st.markdown("---")
    
    # Summary statistics
    st.subheader("📈 Sentiment Summary")
    
    summary = AnalyticsEngine.get_sentiment_summary(merged)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", summary["total_records"])
    with col2:
        positive = summary["sentiment_percentages"].get("positive", 0)
        st.metric("Positive 😊", f"{positive:.1f}%")
    with col3:
        neutral = summary["sentiment_percentages"].get("neutral", 0)
        st.metric("Neutral 😐", f"{neutral:.1f}%")
    with col4:
        negative = summary["sentiment_percentages"].get("negative", 0)
        st.metric("Negative 😞", f"{negative:.1f}%")
    
    st.markdown("---")
    
    # Charts
    st.subheader("📊 Visualizations")
    
    col1, col2 = st.columns(2)
    
    # Sentiment distribution pie chart
    with col1:
        fig_pie = px.pie(
            merged,
            names="sentiment",
            title="Sentiment Distribution",
            color_discrete_map={
                "positive": "#28a745",
                "neutral": "#ffc107",
                "negative": "#dc3545"
            }
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Sentiment count bar chart
    with col2:
        sentiment_counts = merged["sentiment"].value_counts().reset_index()
        sentiment_counts.columns = ["Sentiment", "Count"]
        
        fig_bar = px.bar(
            sentiment_counts,
            x="Sentiment",
            y="Count",
            color="Sentiment",
            color_discrete_map={
                "positive": "#28a745",
                "neutral": "#ffc107",
                "negative": "#dc3545"
            },
            title="Sentiment Count"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Location analysis
    if "location" in merged.columns:
        fig_loc = px.bar(
            merged.fillna({"location": "Unknown"}),
            x="location",
            color="sentiment",
            title="Sentiment by Location",
            color_discrete_map={
                "positive": "#28a745",
                "neutral": "#ffc107",
                "negative": "#dc3545"
            }
        )
        st.plotly_chart(fig_loc, use_container_width=True)
    
    # Tech Stack analysis
    if "tech_stack" in merged.columns:
        fig_stack = px.bar(
            merged.fillna({"tech_stack": "Unknown"}),
            x="tech_stack",
            color="sentiment",
            title="Sentiment by Tech Stack",
            color_discrete_map={
                "positive": "#28a745",
                "neutral": "#ffc107",
                "negative": "#dc3545"
            }
        )
        st.plotly_chart(fig_stack, use_container_width=True)
    
    # Time trend
    if "date_parsed" in merged.columns:
        trend = AnalyticsEngine.get_monthly_trend(merged)
        if not trend.empty:
            fig_trend = px.line(
                trend,
                x="month",
                y="count",
                color="sentiment",
                markers=True,
                title="Monthly Sentiment Trend",
                color_discrete_map={
                    "positive": "#28a745",
                    "neutral": "#ffc107",
                    "negative": "#dc3545"
                }
            )
            st.plotly_chart(fig_trend, use_container_width=True)
    
    st.markdown("---")
    
    # Top keywords analysis
    st.subheader("🔍 Top Negative Keywords (TF-IDF)")
    
    try:
        keywords = AnalyticsEngine.extract_top_keywords(merged, "negative", 20)
        if not keywords.empty:
            fig_kw = px.bar(
                keywords,
                x="keyword",
                y="score",
                title="Top 20 Negative Keywords",
                color="score",
                color_continuous_scale="Reds"
            )
            st.plotly_chart(fig_kw, use_container_width=True)
        else:
            st.info("Not enough negative samples for keyword analysis")
    except Exception as e:
        st.warning(f"Could not extract keywords: {str(e)}")
        log.warning(f"Keyword extraction error: {e}")
    
    st.markdown("---")
    
    # ========================================================================
    # STEP 7: RECOMMENDATIONS
    # ========================================================================
    
    st.subheader("💡 Actionable Recommendations")
    
    try:
        recommendations = AnalyticsEngine.generate_recommendations(merged)
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"**{i}.** {rec}")
        else:
            st.info("✅ No critical issues detected. Keep monitoring sentiment trends.")
    
    except Exception as e:
        st.error(f"Could not generate recommendations: {str(e)}")
        log.error(f"Recommendations generation error: {e}")
    
    st.markdown("---")
    
    # ========================================================================
    # STEP 8: EXPORT
    # ========================================================================
    
    st.subheader("📥 Export Results")
    
    if save_intermediate:
        try:
            # Prepare export data
            export_df = merged.copy()
            
            # Create CSV
            csv_buffer = export_df.to_csv(index=False)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📊 Download CSV Results",
                    data=csv_buffer,
                    file_name=f"sentiment_analysis_{timestamp}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Create summary JSON
                summary_json = {
                    "analysis_date": timestamp,
                    "total_records": int(summary["total_records"]),
                    "sentiment_distribution": summary["sentiment_distribution"],
                    "negative_ratio": float(summary["negative_ratio"]),
                    "model_used": model_used,
                    "recommendations_count": len(recommendations) if recommendations else 0
                }
                
                import json
                summary_text = json.dumps(summary_json, indent=2)
                
                st.download_button(
                    label="📋 Download Summary",
                    data=summary_text,
                    file_name=f"summary_{timestamp}.json",
                    mime="application/json"
                )
        
        except Exception as e:
            st.error(f"Export failed: {str(e)}")
            log.error(f"Export error: {e}")

else:
    if csv_file is None and not audio_files:
        st.info("👈 Upload CSV and/or audio files to get started!")
    else:
        st.warning("⏳ Processing data...")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; margin-top: 30px;'>
        <p>Sentiment & Sales Insights Platform v1.0.0</p>
        <p>Built with ❤️ using Streamlit, Whisper, Transformers & Scikit-learn</p>
    </div>
    """,
    unsafe_allow_html=True
)
