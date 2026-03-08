import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


class EmailNotifier:
    """E-posta bildirim gönderici."""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("EMAIL_FROM", self.smtp_username)
        self.to_email = os.getenv("EMAIL_TO", self.smtp_username)
        self.enabled = bool(self.smtp_username and self.smtp_password)
    
    def send_alert(self, subject: str, message: str, alerts: List[str]) -> bool:
        """
        Kritik uyarıları e-posta ile gönderir.
        
        Args:
            subject: E-posta konusu
            message: E-posta mesajı
            alerts: Uyarı listesi
            
        Returns:
            bool: Başarılı ise True
        """
        if not self.enabled:
            logger.warning("E-posta bildirimi devre dışı (SMTP ayarları eksik)")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = self.to_email
            msg['Subject'] = subject
            
            body = f"{message}\n\n"
            body += "Kritik Uyarılar:\n"
            body += "-" * 50 + "\n"
            for alert in alerts:
                body += f"• {alert}\n"
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"E-posta bildirimi gönderildi: {subject}")
            return True
        except Exception as e:
            logger.error(f"E-posta gönderme hatası: {e}")
            return False
    
    def send_daily_report(self, report_data: List[dict]) -> bool:
        """
        Günlük raporu e-posta ile gönderir.
        
        Args:
            report_data: Rapor verisi
            
        Returns:
            bool: Başarılı ise True
        """
        if not self.enabled:
            return False
        
        try:
            subject = "📊 Borsa & Fon Günlük Raporu"
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = self.to_email
            msg['Subject'] = subject
            
            body = "Günlük Portföy Raporu\n"
            body += "=" * 50 + "\n\n"
            
            for item in report_data:
                if "error" in item:
                    body += f"{item['symbol']}: HATA - {item['error']}\n"
                else:
                    body += f"{item['symbol']} ({item['asset_type']}):\n"
                    body += f"  Güncel Fiyat: {item['current_price']:.2f} TL\n"
                    body += f"  Günlük Değişim: %{item['daily_change_pct']:.2f}\n"
                    body += f"  Toplam Değişim: %{item['total_change_pct']:.2f}\n\n"
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info("Günlük rapor e-postası gönderildi")
            return True
        except Exception as e:
            logger.error(f"Günlük rapor e-postası gönderme hatası: {e}")
            return False


class TelegramNotifier:
    """Telegram bildirim gönderici."""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.bot_token and self.chat_id)
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage" if self.bot_token else None
    
    def send_message(self, text: str) -> bool:
        """
        Telegram'a mesaj gönderir.
        
        Args:
            text: Gönderilecek mesaj
            
        Returns:
            bool: Başarılı ise True
        """
        if not self.enabled:
            logger.warning("Telegram bildirimi devre dışı (bot token veya chat ID eksik)")
            return False
        
        try:
            import requests
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            response = requests.post(self.api_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Telegram mesajı gönderildi")
            return True
        except Exception as e:
            logger.error(f"Telegram mesaj gönderme hatası: {e}")
            return False
    
    def send_alert(self, alerts: List[str]) -> bool:
        """
        Kritik uyarıları Telegram ile gönderir.
        
        Args:
            alerts: Uyarı listesi
            
        Returns:
            bool: Başarılı ise True
        """
        if not alerts:
            return True
        
        text = "🔔 <b>Kritik Uyarılar</b>\n\n"
        for alert in alerts:
            text += f"⚠️ {alert}\n"
        
        return self.send_message(text)
    
    def send_daily_report(self, report_data: List[dict], alerts: List[str] = None) -> bool:
        """
        Günlük raporu Telegram ile gönderir.
        
        Args:
            report_data: Rapor verisi
            alerts: Uyarı listesi (opsiyonel)
            
        Returns:
            bool: Başarılı ise True
        """
        text = "📊 <b>Günlük Portföy Raporu</b>\n\n"
        
        for item in report_data:
            if "error" in item:
                text += f"❌ <b>{item['symbol']}</b>: {item['error']}\n"
            else:
                daily_emoji = "📈" if item['daily_change_pct'] >= 0 else "📉"
                total_emoji = "✅" if item['total_change_pct'] >= 0 else "❌"
                text += f"{daily_emoji} <b>{item['symbol']}</b> ({item['asset_type']})\n"
                text += f"   Fiyat: {item['current_price']:.2f} TL\n"
                text += f"   Günlük: %{item['daily_change_pct']:.2f}\n"
                text += f"   Toplam: {total_emoji} %{item['total_change_pct']:.2f}\n\n"
        
        if alerts:
            text += "\n🔔 <b>Kritik Uyarılar:</b>\n"
            for alert in alerts:
                text += f"⚠️ {alert}\n"
        
        return self.send_message(text)


def send_notifications(alerts: List[str], report_data: Optional[List[dict]] = None):
    """
    Tüm bildirim kanallarına uyarı gönderir.
    
    Args:
        alerts: Uyarı listesi
        report_data: Rapor verisi (opsiyonel)
    """
    if not alerts:
        return
    
    # E-posta bildirimi
    email_notifier = EmailNotifier()
    if email_notifier.enabled:
        email_notifier.send_alert(
            subject="🔔 Borsa & Fon Kritik Uyarı",
            message="Portföyünüzde kritik değişiklikler tespit edildi.",
            alerts=alerts
        )
    
    # Telegram bildirimi
    telegram_notifier = TelegramNotifier()
    if telegram_notifier.enabled:
        telegram_notifier.send_alert(alerts)
