"""
HTTP API Server for Borsa & Fon Asistani
Web arayüzü veya HTTP client'lar için REST API sağlar.
"""
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv

from database import BorsaDB
from engine import check_alerts, generate_daily_report
from tracker import get_stock_price, get_fund_price
from export import export_portfolio_to_json, export_price_history_to_json
from config import (
    API_VERSION, CORS_ORIGINS, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT
)

load_dotenv()

# Logging yapılandırması
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Borsa & Fon Asistanı API",
    description="Borsa İstanbul ve TEFAS fon takip API'si",
    version=API_VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = BorsaDB()

# Request/Response modelleri
class AddAssetRequest(BaseModel):
    symbol: str
    asset_type: str
    price: float
    threshold: float = DEFAULT_THRESHOLD

class UpdateThresholdRequest(BaseModel):
    new_threshold: float

class UpdatePriceRequest(BaseModel):
    new_price: float

class ExportRequest(BaseModel):
    format: str = "json"
    filename: Optional[str] = None

@app.get("/")
async def root():
    """API ana sayfası"""
    return {
        "message": "Borsa & Fon Asistanı API",
        "version": API_VERSION,
        "endpoints": {
            "watchlist": "/api/watchlist",
            "portfolio": "/api/portfolio",
            "alerts": "/api/alerts",
            "asset_details": "/api/asset/{symbol}",
            "price_history": "/api/price-history/{symbol}"
        }
    }

@app.get("/api/watchlist")
async def get_watchlist():
    """Tüm watchlist'i döndürür"""
    try:
        assets = db.get_all_assets()
        watchlist = [
            {
                "symbol": symbol,
                "asset_type": asset_type,
                "purchase_price": purchase_price,
                "threshold_percent": threshold
            }
            for symbol, asset_type, purchase_price, threshold in assets
        ]
        return {
            "total_assets": len(watchlist),
            "assets": watchlist
        }
    except Exception as e:
        logger.error(f"Error getting watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/watchlist")
async def add_to_watchlist(request: AddAssetRequest):
    """Watchlist'e varlık ekler"""
    try:
        if request.asset_type not in VALID_ASSET_TYPES:
            raise HTTPException(status_code=400, detail=f"asset_type must be one of {VALID_ASSET_TYPES}")
        if request.price <= 0:
            raise HTTPException(status_code=400, detail="price must be positive")
        if request.threshold < MIN_THRESHOLD:
            raise HTTPException(status_code=400, detail=f"threshold must be >= {MIN_THRESHOLD}")
        
        db.add_asset(request.symbol, request.asset_type, request.price, request.threshold)
        logger.info(f"Added {request.symbol} to watchlist")
        return {"message": f"✅ {request.symbol} successfully added to watchlist", "symbol": request.symbol}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/watchlist/{symbol}")
async def remove_from_watchlist(symbol: str):
    """Watchlist'ten varlık çıkarır"""
    try:
        db.delete_asset(symbol)
        logger.info(f"Removed {symbol} from watchlist")
        return {"message": f"✅ {symbol} removed from watchlist"}
    except Exception as e:
        logger.error(f"Error removing from watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio")
async def get_portfolio():
    """Portföy durumunu döndürür"""
    try:
        report_data = generate_daily_report()
        alerts = check_alerts(send_notification=False)
        return {
            "summary": report_data,
            "critical_alerts": alerts
        }
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerts")
async def get_alerts():
    """Kritik uyarıları döndürür"""
    try:
        alerts = check_alerts(send_notification=False)
        return {
            "alerts": alerts,
            "count": len(alerts)
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/asset/{symbol}")
async def get_asset_details(symbol: str):
    """Belirli bir varlığın detaylarını döndürür"""
    try:
        asset = db.get_asset(symbol)
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {symbol} not found")
        
        symbol_db, asset_type, purchase_price, threshold = asset
        
        try:
            if asset_type == 'hisse':
                price_data = get_stock_price(symbol)
            else:
                price_data = get_fund_price(symbol)
            
            from engine import calculate_change
            current_price = price_data["current"]
            prev_close = price_data["previous_close"]
            
            daily_change_pct = calculate_change(current_price, prev_close)
            total_change_pct = calculate_change(current_price, purchase_price)
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting asset details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/price-history/{symbol}")
async def get_price_history(symbol: str, days: int = 30):
    """Fiyat geçmişini döndürür"""
    try:
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
        
        return {
            "symbol": symbol,
            "total_days": len(history_list),
            "history": history_list
        }
    except Exception as e:
        logger.error(f"Error getting price history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/watchlist/{symbol}/threshold")
async def update_threshold(symbol: str, request: UpdateThresholdRequest):
    """Eşik değerini günceller"""
    try:
        if request.new_threshold < 0:
            raise HTTPException(status_code=400, detail="threshold must be non-negative")
        
        asset = db.get_asset(symbol)
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {symbol} not found")
        
        success = db.update_threshold(symbol, request.new_threshold)
        if success:
            return {"message": f"✅ Threshold for {symbol} updated to {request.new_threshold}%"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update threshold")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating threshold: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/watchlist/{symbol}/price")
async def update_purchase_price(symbol: str, request: UpdatePriceRequest):
    """Alış fiyatını günceller"""
    try:
        if request.new_price <= 0:
            raise HTTPException(status_code=400, detail="price must be positive")
        
        asset = db.get_asset(symbol)
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {symbol} not found")
        
        success = db.update_purchase_price(symbol, request.new_price)
        if success:
            return {"message": f"✅ Purchase price for {symbol} updated to {request.new_price}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update price")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating price: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/portfolio")
async def export_portfolio(request: ExportRequest):
    """Portföyü export eder"""
    try:
        report_data = generate_daily_report()
        
        if request.format.lower() == "json":
            filepath = export_portfolio_to_json(report_data, request.filename)
            return {"message": "Portfolio exported successfully", "filepath": filepath}
        else:
            raise HTTPException(status_code=400, detail="Only 'json' format is supported via API")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    from config import API_PORT, API_HOST
    logger.info(f"Starting API server on http://{API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)
