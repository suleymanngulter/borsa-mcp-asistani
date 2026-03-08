# 📡 API Dokümantasyonu

Bu dokümantasyon, Borsa & Fon Asistanı HTTP REST API'sinin detaylı kullanımını açıklar.

## 🌐 Base URL

```
http://localhost:8080
```

Varsayılan port 8080'dir. `API_PORT` environment variable ile değiştirilebilir.

## 📚 Endpoints

### Ana Sayfa

**GET** `/`

API hakkında genel bilgi ve mevcut endpoint'leri döndürür.

**Response:**
```json
{
  "message": "Borsa & Fon Asistanı API",
  "version": "1.0.0",
  "endpoints": {
    "watchlist": "/api/watchlist",
    "portfolio": "/api/portfolio",
    "alerts": "/api/alerts",
    "asset_details": "/api/asset/{symbol}",
    "price_history": "/api/price-history/{symbol}"
  }
}
```

### Watchlist Yönetimi

#### Watchlist'i Görüntüleme

**GET** `/api/watchlist`

Tüm watchlist'i döndürür.

**Response:**
```json
{
  "total_assets": 2,
  "assets": [
    {
      "symbol": "THYAO",
      "asset_type": "hisse",
      "purchase_price": 250.0,
      "threshold_percent": 5.0
    }
  ]
}
```

#### Varlık Ekleme

**POST** `/api/watchlist`

Watchlist'e yeni varlık ekler.

**Request Body:**
```json
{
  "symbol": "THYAO",
  "asset_type": "hisse",
  "price": 250.0,
  "threshold": 5.0
}
```

**Response:**
```json
{
  "message": "✅ THYAO successfully added to watchlist",
  "symbol": "THYAO"
}
```

#### Varlık Silme

**DELETE** `/api/watchlist/{symbol}`

Watchlist'ten varlık çıkarır.

**Response:**
```json
{
  "message": "✅ THYAO removed from watchlist"
}
```

### Portföy Durumu

**GET** `/api/portfolio`

Portföy performansını ve kritik uyarıları döndürür.

**Response:**
```json
{
  "summary": [
    {
      "symbol": "THYAO",
      "asset_type": "hisse",
      "current_price": 276.75,
      "daily_change_pct": -2.72,
      "total_change_pct": 10.7
    }
  ],
  "critical_alerts": [
    "CRITICAL: THYAO change (10.70%) exceeds threshold (10.0%)!"
  ]
}
```

### Kritik Uyarılar

**GET** `/api/alerts`

Aktif kritik uyarıları döndürür.

**Response:**
```json
{
  "alerts": [
    "CRITICAL: THYAO change (10.70%) exceeds threshold (10.0%)!"
  ],
  "count": 1
}
```

### Varlık Detayları

**GET** `/api/asset/{symbol}`

Belirli bir varlık için detaylı bilgi döndürür.

**Response:**
```json
{
  "symbol": "THYAO",
  "asset_type": "hisse",
  "purchase_price": 250.0,
  "current_price": 276.75,
  "previous_close": 284.5,
  "threshold_percent": 5.0,
  "daily_change_pct": -2.72,
  "total_change_pct": 10.7,
  "threshold_exceeded": true,
  "status": "CRITICAL"
}
```

### Fiyat Geçmişi

**GET** `/api/price-history/{symbol}?days=30`

Varlık için fiyat geçmişini döndürür.

**Query Parameters:**
- `days` (optional): Gün sayısı (varsayılan: 30, maksimum: 365)

**Response:**
```json
{
  "symbol": "THYAO",
  "total_days": 30,
  "history": [
    {
      "date": "2026-03-08",
      "price": 276.75,
      "previous_close": 284.5
    }
  ]
}
```

### Eşik Değeri Güncelleme

**PATCH** `/api/watchlist/{symbol}/threshold`

Varlık için eşik değerini günceller.

**Request Body:**
```json
{
  "new_threshold": 10.0
}
```

**Response:**
```json
{
  "message": "✅ Threshold for THYAO updated to 10.0%"
}
```

### Alış Fiyatı Güncelleme

**PATCH** `/api/watchlist/{symbol}/price`

Varlık için alış fiyatını günceller.

**Request Body:**
```json
{
  "new_price": 260.0
}
```

**Response:**
```json
{
  "message": "✅ Purchase price for THYAO updated to 260.0"
}
```

### Export İşlemleri

#### Portföy Export

**POST** `/api/export/portfolio`

Portföy raporunu export eder.

**Request Body:**
```json
{
  "format": "json",
  "filename": "portfolio_report.json"
}
```

**Response:**
```json
{
  "message": "✅ Portfolio exported successfully",
  "filepath": "portfolio_report_20260308_165621.json"
}
```

#### Fiyat Geçmişi Export

**POST** `/api/export/price-history/{symbol}`

Fiyat geçmişini export eder.

**Request Body:**
```json
{
  "days": 30,
  "format": "csv",
  "filename": "thyao_history.csv"
}
```

### Grafik Oluşturma

#### Fiyat Grafiği

**POST** `/api/charts/price/{symbol}`

Varlık için fiyat trend grafiği oluşturur.

**Request Body:**
```json
{
  "days": 30,
  "filename": "thyao_chart.png"
}
```

**Response:**
```json
{
  "message": "✅ Price chart generated successfully",
  "filepath": "price_chart_THYAO_20260308_165621.png"
}
```

#### Portföy Karşılaştırma Grafiği

**POST** `/api/charts/portfolio`

Portföy karşılaştırma grafiği oluşturur.

**Request Body:**
```json
{
  "filename": "portfolio_comparison.png"
}
```

## 🔐 Hata Yönetimi

API, standart HTTP status kodlarını kullanır:

- `200 OK`: Başarılı istek
- `400 Bad Request`: Geçersiz parametreler
- `404 Not Found`: Kaynak bulunamadı
- `500 Internal Server Error`: Sunucu hatası

**Hata Response Formatı:**
```json
{
  "detail": "Hata mesajı burada görünür"
}
```

## 📝 Örnek Kullanımlar

### cURL Örnekleri

```bash
# Watchlist'i görüntüle
curl http://localhost:8080/api/watchlist

# Varlık ekle
curl -X POST http://localhost:8080/api/watchlist \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "THYAO",
    "asset_type": "hisse",
    "price": 250.0,
    "threshold": 5.0
  }'

# Portföy durumunu kontrol et
curl http://localhost:8080/api/portfolio

# Kritik uyarıları kontrol et
curl http://localhost:8080/api/alerts
```

### Python Örnekleri

```python
import requests

BASE_URL = "http://localhost:8080"

# Watchlist'e varlık ekle
response = requests.post(
    f"{BASE_URL}/api/watchlist",
    json={
        "symbol": "THYAO",
        "asset_type": "hisse",
        "price": 250.0,
        "threshold": 5.0
    }
)
print(response.json())

# Portföy durumunu al
response = requests.get(f"{BASE_URL}/api/portfolio")
portfolio = response.json()
print(f"Toplam varlık: {len(portfolio['summary'])}")
```

### JavaScript Örnekleri

```javascript
const BASE_URL = 'http://localhost:8080';

// Watchlist'e varlık ekle
async function addAsset(symbol, assetType, price, threshold) {
  const response = await fetch(`${BASE_URL}/api/watchlist`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      symbol: symbol,
      asset_type: assetType,
      price: price,
      threshold: threshold
    })
  });
  return await response.json();
}

// Portföy durumunu al
async function getPortfolio() {
  const response = await fetch(`${BASE_URL}/api/portfolio`);
  return await response.json();
}
```

## 🔄 Swagger UI

API dokümantasyonu için interaktif Swagger UI kullanılabilir:

```
http://localhost:8080/docs
```

Alternatif olarak ReDoc:

```
http://localhost:8080/redoc
```

## 📊 Rate Limiting

Şu anda rate limiting yoktur. Production ortamında rate limiting eklenmesi önerilir.

## 🔒 Güvenlik

- CORS ayarları `CORS_ORIGINS` environment variable ile yapılandırılabilir
- Production ortamında spesifik domain'ler belirtilmelidir
- API key authentication eklenebilir (gelecek sürüm)
