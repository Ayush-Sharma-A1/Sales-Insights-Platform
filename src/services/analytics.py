"""
Analytics and business intelligence services.
Generates insights and actionable recommendations from sentiment data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer

from config.settings import config
from src.utils.logger import Logger

log = Logger.get_logger(__name__)


class AnalyticsEngine:
    """Generates analytics and recommendations from sentiment data"""
    
    @staticmethod
    def get_sentiment_summary(df: pd.DataFrame) -> Dict:
        """
        Generate sentiment summary statistics.
        
        Args:
            df: DataFrame with 'sentiment' column
            
        Returns:
            Dictionary with summary statistics
        """
        sentiment_counts = df["sentiment"].value_counts()
        total = len(df)
        
        summary = {
            "total_records": total,
            "sentiment_distribution": sentiment_counts.to_dict(),
            "sentiment_percentages": (sentiment_counts / total * 100).round(2).to_dict(),
            "negative_ratio": (sentiment_counts.get("negative", 0) / total) if total > 0 else 0,
            "positive_ratio": (sentiment_counts.get("positive", 0) / total) if total > 0 else 0,
            "neutral_ratio": (sentiment_counts.get("neutral", 0) / total) if total > 0 else 0,
        }
        
        return summary
    
    @staticmethod
    def extract_top_keywords(
        df: pd.DataFrame,
        sentiment: str = "negative",
        top_n: int = None
    ) -> pd.DataFrame:
        """
        Extract top keywords using TF-IDF for specific sentiment.
        
        Args:
            df: DataFrame with 'sentiment' and 'combined_text' columns
            sentiment: Sentiment to extract keywords for
            top_n: Number of top keywords to return
            
        Returns:
            DataFrame with keywords and scores
        """
        if top_n is None:
            top_n = config.TOP_KEYWORDS_COUNT
        
        # Filter by sentiment
        texts = df[df["sentiment"] == sentiment]["combined_text"].dropna()
        
        if len(texts) < 3:
            log.warning(f"Not enough {sentiment} samples for keyword extraction")
            return pd.DataFrame(columns=["keyword", "score"])
        
        # TF-IDF extraction
        vectorizer = TfidfVectorizer(
            max_features=top_n * 3,
            stop_words="english"
        )
        X = vectorizer.fit_transform(texts)
        
        # Sum TF-IDF scores
        scores = np.asarray(X.sum(axis=0)).ravel()
        vocab = np.array(vectorizer.get_feature_names_out())
        
        result = pd.DataFrame({
            "keyword": vocab,
            "score": scores
        }).sort_values("score", ascending=False).head(top_n)
        
        return result
    
    @staticmethod
    def analyze_by_dimension(
        df: pd.DataFrame,
        dimension: str
    ) -> Dict[str, float]:
        """
        Analyze sentiment ratios by a specific dimension (location, tech_stack, etc.).
        
        Args:
            df: Input DataFrame
            dimension: Column name to group by
            
        Returns:
            Dictionary mapping dimension values to negative sentiment ratio
        """
        if dimension not in df.columns:
            return {}
        
        by_dim = df.groupby(dimension)["sentiment"].apply(
            lambda s: (s == "negative").mean()
        ).sort_values(ascending=False)
        
        return by_dim.to_dict()
    
    @staticmethod
    def generate_recommendations(df: pd.DataFrame) -> List[str]:
        """
        Generate actionable business recommendations based on sentiment data.
        
        Args:
            df: Merged DataFrame with sentiment predictions
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if df is None or len(df) == 0:
            return recommendations
        
        total = len(df)
        summary = AnalyticsEngine.get_sentiment_summary(df)
        neg_ratio = summary["negative_ratio"]
        text_all = " ".join(
            df.get("combined_text", pd.Series(dtype=str)).dropna().astype(str).tolist()
        ).lower()
        
        # 1. Overall negativity check
        if neg_ratio > config.NEGATIVE_RATIO_ALERT:
            recommendations.append(
                f"⚠️ HIGH NEGATIVITY: {neg_ratio:.0%} negative sentiment detected. "
                "Consider immediate quality review and student support interventions."
            )
        
        # 2. Location-based analysis
        if "location" in df.columns:
            loc_analysis = AnalyticsEngine.analyze_by_dimension(df, "location")
            for location, ratio in loc_analysis.items():
                if pd.notna(location) and ratio >= config.NEGATIVE_SENTIMENT_THRESHOLD:
                    recommendations.append(
                        f"📍 {location}: {ratio:.0%} negative sentiment. "
                        "Action: Review local counselors, improve center infrastructure, "
                        "or create location-specific support programs."
                    )
        
        # 3. Tech Stack analysis
        if "tech_stack" in df.columns:
            stack_analysis = AnalyticsEngine.analyze_by_dimension(df, "tech_stack")
            stack_tips = {
                "python": "show job outcomes with real case studies and projects",
                "java": "offer flexible payment plans and showcase enterprise placements",
                "mern": "display live GitHub repositories and alumni success stories",
                "ai": "clarify math prerequisites and provide foundational bridge modules",
                "web": "highlight frontend portfolio building opportunities",
                "devops": "emphasize industry-relevant certifications and hands-on labs"
            }
            
            for stack, ratio in stack_analysis.items():
                if pd.notna(stack) and ratio >= config.NEGATIVE_SENTIMENT_THRESHOLD:
                    stack_lower = str(stack).lower()
                    action = "Improve curriculum design and student engagement"
                    for key, tip in stack_tips.items():
                        if key in stack_lower:
                            action = tip
                            break
                    
                    recommendations.append(
                        f"💻 {stack}: {ratio:.0%} negative. "
                        f"Action: {action.capitalize()}."
                    )
        
        # 4. Keyword-based insights
        keyword_themes = {
            "fee|fees|price|cost|expensive": (
                "💰 FEE CONCERNS: Offer flexible payment plans, scholarships, "
                "limited-time discounts, or EMI options."
            ),
            "time|timing|slot|schedule|evening|weekend": (
                "⏰ TIMING ISSUES: Add evening/weekend batches and flexible scheduling. "
                "Consider hybrid and async learning options."
            ),
            "location|distance|commute|travel": (
                "🚗 LOCATION/COMMUTE: Promote online/hybrid options and campus flexibility. "
                "Consider satellite centers in high-demand locations."
            ),
            "doubt|support|mentor|teacher|faculty": (
                "👨‍🏫 SUPPORT CONCERNS: Create structured mentorship programs, "
                "doubt-solving sessions, and community channels (Discord/Slack)."
            ),
            "job|placement|interview|hire|career": (
                "💼 CAREER FOCUS: Highlight placement statistics, alumni outcomes, "
                "resume workshops, and mock interview sessions."
            ),
            "quality|curriculum|syllabus|content|course": (
                "🎓 CURRICULUM: Update content, add industry-relevant projects, "
                "and ensure instructors cover latest technologies."
            ),
            "online|learning|platform|app|tool": (
                "🖥️ PLATFORM/TOOL: Improve LMS usability, add more resources, "
                "and ensure technical support for learning platforms."
            ),
        }
        
        for keywords, recommendation in keyword_themes.items():
            keyword_list = keywords.split("|")
            if any(kw in text_all for kw in keyword_list):
                if recommendation not in recommendations:
                    recommendations.append(recommendation)
        
        # 5. Year level analysis if available
        if "year" in df.columns and df["year"].notna().any():
            year_analysis = AnalyticsEngine.analyze_by_dimension(df, "year")
            for year, ratio in year_analysis.items():
                if pd.notna(year) and ratio >= config.NEGATIVE_SENTIMENT_THRESHOLD:
                    recommendations.append(
                        f"📅 Year {year}: {ratio:.0%} negative sentiment. "
                        "Action: Plan targeted interventions for this cohort."
                    )
        
        # 6. Positive feedback highlight
        pos_ratio = summary["positive_ratio"]
        if pos_ratio >= 0.5:
            recommendations.append(
                f"✅ STRENGTH: {pos_ratio:.0%} positive sentiment! "
                "Document success factors and scale them across all programs."
            )
        
        log.info(f"Generated {len(recommendations)} recommendations")
        return recommendations
    
    @staticmethod
    def get_monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate monthly sentiment trend.
        
        Args:
            df: DataFrame with 'date_parsed' and 'sentiment' columns
            
        Returns:
            DataFrame with monthly trends
        """
        if "date_parsed" not in df.columns or df["date_parsed"].isna().all():
            return pd.DataFrame()
        
        temp = df.dropna(subset=["date_parsed"]).copy()
        if temp.empty:
            return pd.DataFrame()
        
        temp["month"] = temp["date_parsed"].dt.to_period("M").astype(str)
        trend = temp.groupby(["month", "sentiment"]).size().reset_index(name="count")
        
        return trend
