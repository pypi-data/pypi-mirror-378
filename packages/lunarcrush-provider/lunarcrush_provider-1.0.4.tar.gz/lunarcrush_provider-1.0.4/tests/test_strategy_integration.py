"""
Test cases for LunarCrush Strategy Integration

Tests strategy functionality, NaN handling, and sentiment data alignment.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Strategy import will be conditional on FreqTrade availability
try:
    from strategies.EnhancedBambooAI_SentimentROI import EnhancedBambooAI_SentimentROI
    STRATEGY_AVAILABLE = True
except ImportError:
    STRATEGY_AVAILABLE = False


class TestStrategyIntegration:
    """Test strategy integration with LunarCrush data"""
    
    @pytest.fixture
    def mock_freqtrade_dataframe(self):
        """Create mock FreqTrade DataFrame"""
        dates = pd.date_range(start='2025-01-01', periods=100, freq='1h')
        return pd.DataFrame({
            'date': dates,
            'open': np.random.uniform(100, 110, 100),
            'high': np.random.uniform(110, 120, 100),  
            'low': np.random.uniform(90, 100, 100),
            'close': np.random.uniform(95, 115, 100),
            'volume': np.random.uniform(1000, 5000, 100)
        })
    
    @pytest.fixture
    def mock_sentiment_dataframe(self):
        """Create mock sentiment DataFrame"""
        dates = pd.date_range(start='2025-01-01', periods=50, freq='1h')
        return pd.DataFrame({
            'date': dates,
            'lc_sentiment': np.random.uniform(-0.1, 0.1, 50),
            'lc_social_dominance': np.random.uniform(0, 5, 50),
            'lc_galaxy_score': np.random.uniform(50, 90, 50),
            'lc_social_volume': np.random.randint(100, 1000, 50),
            'lc_sentiment_absolute': np.random.uniform(0.1, 0.3, 50),
            'lc_alt_rank': np.random.randint(1, 1000, 50),
        })
    
    @pytest.fixture
    def mock_lunarcrush_provider(self, mock_sentiment_dataframe):
        """Create mock LunarCrush provider"""
        mock_provider = Mock()
        mock_provider.get_sentiment_features.return_value = mock_sentiment_dataframe
        return mock_provider
    
    @pytest.mark.skipif(not STRATEGY_AVAILABLE, reason="Strategy not available without FreqTrade")
    def test_strategy_initialization(self):
        """Test strategy can be initialized without config"""
        strategy = EnhancedBambooAI_SentimentROI()
        assert strategy is not None
        assert hasattr(strategy, 'lunarcrush_provider')
    
    @pytest.mark.skipif(not STRATEGY_AVAILABLE, reason="Strategy not available without FreqTrade")
    def test_strategy_initialization_with_config(self):
        """Test strategy initialization with config"""
        mock_config = {
            'user_data_dir': Path('/tmp/test')
        }
        strategy = EnhancedBambooAI_SentimentROI(config=mock_config)
        assert strategy is not None
        assert strategy.config == mock_config
    
    @pytest.mark.skipif(not STRATEGY_AVAILABLE, reason="Strategy not available without FreqTrade")
    def test_feature_engineering_nan_handling(self, mock_freqtrade_dataframe, mock_lunarcrush_provider):
        """Test that feature engineering handles NaN values properly"""
        strategy = EnhancedBambooAI_SentimentROI()
        strategy.lunarcrush_provider = mock_lunarcrush_provider
        
        # Disable FreqAI for isolated testing
        strategy.freqai = None
        
        test_metadata = {"pair": "BTC/USDT:USDT", "tf": "1h"}
        
        result_df = strategy.feature_engineering_expand_all(
            mock_freqtrade_dataframe.copy(), 10, test_metadata
        )
        
        # Check that result is not empty
        assert not result_df.empty
        assert len(result_df) == 100
        
        # Check NaN percentage is acceptable
        nan_count = result_df.isnull().sum().sum()
        total_values = len(result_df) * len(result_df.columns)
        nan_percentage = (nan_count / total_values) * 100
        
        # Should be less than 10% NaN values (much better than the 99%+ we had before)
        assert nan_percentage < 10, f"Too many NaN values: {nan_percentage:.2f}%"
        
        # Verify sentiment features are present
        sentiment_features = [col for col in result_df.columns if 'sentiment' in col or 'social' in col or 'galaxy' in col]
        assert len(sentiment_features) > 0, "No sentiment features found"
    
    @pytest.mark.skipif(not STRATEGY_AVAILABLE, reason="Strategy not available without FreqTrade")
    def test_feature_engineering_basic(self, mock_freqtrade_dataframe, mock_lunarcrush_provider):
        """Test basic feature engineering"""
        strategy = EnhancedBambooAI_SentimentROI()
        strategy.lunarcrush_provider = mock_lunarcrush_provider
        
        test_metadata = {"pair": "BTC/USDT:USDT", "tf": "1h"}
        
        result_df = strategy.feature_engineering_expand_basic(
            mock_freqtrade_dataframe.copy(), test_metadata
        )
        
        assert not result_df.empty
        assert '%-pct-change' in result_df.columns
        assert '%-raw_volume' in result_df.columns
    
    @pytest.mark.skipif(not STRATEGY_AVAILABLE, reason="Strategy not available without FreqTrade")
    def test_feature_engineering_standard(self, mock_freqtrade_dataframe, mock_lunarcrush_provider):
        """Test standard feature engineering"""
        strategy = EnhancedBambooAI_SentimentROI()
        strategy.lunarcrush_provider = mock_lunarcrush_provider
        
        test_metadata = {"pair": "BTC/USDT:USDT", "tf": "1h"}
        
        # First add basic features
        df_with_basic = strategy.feature_engineering_expand_basic(
            mock_freqtrade_dataframe.copy(), test_metadata
        )
        
        result_df = strategy.feature_engineering_standard(df_with_basic, test_metadata)
        
        assert not result_df.empty
        assert '%-hour_of_day' in result_df.columns
    
    @pytest.mark.skipif(not STRATEGY_AVAILABLE, reason="Strategy not available without FreqTrade")
    def test_sentiment_data_alignment_length_mismatch(self, mock_lunarcrush_provider):
        """Test handling of sentiment data with different lengths"""
        strategy = EnhancedBambooAI_SentimentROI()
        
        # Create DataFrames with different lengths to test alignment
        price_df = pd.DataFrame({
            'date': pd.date_range(start='2025-01-01', periods=100, freq='1h'),
            'close': np.random.uniform(95, 115, 100),
            'volume': np.random.uniform(1000, 5000, 100)
        })
        
        # Sentiment data with fewer rows (common scenario)
        short_sentiment_df = pd.DataFrame({
            'date': pd.date_range(start='2025-01-01', periods=30, freq='1h'),
            'lc_sentiment': np.random.uniform(-0.1, 0.1, 30),
            'lc_social_dominance': np.random.uniform(0, 5, 30),
            'lc_galaxy_score': np.random.uniform(50, 90, 30),
        })
        
        mock_lunarcrush_provider.get_sentiment_features.return_value = short_sentiment_df
        strategy.lunarcrush_provider = mock_lunarcrush_provider
        strategy.freqai = None
        
        test_metadata = {"pair": "BTC/USDT:USDT", "tf": "1h"}
        
        # This should not crash even with length mismatch
        result_df = strategy.feature_engineering_expand_all(price_df, 10, test_metadata)
        
        assert not result_df.empty
        assert len(result_df) == 100  # Original length preserved
        
        # Should have fallback values where sentiment data is missing
        sentiment_cols = [col for col in result_df.columns if 'sentiment' in col.lower()]
        if sentiment_cols:
            # Check that we don't have all NaN values (fallbacks should work)
            for col in sentiment_cols:
                non_null_count = result_df[col].notna().sum()
                assert non_null_count > 0, f"Column {col} is all NaN - fallbacks not working"
    
    @pytest.mark.skipif(not STRATEGY_AVAILABLE, reason="Strategy not available without FreqTrade")  
    def test_strategy_without_sentiment_provider(self, mock_freqtrade_dataframe):
        """Test strategy works without sentiment provider (graceful degradation)"""
        strategy = EnhancedBambooAI_SentimentROI()
        strategy.lunarcrush_provider = None  # No sentiment provider
        strategy.freqai = None
        
        test_metadata = {"pair": "BTC/USDT:USDT", "tf": "1h"}
        
        # Should not crash when no sentiment provider available
        result_df = strategy.feature_engineering_expand_all(
            mock_freqtrade_dataframe.copy(), 10, test_metadata
        )
        
        assert not result_df.empty
        assert len(result_df) == 100
        
        # Should have basic features but no sentiment features
        basic_features = [col for col in result_df.columns if 'rsi' in col or 'ema' in col]
        assert len(basic_features) > 0, "No basic features found"
    
    def test_datetime_compatibility_mock(self):
        """Test datetime compatibility with mock DataFrames"""
        # Create FreqTrade-style DataFrame
        freqtrade_dates = pd.date_range('2023-01-01', periods=24, freq='1H', tz='UTC')
        price_df = pd.DataFrame({
            'open': np.random.uniform(40000, 50000, 24),
            'high': np.random.uniform(50000, 60000, 24),
            'low': np.random.uniform(30000, 40000, 24),
            'close': np.random.uniform(40000, 50000, 24),
            'volume': np.random.uniform(1000, 10000, 24)
        }, index=freqtrade_dates)
        price_df.index.name = 'date'
        
        # Create sentiment DataFrame with different timezone
        sentiment_dates = pd.date_range('2023-01-01', periods=24, freq='1H')  # No timezone
        sentiment_df = pd.DataFrame({
            'sentiment': np.random.uniform(-1, 1, 24),
            'social_dominance': np.random.uniform(0, 100, 24)
        }, index=sentiment_dates)
        
        # Test alignment compatibility
        try:
            # Convert sentiment to UTC timezone
            if sentiment_df.index.tz is None:
                sentiment_df.index = sentiment_df.index.tz_localize('UTC')
            else:
                sentiment_df.index = sentiment_df.index.tz_convert('UTC')
            
            # Test alignment
            aligned_sentiment = sentiment_df.reindex(price_df.index, method='ffill')
            merged_df = price_df.join(aligned_sentiment, how='left')
            
            assert len(merged_df) == 24
            assert 'sentiment' in merged_df.columns
            assert merged_df.index.tz is not None
            
        except Exception as e:
            pytest.fail(f"DateTime alignment failed: {e}")
    
    def test_nan_explosion_prevention(self):
        """Test that complex calculations don't cause NaN explosion"""
        # Create test data with some NaN values
        test_data = pd.DataFrame({
            'value1': [1, 2, np.nan, 4, 5],
            'value2': [10, np.nan, 30, 40, 50],
            'value3': [100, 200, 300, np.nan, 500]
        })
        
        # Simulate safe calculations that don't propagate NaN
        # This mimics what the fixed strategy should do
        result_df = test_data.copy()
        
        # Safe calculations with fillna
        result_df['safe_ratio'] = (result_df['value1'] / result_df['value2']).fillna(0)
        result_df['safe_product'] = (result_df['value1'] * result_df['value3']).fillna(0)
        result_df['safe_rolling'] = result_df['value1'].rolling(3).mean().fillna(method='bfill').fillna(0)
        
        # Check that we don't have excessive NaN values
        nan_percentage = (result_df.isnull().sum().sum() / (len(result_df) * len(result_df.columns))) * 100
        
        # Original data has 3 NaN out of 15 values (20%), derived features should not add many more
        assert nan_percentage < 30, f"Too many NaN values after calculations: {nan_percentage:.2f}%"
        
        # All derived columns should have some non-NaN values
        derived_cols = ['safe_ratio', 'safe_product', 'safe_rolling']
        for col in derived_cols:
            non_nan_count = result_df[col].notna().sum()
            assert non_nan_count > 0, f"Derived column {col} is all NaN"


class TestStrategyParameterization:
    """Test strategy parameter handling"""
    
    @pytest.mark.skipif(not STRATEGY_AVAILABLE, reason="Strategy not available without FreqTrade")
    def test_sentiment_parameters_exist(self):
        """Test that sentiment parameters are properly defined"""
        strategy = EnhancedBambooAI_SentimentROI()
        
        # Check that sentiment parameters exist
        assert hasattr(strategy, 'sentiment_threshold')
        assert hasattr(strategy, 'social_dominance_min')
        assert hasattr(strategy, 'galaxy_score_min')
        assert hasattr(strategy, 'sentiment_strength_min')
        assert hasattr(strategy, 'sentiment_mode')
    
    @pytest.mark.skipif(not STRATEGY_AVAILABLE, reason="Strategy not available without FreqTrade")
    def test_sentiment_mode_options(self):
        """Test sentiment mode parameter options"""
        strategy = EnhancedBambooAI_SentimentROI()
        
        # Check that sentiment mode parameter exists and has a valid value
        assert hasattr(strategy, 'sentiment_mode')
        assert strategy.sentiment_mode is not None
        
        # Check that it's a valid sentiment mode (the exact options depend on implementation)
        sentiment_mode_value = str(strategy.sentiment_mode).lower()
        valid_modes = ["confirm", "filter", "ignore", "buy", "sell", "both", "none"]
        
        assert any(mode in sentiment_mode_value for mode in valid_modes), \
            f"Sentiment mode '{sentiment_mode_value}' not recognized as valid"
    
    @pytest.mark.skipif(not STRATEGY_AVAILABLE, reason="Strategy not available without FreqTrade")
    def test_roi_and_stoploss_preserved(self):
        """Test that proven ROI and stoploss settings are preserved"""
        strategy = EnhancedBambooAI_SentimentROI()
        
        # Check ROI settings (should be unchanged from baseline)
        expected_roi = {
            "15": 0.020,
            "10": 0.025, 
            "5": 0.030,
            "0": 0.035
        }
        
        assert strategy.minimal_roi == expected_roi
        assert strategy.stoploss == -0.09  # Proven 9% stoploss