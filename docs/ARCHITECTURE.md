# 🏗️ Mimari Dokümantasyon

Bu dokümantasyon, Borsa & Fon Asistanı projesinin mimari yapısını ve tasarım kararlarını açıklar.

## 📐 Genel Mimari

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Server (main.py)                  │
│              FastMCP ile 15 MCP Tool                     │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼──────────┐ ┌───────────────┐
│  HTTP API    │ │  Engine     │ │  Database    │
│ (api_server) │ │  (engine)   │ │  (database)  │
└───────┬──────┘ └──┬───────────┘ └──────┬───────┘
        │           │                    │
        │    ┌──────▼──────────┐        │
        │    │   Tracker        │        │
        │    │  (tracker)       │        │
        │    └──────┬───────────┘        │
        │           │                    │
        │    ┌──────▼───────────┐       │
        │    │ Notifications    │       │
        │    │ (notifications)  │       │
        │    └──────────────────┘       │
        │                                │
┌───────▼───────────────────────────────▼──────┐
│         External Services                      │
│  - yfinance (BIST stocks)                      │
│  - TEFAS Crawler (Funds)                       │
│  - Gemini AI (Market Analysis)                 │
│  - SMTP (Email)                                 │
│  - Telegram API                                 │
└────────────────────────────────────────────────┘
```

## 📦 Modül Yapısı

### Core Modüller

#### `src/main.py`
- **Rol:** MCP server ana giriş noktası
- **Sorumluluklar:**
  - FastMCP server başlatma
  - 15 MCP tool tanımlama
  - Gemini AI entegrasyonu
  - Tool'lar arası koordinasyon

#### `src/database.py`
- **Rol:** Veritabanı yönetimi
- **Sorumluluklar:**
  - SQLite veritabanı işlemleri
  - Watchlist CRUD operasyonları
  - Fiyat geçmişi saklama
  - Veri bütünlüğü

#### `src/tracker.py`
- **Rol:** Fiyat verisi çekme
- **Sorumluluklar:**
  - BIST hisse fiyatları (yfinance)
  - TEFAS fon fiyatları (tefas-crawler)
  - Retry mekanizması
  - Hata yönetimi

#### `src/engine.py`
- **Rol:** İş mantığı ve hesaplamalar
- **Sorumluluklar:**
  - Uyarı kontrolü
  - Günlük rapor oluşturma
  - Performans hesaplamaları
  - Paralel işleme

### API Modülü

#### `src/api_server.py`
- **Rol:** HTTP REST API sunucusu
- **Sorumluluklar:**
  - FastAPI uygulaması
  - REST endpoint'leri
  - Request/Response validation
  - CORS yönetimi

### Yardımcı Modüller

#### `src/notifications.py`
- **Rol:** Bildirim sistemi
- **Sorumluluklar:**
  - E-posta bildirimleri
  - Telegram bildirimleri
  - Bildirim formatlama

#### `src/scheduler.py`
- **Rol:** Zamanlanmış görevler
- **Sorumluluklar:**
  - Periyodik uyarı kontrolleri
  - Günlük rapor gönderimi
  - Schedule yönetimi

#### `src/export.py`
- **Rol:** Veri export
- **Sorumluluklar:**
  - CSV export
  - JSON export
  - Dosya yönetimi

#### `src/graph.py`
- **Rol:** Grafik görselleştirme
- **Sorumluluklar:**
  - Fiyat trend grafikleri
  - Portföy karşılaştırma grafikleri
  - Matplotlib entegrasyonu

#### `src/config.py`
- **Rol:** Yapılandırma yönetimi
- **Sorumluluklar:**
  - Merkezi sabitler
  - Environment variable yönetimi
  - Varsayılan değerler

## 🔄 Veri Akışı

### Fiyat Çekme Akışı

```
User Request
    │
    ▼
MCP Tool / API Endpoint
    │
    ▼
engine.py → tracker.py
    │
    ├──► get_stock_price() → yfinance
    │
    └──► get_fund_price() → TEFAS Crawler
    │
    ▼
Price Data
    │
    ▼
database.py → SQLite
    │
    ▼
Response to User
```

### Uyarı Kontrolü Akışı

```
Scheduler / Manual Trigger
    │
    ▼
engine.check_alerts()
    │
    ├──► Parallel Processing (ThreadPoolExecutor)
    │   ├──► Asset 1 → Price Check
    │   ├──► Asset 2 → Price Check
    │   └──► Asset N → Price Check
    │
    ▼
Threshold Comparison
    │
    ├──► Exceeded? → Critical Alert
    │
    ▼
notifications.py
    │
    ├──► Email Notification
    └──► Telegram Notification
```

## 🗄️ Veritabanı Şeması

### `watchlist` Tablosu

```sql
CREATE TABLE watchlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    asset_type TEXT CHECK(asset_type IN ('hisse', 'fon')),
    purchase_price REAL NOT NULL,
    threshold_percent REAL NOT NULL
);
```

### `historical_prices` Tablosu

```sql
CREATE TABLE historical_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    date DATE NOT NULL,
    price REAL NOT NULL,
    previous_close REAL,
    UNIQUE(symbol, date)
);
```

## 🔧 Tasarım Kararları

### 1. Modüler Yapı
- Her modül tek bir sorumluluğa sahip
- Loose coupling, high cohesion
- Kolay test edilebilir

### 2. Paralel İşleme
- ThreadPoolExecutor kullanımı
- Çoklu varlık fiyat çekmelerinde performans artışı
- Configurable worker sayısı

### 3. Retry Mekanizması
- Network hatalarına karşı dayanıklılık
- Configurable retry count
- Exponential backoff (gelecek sürüm)

### 4. Merkezi Yapılandırma
- Tüm sabitler `config.py`'de
- Environment variable desteği
- Kolay bakım ve güncelleme

### 5. Hata Yönetimi
- Try-except blokları
- Detaylı logging
- Kullanıcı dostu hata mesajları

## 🚀 Performans Optimizasyonları

1. **Paralel İşleme:** ThreadPoolExecutor ile çoklu fiyat çekme
2. **Veritabanı İndeksleri:** Symbol ve date için unique constraint
3. **Caching:** (Gelecek sürüm) Fiyat verileri için cache
4. **Connection Pooling:** (Gelecek sürüm) Veritabanı bağlantı havuzu

## 🔐 Güvenlik

1. **Input Validation:** Pydantic modelleri ile validation
2. **SQL Injection:** Parametrized queries
3. **CORS:** Configurable CORS ayarları
4. **API Key:** (Gelecek sürüm) API authentication

## 📈 Ölçeklenebilirlik

### Mevcut Sınırlamalar
- SQLite (tek kullanıcı, düşük trafik)
- Tek sunucu mimarisi
- Memory-based processing

### Gelecek İyileştirmeler
- PostgreSQL/MongoDB desteği
- Redis cache
- Microservices mimarisi
- Load balancing

## 🧪 Test Stratejisi

1. **Unit Tests:** Her modül için ayrı testler
2. **Integration Tests:** Modüller arası entegrasyon
3. **Mocking:** External API'ler için mock'lar
4. **Coverage:** Minimum %80 coverage hedefi

## 📝 Notlar

- Proje eğitim ve pratik amaçlı geliştirilmiştir
- Production kullanımı için ek güvenlik önlemleri gerekebilir
- Performans testleri yapılmalıdır
- Monitoring ve alerting eklenmelidir
