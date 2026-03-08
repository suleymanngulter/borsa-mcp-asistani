import pytest
import sys
import os
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import BorsaDB
from engine import check_alerts, generate_daily_report, calculate_change


class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        db = BorsaDB(db_path=path)
        yield db
        os.unlink(path)
    
    def test_full_workflow(self, temp_db, monkeypatch):
        """Test a complete workflow: add asset, check alerts, generate report."""
        # Mock price data to avoid actual API calls
        def mock_get_stock_price(symbol, retry_count=3):
            return {"current": 155.0, "previous_close": 150.0}
        
        def mock_get_fund_price(symbol, retry_count=3):
            return {"current": 11.0, "previous_close": 10.0}
        
        # Add assets
        temp_db.add_asset("THYAO", "hisse", 150.0, 5.0)
        temp_db.add_asset("GMR", "fon", 10.0, 3.0)
        
        # Mock the price functions
        import engine
        monkeypatch.setattr(engine, "get_stock_price", mock_get_stock_price)
        monkeypatch.setattr(engine, "get_fund_price", mock_get_fund_price)
        
        # Generate report
        report = generate_daily_report()
        assert len(report) == 2
        
        # Check alerts (THYAO should trigger: 155/150 = 3.33%, GMR should trigger: 11/10 = 10%)
        alerts = check_alerts()
        # GMR should trigger alert (10% > 3%)
        assert any("GMR" in alert for alert in alerts)
    
    def test_price_history_integration(self, temp_db):
        """Test price history integration with reports."""
        temp_db.add_asset("THYAO", "hisse", 150.0, 5.0)
        
        # Save some price history
        from datetime import date
        temp_db.save_price_history("THYAO", 152.0, 150.0, date(2024, 1, 1))
        temp_db.save_price_history("THYAO", 153.0, 152.0, date(2024, 1, 2))
        
        # Retrieve history
        history = temp_db.get_price_history("THYAO", 10)
        assert len(history) == 2
        
        # Get latest
        latest = temp_db.get_latest_price("THYAO")
        assert latest is not None
        assert latest[1] == 153.0
