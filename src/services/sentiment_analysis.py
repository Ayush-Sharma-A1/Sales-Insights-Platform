"""
Sentiment analysis services.
Supports both pretrained models and custom training with scikit-learn.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict
import streamlit as st

from config.settings import config
from src.utils.logger import Logger

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from transformers import pipeline

log = Logger.get_logger(__name__)


class SentimentAnalyzer:
    """Handles sentiment analysis using multiple models"""
    
    @staticmethod
    @st.cache_resource(show_spinner=False)
    def load_pretrained_pipeline():
        """
        Load HuggingFace pretrained sentiment model.
        Uses DistilBERT for efficiency.
        
        Returns:
            Pipeline object for sentiment classification
        """
        log.info(f"Loading pretrained model: {config.PRETRAINED_MODEL}")
        return pipeline(
            "sentiment-analysis",
            model=config.PRETRAINED_MODEL
        )
    
    @staticmethod
    def train_custom_model(
        texts: pd.Series,
        labels: pd.Series
    ) -> Tuple[TfidfVectorizer, LogisticRegression, str]:
        """
        Train custom TF-IDF + LogisticRegression model on labeled data.
        
        Args:
            texts: Input text samples
            labels: Sentiment labels (positive/neutral/negative)
            
        Returns:
            Tuple of (vectorizer, trained_model, classification_report)
            
        Raises:
            ValueError: If insufficient label diversity or other training issues
        """
        # Normalize labels
        y = labels.astype(str).str.lower().replace({
            "pos": "positive",
            "neg": "negative",
            "neu": "neutral",
            "n": "negative",
            "p": "positive"
        })
        
        # Check label distribution
        unique_labels = y.nunique()
        if unique_labels < 2:
            raise ValueError(
                f"Need at least 2 different labels for training. Found: {unique_labels}"
            )
        
        log.info(f"Training custom model with labels: {y.unique().tolist()}")
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            texts, y,
            test_size=config.SKLEARN_TEST_SIZE,
            random_state=42,
            stratify=y
        )
        
        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer(
            ngram_range=config.TFIDF_NGRAM_RANGE,
            min_df=config.TFIDF_MIN_DF,
            max_features=config.TFIDF_MAX_FEATURES
        )
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)
        
        # Train LogisticRegression
        clf = LogisticRegression(
            max_iter=config.SKLEARN_MAX_ITER,
            random_state=42
        )
        clf.fit(X_train_vec, y_train)
        
        # Generate report
        y_pred = clf.predict(X_test_vec)
        report = classification_report(y_test, y_pred)
        
        log.info("Custom model training completed")
        log.info(f"\n{report}")
        
        return vectorizer, clf, report
    
    @staticmethod
    def predict_sentiment_custom(
        texts: pd.Series,
        vectorizer: TfidfVectorizer,
        model: LogisticRegression
    ) -> Tuple[list, list]:
        """
        Predict sentiments using trained custom model.
        
        Args:
            texts: Input text samples
            vectorizer: Fitted TF-IDF vectorizer
            model: Trained classifier
            
        Returns:
            Tuple of (predictions, confidence_scores)
        """
        X = vectorizer.transform(texts.fillna(""))
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)
        max_prob = probabilities.max(axis=1)
        
        return predictions.tolist(), max_prob.tolist()
    
    @staticmethod
    def predict_sentiment_pretrained(
        texts: pd.Series,
        pipeline_model
    ) -> Tuple[list, list]:
        """
        Predict sentiments using pretrained HuggingFace model.
        
        Args:
            texts: Input text samples
            pipeline_model: HuggingFace pipeline object
            
        Returns:
            Tuple of (predictions, confidence_scores)
        """
        predictions = []
        scores = []
        
        for i, txt in enumerate(texts.fillna("")):
            try:
                # Truncate for efficiency
                txt_truncated = txt[:config.MAX_TEXT_LENGTH]
                
                result = pipeline_model(txt_truncated)[0]
                label = result["label"].lower()
                
                # Map BERT output to our label space
                if label == "positive":
                    pred = "positive"
                elif label == "negative":
                    pred = "negative"
                else:
                    pred = "neutral"
                
                predictions.append(pred)
                scores.append(float(result.get("score", np.nan)))
                
            except Exception as e:
                log.warning(f"Prediction failed for sample {i}: {e}")
                predictions.append("neutral")
                scores.append(np.nan)
        
        return predictions, scores
    
    @staticmethod
    def get_model_metrics(
        y_true: pd.Series,
        y_pred: list
    ) -> Dict:
        """
        Calculate sentiment model evaluation metrics.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            
        Returns:
            Dictionary of metrics
        """
        report = classification_report(y_true, y_pred, output_dict=True)
        cm = confusion_matrix(y_true, y_pred)
        
        return {
            "classification_report": report,
            "confusion_matrix": cm,
            "accuracy": report.get("accuracy", 0)
        }
