"""
LunarCrush Sentiment Data Provider for FreqTrade

Integrates LunarCrush social sentiment data with FreqTrade strategies.
Provides sentiment features for FreqAI model training and prediction.
"""

from .client import LunarCrushClient
from .cache import LunarCrushCache
from .converter import TimeframeConverter
from .provider import LunarCrushProvider, get_lunarcrush_provider

__version__ = "1.0.0"
__author__ = "FreqAI Enhancement Project"

# Main entry points
__all__ = [
    'LunarCrushClient',
    'LunarCrushCache', 
    'TimeframeConverter',
    'LunarCrushProvider',
    'get_lunarcrush_provider'
]

# Default configuration
DEFAULT_CONFIG = {
    'cache_dir': 'external_data_providers/lunarcrush/data',
    'update_interval_hours': 1,
    'max_cache_age_days': 30,
    'rate_limits': {
        'requests_per_minute': 10,
        'requests_per_day': 2000
    }
}

# All FreqTrade timeframes supported
SUPPORTED_TIMEFRAMES = [
    '1s', '5s', '10s', '15s', '30s', '1m', '2m', '3m', '4m', '5m', '6m',
    '10m', '12m', '15m', '20m', '30m', '1h', '2h', '3h', '4h', '6h', '8h',
    '12h', '1d', '3d', '1w', '2w', '1M'
]

# Feature information
SENTIMENT_FEATURES = [
    'lc_social_dominance', 'lc_social_volume', 'lc_sentiment', 'lc_sentiment_absolute',
    'lc_sentiment_relative', 'lc_galaxy_score', 'lc_alt_rank', 'lc_market_cap_rank',
    'lc_price_score', 'lc_social_impact_score', 'lc_correlation_rank', 'lc_volatility',
    'lc_social_volume_ma_3', 'lc_social_volume_ma_12', 'lc_social_volume_change',
    'lc_sentiment_ma_3', 'lc_sentiment_ma_12', 'lc_sentiment_change', 'lc_sentiment_volatility',
    'lc_galaxy_score_ma_3', 'lc_galaxy_score_change', 'lc_social_dominance_ma_3',
    'lc_social_dominance_change', 'lc_sentiment_strength', 'lc_rank_stability', 'lc_social_engagement'
]

# Quick setup function
def create_provider(bearer_token: str, **kwargs) -> LunarCrushProvider:
    """
    Quick setup function for LunarCrush provider
    
    Args:
        bearer_token: LunarCrush API bearer token
        **kwargs: Additional configuration options including:
            - cache_dir: Cache directory path
            - update_interval_hours: Update frequency in hours
            - max_cache_age_days: Maximum cache age in days
        
    Returns:
        Configured LunarCrushProvider instance
    
    Example:
        >>> provider = create_provider("your_bearer_token_here")
        >>> features = provider.get_sentiment_features("DOGE/USDT", "5m", since_ms)
    """
    # Filter out kwargs that aren't valid for LunarCrushProvider
    valid_params = {
        'cache_dir', 'update_interval_hours', 'max_cache_age_days'
    }
    
    provider_kwargs = {k: v for k, v in kwargs.items() if k in valid_params}
    
    # Apply defaults for missing parameters
    for key, default_value in DEFAULT_CONFIG.items():
        if key not in provider_kwargs and key != 'rate_limits':
            provider_kwargs[key] = default_value
    
    return LunarCrushProvider(bearer_token, **provider_kwargs)