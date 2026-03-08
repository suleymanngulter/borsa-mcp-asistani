"""
Otomatik periyodik kontroller için scheduler modülü.
"""
import schedule
import time
import logging
from datetime import datetime
from engine import check_alerts, generate_daily_report
from notifications import EmailNotifier, TelegramNotifier, send_notifications

logger = logging.getLogger(__name__)


def run_alert_check():
    """Kritik uyarıları kontrol eder ve bildirim gönderir."""
    logger.info("Running scheduled alert check...")
    try:
        alerts = check_alerts(send_notification=True)
        if alerts:
            logger.info(f"Found {len(alerts)} critical alerts")
        else:
            logger.info("No critical alerts found")
    except Exception as e:
        logger.error(f"Error in scheduled alert check: {e}")


def run_daily_report():
    """Günlük raporu oluşturur ve bildirim gönderir."""
    logger.info("Running scheduled daily report...")
    try:
        report_data = generate_daily_report()
        alerts = check_alerts(send_notification=False)
        
        email_notifier = EmailNotifier()
        telegram_notifier = TelegramNotifier()
        
        if email_notifier.enabled:
            email_notifier.send_daily_report(report_data)
        
        if telegram_notifier.enabled:
            telegram_notifier.send_daily_report(report_data, alerts)
        
        logger.info("Daily report sent successfully")
    except Exception as e:
        logger.error(f"Error in scheduled daily report: {e}")


def start_scheduler(
    alert_interval_minutes: int = 60,
    daily_report_time: str = "09:00",
    enable_alerts: bool = True,
    enable_daily_report: bool = True
):
    """
    Scheduler'ı başlatır.
    
    Args:
        alert_interval_minutes: Uyarı kontrolü aralığı (dakika)
        daily_report_time: Günlük rapor gönderim saati (HH:MM formatında)
        enable_alerts: Uyarı kontrollerini etkinleştir
        enable_daily_report: Günlük raporu etkinleştir
    """
    logger.info("Starting scheduler...")
    
    if enable_alerts:
        schedule.every(alert_interval_minutes).minutes.do(run_alert_check)
        logger.info(f"Alert checks scheduled every {alert_interval_minutes} minutes")
    
    if enable_daily_report:
        schedule.every().day.at(daily_report_time).do(run_daily_report)
        logger.info(f"Daily report scheduled at {daily_report_time}")
    
    logger.info("Scheduler started. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Her dakika kontrol et
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Logging yapılandırması
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Environment değişkenlerinden ayarları al
    alert_interval = int(os.getenv("ALERT_INTERVAL_MINUTES", "60"))
    daily_report_time = os.getenv("DAILY_REPORT_TIME", "09:00")
    enable_alerts = os.getenv("ENABLE_ALERTS", "true").lower() == "true"
    enable_daily_report = os.getenv("ENABLE_DAILY_REPORT", "true").lower() == "true"
    
    start_scheduler(
        alert_interval_minutes=alert_interval,
        daily_report_time=daily_report_time,
        enable_alerts=enable_alerts,
        enable_daily_report=enable_daily_report
    )
