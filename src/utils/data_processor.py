"""
Data processing and utility functions.
Handles CSV loading, parsing, and data validation.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from dateutil import parser as date_parser
from datetime import datetime

from src.utils.logger import Logger

log = Logger.get_logger(__name__)


class DataProcessor:
    """Data loading and processing utilities"""

    @staticmethod
    def load_csv(file_path_or_object) -> tuple[pd.DataFrame, str]:
        try:
            df = pd.read_csv(file_path_or_object)
            log.info(f"CSV loaded successfully with shape {df.shape}")
            return df, "success"

        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_path_or_object, encoding="latin-1")
                log.info(f"CSV loaded with latin-1 encoding, shape {df.shape}")
                return df, "success_latin1"

            except Exception as e:
                log.error(f"Failed to load CSV: {e}")
                raise ValueError(f"Could not load CSV: {str(e)}")

    @staticmethod
    def parse_date(value: Any) -> Optional[datetime]:
        if pd.isna(value):
            return None

        try:
            return date_parser.parse(str(value), dayfirst=False, yearfirst=True)
        except Exception as e:
            log.debug(f"Failed to parse date '{value}': {e}")
            return None

    @staticmethod
    def build_dataframe(df_raw: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:

        def pick(colname):
            if colname is None or colname == "<none>":
                return None
            return df_raw[colname] if colname in df_raw.columns else None

        def safe_pick(colname, default_series):
            col = pick(colname)
            return col if col is not None else default_series

        n = len(df_raw)

        processed = pd.DataFrame({
            "call_id": safe_pick(column_mapping.get("call_id"), pd.Series([None] * n)),

            "student_name": safe_pick(column_mapping.get("student_name"), pd.Series([None] * n)),

            "year": safe_pick(column_mapping.get("year"), pd.Series([None] * n)),

            "tech_stack": safe_pick(column_mapping.get("tech_stack"), pd.Series([None] * n)),

            "location": safe_pick(column_mapping.get("location"), pd.Series([None] * n)),

            "remarks": safe_pick(column_mapping.get("remarks"), pd.Series([""] * n)).fillna(""),

            "date": safe_pick(column_mapping.get("date"), pd.Series([None] * n)),

            "label": safe_pick(column_mapping.get("label"), pd.Series([None] * n)),
        })

        # Parse dates
        processed["date_parsed"] = processed["date"].apply(
            DataProcessor.parse_date
        )

        log.info(f"Built standardized dataframe: {processed.shape}")
        return processed

    @staticmethod
    def merge_transcripts(df: pd.DataFrame, df_transcripts: pd.DataFrame) -> pd.DataFrame:

        if df is None or df.empty:
            return df_transcripts

        if df_transcripts is None or df_transcripts.empty:
            df["transcript_text"] = ""
            df["combined_text"] = df.get("remarks", pd.Series(dtype=str)).fillna("").astype(str)
            return df

        # Standardize call_id
        if "call_id" in df.columns:
            df["call_id"] = df["call_id"].astype(str)

        if "call_id" in df_transcripts.columns:
            df_transcripts["call_id"] = df_transcripts["call_id"].astype(str)

        # Merge
        if "call_id" in df.columns:
            merged = pd.merge(df, df_transcripts, on="call_id", how="outer")
        else:
            merged = df.copy()

        # Ensure transcript column exists
        if "transcript_text" not in merged.columns:
            merged["transcript_text"] = ""

        merged["transcript_text"] = merged["transcript_text"].fillna("")

        # Combine text
        remarks_col = merged.get("remarks", pd.Series(dtype=str)).fillna("")
        merged["combined_text"] = (
            remarks_col.astype(str) + " " +
            merged["transcript_text"].astype(str)
        ).str.strip()

        log.info(f"Merged data: {merged.shape}")
        return merged

    @staticmethod
    def extract_keywords_from_text(text: str, keywords: list) -> bool:
        text_lower = str(text).lower()
        return any(kw in text_lower for kw in keywords)