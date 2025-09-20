"""
LunarCrush FreqTrade Provider

Integrates LunarCrush sentiment data with FreqTrade's external data provider system.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from .client import LunarCrushClient
from .cache import LunarCrushCache
from .converter import TimeframeConverter

logger = logging.getLogger(__name__)


class LunarCrushProvider:
    """
    FreqTrade external data provider for LunarCrush sentiment data
    """
    
    def __init__(self,
                 bearer_token: str,
                 cache_dir: str = "external_data_providers/lunarcrush/data",
                 update_interval_hours: int = 1,
                 max_cache_age_days: int = 30):
        """
        Initialize LunarCrush provider
        
        Args:
            bearer_token: LunarCrush API bearer token
            cache_dir: Cache directory path
            update_interval_hours: How often to fetch new data (hours)
            max_cache_age_days: Maximum age in days to keep cached data
        """
        self.bearer_token = bearer_token  # Store token for test access
        self.client = LunarCrushClient(bearer_token)
        self.cache = LunarCrushCache(cache_dir)
        self.converter = TimeframeConverter()
        self.update_interval_hours = update_interval_hours
        self.max_cache_age_days = max_cache_age_days
        
        # Ensure coin list is cached
        self._ensure_coin_list()
        
        logger.info("LunarCrushProvider initialized")
    
    def _ensure_coin_list(self) -> None:
        """Ensure coin list is cached and up-to-date"""
        try:
            if self.cache.is_coin_list_stale(max_age_hours=24):
                logger.info("Refreshing stale coin list cache")
                coin_list = self.client.get_coin_list()
                if coin_list:
                    self.cache.save_coin_list(coin_list)
                else:
                    logger.warning("Failed to refresh coin list")
        except Exception as e:
            logger.error(f"Failed to ensure coin list: {e}")
    
    def get_sentiment_features(
        self,
        pair: str,
        timeframe: str,
        since_ms: int,
        candle_type: str = "",
        end_ms: int = None,
    ) -> pd.DataFrame:
        """
        Get sentiment features for a trading pair and timeframe

        This is the main entry point called by FreqTrade strategies.

        Args:
            pair: Trading pair (e.g., 'DOGE/USDT')
            timeframe: FreqTrade timeframe ('3m', '5m', '15m', '1h')
            since_ms: Start timestamp in milliseconds
            candle_type: Candle type (unused for sentiment data)
            end_ms: End timestamp in milliseconds (if None, uses current time)

        Returns:
            DataFrame with sentiment features indexed by datetime
        """
        try:
            # Extract coin symbol from pair
            coin_symbol = self._extract_coin_symbol(pair)
            if not coin_symbol:
                logger.warning(f"Could not extract coin symbol from pair: {pair}")
                return pd.DataFrame()

            # Convert to datetime range with UTC timezone
            start_time = pd.to_datetime(since_ms / 1000, unit="s", utc=True).to_pydatetime()
            end_time = (
                pd.to_datetime(end_ms / 1000, unit="s", utc=True).to_pydatetime()
                if end_ms
                else pd.to_datetime(datetime.now(), utc=True).to_pydatetime()
            )

            logger.info(
                f"Fetching sentiment features for {coin_symbol} ({timeframe}) from {start_time}"
            )

            # Get sentiment data and convert to target timeframe
            sentiment_data = self._get_sentiment_data(coin_symbol, start_time, end_time)
            if not sentiment_data:
                logger.warning(f"No sentiment data available for {coin_symbol}")
                return pd.DataFrame()

            features_df = self.converter.convert_to_timeframe(sentiment_data, timeframe)
            if features_df.empty:
                logger.warning(f"No features generated for {coin_symbol} in {timeframe}")
                return pd.DataFrame()

            # Filter to requested time range
            start_time_utc = pd.to_datetime(start_time, utc=True)
            features_df = features_df[features_df.index >= start_time_utc]

            # Convert to FreqTrade format and add prefixes
            features_df = self._convert_to_freqtrade_format(features_df)
            features_df = self._add_feature_prefixes(features_df)

            if features_df.empty:
                return pd.DataFrame()

            # Clean problematic columns
            lc_columns = [col for col in features_df.columns if col.startswith("lc_")]
            if not lc_columns:
                return features_df

            lc_data = features_df[lc_columns].ffill().bfill().fillna(0)

            # Remove columns that are all zeros or have zero variance
            valid_cols = []
            for col in lc_columns:
                col_data = lc_data[col]
                if not ((col_data == 0).all() or col_data.var() == 0):
                    valid_cols.append(col)

            if not valid_cols:
                logger.warning(
                    f"All LunarCrush features for {coin_symbol} are invalid - excluding sentiment data"
                )
                return pd.DataFrame()

            # Rebuild dataframe with only valid columns
            non_lc_cols = [col for col in features_df.columns if not col.startswith("lc_")]
            features_df = pd.concat([features_df[non_lc_cols], lc_data[valid_cols]], axis=1)

            removed_count = len(lc_columns) - len(valid_cols)
            if removed_count > 0:
                logger.info(f"Removed {removed_count} invalid columns for {coin_symbol}")

            logger.info(
                f"Generated {len(features_df)} sentiment features with {len(valid_cols)} valid columns for {coin_symbol}"
            )
            return features_df

        except Exception as e:
            logger.error(f"Failed to get sentiment features for {pair}: {e}")
            return pd.DataFrame()

    def _extract_coin_symbol(self, pair: str) -> Optional[str]:
        """
        Extract coin symbol from FreqTrade pair format
        
        Args:
            pair: Trading pair (e.g., 'DOGE/USDT', 'BTC/USD')
            
        Returns:
            Coin symbol or None if not extractable
        """
        try:
            # Handle common pair formats
            if '/' in pair:
                base_currency = pair.split('/')[0]
            elif '_' in pair:
                base_currency = pair.split('_')[0]
            else:
                # Assume the whole string is the symbol
                base_currency = pair
            
            # Clean up common prefixes/suffixes
            base_currency = base_currency.upper().strip()
            
            # Remove common exchange prefixes
            for prefix in ['BINANCE:', 'SPOT:', 'FUTURES:']:
                if base_currency.startswith(prefix):
                    base_currency = base_currency[len(prefix):]
            
            # Validate that we have a coin ID for this symbol
            coin_id = self.cache.get_coin_id(base_currency)
            if coin_id is None:
                logger.debug(f"No LunarCrush coin ID found for symbol: {base_currency}")
                return None
            
            return base_currency
            
        except Exception as e:
            logger.error(f"Failed to extract coin symbol from {pair}: {e}")
            return None
    
    def _ensure_compatible_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensure DataFrame has a compatible datetime index for FreqTrade alignment
        
        Args:
            df: DataFrame with datetime index
            
        Returns:
            DataFrame with properly formatted datetime index
        """
        try:
            if df.empty:
                return df
            
            # Ensure index is timezone-aware UTC DatetimeIndex
            if not isinstance(df.index, pd.DatetimeIndex):
                logger.warning("Converting non-DatetimeIndex to DatetimeIndex")
                df.index = pd.to_datetime(df.index, utc=True)
            elif df.index.tz is None:
                logger.debug("Localizing timezone-naive index to UTC")
                df.index = df.index.tz_localize('UTC')
            elif str(df.index.tz) != 'UTC':
                logger.debug(f"Converting from {df.index.tz} to UTC")
                df.index = df.index.tz_convert('UTC')
            
            # Ensure index name is consistent
            df.index.name = 'date'
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to ensure compatible index: {e}")
            return df
    
    def _convert_to_freqtrade_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert sentiment DataFrame to FreqTrade format:
        - Integer index (0, 1, 2, ...)
        - Datetime data in 'date' column
        
        Args:
            df: DataFrame with datetime index
            
        Returns:
            DataFrame with integer index and 'date' column
        """
        try:
            if df.empty:
                return df
            
            # Create a new DataFrame with FreqTrade format
            freqtrade_df = df.copy()
            
            # Move datetime index to 'date' column
            freqtrade_df['date'] = df.index
            
            # Reset to integer index
            freqtrade_df.reset_index(drop=True, inplace=True)
            
            return freqtrade_df
            
        except Exception as e:
            logger.error(f"Failed to convert to FreqTrade format: {e}")
            return df
    
    def _add_feature_prefixes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add 'lc_' prefix to feature columns (but not 'date' column) to avoid naming conflicts
        
        Args:
            df: DataFrame with sentiment features and date column
            
        Returns:
            DataFrame with prefixed column names
        """
        try:
            if df.empty:
                return df
            
            # Add 'lc_' prefix to all columns except 'date'
            new_columns = {}
            for col in df.columns:
                if col == 'date':
                    new_columns[col] = col  # Keep 'date' as is
                else:
                    new_columns[col] = f"lc_{col}"
            
            df = df.rename(columns=new_columns)
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to add feature prefixes: {e}")
            return df
    
    def _get_sentiment_data(self, 
                          coin_symbol: str, 
                          start_time: datetime, 
                          end_time: datetime) -> List[Dict[str, Any]]:
        """
        Get sentiment data for coin within time range
        
        Args:
            coin_symbol: Coin symbol (e.g., 'DOGE')
            start_time: Start datetime
            end_time: End datetime
            
        Returns:
            List of hourly sentiment data points
        """
        try:
            # Convert to timestamps - handle timezone-aware datetimes
            if hasattr(start_time, 'timestamp'):
                start_timestamp = int(start_time.timestamp())
            else:
                start_timestamp = int(pd.to_datetime(start_time, utc=True).timestamp())
                
            if hasattr(end_time, 'timestamp'):
                end_timestamp = int(end_time.timestamp())
            else:
                end_timestamp = int(pd.to_datetime(end_time, utc=True).timestamp())
            
            # Check for missing data ranges - skip small boundary gaps for backtesting efficiency
            is_backtesting = end_time != pd.to_datetime(datetime.now(), utc=True).to_pydatetime()
            missing_ranges = self.cache.get_missing_timerange(
                coin_symbol, start_timestamp, end_timestamp, skip_boundary_gaps=is_backtesting
            )
            
            # Fetch missing data
            for range_start, range_end in missing_ranges:
                try:
                    logger.info(f"Fetching missing data for {coin_symbol}: "
                              f"{datetime.fromtimestamp(range_start)} to {datetime.fromtimestamp(range_end)}")
                    
                    # Get coin ID
                    coin_id = self.cache.get_coin_id(coin_symbol)
                    if not coin_id:
                        logger.error(f"No coin ID found for {coin_symbol}")
                        continue
                    
                    # Fetch time series data
                    timeseries_data = self.client.get_coin_timeseries(
                        coin_id=coin_id,
                        start_time=range_start,
                        end_time=range_end
                    )
                    
                    if timeseries_data:
                        # Cache the new data
                        self.cache.save_timeseries(coin_symbol, timeseries_data)
                        logger.info(f"Cached new sentiment data for {coin_symbol}")
                    
                except Exception as e:
                    logger.error(f"Failed to fetch missing data for {coin_symbol}: {e}")
                    continue
            
            # Load complete cached data
            cached_data = self.cache.load_timeseries(coin_symbol)
            if not cached_data:
                logger.warning(f"No cached data available for {coin_symbol}")
                return []
            
            # Extract data points within time range
            all_data_points = cached_data.get('data', {})
            filtered_points = []
            
            for timestamp_str, data_point in all_data_points.items():
                timestamp = int(timestamp_str)
                if start_timestamp <= timestamp <= end_timestamp:
                    filtered_points.append(data_point)
            
            # Sort by timestamp
            filtered_points.sort(key=lambda x: x.get('time', 0))
            
            logger.info(f"Retrieved {len(filtered_points)} sentiment data points for {coin_symbol}")
            return filtered_points
            
        except Exception as e:
            logger.error(f"Failed to get sentiment data for {coin_symbol}: {e}")
            return []
    
    def get_available_pairs(self) -> List[str]:
        """
        Get list of available pairs that have LunarCrush data
        
        Returns:
            List of available pair symbols
        """
        try:
            coin_list = self.cache.load_coin_list()
            if not coin_list:
                return []
            
            coin_mapping = coin_list.get('coin_mapping', {})
            
            # Return symbols that have coin IDs
            available_pairs = []
            for symbol, coin_info in coin_mapping.items():
                if coin_info.get('id'):
                    # Format as common trading pairs
                    available_pairs.extend([
                        f"{symbol}/USDT",
                        f"{symbol}/USD",
                        f"{symbol}/BTC"
                    ])
            
            logger.info(f"Found {len(available_pairs)} available pairs")
            return available_pairs
            
        except Exception as e:
            logger.error(f"Failed to get available pairs: {e}")
            return []
    
    def get_feature_columns(self) -> List[str]:
        """
        Get list of feature columns that will be provided
        
        Returns:
            List of feature column names with 'lc_' prefix
        """
        base_features = self.converter.get_feature_columns()
        
        # Add LunarCrush prefix to avoid naming conflicts
        prefixed_features = [f"lc_{feature}" for feature in base_features]
        
        return prefixed_features
    
    def update_data(self, pairs: List[str] = None) -> Dict[str, Any]:
        """
        Update sentiment data for specified pairs
        
        Args:
            pairs: List of pairs to update, None for all cached pairs
            
        Returns:
            Dict with update statistics
        """
        try:
            stats = {
                'pairs_processed': 0,
                'data_points_added': 0,
                'errors': [],
                'updated_at': datetime.now().isoformat()
            }
            
            # Determine pairs to update
            if pairs is None:
                # Get all cached pairs
                cache_stats = self.cache.get_cache_stats()
                symbols_to_update = cache_stats.get('coins_cached', [])
            else:
                # Extract symbols from provided pairs
                symbols_to_update = []
                for pair in pairs:
                    symbol = self._extract_coin_symbol(pair)
                    if symbol:
                        symbols_to_update.append(symbol)
            
            # Update each symbol
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=self.update_interval_hours * 2)  # Some overlap
            
            for symbol in symbols_to_update:
                try:
                    data_points = self._get_sentiment_data(symbol, start_time, end_time)
                    stats['data_points_added'] += len(data_points)
                    stats['pairs_processed'] += 1
                    
                except Exception as e:
                    error_msg = f"Failed to update {symbol}: {e}"
                    stats['errors'].append(error_msg)
                    logger.error(error_msg)
            
            logger.info(f"Update completed: {stats['pairs_processed']} pairs, "
                       f"{stats['data_points_added']} data points")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to update data: {e}")
            return {'error': str(e)}
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the provider
        
        Returns:
            Dict with provider information
        """
        try:
            cache_stats = self.cache.get_cache_stats()
            
            info = {
                'provider_name': 'LunarCrush',
                'version': '1.0.0',
                'supported_timeframes': self.converter.SUPPORTED_TIMEFRAMES,
                'feature_count': len(self.get_feature_columns()),
                'cache_stats': cache_stats,
                'update_interval_hours': self.update_interval_hours,
                'rate_limits': {
                    'requests_per_minute': 10,
                    'requests_per_day': 2000
                }
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get provider info: {e}")
            return {'error': str(e)}
    
    def cleanup_old_data(self, max_age_days: int = 30) -> Dict[str, Any]:
        """
        Clean up old cached data
        
        Args:
            max_age_days: Maximum age in days to keep
            
        Returns:
            Dict with cleanup statistics
        """
        try:
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            cutoff_timestamp = int(cutoff_time.timestamp())
            
            stats = {
                'files_processed': 0,
                'data_points_removed': 0,
                'files_removed': 0
            }
            
            # Process each cached coin
            cache_stats = self.cache.get_cache_stats()
            for coin_symbol in cache_stats.get('coins_cached', []):
                try:
                    cached_data = self.cache.load_timeseries(coin_symbol)
                    if not cached_data:
                        continue
                    
                    # Filter out old data points
                    all_data = cached_data.get('data', {})
                    filtered_data = {}
                    removed_count = 0
                    
                    for timestamp_str, data_point in all_data.items():
                        timestamp = int(timestamp_str)
                        if timestamp >= cutoff_timestamp:
                            filtered_data[timestamp_str] = data_point
                        else:
                            removed_count += 1
                    
                    if removed_count > 0:
                        # Update cache with filtered data
                        cached_data['data'] = filtered_data
                        cached_data['metadata']['data_points'] = len(filtered_data)
                        cached_data['metadata']['last_cleanup'] = int(datetime.now().timestamp())
                        
                        if filtered_data:
                            # Save updated cache
                            self.cache.save_timeseries(coin_symbol, {
                                'data': list(filtered_data.values()),
                                'config': cached_data.get('config', {})
                            })
                        else:
                            # Remove empty cache file
                            self.cache.clear_cache(coin_symbol)
                            stats['files_removed'] += 1
                        
                        stats['data_points_removed'] += removed_count
                    
                    stats['files_processed'] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to cleanup data for {coin_symbol}: {e}")
                    continue
            
            logger.info(f"Cleanup completed: {stats['data_points_removed']} old data points removed")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return {'error': str(e)}


# FreqTrade external data provider entry point
def get_lunarcrush_provider(bearer_token: str, **kwargs) -> LunarCrushProvider:
    """
    Factory function for creating LunarCrush provider instance
    
    Args:
        bearer_token: LunarCrush API bearer token
        **kwargs: Additional configuration parameters
        
    Returns:
        Configured LunarCrushProvider instance
    """
    return LunarCrushProvider(bearer_token, **kwargs)