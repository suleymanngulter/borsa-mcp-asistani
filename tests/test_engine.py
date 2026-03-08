import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from engine import calculate_change


class TestEngine:
    """Test cases for engine functions."""
    
    def test_calculate_change_positive(self):
        """Test calculating positive change."""
        result = calculate_change(110.0, 100.0)
        assert result == 10.0
    
    def test_calculate_change_negative(self):
        """Test calculating negative change."""
        result = calculate_change(90.0, 100.0)
        assert result == -10.0
    
    def test_calculate_change_zero_purchase(self):
        """Test calculating change with zero purchase price."""
        result = calculate_change(100.0, 0.0)
        assert result == 0.0
    
    def test_calculate_change_zero_current(self):
        """Test calculating change with zero current price."""
        result = calculate_change(0.0, 100.0)
        assert result == -100.0
    
    def test_calculate_change_same_price(self):
        """Test calculating change with same price."""
        result = calculate_change(100.0, 100.0)
        assert result == 0.0
