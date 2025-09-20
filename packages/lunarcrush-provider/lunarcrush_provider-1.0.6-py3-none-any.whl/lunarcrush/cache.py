"""
LunarCrush Cache Manager

Handles persistent storage and retrieval of coin mappings and time series data.
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LunarCrushCache:
    """
    Persistent JSON cache for LunarCrush data
    """
    
    def __init__(self, cache_dir: str = "external_data_providers/lunarcrush/data"):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory path for cache storage
        """
        self.cache_dir = Path(cache_dir)
        self.timeseries_dir = self.cache_dir / "timeseries"
        self.coin_list_path = self.cache_dir / "coin_list.json"
        
        # Ensure cache directories exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeseries_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"LunarCrush cache initialized: {self.cache_dir}")
    
    def _get_timeseries_path(self, coin_symbol: str) -> Path:
        """Get path for coin timeseries cache file"""
        return self.timeseries_dir / f"{coin_symbol.lower()}_1h.json"
    
    def save_coin_list(self, coin_list_data: Dict[str, Any]) -> None:
        """
        Save coin list data to cache
        
        Args:
            coin_list_data: Raw response from coins/list/v1 endpoint
        """
        try:
            # Extract and index coins by symbol for easy lookup
            coins = coin_list_data.get('data', [])
            
            coin_mapping = {}
            for coin in coins:
                symbol = coin.get('symbol', '').upper()
                if symbol:
                    coin_mapping[symbol] = {
                        'id': coin.get('id'),
                        'symbol': symbol,
                        'name': coin.get('name', ''),
                        'topic': coin.get('topic', ''),
                        'market_cap_rank': coin.get('market_cap_rank'),
                        'cached_at': int(time.time())
                    }
            
            cache_data = {
                'total_coins': len(coins),
                'cached_at': int(time.time()),
                'source_config': coin_list_data.get('config', {}),
                'coin_mapping': coin_mapping
            }
            
            with open(self.coin_list_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"Cached {len(coin_mapping)} coin mappings")
            
        except Exception as e:
            logger.error(f"Failed to save coin list: {e}")
            raise
    
    def load_coin_list(self) -> Optional[Dict[str, Any]]:
        """
        Load coin list from cache
        
        Returns:
            Cached coin data or None if not found
        """
        try:
            if not self.coin_list_path.exists():
                logger.info("No cached coin list found")
                return None
            
            with open(self.coin_list_path, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Loaded {data.get('total_coins', 0)} cached coins")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load coin list: {e}")
            return None
    
    def get_coin_id(self, symbol: str) -> Optional[int]:
        """
        Get coin ID for symbol from cache
        
        Args:
            symbol: Coin symbol (e.g., 'BTC', 'ETH', 'DOGE')
            
        Returns:
            Coin ID or None if not found
        """
        coin_list = self.load_coin_list()
        if not coin_list:
            return None
        
        coin_mapping = coin_list.get('coin_mapping', {})
        coin_info = coin_mapping.get(symbol.upper())
        
        if coin_info:
            return coin_info.get('id')
        
        logger.warning(f"Coin ID not found for symbol: {symbol}")
        return None
    
    def is_coin_list_stale(self, max_age_hours: int = 24) -> bool:
        """
        Check if coin list cache is stale
        
        Args:
            max_age_hours: Maximum age in hours before considering stale
            
        Returns:
            True if cache is stale or missing
        """
        coin_list = self.load_coin_list()
        if not coin_list:
            return True
        
        cached_at = coin_list.get('cached_at', 0)
        max_age_seconds = max_age_hours * 3600
        
        return (int(time.time()) - cached_at) > max_age_seconds
    
    def save_timeseries(self, coin_symbol: str, timeseries_data: Dict[str, Any]) -> None:
        """
        Save or update timeseries data for a coin
        
        Args:
            coin_symbol: Coin symbol (e.g., 'DOGE')
            timeseries_data: Raw response from time-series endpoint
        """
        try:
            cache_path = self._get_timeseries_path(coin_symbol)
            
            # Load existing cache if present
            existing_data = {}
            if cache_path.exists():
                with open(cache_path, 'r') as f:
                    existing_data = json.load(f)
            
            # Extract new data points
            new_data_points = timeseries_data.get('data', [])
            config = timeseries_data.get('config', {})
            
            # Initialize cache structure
            if 'metadata' not in existing_data:
                existing_data = {
                    'metadata': {
                        'coin_id': config.get('id', '').replace('coins:', ''),
                        'symbol': coin_symbol.upper(),
                        'name': config.get('name', ''),
                        'topic': config.get('topic', ''),
                        'last_update': int(time.time()),
                        'data_points': 0
                    },
                    'data': {}
                }
            
            # Update/add new data points (indexed by timestamp)
            for data_point in new_data_points:
                timestamp = str(data_point.get('time', 0))
                if timestamp != '0':
                    existing_data['data'][timestamp] = data_point
            
            # Update metadata
            existing_data['metadata']['last_update'] = int(time.time())
            existing_data['metadata']['data_points'] = len(existing_data['data'])
            
            # Sort data by timestamp for efficient access
            sorted_data = dict(sorted(existing_data['data'].items(), key=lambda x: int(x[0])))
            existing_data['data'] = sorted_data
            
            # Save updated cache
            with open(cache_path, 'w') as f:
                json.dump(existing_data, f, separators=(',', ':'))  # Compact format
            
            logger.info(f"Cached {len(new_data_points)} new data points for {coin_symbol}")
            
        except Exception as e:
            logger.error(f"Failed to save timeseries for {coin_symbol}: {e}")
            raise
    
    def load_timeseries(self, coin_symbol: str) -> Optional[Dict[str, Any]]:
        """
        Load cached timeseries data for a coin
        
        Args:
            coin_symbol: Coin symbol (e.g., 'DOGE')
            
        Returns:
            Cached timeseries data or None if not found
        """
        try:
            cache_path = self._get_timeseries_path(coin_symbol)
            
            if not cache_path.exists():
                logger.info(f"No cached timeseries found for {coin_symbol}")
                return None
            
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            data_points = data.get('metadata', {}).get('data_points', 0)
            logger.info(f"Loaded {data_points} cached data points for {coin_symbol}")
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to load timeseries for {coin_symbol}: {e}")
            return None
    
    def get_missing_timerange(self, coin_symbol: str, start_time: int, end_time: int,
                            skip_boundary_gaps: bool = False) -> List[Tuple[int, int]]:
        """
        Identify missing time ranges for a coin with intelligent gap detection
        
        Args:
            coin_symbol: Coin symbol
            start_time: Desired start timestamp
            end_time: Desired end timestamp
            skip_boundary_gaps: If True, skip small gaps at boundaries (useful for backtesting)
            
        Returns:
            List of (start, end) tuples for missing ranges
        """
        cached_data = self.load_timeseries(coin_symbol)
        if not cached_data:
            return [(start_time, end_time)]
        
        # Get cached timestamps
        cached_timestamps = set(int(ts) for ts in cached_data.get('data', {}).keys())
        
        # Debug logging to understand cache coverage
        if cached_timestamps:
            cached_min = min(cached_timestamps)
            cached_max = max(cached_timestamps)
            logger.debug(f"Cache for {coin_symbol}: {len(cached_timestamps)} points from "
                        f"{datetime.fromtimestamp(cached_min)} to {datetime.fromtimestamp(cached_max)}")
            logger.debug(f"Requested range: {datetime.fromtimestamp(start_time)} to {datetime.fromtimestamp(end_time)}")
            
            # # Intelligent boundary checking
            # overlap_start = max(start_time, cached_min - 3600)  # Allow 1 hour before cache
            # overlap_end = min(end_time, cached_max + 3600)     # Allow 1 hour after cache
            
            # If request is mostly outside cache boundaries, be smarter
            if start_time < cached_min - 24*3600:  # More than 1 day before cache
                logger.info(f"Request starts {(cached_min - start_time)/3600:.1f} hours before cache. "
                           f"Using cache boundary as effective start.")
                effective_start = cached_min
            else:
                effective_start = start_time
                
            if end_time > cached_max + 24*3600:  # More than 1 day after cache
                logger.info(f"Request ends {(end_time - cached_max)/3600:.1f} hours after cache. "
                           f"Using cache boundary as effective end.")
                effective_end = cached_max
            else:
                effective_end = end_time
        else:
            effective_start = start_time
            effective_end = end_time
        
        # Find missing hourly timestamps within the effective range
        missing_ranges = []
        current_time = effective_start
        range_start = None
        
        # Align to hourly boundaries
        aligned_start = (effective_start // 3600) * 3600
        current_time = aligned_start
        
        while current_time <= effective_end:
            if current_time not in cached_timestamps:
                if range_start is None:
                    range_start = current_time
            else:
                if range_start is not None:
                    missing_ranges.append((range_start, current_time - 3600))
                    range_start = None
            
            current_time += 3600  # 1 hour intervals
        
        # Handle final range
        if range_start is not None:
            missing_ranges.append((range_start, effective_end))
        
        # Filter out boundary gaps for backtesting efficiency if requested
        filtered_ranges = []
        for range_start_ts, range_end_ts in missing_ranges:
            gap_hours = (range_end_ts - range_start_ts) / 3600
            
            # Check if this is a boundary gap (starts at beginning or ends at end)
            is_start_boundary = range_start_ts == aligned_start
            is_end_boundary = range_end_ts == effective_end
            is_boundary_gap = is_start_boundary or is_end_boundary
            
            # Skip boundary gaps for backtesting efficiency
            if skip_boundary_gaps and gap_hours <= 6 and is_boundary_gap:
                logger.info(f"Skipping boundary gap for backtesting efficiency: {gap_hours:.1f} hours "
                           f"(start_boundary: {is_start_boundary}, end_boundary: {is_end_boundary})")
                continue
            elif not skip_boundary_gaps and gap_hours < 2 and is_boundary_gap:
                logger.debug(f"Skipping tiny boundary gap: {gap_hours:.1f} hours")
                continue
                
            filtered_ranges.append((range_start_ts, range_end_ts))
        
        # Enhanced debug logging for missing ranges
        if filtered_ranges:
            total_missing = sum((end - start) / 3600 for start, end in filtered_ranges)
            logger.debug(f"Found {len(filtered_ranges)} significant gaps for {coin_symbol} "
                        f"(total: {total_missing:.1f} hours):")
            for i, (range_start_ts, range_end_ts) in enumerate(filtered_ranges):
                hours_missing = (range_end_ts - range_start_ts) / 3600
                logger.debug(f"  Gap {i+1}: {datetime.fromtimestamp(range_start_ts)} to "
                           f"{datetime.fromtimestamp(range_end_ts)} ({hours_missing:.1f} hours)")
        else:
            logger.debug(f"No significant gaps found for {coin_symbol}")
            
        return filtered_ranges
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dict with cache statistics
        """
        stats = {
            'cache_dir': str(self.cache_dir),
            'coin_list_cached': self.coin_list_path.exists(),
            'timeseries_files': 0,
            'total_data_points': 0,
            'coins_cached': []
        }
        
        try:
            # Count timeseries files
            for file_path in self.timeseries_dir.glob("*_1h.json"):
                stats['timeseries_files'] += 1
                coin_symbol = file_path.stem.replace('_1h', '').upper()
                stats['coins_cached'].append(coin_symbol)
                
                # Count data points
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        points = data.get('metadata', {}).get('data_points', 0)
                        stats['total_data_points'] += points
                except Exception:
                    pass
            
            # Coin list info
            if stats['coin_list_cached']:
                coin_list = self.load_coin_list()
                if coin_list:
                    stats['total_coins_available'] = coin_list.get('total_coins', 0)
                    stats['coin_list_age_hours'] = (int(time.time()) - coin_list.get('cached_at', 0)) / 3600
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
        
        return stats
    
    def clear_cache(self, coin_symbol: Optional[str] = None) -> None:
        """
        Clear cache data
        
        Args:
            coin_symbol: Specific coin to clear, or None for all data
        """
        try:
            if coin_symbol:
                # Clear specific coin
                cache_path = self._get_timeseries_path(coin_symbol)
                if cache_path.exists():
                    cache_path.unlink()
                    logger.info(f"Cleared cache for {coin_symbol}")
            else:
                # Clear all cache
                if self.coin_list_path.exists():
                    self.coin_list_path.unlink()
                
                for file_path in self.timeseries_dir.glob("*_1h.json"):
                    file_path.unlink()
                
                logger.info("Cleared all cache data")
                
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            raise