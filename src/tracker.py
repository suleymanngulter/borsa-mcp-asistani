import yfinance as yf
import pandas as pd
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional
from tefas import Crawler
from config import DEFAULT_RETRY_COUNT, RETRY_DELAY_SECONDS, TEFAS_FETCH_DAYS

# Logging yapılandırması
logger = logging.getLogger(__name__)

def get_stock_price(symbol: str, retry_count: int = None) -> Dict[str, float]:
    """
    Fetches the current real-time price for a BIST stock using yfinance.
    Appends '.IS' automatically if not present.
    
    Args:
        symbol (str): The stock ticker (e.g., 'THYAO').
        retry_count (int): Number of retry attempts. If None, uses default from config.
        
    Returns:
        Dict[str, float]: {"current": current_price, "previous_close": previous_close}
        
    Raises:
        ValueError: If the price cannot be retrieved after retries.
    """
    if retry_count is None:
        retry_count = DEFAULT_RETRY_COUNT
    
    clean_symbol = symbol.upper()
    if not clean_symbol.endswith(".IS"):
        clean_symbol += ".IS"
    
    last_error = None
    for attempt in range(retry_count):
        try:
            ticker = yf.Ticker(clean_symbol)
            current = float(ticker.fast_info['last_price'])
            prev_close = float(ticker.fast_info['previous_close'])
            
            if current == 0:
                raise ValueError(f"No valid price returned for {symbol}")
            
            logger.info(f"Successfully fetched price for {symbol}: {current}")
            return {"current": current, "previous_close": prev_close}
            
        except Exception as e:
            last_error = e
            logger.warning(f"Attempt {attempt + 1}/{retry_count} failed for {symbol}: {e}")
            if attempt < retry_count - 1:
                time.sleep(RETRY_DELAY_SECONDS)
    
    error_msg = f"Could not retrieve price for stock {symbol} after {retry_count} attempts: {last_error}"
    logger.error(error_msg)
    raise ValueError(error_msg)


def get_fund_price(symbol: str, retry_count: int = None) -> Dict[str, float]:
    """
    Fetches the current price for a TEFAS investment fund.
    
    Args:
        symbol (str): The fund code (e.g., 'GMR', 'YAS').
        retry_count (int): Number of retry attempts. If None, uses default from config.
        
    Returns:
        Dict[str, float]: {"current": current_price, "previous_close": previous_close}
        
    Raises:
        ValueError: If the price cannot be retrieved after retries.
    """
    if retry_count is None:
        retry_count = DEFAULT_RETRY_COUNT
    
    clean_symbol = symbol.upper()
    last_error = None
    
    for attempt in range(retry_count):
        try:
            crawler = Crawler()
            
            # TEFAS crawler'ın fetch() metodu start ve end parametreleri gerektirir
            # Son N günün verisini çek (config'den alınır)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=TEFAS_FETCH_DAYS)
            
            # Tarihleri 'YYYY-MM-DD' formatında string olarak gönder
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            data = crawler.fetch(start=start_str, end=end_str)
            
            if data is None or data.empty:
                raise ValueError(f"No data returned from TEFAS for {clean_symbol}")
            
            # Fon koduna göre filtrele
            fund_data = data[data['code'] == clean_symbol]
            
            if fund_data.empty:
                raise ValueError(f"Fund {clean_symbol} not found in TEFAS data")
            
            # Tarihe göre sırala (en yeni en sonda)
            if 'date' in fund_data.columns:
                fund_data = fund_data.sort_values('date')
            
            # En son veriyi al
            latest = fund_data.iloc[-1]
            current_price = float(latest['price'])
            
            # Önceki günün fiyatını bul
            prev_close = current_price  # Varsayılan olarak aynı fiyat
            if len(fund_data) > 1:
                previous = fund_data.iloc[-2]
                prev_close = float(previous['price'])
            else:
                logger.warning(f"Only one day of data available for {clean_symbol}, using same price for previous_close")
            
            logger.info(f"Successfully fetched price for fund {clean_symbol}: {current_price}")
            return {
                'current': current_price,
                'previous_close': prev_close
            }
            
        except Exception as e:
            last_error = e
            logger.warning(f"Attempt {attempt + 1}/{retry_count} failed for fund {clean_symbol}: {e}")
            if attempt < retry_count - 1:
                time.sleep(RETRY_DELAY_SECONDS)
    
    error_msg = f"Could not retrieve price for fund {clean_symbol} after {retry_count} attempts: {last_error}"
    logger.error(error_msg)
    raise ValueError(error_msg)