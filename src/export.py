"""
CSV ve JSON export fonksiyonları.
"""
import csv
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


def export_portfolio_to_csv(report_data: List[Dict[str, Any]], filename: str = None) -> str:
    """
    Portföy raporunu CSV formatında export eder.
    
    Args:
        report_data: Rapor verisi
        filename: Dosya adı (opsiyonel, otomatik oluşturulur)
        
    Returns:
        str: Export edilen dosya yolu
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"portfolio_report_{timestamp}.csv"
    
    filepath = Path(filename)
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['symbol', 'asset_type', 'current_price', 'daily_change_pct', 'total_change_pct']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for item in report_data:
                if "error" not in item:
                    writer.writerow({
                        'symbol': item['symbol'],
                        'asset_type': item['asset_type'],
                        'current_price': item['current_price'],
                        'daily_change_pct': item['daily_change_pct'],
                        'total_change_pct': item['total_change_pct']
                    })
        
        logger.info(f"Portfolio exported to CSV: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        raise


def export_portfolio_to_json(report_data: List[Dict[str, Any]], filename: str = None) -> str:
    """
    Portföy raporunu JSON formatında export eder.
    
    Args:
        report_data: Rapor verisi
        filename: Dosya adı (opsiyonel, otomatik oluşturulur)
        
    Returns:
        str: Export edilen dosya yolu
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"portfolio_report_{timestamp}.json"
    
    filepath = Path(filename)
    
    try:
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_assets': len(report_data),
            'portfolio': report_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"Portfolio exported to JSON: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        raise


def export_price_history_to_csv(history_data: List[Dict[str, Any]], symbol: str, filename: str = None) -> str:
    """
    Fiyat geçmişini CSV formatında export eder.
    
    Args:
        history_data: Geçmiş fiyat verisi
        symbol: Varlık sembolü
        filename: Dosya adı (opsiyonel, otomatik oluşturulur)
        
    Returns:
        str: Export edilen dosya yolu
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"price_history_{symbol}_{timestamp}.csv"
    
    filepath = Path(filename)
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['date', 'price', 'previous_close']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for item in history_data:
                writer.writerow({
                    'date': item['date'],
                    'price': item['price'],
                    'previous_close': item.get('previous_close', '')
                })
        
        logger.info(f"Price history exported to CSV: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Error exporting price history to CSV: {e}")
        raise


def export_price_history_to_json(history_data: List[Dict[str, Any]], symbol: str, filename: str = None) -> str:
    """
    Fiyat geçmişini JSON formatında export eder.
    
    Args:
        history_data: Geçmiş fiyat verisi
        symbol: Varlık sembolü
        filename: Dosya adı (opsiyonel, otomatik oluşturulur)
        
    Returns:
        str: Export edilen dosya yolu
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"price_history_{symbol}_{timestamp}.json"
    
    filepath = Path(filename)
    
    try:
        export_data = {
            'symbol': symbol,
            'export_date': datetime.now().isoformat(),
            'total_records': len(history_data),
            'history': history_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"Price history exported to JSON: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Error exporting price history to JSON: {e}")
        raise
