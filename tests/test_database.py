import pytest
import os
import tempfile
import sys
from datetime import date

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import BorsaDB


class TestBorsaDB:
    """Test cases for BorsaDB class."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        db = BorsaDB(db_path=path)
        yield db
        os.unlink(path)
    
    def test_add_asset(self, temp_db):
        """Test adding an asset to watchlist."""
        temp_db.add_asset("THYAO", "hisse", 150.0, 5.0)
        asset = temp_db.get_asset("THYAO")
        assert asset is not None
        assert asset[0] == "THYAO"
        assert asset[1] == "hisse"
        assert asset[2] == 150.0
        assert asset[3] == 5.0
    
    def test_add_duplicate_asset(self, temp_db):
        """Test that adding duplicate asset updates it."""
        temp_db.add_asset("THYAO", "hisse", 150.0, 5.0)
        temp_db.add_asset("THYAO", "hisse", 160.0, 6.0)
        asset = temp_db.get_asset("THYAO")
        assert asset[2] == 160.0
        assert asset[3] == 6.0
    
    def test_get_all_assets(self, temp_db):
        """Test retrieving all assets."""
        temp_db.add_asset("THYAO", "hisse", 150.0, 5.0)
        temp_db.add_asset("GMR", "fon", 10.0, 3.0)
        assets = temp_db.get_all_assets()
        assert len(assets) == 2
    
    def test_delete_asset(self, temp_db):
        """Test deleting an asset."""
        temp_db.add_asset("THYAO", "hisse", 150.0, 5.0)
        temp_db.delete_asset("THYAO")
        asset = temp_db.get_asset("THYAO")
        assert asset is None
    
    def test_update_threshold(self, temp_db):
        """Test updating threshold."""
        temp_db.add_asset("THYAO", "hisse", 150.0, 5.0)
        success = temp_db.update_threshold("THYAO", 7.0)
        assert success is True
        asset = temp_db.get_asset("THYAO")
        assert asset[3] == 7.0
    
    def test_update_purchase_price(self, temp_db):
        """Test updating purchase price."""
        temp_db.add_asset("THYAO", "hisse", 150.0, 5.0)
        success = temp_db.update_purchase_price("THYAO", 155.0)
        assert success is True
        asset = temp_db.get_asset("THYAO")
        assert asset[2] == 155.0
    
    def test_save_price_history(self, temp_db):
        """Test saving price history."""
        temp_db.add_asset("THYAO", "hisse", 150.0, 5.0)
        temp_db.save_price_history("THYAO", 152.0, 150.0)
        history = temp_db.get_price_history("THYAO", 1)
        assert len(history) == 1
        assert history[0][1] == 152.0
    
    def test_get_price_history(self, temp_db):
        """Test retrieving price history."""
        temp_db.add_asset("THYAO", "hisse", 150.0, 5.0)
        temp_db.save_price_history("THYAO", 152.0, 150.0, date(2024, 1, 1))
        temp_db.save_price_history("THYAO", 153.0, 152.0, date(2024, 1, 2))
        history = temp_db.get_price_history("THYAO", 10)
        assert len(history) == 2
    
    def test_get_latest_price(self, temp_db):
        """Test getting latest price."""
        temp_db.add_asset("THYAO", "hisse", 150.0, 5.0)
        temp_db.save_price_history("THYAO", 152.0, 150.0, date(2024, 1, 1))
        temp_db.save_price_history("THYAO", 153.0, 152.0, date(2024, 1, 2))
        latest = temp_db.get_latest_price("THYAO")
        assert latest is not None
        assert latest[1] == 153.0
