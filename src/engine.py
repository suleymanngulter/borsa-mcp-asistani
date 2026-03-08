import sys
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple, Optional
from database import BorsaDB
from tracker import get_stock_price, get_fund_price
from notifications import send_notifications

# Logging yapılandırması
logger = logging.getLogger(__name__)

def calculate_change(current: float, purchase: float) -> float:
    """Calculates percentage change."""
    if purchase == 0: return 0.0
    return ((current - purchase) / purchase) * 100.0

def _get_price_data(symbol: str, asset_type: str) -> Dict[str, float]:
    """Helper to fetch price data based on asset type."""
    if asset_type == 'hisse':
        return get_stock_price(symbol)
    else:
        return get_fund_price(symbol)

def _check_single_alert(symbol: str, asset_type: str, purchase_price: float, threshold: float) -> str | None:
    """Helper function to check alert for a single asset (for parallel processing)."""
    try:
        price_data = _get_price_data(symbol, asset_type)
        current_price = price_data["current"]
        
        change_pct = calculate_change(current_price, purchase_price)
        
        # Absolute value check for threshold (supports both drop and rise)
        if abs(change_pct) >= threshold:
            alert_msg = f"CRITICAL: {symbol} change ({change_pct:.2f}%) exceeds threshold ({threshold}%)!"
            logger.warning(alert_msg)
            return alert_msg
        return None
    except Exception as e:
        error_msg = f"ERROR: Could not check alert for {symbol}: {e}"
        logger.error(error_msg)
        return error_msg

def check_alerts(send_notification: bool = False) -> List[str]:
    """
    Compares current prices with purchase_price.
    If the change % exceeds 'threshold_percent', returns a CRITICAL status.
    Uses parallel processing for better performance.
    
    Args:
        send_notification: If True, sends notifications for critical alerts.
    """
    db = BorsaDB()
    watchlist = db.get_all_assets()
    alerts = []
    
    logger.info(f"Checking alerts for {len(watchlist)} assets (parallel processing)")
    
    # Use ThreadPoolExecutor for parallel price fetching
    with ThreadPoolExecutor(max_workers=min(len(watchlist), 10)) as executor:
        futures = {
            executor.submit(_check_single_alert, symbol, asset_type, purchase_price, threshold): symbol
            for symbol, asset_type, purchase_price, threshold in watchlist
        }
        
        for future in as_completed(futures):
            symbol = futures[future]
            try:
                result = future.result()
                if result:
                    alerts.append(result)
            except Exception as e:
                error_msg = f"ERROR: Unexpected error checking alert for {symbol}: {e}"
                alerts.append(error_msg)
                logger.error(error_msg)
    
    # Send notifications if enabled and alerts exist
    if send_notification and alerts:
        try:
            send_notifications(alerts)
        except Exception as e:
            logger.error(f"Failed to send notifications: {e}")
            
    return alerts

def _generate_single_report(symbol: str, asset_type: str, purchase_price: float, threshold: float, save_history: bool = True) -> Dict[str, Any]:
    """Helper function to generate report for a single asset (for parallel processing)."""
    try:
        price_data = _get_price_data(symbol, asset_type)
        current_price = price_data["current"]
        prev_close = price_data["previous_close"]
        
        # Save to price history if enabled
        if save_history:
            try:
                db = BorsaDB()
                db.save_price_history(symbol, current_price, prev_close)
            except Exception as e:
                logger.warning(f"Failed to save price history for {symbol}: {e}")
        
        daily_change_pct = calculate_change(current_price, prev_close)
        total_change_pct = calculate_change(current_price, purchase_price)
        
        result = {
            "symbol": symbol,
            "asset_type": asset_type,
            "current_price": current_price,
            "daily_change_pct": daily_change_pct,
            "total_change_pct": total_change_pct
        }
        logger.debug(f"Report generated for {symbol}: {current_price} ({daily_change_pct:.2f}% daily, {total_change_pct:.2f}% total)")
        return result
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error generating report for {symbol}: {error_msg}")
        return {
            "symbol": symbol,
            "asset_type": asset_type,
            "error": error_msg
        }

def generate_daily_report() -> List[Dict[str, Any]]:
    """
    Calculates daily opening vs closing/current performance for the entire watchlist.
    Uses parallel processing for better performance.
    """
    db = BorsaDB()
    watchlist = db.get_all_assets()
    report = []
    
    logger.info(f"Generating daily report for {len(watchlist)} assets (parallel processing)")
    
    # Use ThreadPoolExecutor for parallel price fetching
    with ThreadPoolExecutor(max_workers=min(len(watchlist), 10)) as executor:
        futures = {
            executor.submit(_generate_single_report, symbol, asset_type, purchase_price, threshold, save_history=True): symbol
            for symbol, asset_type, purchase_price, threshold in watchlist
        }
        
        # Create a dictionary to maintain order
        results_dict = {}
        for future in as_completed(futures):
            symbol = futures[future]
            try:
                result = future.result()
                results_dict[symbol] = result
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Unexpected error generating report for {symbol}: {error_msg}")
                results_dict[symbol] = {
                    "symbol": symbol,
                    "asset_type": "unknown",
                    "error": error_msg
                }
        
        # Maintain original order
        for symbol, asset_type, purchase_price, threshold in watchlist:
            if symbol in results_dict:
                report.append(results_dict[symbol])
            
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Borsa & Fund Tracker Engine")
    parser.add_argument("--report", action="store_true", help="Generate and print daily report")
    parser.add_argument("--alerts", action="store_true", help="Check and print critical alerts")
    
    args = parser.parse_args()
    
    if args.alerts:
        print("--- Critical Alerts ---")
        alerts = check_alerts()
        if alerts:
            for alert in alerts:
                print(alert)
        else:
            print("No critical alerts triggered.")
            
    if args.report or not (args.alerts or args.report):  # Default to report if nothing provided
        print(f"\n{'Symbol':<10} | {'Type':<6} | {'Current':<10} | {'Daily %':<10} | {'Total %':<10}")
        print("-" * 55)
        reports = generate_daily_report()
        for r in reports:
            if "error" in r:
                print(f"{r['symbol']:<10} | {r['asset_type']:<6} | ERROR: {r['error']}")
            else:
                print(f"{r['symbol']:<10} | {r['asset_type']:<6} | {r['current_price']:<10.4f} | %{r['daily_change_pct']:<9.2f} | %{r['total_change_pct']:<9.2f}")