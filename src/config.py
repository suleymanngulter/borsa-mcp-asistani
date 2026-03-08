"""
Proje yapılandırma sabitleri ve varsayılan değerler.
"""
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

# API Ayarları
API_PORT = int(os.getenv("API_PORT", "8000"))
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_VERSION = "1.0.0"

# CORS Ayarları
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS") != "*" else ["*"]

# Veritabanı Ayarları
DEFAULT_DB_PATH = os.getenv("DB_PATH", "borsa_asistani.db")

# Fiyat Çekme Ayarları
DEFAULT_RETRY_COUNT = 3
RETRY_DELAY_SECONDS = 1
MAX_WORKERS = 10  # Paralel işleme için

# TEFAS Ayarları
TEFAS_FETCH_DAYS = 7  # Son kaç günün verisi çekilecek

# Eşik ve Limitler
DEFAULT_THRESHOLD = 5.0
MIN_THRESHOLD = 0.0
MAX_PRICE_HISTORY_DAYS = 365
MIN_PRICE = 0.0

# Asset Types
VALID_ASSET_TYPES: List[str] = ["hisse", "fon"]

# Export Ayarları
EXPORT_DATE_FORMAT = "%Y%m%d_%H%M%S"
SUPPORTED_EXPORT_FORMATS: List[str] = ["json", "csv"]

# Logging Ayarları
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Scheduler Ayarları
DEFAULT_ALERT_INTERVAL_MINUTES = int(os.getenv("ALERT_INTERVAL_MINUTES", "60"))
DEFAULT_DAILY_REPORT_TIME = os.getenv("DAILY_REPORT_TIME", "09:00")
ENABLE_ALERTS = os.getenv("ENABLE_ALERTS", "true").lower() == "true"
ENABLE_DAILY_REPORT = os.getenv("ENABLE_DAILY_REPORT", "true").lower() == "true"

# Gemini AI Ayarları
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"

# SMTP Ayarları
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USERNAME)
EMAIL_TO = os.getenv("EMAIL_TO", SMTP_USERNAME)

# Telegram Ayarları
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage" if TELEGRAM_BOT_TOKEN else None
