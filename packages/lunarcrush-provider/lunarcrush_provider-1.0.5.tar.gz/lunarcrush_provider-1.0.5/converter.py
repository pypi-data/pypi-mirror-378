"""
LunarCrush Timeframe Converter - Speed Optimized
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class TimeframeConverter:
    TIMEFRAME_MINUTES = {
        "1s": 1 / 60,
        "5s": 5 / 60,
        "10s": 10 / 60,
        "15s": 15 / 60,
        "30s": 30 / 60,
        "1m": 1,
        "2m": 2,
        "3m": 3,
        "4m": 4,
        "5m": 5,
        "6m": 6,
        "10m": 10,
        "12m": 12,
        "15m": 15,
        "20m": 20,
        "30m": 30,
        "1h": 60,
        "2h": 120,
        "3h": 180,
        "4h": 240,
        "6h": 360,
        "8h": 480,
        "12h": 720,
        "1d": 1440,
        "3d": 4320,
        "1w": 10080,
        "2w": 20160,
        "1M": 43200,
    }
    
    # Supported timeframes for the provider info
    SUPPORTED_TIMEFRAMES = list(TIMEFRAME_MINUTES.keys())

    # Pre-compute aggregation methods to avoid dict recreation
    AGG_METHODS = {
        "social_dominance": "mean",
        "sentiment": "mean",
        "sentiment_absolute": "mean",
        "sentiment_relative": "mean",
        "galaxy_score": "mean",
        "price_score": "mean",
        "social_impact_score": "mean",
        "volatility": "mean",
        "social_volume": "sum",
        "contributors_active": "sum",
        "contributors_created": "sum",
        "interactions": "sum",
        "posts_active": "sum",
        "posts_created": "sum",
        "spam": "sum",
        "alt_rank": "last",
        "market_cap_rank": "last",
        "correlation_rank": "last",
        # Market data fields
        "circulating_supply": "last",
        "market_cap": "last",
        "market_dominance": "last",
        "volume_24h": "sum",
    }

    # Pre-define column sets for faster iteration
    LINEAR_METRICS = {
        "social_dominance",
        "sentiment",
        "sentiment_absolute",
        "sentiment_relative",
        "galaxy_score",
        "price_score",
        "social_impact_score",
        "volatility",
    }

    DISCRETE_METRICS = {
        "social_volume",
        "alt_rank",
        "market_cap_rank",
        "correlation_rank",
        "contributors_active",
        "contributors_created",
        "interactions",
        "posts_active",
        "posts_created",
        "spam",
        "circulating_supply",
        "market_cap",
        "market_dominance",
        "volume_24h",
    }

    def convert_to_timeframe(
        self, hourly_data: List[Dict[str, Any]], target_timeframe: str
    ) -> pd.DataFrame:
        if not hourly_data:
            return pd.DataFrame()

        target_minutes = self.TIMEFRAME_MINUTES.get(target_timeframe)
        if target_minutes is None:
            raise ValueError(f"Unsupported timeframe: {target_timeframe}")

        df = self._prepare_hourly_dataframe(hourly_data)
        if df.empty:
            return df

        if target_minutes < 60:
            return self._upsample_data(df, target_timeframe, target_minutes)
        elif target_minutes > 60:
            return self._downsample_data(df, target_timeframe, target_minutes)
        else:
            return df.fillna(0)

    def _prepare_hourly_dataframe(
        self, hourly_data: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        try:
            # Vectorized processing using list comprehension
            records = []
            for data_point in hourly_data:
                timestamp = data_point.get("time", 0)
                if not timestamp:
                    continue

                records.append(
                    {
                        "datetime": pd.to_datetime(timestamp, unit="s", utc=True),
                        "social_dominance": float(
                            data_point.get("social_dominance", 0)
                        ),
                        "social_volume": int(data_point.get("social_volume", 0)),
                        "sentiment": float(data_point.get("sentiment", 0)),
                        "sentiment_absolute": float(
                            data_point.get("sentiment_absolute", 0)
                        ),
                        "sentiment_relative": float(
                            data_point.get("sentiment_relative", 0)
                        ),
                        "galaxy_score": float(data_point.get("galaxy_score", 0)),
                        "alt_rank": int(data_point.get("alt_rank", 0)),
                        "market_cap_rank": int(data_point.get("market_cap_rank", 0)),
                        "price_score": float(data_point.get("price_score", 0)),
                        "social_impact_score": float(
                            data_point.get("social_impact_score", 0)
                        ),
                        "correlation_rank": int(data_point.get("correlation_rank", 0)),
                        "volatility": float(data_point.get("volatility", 0)),
                        "contributors_active": int(
                            data_point.get("contributors_active", 0)
                        ),
                        "contributors_created": int(
                            data_point.get("contributors_created", 0)
                        ),
                        "interactions": int(data_point.get("interactions", 0)),
                        "posts_active": int(data_point.get("posts_active", 0)),
                        "posts_created": int(data_point.get("posts_created", 0)),
                        "spam": int(data_point.get("spam", 0)),
                        # Market data fields
                        "circulating_supply": float(data_point.get("circulating_supply", 0)),
                        "market_cap": float(data_point.get("market_cap", 0)),
                        "market_dominance": float(data_point.get("market_dominance", 0)),
                        "volume_24h": float(data_point.get("volume_24h", 0)),
                    }
                )

            if not records:
                return pd.DataFrame()

            df = pd.DataFrame(records)
            df.set_index("datetime", inplace=True)
            return df.sort_index()

        except Exception:
            return pd.DataFrame()

    def _upsample_data(
        self, df: pd.DataFrame, target_timeframe: str, target_minutes: float
    ) -> pd.DataFrame:
        try:
            # Compute frequency string once
            if target_minutes < 1:
                freq = f"{int(target_minutes * 60)}S"
            else:
                freq = f"{int(target_minutes)}T"

            target_index = pd.date_range(df.index.min(), df.index.max(), freq=freq)
            result_df = df.reindex(target_index)

            # Bulk interpolation
            linear_cols = [c for c in result_df.columns if c in self.LINEAR_METRICS]
            discrete_cols = [c for c in result_df.columns if c in self.DISCRETE_METRICS]

            if linear_cols:
                result_df[linear_cols] = result_df[linear_cols].interpolate(
                    method="linear", limit_direction="both"
                )
            if discrete_cols:
                result_df[discrete_cols] = result_df[discrete_cols].ffill().bfill()

            result_df.fillna(0, inplace=True)
            return result_df

        except Exception:
            return pd.DataFrame()

    def _downsample_data(
        self, df: pd.DataFrame, target_timeframe: str, target_minutes: float
    ) -> pd.DataFrame:
        try:
            # Direct frequency calculation
            if target_minutes >= 1440:
                freq = {1440: "D", 10080: "W", 43200: "M"}.get(
                    target_minutes, f"{int(target_minutes / 60)}H"
                )
            else:
                freq = f"{int(target_minutes / 60)}H"

            result_df = df.resample(freq).agg(self.AGG_METHODS)
            return result_df.fillna(0)

        except Exception:
            return pd.DataFrame()

    def _add_feature_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Simplified version - only return raw data with basic cleanup
        Moving averages and derived features should be calculated in strategies
        """
        try:
            return df.fillna(0)
        except Exception:
            return df

    def get_feature_columns(self) -> List[str]:
        """Return only raw data columns - moving averages should be calculated in strategies"""
        return [
            # Social sentiment fields
            "social_dominance",
            "social_volume",
            "sentiment",
            "sentiment_absolute",
            "sentiment_relative",
            "galaxy_score",
            "price_score",
            "social_impact_score",
            "volatility",
            # Ranking fields
            "alt_rank",
            "market_cap_rank",
            "correlation_rank",
            # Community activity fields
            "contributors_active",
            "contributors_created",
            "interactions",
            "posts_active",
            "posts_created",
            "spam",
            # Market data fields
            "circulating_supply",
            "market_cap",
            "market_dominance",
            "volume_24h",
        ]

    def validate_converted_data(self, df: pd.DataFrame, target_timeframe: str) -> bool:
        if df.empty:
            return False

        # Quick validation
        nan_pct = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
        if nan_pct > 5:
            logger.warning(f"{nan_pct:.1f}% NaN values")

        return True

    def get_conversion_stats(
        self, original_df: pd.DataFrame, converted_df: pd.DataFrame
    ) -> Dict[str, Any]:
        try:
            return {
                "original_points": len(original_df),
                "converted_points": len(converted_df),
                "expansion_ratio": len(converted_df) / len(original_df)
                if len(original_df) > 0
                else 0,
                "feature_count": len(converted_df.columns)
                if not converted_df.empty
                else 0,
                "nan_count": converted_df.isnull().sum().sum()
                if not converted_df.empty
                else 0,
            }
        except Exception:
            return {}
