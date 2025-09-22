"""
Comprehensive tests for check_data_columns function focusing on timezone handling.
Tests various time column formats including mixed naive/tz-aware and DST transitions.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
import warnings

from iglu_python.utils import check_data_columns,set_local_tz


class TestCheckDataColumnsTimezone:
    """Test timezone handling in check_data_columns function."""

    def test_mixed_naive_and_tz_aware_times(self):
        """Test that mixed naive and timezone-aware timestamps raise ValueError."""
        # Create mixed time data - convert tz-aware to naive first
        naive_time = pd.Timestamp('2023-01-01 10:00:00')
        tz_aware_time = pd.Timestamp('2023-01-01 11:00:00', tz='UTC')
        
        data = pd.DataFrame({
            'id': ['A', 'A'],
            'time': [naive_time, tz_aware_time],
            'gl': [120, 140]
        })
        
        # Test with tz="" - should raise ValueError
        with pytest.raises(ValueError, match="Mixed naive and timezone-aware timestamps are not allowed"):
            check_data_columns(data, tz="")

    def test_mixed_naive_and_tz_aware_with_specific_tz(self):
        """Test that mixed times with specific timezone raise ValueError."""
        naive_time = pd.Timestamp('2023-01-01 10:00:00')
        tz_aware_time = pd.Timestamp('2023-01-01 11:00:00', tz='UTC')
        
        data = pd.DataFrame({
            'id': ['A', 'A'],
            'time': [naive_time, tz_aware_time],
            'gl': [120, 140]
        })
        
        # Test with specific timezone - should raise ValueError
        with pytest.raises(ValueError, match="Mixed naive and timezone-aware timestamps are not allowed"):
            check_data_columns(data, tz="US/Eastern")

    def test_naive_times_crossing_dst_spring_forward(self):
        """Test naive timestamps crossing DST spring forward transition."""
        local_timezone = "US/Eastern"
        set_local_tz(local_timezone)
        # DST spring forward: 2 AM becomes 3 AM (hour is skipped)
        # March 12, 2023: 2:00 AM EST -> 3:00 AM EDT
        times = [
            '2023-03-12 01:30:00',  # Before DST
            '2023-03-12 01:45:00',  # Before DST
            '2023-03-12 02:00:00',  # during DST switch
            '2023-03-12 02:15:00',  # during DST switch
            '2023-03-12 02:30:00',  # during DST switch
            '2023-03-12 02:45:00',  # during DST switch
            '2023-03-12 03:00:00',  # after DST switch (2:00 AM doesn't exist)
            '2023-03-12 03:15:00',  # After DST
        ]
        
        data = pd.DataFrame({
            'id': ['A'] * 8,
            'time': times,
            'gl': [120, 125, 130, 135, 140, 145, 150, 155]
        })
        
        # Test with tz=""
        result = check_data_columns(data, tz="")

        assert len(result) == 8
        # Should handle DST transition
        assert result['time'].dt.tz is not None
        # all tz have to be the same
        tz_list = [t.tz for t in result['time']]
        assert len(set(tz_list)) == 1
        assert result['gl'].tolist() == [120, 125, 130, 135, 140, 145, 150, 155]
        # Assert all data['time'] are 15 min apart
        time_diffs = result['time'].sort_values().diff().dropna()
        # All diffs should be 15 minutes (900 seconds)
        assert all(td.total_seconds() == 900 for td in time_diffs)
        

    def test_naive_times_crossing_dst_fall_back(self):
        """Test naive timestamps crossing DST fall back transition."""
        local_timezone = "US/Eastern"
        set_local_tz(local_timezone)
        # DST fall back: 2 AM becomes 1 AM (hour is repeated)
        # November 5, 2023: 2:00 AM EDT -> 1:00 AM EST
        times = [
            '2023-11-05 00:30:00',  # Before DST
            '2023-11-05 00:45:00',  # Before DST
            '2023-11-05 01:00:00',  # during DST switch
            '2023-11-05 01:15:00',  # during DST switch
            '2023-11-05 01:30:00',  # First occurrence of 1:30 AM
            '2023-11-05 01:45:00',  # First occurrence of 1:30 AM
            '2023-11-05 02:00:00',  # after DST switch
            '2023-11-05 02:15:00',  # after DST switch
        ]
        
        data = pd.DataFrame({
            'id': ['A'] * 8,
            'time': times,
            'gl': [120, 125, 130, 135, 140, 145, 150, 155]
        })
        
        # Test with tz=""
        result = check_data_columns(data)
        
        # Should handle DST transition (ambiguous times become NaT)
        assert result['time'].dt.tz is not None
        # all tz have to be the same
        tz_list = [t.tz for t in result['time']]
        assert len(set(tz_list)) == 1
        # Assert all data['time'] are 15 min apart
        time_diffs = result['time'].sort_values().diff().dropna()
        # All diffs should be 15 minutes (900 seconds)
        assert all(td.total_seconds() == 900 for td in time_diffs)

    def test_naive_times_with_tz_none(self):
        """Test naive timestamps with tz=None (should be treated same as tz="")."""
        times = [
            '2023-01-01 10:00:00',
            '2023-01-01 11:00:00',
            '2023-01-01 12:00:00',
        ]
        
        data = pd.DataFrame({
            'id': ['A'] * 3,
            'time': times,
            'gl': [120, 125, 130]
        })
        
        # Test with tz="" (default)
        result = check_data_columns(data, tz="")
        
        # Should convert to UTC
        assert result['time'].dt.tz is not None
        assert len(result) == 3

    def test_naive_times_with_specific_timezone(self):
        """Test naive timestamps with specific timezone."""
        times = [
            '2023-01-01 10:00:00',
            '2023-01-01 11:00:00',
            '2023-01-01 12:00:00',
        ]
        
        data = pd.DataFrame({
            'id': ['A'] * 3,
            'time': times,
            'gl': [120, 125, 130]
        })
        
        # Test with specific timezone
        result = check_data_columns(data, tz="US/Pacific")
        
        # Should convert to US/Pacific
        assert result['time'].dt.tz is not None
        # Check that utcoffset for the first item is the same as 'US/Pacific'
        import pytz
        first_time = result['time'].iloc[0]
        pacific = pytz.timezone('US/Pacific')
        # Localize the naive time to US/Pacific for comparison
        naive_time = pd.to_datetime('2023-01-01 10:00:00')
        pacific_offset = pacific.utcoffset(naive_time)
        assert first_time.utcoffset() == pacific_offset
        assert len(result) == 3
        # all tz have to be the same
        tz_list = [t.tz for t in result['time']]
        assert len(set(tz_list)) == 1

    def test_string_times_with_timezone_info(self):
        """Test string timestamps that include timezone information."""
        local_timezone = "US/Pacific"
        set_local_tz(local_timezone)
        times = [
            '2023-01-01 10:00:00',  # Naive string
            '2023-01-01 11:00:00',  # Naive string
            '2023-01-01 12:00:00',  # Naive string
        ]
        
        data = pd.DataFrame({
            'id': ['A'] * 3,
            'time': times,
            'gl': [120, 125, 130]
        })
        
        # Test with tz=""
        result = check_data_columns(data, tz="")
        
        # Should handle timezone-aware strings
        assert result['time'].dt.tz is not None
        # Check that utcoffset for the first item is the same as 'US/Pacific'
        import pytz
        first_time = result['time'].iloc[0]
        pacific = pytz.timezone('US/Pacific')
        # Localize the naive time to US/Pacific for comparison
        naive_time = pd.to_datetime('2023-01-01 10:00:00')
        pacific_offset = pacific.utcoffset(naive_time)
        assert first_time.utcoffset() == pacific_offset
        assert len(result) == 3
        # all tz have to be the same
        tz_list = [t.tz for t in result['time']]
        assert len(set(tz_list)) == 1


    def test_mixed_time_formats_with_dst(self):
        """Test mixed time formats crossing DST transitions."""
        local_timezone = "US/Eastern"
        set_local_tz(local_timezone)
        # Mix of naive and timezone-aware times around DST
        times = [
            pd.Timestamp('2023-03-12 00:00:00'),
            pd.Timestamp('2023-03-12 01:00:00'),  # Naive
            pd.Timestamp('2023-03-12 03:00:00', tz='UTC').tz_localize(None),  # TZ-aware converted to naive
            '2023-03-12 04:00:00',  # String
        ]
        
        data = pd.DataFrame({
            'id': ['A'] * 4,
            'time': times,
            'gl': [120, 125, 130, 135]
        })
        
        # Test with tz=""
        result = check_data_columns(data, tz="")
        
        # Should handle mixed formats
        assert result['time'].dt.tz is not None
        # Check that utcoffset for the first item is the same as 'US/Pacific'
        import pytz
        first_time = result['time'].iloc[0]
        local = pytz.timezone(local_timezone)
        # Localize the naive time to US/Pacific for comparison
        naive_time = pd.to_datetime('2023-01-01 10:00:00')
        local_offset = local.utcoffset(naive_time)
        assert first_time.utcoffset() == local_offset

    def test_invalid_timezone_handling(self):
        """Test handling of invalid timezone strings."""
        times = [
            '2023-01-01 10:00:00',
            '2023-01-01 11:00:00',
        ]
        
        data = pd.DataFrame({
            'id': ['A'] * 2,
            'time': times,
            'gl': [120, 125]
        })
        
        # Test with invalid timezone
        with pytest.raises(Exception):  # Should raise an error
            check_data_columns(data, tz="Invalid/Timezone")

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        data = pd.DataFrame(columns=['id', 'time', 'gl'])
        
        with pytest.raises(ValueError, match="Data frame is empty"):
            check_data_columns(data)

    def test_missing_columns(self):
        """Test handling of missing required columns."""
        data = pd.DataFrame({
            'id': ['A'],
            'gl': [120]
            # Missing 'time' column
        })
        
        with pytest.raises(ValueError, match="Missing required columns"):
            check_data_columns(data)

    def test_non_numeric_glucose_values(self):
        """Test handling of non-numeric glucose values."""
        data = pd.DataFrame({
            'id': ['A'],
            'time': ['2023-01-01 10:00:00'],
            'gl': ['not_a_number']
        })
        
        with pytest.raises(ValueError, match="Column 'gl' must be numeric"):
            check_data_columns(data)

    def test_all_na_glucose_values(self):
        """Test handling of all NaN glucose values."""
        data = pd.DataFrame({
            'id': ['A'],
            'time': ['2023-01-01 10:00:00'],
            'gl': [np.nan]
        })
        
        with pytest.raises(ValueError, match="Data contains no glucose values"):
            check_data_columns(data)

if __name__ == "__main__":
    pytest.main([__file__])
