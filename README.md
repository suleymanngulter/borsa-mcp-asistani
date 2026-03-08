# Borsa & Fon Asistanı - MCP Server

Borsa İstanbul (BIST) hisse senetleri ve TEFAS yatırım fonlarını takip eden, eşik bazlı uyarılar veren ve Gemini AI ile piyasa analizi yapan bir Model Context Protocol (MCP) sunucusu.

## 🚀 Özellikler

- ✅ **Watchlist Yönetimi**: Hisse senetleri ve yatırım fonlarını izleme listesine ekleme/çıkarma
- 📊 **Gerçek Zamanlı Fiyat Takibi**: BIST hisseleri (yfinance) ve TEFAS fonları için güncel fiyat bilgisi
- 🔔 **Eşik Bazlı Uyarılar**: Belirlediğiniz yüzde eşiğine göre kritik uyarılar
- 📈 **Günlük Raporlar**: Portföy performansı ve günlük değişim analizi
- 🤖 **AI Destekli Analiz**: Gemini 2.0 Flash ile akıllı piyasa analizi ve öneriler
- 💾 **SQLite Veritabanı**: Yerel veritabanı ile hızlı ve güvenilir veri saklama
- 📉 **Geçmiş Fiyat Verileri**: Otomatik fiyat geçmişi kaydı ve görüntüleme
- ⚡ **Paralel İşleme**: Çoklu varlık fiyat çekmelerinde performans optimizasyonu
- 🔍 **Detaylı Varlık Bilgisi**: Tek bir varlık için kapsamlı analiz
- 🛠️ **Esnek Yönetim**: Eşik ve alış fiyatı güncelleme özellikleri
- 📧 **E-posta Bildirimleri**: SMTP ile kritik uyarı ve rapor gönderimi
- 📱 **Telegram Bildirimleri**: Telegram bot ile anlık bildirimler
- ⏰ **Otomatik Scheduler**: Periyodik kontroller ve raporlama
- 📤 **Export Özellikleri**: CSV/JSON formatında veri export
- 📊 **Grafik Görselleştirme**: Fiyat trend ve portföy karşılaştırma grafikleri

## 📋 Gereksinimler

- Python 3.8+
- GEMINI_API_KEY (opsiyonel, AI analizi için)

## 🔧 Kurulum

1. **Projeyi klonlayın veya indirin**

2. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Environment değişkenlerini ayarlayın:**
```bash
cp .env.example .env
# .env dosyasını düzenleyip GEMINI_API_KEY'inizi ekleyin
```

## ⚙️ MCP Client Konfigürasyonu

### Claude Desktop için

`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) veya `%APPDATA%\Claude\claude_desktop_config.json` (Windows) dosyasına ekleyin:

```json
{
  "mcpServers": {
    "borsa-asistani": {
      "command": "python",
      "args": ["/home/suleymangulter/Projects/borsa-mcp-asistani/src/main.py"]
    }
  }
}
```

### Cursor için

Cursor ayarlarında MCP server olarak ekleyin.

## 🛠️ Kullanım

### Hızlı Başlangıç (3 Adım)

1. **API Server'ı Başlatın:**
   ```bash
   source venv/bin/activate
   API_PORT=8080 python src/api_server.py
   ```

2. **Tarayıcıda Açın:**
   - http://localhost:8080/docs (Swagger UI - İnteraktif API dokümantasyonu)

3. **İlk Varlığınızı Ekleyin:**
   - `POST /api/watchlist` endpoint'ini seçin
   - "Try it out" → Parametreleri doldurun → "Execute"
   - Örnek:
     ```json
     {
       "symbol": "THYAO",
       "asset_type": "hisse",
       "price": 250.0,
       "threshold": 5.0
     }
     ```

**Detaylı kullanım için:** [KULLANIM_KILAVUZU.md](KULLANIM_KILAVUZU.md) dosyasına bakın.

### MCP Araçları

#### 1. `add_to_watchlist`
Bir hisse senedi veya fonu izleme listesine ekler.

**Parametreler:**
- `symbol`: Ticker sembolü (örn: THYAO, GMR)
- `asset_type`: 'hisse' veya 'fon'
- `price`: Alış/Referans fiyatı
- `threshold`: Uyarı eşiği yüzdesi (varsayılan: 5.0%)

**Örnek:**
```
add_to_watchlist(symbol="THYAO", asset_type="hisse", price=150.0, threshold=5.0)
```

#### 2. `remove_from_watchlist`
İzleme listesinden bir varlığı çıkarır.

**Parametreler:**
- `symbol`: Çıkarılacak ticker sembolü

#### 3. `get_portfolio_status`
Mevcut portföy performansını ve aktif kritik uyarıları döndürür.

**Dönen Veri:**
- Portföy özeti (sembol, fiyat, günlük/toplam değişim)
- Kritik uyarılar listesi

#### 4. `get_market_analysis`
Gemini AI kullanarak portföy verilerini analiz eder ve insan benzeri öngörüler sağlar.

**Not:** Bu özellik için GEMINI_API_KEY gereklidir.

#### 5. `get_asset_details`
Belirli bir varlığın detaylı bilgilerini döndürür.

**Parametreler:**
- `symbol`: Detayları alınacak ticker sembolü

**Dönen Veri:**
- Sembol, varlık tipi, alış fiyatı, güncel fiyat
- Günlük ve toplam değişim yüzdeleri
- Eşik durumu ve uyarı durumu

#### 6. `update_threshold`
Bir varlığın uyarı eşiğini günceller.

**Parametreler:**
- `symbol`: Güncellenecek ticker sembolü
- `new_threshold`: Yeni eşik yüzdesi (>= 0)

#### 7. `update_purchase_price`
Bir varlığın alış/referans fiyatını günceller.

**Parametreler:**
- `symbol`: Güncellenecek ticker sembolü
- `new_price`: Yeni alış fiyatı (> 0)

#### 8. `get_watchlist`
Tüm izleme listesini döndürür.

**Dönen Veri:**
- Toplam varlık sayısı
- Tüm varlıkların listesi (sembol, tip, alış fiyatı, eşik)

#### 9. `get_price_history`
Bir varlığın geçmiş fiyat verilerini döndürür.

**Parametreler:**
- `symbol`: Geçmiş verisi alınacak ticker sembolü
- `days`: Kaç günlük veri alınacak (varsayılan: 30, maksimum: 365)

**Dönen Veri:**
- Tarih, fiyat ve önceki kapanış fiyatı bilgileri

#### 10. `send_alert_notifications`
Kritik uyarıları kontrol eder ve yapılandırılmış bildirim kanallarına gönderir.

#### 11. `send_daily_report_notification`
Günlük portföy raporunu yapılandırılmış bildirim kanallarına gönderir.

#### 12. `export_portfolio`
Portföy raporunu CSV veya JSON formatında export eder.

**Parametreler:**
- `format`: Export formatı ('csv' veya 'json', varsayılan: 'json')
- `filename`: Dosya adı (opsiyonel)

#### 13. `export_price_history`
Bir varlığın fiyat geçmişini CSV veya JSON formatında export eder.

**Parametreler:**
- `symbol`: Ticker sembolü
- `days`: Kaç günlük veri (varsayılan: 30, maksimum: 365)
- `format`: Export formatı ('csv' veya 'json')
- `filename`: Dosya adı (opsiyonel)

#### 14. `generate_price_chart`
Bir varlık için fiyat trend grafiği oluşturur.

**Parametreler:**
- `symbol`: Ticker sembolü
- `days`: Kaç günlük veri (varsayılan: 30, maksimum: 365)
- `filename`: Dosya adı (opsiyonel)

#### 15. `generate_portfolio_chart`
Portföydeki tüm varlıkların performans karşılaştırma grafiğini oluşturur.

**Parametreler:**
- `filename`: Dosya adı (opsiyonel)

### HTTP API Server

Web arayüzü veya HTTP client'lar için REST API:

```bash
# API server'ı başlat (varsayılan port: 8000)
python src/api_server.py

# Tarayıcıdan eriş: http://localhost:8000
# API dokümantasyonu: http://localhost:8000/docs
```

**API Endpoints:**
- `GET /` - API bilgileri
- `GET /api/watchlist` - Tüm watchlist
- `POST /api/watchlist` - Watchlist'e varlık ekle
- `DELETE /api/watchlist/{symbol}` - Watchlist'ten varlık çıkar
- `GET /api/portfolio` - Portföy durumu
- `GET /api/alerts` - Kritik uyarılar
- `GET /api/asset/{symbol}` - Varlık detayları
- `GET /api/price-history/{symbol}?days=30` - Fiyat geçmişi
- `PATCH /api/watchlist/{symbol}/threshold` - Eşik güncelle
- `PATCH /api/watchlist/{symbol}/price` - Alış fiyatı güncelle
- `POST /api/export/portfolio` - Portföy export

Port'u değiştirmek için `.env` dosyasına `API_PORT=8080` ekleyin.

### Komut Satırı Kullanımı

```bash
# Günlük rapor oluştur
python src/engine.py --report

# Kritik uyarıları kontrol et
python src/engine.py --alerts
```

## 📁 Proje Yapısı

```
borsa-mcp-asistani/
├── src/
│   ├── main.py          # MCP server ve tool tanımları
│   ├── database.py      # SQLite veritabanı yönetimi
│   ├── tracker.py       # Fiyat çekme fonksiyonları
│   ├── engine.py        # Rapor ve uyarı motoru
│   ├── notifications.py # E-posta ve Telegram bildirimleri
│   ├── scheduler.py     # Otomatik periyodik kontroller
│   ├── export.py        # CSV/JSON export fonksiyonları
│   ├── graph.py         # Grafik görselleştirme
│   └── api_server.py    # HTTP REST API server
├── tests/               # Test dosyaları
│   ├── test_database.py
│   ├── test_engine.py
│   └── test_integration.py
├── requirements.txt     # Python bağımlılıkları
├── pytest.ini          # Pytest yapılandırması
├── .env.example        # Environment değişken şablonu
├── borsa_asistani.db   # SQLite veritabanı (otomatik oluşur)
└── README.md           # Bu dosya
```

## 🔍 Desteklenen Varlık Türleri

### Hisse Senetleri (BIST)
- Format: Sembol (örn: THYAO, AKBNK, GARAN)
- Veri Kaynağı: yfinance (Yahoo Finance)
- Otomatik olarak `.IS` uzantısı eklenir

### Yatırım Fonları (TEFAS)
- Format: Fon kodu (örn: GMR, YAS)
- Veri Kaynağı: tefas-crawler

## 🐛 Sorun Giderme

### Fiyat verisi alınamıyor
- İnternet bağlantınızı kontrol edin
- Sembolün doğru olduğundan emin olun
- API limitlerini kontrol edin

### Gemini AI çalışmıyor
- `.env` dosyasında `GEMINI_API_KEY` tanımlı olduğundan emin olun
- API key'in geçerli olduğunu kontrol edin

### Bildirimler çalışmıyor
- **E-posta için:** `.env` dosyasında `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` ayarlarını kontrol edin
- **Telegram için:** `.env` dosyasında `TELEGRAM_BOT_TOKEN` ve `TELEGRAM_CHAT_ID` ayarlarını kontrol edin
- Telegram bot token'ı [@BotFather](https://t.me/botfather) üzerinden alabilirsiniz

### Scheduler kullanımı
```bash
# Scheduler'ı başlat
python src/scheduler.py

# Environment değişkenleri ile özelleştir:
# ALERT_INTERVAL_MINUTES=60 (varsayılan: 60)
# DAILY_REPORT_TIME=09:00 (varsayılan: 09:00)
# ENABLE_ALERTS=true (varsayılan: true)
# ENABLE_DAILY_REPORT=true (varsayılan: true)
```

### Testleri çalıştırma
```bash
# Tüm testleri çalıştır
pytest

# Coverage ile çalıştır
pytest --cov=src
```

## 📝 Lisans

Bu proje eğitim ve pratik amaçlı geliştirilmiştir.

## 🤝 Katkıda Bulunma

Öneriler ve iyileştirmeler için issue açabilir veya pull request gönderebilirsiniz.

## 📚 Detaylı Kullanım Kılavuzu

Kapsamlı kullanım örnekleri ve senaryolar için [KULLANIM_KILAVUZU.md](KULLANIM_KILAVUZU.md) dosyasına bakın.

## 📧 İletişim

Sorularınız için issue açabilirsiniz.
