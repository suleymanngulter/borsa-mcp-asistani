import os
import asyncio
import logging
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import google.generativeai as genai

from database import BorsaDB
from engine import check_alerts, generate_daily_report, calculate_change
from tracker import get_stock_price, get_fund_price
from notifications import EmailNotifier, TelegramNotifier
from export import (
    export_portfolio_to_csv, export_portfolio_to_json,
    export_price_history_to_csv, export_price_history_to_json
)
from graph import plot_price_history, plot_portfolio_comparison
from config import (
    LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT,
    GEMINI_API_KEY, GEMINI_MODEL, VALID_ASSET_TYPES
)

load_dotenv()

# Logging yapılandırması
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT
)
logger = logging.getLogger(__name__)

# Gemini AI yapılandırması
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        logger.info("Gemini AI model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini AI: {e}")
        model = None
else:
    logger.warning("GEMINI_API_KEY not set. AI analysis features will be disabled.")
    model = None

mcp = FastMCP("Borsa-Fon Asistani")
db = BorsaDB()
logger.info("MCP server 'Borsa-Fon Asistani' initialized")

@mcp.tool()
def add_to_watchlist(symbol: str, asset_type: str, price: float, threshold: float = None) -> str:
    """
    Adds a new stock/fund to the watchlist.
    
    Args:
        symbol: Ticker symbol (e.g., THYAO, GMR)
        asset_type: 'hisse' or 'fon'
        price: Purchase/Reference price
        threshold: Alert threshold percentage. If None, uses default from config.
    """
    try:
        if threshold is None:
            threshold = DEFAULT_THRESHOLD
        
        if asset_type not in VALID_ASSET_TYPES:
            raise ValueError(f"Invalid asset_type: {asset_type}. Must be one of {VALID_ASSET_TYPES}")
        if price <= 0:
            raise ValueError(f"Price must be positive, got: {price}")
        if threshold < MIN_THRESHOLD:
            raise ValueError(f"Threshold must be >= {MIN_THRESHOLD}, got: {threshold}")
        
        db.add_asset(symbol, asset_type, price, threshold)
        logger.info(f"Added {symbol} ({asset_type}) to watchlist with price {price} and threshold {threshold}%")
        return f"✅ {symbol} successfully added to watchlist. Threshold: {threshold}%"
    except Exception as e:
        error_msg = f"❌ Failed to add {symbol} to watchlist: {e}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def remove_from_watchlist(symbol: str) -> str:
    """
    Removes an asset from the watchlist.
    
    Args:
        symbol: The ticker symbol to remove.
    """
    try:
        db.delete_asset(symbol)
        logger.info(f"Removed {symbol} from watchlist")
        return f"✅ {symbol} removed from watchlist."
    except Exception as e:
        error_msg = f"❌ Failed to remove {symbol} from watchlist: {e}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def get_portfolio_status() -> dict:
    """
    Returns the current portfolio performance and active critical alerts.
    """
    try:
        logger.info("Generating portfolio status report")
        report_data = generate_daily_report()
        alerts = check_alerts()
        return {
            "summary": report_data,
            "critical_alerts": alerts
        }
    except Exception as e:
        error_msg = f"❌ Error generating portfolio status: {e}"
        logger.error(error_msg)
        return {
            "error": error_msg,
            "summary": [],
            "critical_alerts": []
        }

@mcp.tool()
def get_market_analysis() -> str:
    """
    Sends portfolio data to Gemini 2.0 Flash SDK to provide human-like insights.
    """
    if not model:
        logger.warning("Market analysis requested but Gemini AI is not available")
        return "❌ GEMINI_API_KEY is not set. Cannot perform market analysis."
    
    try:
        logger.info("Generating market analysis with Gemini AI")
        report_data = generate_daily_report()
        alerts = check_alerts()
        
        prompt = f"""
        You are an expert financial advisor specializing in Borsa Istanbul (BIST) and Turkish Investment Funds (TEFAS).
        Please analyze the following portfolio data and provide human-like insights.
        Identify which assets are underperforming, which are overperforming, and give a brief market perspective.
        
        Portfolio Data:
        {report_data}
        
        Critical Alerts Triggered:
        {alerts}
        """
        
        response = model.generate_content(prompt)
        logger.info("Market analysis generated successfully")
        return response.text
    except Exception as e:
        error_msg = f"❌ Error generating market analysis: {e}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def get_asset_details(symbol: str) -> dict:
    """
    Returns detailed information about a specific asset in the watchlist.
    
    Args:
        symbol: The ticker symbol to get details for.
    """
    try:
        asset = db.get_asset(symbol)
        if not asset:
            return {
                "error": f"❌ Asset {symbol} not found in watchlist",
                "symbol": symbol
            }
        
        symbol_db, asset_type, purchase_price, threshold = asset
        
        # Get current price data
        try:
            if asset_type == 'hisse':
                price_data = get_stock_price(symbol)
            else:
                price_data = get_fund_price(symbol)
            
            current_price = price_data["current"]
            prev_close = price_data["previous_close"]
            
            daily_change_pct = calculate_change(current_price, prev_close)
            total_change_pct = calculate_change(current_price, purchase_price)
            
            # Check if threshold is exceeded
            threshold_exceeded = abs(total_change_pct) >= threshold
            
            return {
                "symbol": symbol_db,
                "asset_type": asset_type,
                "purchase_price": purchase_price,
                "current_price": current_price,
                "previous_close": prev_close,
                "threshold_percent": threshold,
                "daily_change_pct": round(daily_change_pct, 2),
                "total_change_pct": round(total_change_pct, 2),
                "threshold_exceeded": threshold_exceeded,
                "status": "CRITICAL" if threshold_exceeded else "NORMAL"
            }
        except Exception as e:
            return {
                "symbol": symbol_db,
                "asset_type": asset_type,
                "purchase_price": purchase_price,
                "threshold_percent": threshold,
                "error": f"Could not fetch current price: {e}"
            }
    except Exception as e:
        error_msg = f"❌ Error getting asset details for {symbol}: {e}"
        logger.error(error_msg)
        return {"error": error_msg}

@mcp.tool()
def update_threshold(symbol: str, new_threshold: float) -> str:
    """
    Updates the alert threshold percentage for an asset in the watchlist.
    
    Args:
        symbol: The ticker symbol to update.
        new_threshold: The new threshold percentage (must be >= 0).
    """
    try:
        if new_threshold < MIN_THRESHOLD:
            raise ValueError(f"Threshold must be >= {MIN_THRESHOLD}, got: {new_threshold}")
        
        asset = db.get_asset(symbol)
        if not asset:
            return f"❌ Asset {symbol} not found in watchlist"
        
        success = db.update_threshold(symbol, new_threshold)
        if success:
            logger.info(f"Updated threshold for {symbol} to {new_threshold}%")
            return f"✅ Threshold for {symbol} updated to {new_threshold}%"
        else:
            return f"❌ Failed to update threshold for {symbol}"
    except Exception as e:
        error_msg = f"❌ Error updating threshold for {symbol}: {e}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def update_purchase_price(symbol: str, new_price: float) -> str:
    """
    Updates the purchase/reference price for an asset in the watchlist.
    
    Args:
        symbol: The ticker symbol to update.
        new_price: The new purchase price (must be > 0).
    """
    try:
        if new_price <= 0:
            raise ValueError(f"Price must be positive, got: {new_price}")
        
        asset = db.get_asset(symbol)
        if not asset:
            return f"❌ Asset {symbol} not found in watchlist"
        
        success = db.update_purchase_price(symbol, new_price)
        if success:
            logger.info(f"Updated purchase price for {symbol} to {new_price}")
            return f"✅ Purchase price for {symbol} updated to {new_price}"
        else:
            return f"❌ Failed to update purchase price for {symbol}"
    except Exception as e:
        error_msg = f"❌ Error updating purchase price for {symbol}: {e}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def get_watchlist() -> dict:
    """
    Returns the complete watchlist with all assets and their basic information.
    """
    try:
        assets = db.get_all_assets()
        watchlist = []
        
        for symbol, asset_type, purchase_price, threshold in assets:
            watchlist.append({
                "symbol": symbol,
                "asset_type": asset_type,
                "purchase_price": purchase_price,
                "threshold_percent": threshold
            })
        
        logger.info(f"Retrieved watchlist with {len(watchlist)} assets")
        return {
            "total_assets": len(watchlist),
            "assets": watchlist
        }
    except Exception as e:
        error_msg = f"❌ Error retrieving watchlist: {e}"
        logger.error(error_msg)
        return {"error": error_msg, "total_assets": 0, "assets": []}

@mcp.tool()
def get_price_history(symbol: str, days: int = 30) -> dict:
    """
    Returns historical price data for an asset.
    
    Args:
        symbol: The ticker symbol to get history for.
        days: Number of days to retrieve (default: 30, max: 365).
    """
    try:
        # Limit days to reasonable range
        days = min(max(1, days), MAX_PRICE_HISTORY_DAYS)
        
        history = db.get_price_history(symbol, days)
        
        if not history:
            return {
                "symbol": symbol,
                "message": f"No price history found for {symbol}",
                "history": []
            }
        
        history_list = [
            {
                "date": date_str,
                "price": price,
                "previous_close": prev_close
            }
            for date_str, price, prev_close in history
        ]
        
        logger.info(f"Retrieved {len(history_list)} days of price history for {symbol}")
        return {
            "symbol": symbol,
            "total_days": len(history_list),
            "history": history_list
        }
    except Exception as e:
        error_msg = f"❌ Error retrieving price history for {symbol}: {e}"
        logger.error(error_msg)
        return {"error": error_msg, "symbol": symbol}

@mcp.tool()
def send_alert_notifications() -> str:
    """
    Checks for critical alerts and sends notifications via configured channels (Email/Telegram).
    """
    try:
        alerts = check_alerts(send_notification=False)
        
        if not alerts:
            return "✅ No critical alerts to send."
        
        # Send notifications
        from notifications import send_notifications
        send_notifications(alerts)
        
        return f"✅ Notifications sent for {len(alerts)} critical alert(s)."
    except Exception as e:
        error_msg = f"❌ Error sending notifications: {e}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def send_daily_report_notification() -> str:
    """
    Generates and sends daily portfolio report via configured notification channels.
    """
    try:
        report_data = generate_daily_report()
        alerts = check_alerts(send_notification=False)
        
        email_notifier = EmailNotifier()
        telegram_notifier = TelegramNotifier()
        
        sent = False
        if email_notifier.enabled:
            email_notifier.send_daily_report(report_data)
            sent = True
        
        if telegram_notifier.enabled:
            telegram_notifier.send_daily_report(report_data, alerts)
            sent = True
        
        if not sent:
            return "⚠️ No notification channels configured. Please set up Email or Telegram."
        
        return f"✅ Daily report sent via configured channels."
    except Exception as e:
        error_msg = f"❌ Error sending daily report: {e}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def export_portfolio(format: str = "json", filename: str = None) -> str:
    """
    Exports portfolio report to CSV or JSON format.
    
    Args:
        format: Export format ('csv' or 'json', default: 'json')
        filename: Optional filename (auto-generated if not provided)
    """
    try:
        report_data = generate_daily_report()
        
        if format.lower() == "csv":
            filepath = export_portfolio_to_csv(report_data, filename)
        elif format.lower() == "json":
            filepath = export_portfolio_to_json(report_data, filename)
        else:
            return f"❌ Invalid format: {format}. Use 'csv' or 'json'."
        
        return f"✅ Portfolio exported to {filepath}"
    except Exception as e:
        error_msg = f"❌ Error exporting portfolio: {e}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def export_price_history(symbol: str, days: int = 30, format: str = "json", filename: str = None) -> str:
    """
    Exports price history for an asset to CSV or JSON format.
    
    Args:
        symbol: The ticker symbol
        days: Number of days to export (default: 30, max: 365)
        format: Export format ('csv' or 'json', default: 'json')
        filename: Optional filename (auto-generated if not provided)
    """
    try:
        days = min(max(1, days), 365)
        history = db.get_price_history(symbol, days)
        
        if not history:
            return f"❌ No price history found for {symbol}"
        
        history_list = [
            {
                "date": date_str,
                "price": price,
                "previous_close": prev_close
            }
            for date_str, price, prev_close in history
        ]
        
        if format.lower() == "csv":
            filepath = export_price_history_to_csv(history_list, symbol, filename)
        elif format.lower() == "json":
            filepath = export_price_history_to_json(history_list, symbol, filename)
        else:
            return f"❌ Invalid format: {format}. Use 'csv' or 'json'."
        
        return f"✅ Price history for {symbol} exported to {filepath}"
    except Exception as e:
        error_msg = f"❌ Error exporting price history: {e}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def generate_price_chart(symbol: str, days: int = 30, filename: str = None) -> str:
    """
    Generates a price trend chart for an asset.
    
    Args:
        symbol: The ticker symbol
        days: Number of days to include (default: 30, max: 365)
        filename: Optional filename (auto-generated if not provided)
    """
    try:
        days = min(max(1, days), 365)
        history = db.get_price_history(symbol, days)
        
        if not history:
            return f"❌ No price history found for {symbol}"
        
        history_list = [
            {
                "date": date_str,
                "price": price,
                "previous_close": prev_close
            }
            for date_str, price, prev_close in history
        ]
        
        filepath = plot_price_history(history_list, symbol, filename)
        return f"✅ Price chart generated: {filepath}"
    except Exception as e:
        error_msg = f"❌ Error generating price chart: {e}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def generate_portfolio_chart(filename: str = None) -> str:
    """
    Generates a comparison chart showing performance of all assets in the portfolio.
    
    Args:
        filename: Optional filename (auto-generated if not provided)
    """
    try:
        report_data = generate_daily_report()
        
        if not report_data:
            return "❌ No portfolio data available"
        
        filepath = plot_portfolio_comparison(report_data, filename)
        return f"✅ Portfolio comparison chart generated: {filepath}"
    except Exception as e:
        error_msg = f"❌ Error generating portfolio chart: {e}"
        logger.error(error_msg)
        return error_msg

if __name__ == "__main__":
    logger.info("Starting MCP server...")
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
    except Exception as e:
        logger.error(f"MCP server crashed: {e}")
        raise