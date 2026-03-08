import sqlite3
from datetime import datetime, date
from typing import List, Tuple, Optional
from config import DEFAULT_DB_PATH

class BorsaDB:
    def __init__(self, db_path: str = None):
        """
        BorsaDB sınıfı başlatıcı.
        
        Args:
            db_path: Veritabanı dosya yolu. None ise varsayılan yol kullanılır.
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self._init_db()

    def _init_db(self):
        """Tabloları oluşturur."""
        with sqlite3.connect(self.db_path) as conn:
            # Watchlist tablosu
            conn.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL UNIQUE,
                    asset_type TEXT CHECK(asset_type IN ('hisse', 'fon')),
                    purchase_price REAL NOT NULL,
                    threshold_percent REAL NOT NULL
                )
            """)
            # Geçmiş fiyat verileri tablosu
            conn.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date DATE NOT NULL,
                    price REAL NOT NULL,
                    previous_close REAL,
                    UNIQUE(symbol, date),
                    FOREIGN KEY (symbol) REFERENCES watchlist(symbol)
                )
            """)
            # Tarih indeksi için
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_price_history_symbol_date 
                ON price_history(symbol, date DESC)
            """)

    def add_asset(self, symbol: str, asset_type: str, purchase_price: float, threshold_percent: float) -> None:
        """
        Adds a new asset to the watchlist or updates an existing one.
        
        Args:
            symbol (str): The asset ticker/symbol.
            asset_type (str): Type of the asset ('hisse' or 'fon').
            purchase_price (float): The price at which the asset was purchased.
            threshold_percent (float): Percentage change threshold for alerts.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO watchlist (symbol, asset_type, purchase_price, threshold_percent)
                VALUES (?, ?, ?, ?)
            """, (symbol.upper(), asset_type, purchase_price, threshold_percent))

    def get_all_assets(self) -> List[Tuple[str, str, float, float]]:
        """
        Retrieves all assets currently in the watchlist.
        
        Returns:
            List[Tuple[str, str, float, float]]: A list of tuples containing 
            (symbol, asset_type, purchase_price, threshold_percent).
        """
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT symbol, asset_type, purchase_price, threshold_percent FROM watchlist").fetchall()

    def delete_asset(self, symbol: str) -> None:
        """
        Deletes a specific asset from the watchlist.
        
        Args:
            symbol (str): The asset ticker/symbol to remove.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol.upper(),))
    
    def get_asset(self, symbol: str) -> Tuple[str, str, float, float] | None:
        """
        Retrieves a specific asset from the watchlist.
        
        Args:
            symbol (str): The asset ticker/symbol.
            
        Returns:
            Tuple[str, str, float, float] | None: A tuple containing 
            (symbol, asset_type, purchase_price, threshold_percent) or None if not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                "SELECT symbol, asset_type, purchase_price, threshold_percent FROM watchlist WHERE symbol = ?",
                (symbol.upper(),)
            ).fetchone()
            return result
    
    def update_threshold(self, symbol: str, new_threshold: float) -> bool:
        """
        Updates the threshold percentage for a specific asset.
        
        Args:
            symbol (str): The asset ticker/symbol.
            new_threshold (float): The new threshold percentage.
            
        Returns:
            bool: True if update was successful, False if asset not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE watchlist SET threshold_percent = ? WHERE symbol = ?",
                (new_threshold, symbol.upper())
            )
            return cursor.rowcount > 0
    
    def update_purchase_price(self, symbol: str, new_price: float) -> bool:
        """
        Updates the purchase price for a specific asset.
        
        Args:
            symbol (str): The asset ticker/symbol.
            new_price (float): The new purchase price.
            
        Returns:
            bool: True if update was successful, False if asset not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE watchlist SET purchase_price = ? WHERE symbol = ?",
                (new_price, symbol.upper())
            )
            return cursor.rowcount > 0
    
    def save_price_history(self, symbol: str, price: float, previous_close: Optional[float] = None, price_date: Optional[date] = None) -> None:
        """
        Saves price history for an asset.
        
        Args:
            symbol (str): The asset ticker/symbol.
            price (float): The current price.
            previous_close (float, optional): The previous close price.
            price_date (date, optional): The date for the price. Defaults to today.
        """
        if price_date is None:
            price_date = date.today()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO price_history (symbol, date, price, previous_close)
                VALUES (?, ?, ?, ?)
            """, (symbol.upper(), price_date.isoformat(), price, previous_close))
    
    def get_price_history(self, symbol: str, days: int = 30) -> List[Tuple[str, float, Optional[float]]]:
        """
        Retrieves price history for an asset.
        
        Args:
            symbol (str): The asset ticker/symbol.
            days (int): Number of days to retrieve (default: 30).
            
        Returns:
            List[Tuple[str, float, Optional[float]]]: List of tuples containing 
            (date, price, previous_close) ordered by date descending.
        """
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("""
                SELECT date, price, previous_close 
                FROM price_history 
                WHERE symbol = ? 
                ORDER BY date DESC 
                LIMIT ?
            """, (symbol.upper(), days)).fetchall()
    
    def get_latest_price(self, symbol: str) -> Optional[Tuple[str, float, Optional[float]]]:
        """
        Gets the latest price entry for an asset.
        
        Args:
            symbol (str): The asset ticker/symbol.
            
        Returns:
            Optional[Tuple[str, float, Optional[float]]]: Tuple containing 
            (date, price, previous_close) or None if not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("""
                SELECT date, price, previous_close 
                FROM price_history 
                WHERE symbol = ? 
                ORDER BY date DESC 
                LIMIT 1
            """, (symbol.upper(),)).fetchone()
            return result