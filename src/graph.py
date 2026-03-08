"""
Fiyat trend görselleştirme fonksiyonları.
"""
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def plot_price_history(
    history_data: List[Dict[str, Any]],
    symbol: str,
    filename: Optional[str] = None,
    show_previous_close: bool = True
) -> str:
    """
    Fiyat geçmişini grafik olarak görselleştirir.
    
    Args:
        history_data: Geçmiş fiyat verisi (date, price, previous_close içeren dict listesi)
        symbol: Varlık sembolü
        filename: Dosya adı (opsiyonel, otomatik oluşturulur)
        show_previous_close: Önceki kapanış fiyatını da göster
        
    Returns:
        str: Oluşturulan grafik dosyasının yolu
    """
    if not history_data:
        raise ValueError("No history data provided")
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"price_chart_{symbol}_{timestamp}.png"
    
    filepath = Path(filename)
    
    try:
        # Veriyi hazırla
        dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in history_data]
        prices = [item['price'] for item in history_data]
        prev_closes = [item.get('previous_close') for item in history_data] if show_previous_close else None
        
        # Grafik oluştur
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Ana fiyat çizgisi
        ax.plot(dates, prices, marker='o', linewidth=2, markersize=4, label='Fiyat', color='#2E86AB')
        
        # Önceki kapanış çizgisi (varsa)
        if show_previous_close and prev_closes and all(p is not None for p in prev_closes):
            ax.plot(dates, prev_closes, marker='s', linewidth=1.5, markersize=3, 
                   label='Önceki Kapanış', color='#A23B72', linestyle='--', alpha=0.7)
        
        # Grafik düzenlemeleri
        ax.set_xlabel('Tarih', fontsize=12, fontweight='bold')
        ax.set_ylabel('Fiyat (TL)', fontsize=12, fontweight='bold')
        ax.set_title(f'{symbol} Fiyat Trendi', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='best')
        
        # Tarih formatı
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
        plt.xticks(rotation=45, ha='right')
        
        # Layout ayarları
        plt.tight_layout()
        
        # Kaydet
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Price chart saved: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Error creating price chart: {e}")
        raise


def plot_portfolio_comparison(
    report_data: List[Dict[str, Any]],
    filename: Optional[str] = None
) -> str:
    """
    Portföydeki tüm varlıkların performansını karşılaştırmalı grafik olarak gösterir.
    
    Args:
        report_data: Rapor verisi
        filename: Dosya adı (opsiyonel, otomatik oluşturulur)
        
    Returns:
        str: Oluşturulan grafik dosyasının yolu
    """
    if not report_data:
        raise ValueError("No report data provided")
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"portfolio_comparison_{timestamp}.png"
    
    filepath = Path(filename)
    
    try:
        # Veriyi hazırla
        symbols = []
        daily_changes = []
        total_changes = []
        
        for item in report_data:
            if "error" not in item:
                symbols.append(item['symbol'])
                daily_changes.append(item['daily_change_pct'])
                total_changes.append(item['total_change_pct'])
        
        if not symbols:
            raise ValueError("No valid data to plot")
        
        # Grafik oluştur
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Günlük değişim grafiği
        colors_daily = ['#06A77D' if x >= 0 else '#D00000' for x in daily_changes]
        ax1.barh(symbols, daily_changes, color=colors_daily, alpha=0.7)
        ax1.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        ax1.set_xlabel('Günlük Değişim (%)', fontsize=12, fontweight='bold')
        ax1.set_title('Günlük Performans', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Toplam değişim grafiği
        colors_total = ['#06A77D' if x >= 0 else '#D00000' for x in total_changes]
        ax2.barh(symbols, total_changes, color=colors_total, alpha=0.7)
        ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        ax2.set_xlabel('Toplam Değişim (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Toplam Performans', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Genel başlık
        fig.suptitle('Portföy Performans Karşılaştırması', fontsize=15, fontweight='bold', y=1.02)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Portfolio comparison chart saved: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Error creating portfolio comparison chart: {e}")
        raise
