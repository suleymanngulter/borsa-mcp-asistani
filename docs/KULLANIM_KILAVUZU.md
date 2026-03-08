# 📖 Borsa & Fon Asistanı - Kullanım Kılavuzu

Bu kılavuz, Borsa & Fon Asistanı'nı nasıl kullanacağınızı adım adım açıklar.

## 🚀 Hızlı Başlangıç

### 1. Kurulum

```bash
# Projeyi klonlayın veya indirin
cd /path/to/borsa-mcp-asistani

# Virtual environment oluşturun (önerilir)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
# venv\Scripts\activate  # Windows

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

### 2. Yapılandırma

`.env` dosyası oluşturun:

```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin:

```env
# Opsiyonel: Gemini AI için (piyasa analizi özelliği)
GEMINI_API_KEY=your_gemini_api_key_here

# Opsiyonel: E-posta bildirimleri için
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@gmail.com

# Opsiyonel: Telegram bildirimleri için
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Opsiyonel: API server portu (varsayılan: 8000)
API_PORT=8080

# Opsiyonel: Log seviyesi
LOG_LEVEL=INFO
```

### 3. API Server'ı Başlatma

```bash
# Virtual environment'ı aktifleştirin
source venv/bin/activate

# API server'ı başlatın
API_PORT=8080 python src/api_server.py
```

Server başladıktan sonra tarayıcıdan şu adreslere erişebilirsiniz:
- **Ana sayfa:** http://localhost:8080
- **API Dokümantasyonu:** http://localhost:8080/docs
- **Alternatif Dokümantasyon:** http://localhost:8080/redoc

## 📱 Kullanım Senaryoları

### Senaryo 1: Web Arayüzü ile Kullanım (Swagger UI)

1. Tarayıcıda http://localhost:8080/docs adresine gidin
2. İstediğiniz endpoint'i seçin
3. "Try it out" butonuna tıklayın
4. Parametreleri doldurun
5. "Execute" butonuna tıklayın
6. Sonuçları görüntüleyin

### Senaryo 2: cURL ile Kullanım

#### Watchlist'e Varlık Ekleme

```bash
# Hisse senedi ekle
curl -X POST http://localhost:8080/api/watchlist \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "THYAO",
    "asset_type": "hisse",
    "price": 250.0,
    "threshold": 5.0
  }'

# Fon ekle
curl -X POST http://localhost:8080/api/watchlist \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "GMR",
    "asset_type": "fon",
    "price": 10.0,
    "threshold": 3.0
  }'
```

#### Watchlist'i Görüntüleme

```bash
curl http://localhost:8080/api/watchlist | python -m json.tool
```

#### Portföy Durumunu Kontrol Etme

```bash
curl http://localhost:8080/api/portfolio | python -m json.tool
```

#### Kritik Uyarıları Kontrol Etme

```bash
curl http://localhost:8080/api/alerts | python -m json.tool
```

#### Varlık Detaylarını Görüntüleme

```bash
curl http://localhost:8080/api/asset/THYAO | python -m json.tool
```

#### Eşik Değerini Güncelleme

```bash
curl -X PATCH http://localhost:8080/api/watchlist/THYAO/threshold \
  -H "Content-Type: application/json" \
  -d '{"new_threshold": 10.0}'
```

#### Alış Fiyatını Güncelleme

```bash
curl -X PATCH http://localhost:8080/api/watchlist/THYAO/price \
  -H "Content-Type: application/json" \
  -d '{"new_price": 260.0}'
```

#### Varlık Silme

```bash
curl -X DELETE http://localhost:8080/api/watchlist/THYAO
```

#### Fiyat Geçmişini Görüntüleme

```bash
# Son 30 gün
curl "http://localhost:8080/api/price-history/THYAO?days=30" | python -m json.tool

# Son 7 gün
curl "http://localhost:8080/api/price-history/THYAO?days=7" | python -m json.tool
```

#### Portföy Export

```bash
curl -X POST http://localhost:8080/api/export/portfolio \
  -H "Content-Type: application/json" \
  -d '{"format": "json"}'
```

### Senaryo 3: Python ile Kullanım

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
print(f"Kritik uyarı: {len(portfolio['critical_alerts'])}")

# Varlık detaylarını al
response = requests.get(f"{BASE_URL}/api/asset/THYAO")
asset = response.json()
print(f"THYAO Fiyatı: {asset['current_price']} TL")
print(f"Günlük Değişim: %{asset['daily_change_pct']}")
```

### Senaryo 4: JavaScript/Node.js ile Kullanım

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

// Kullanım
addAsset('THYAO', 'hisse', 250.0, 5.0)
  .then(result => console.log('Eklendi:', result));

getPortfolio()
  .then(portfolio => {
    console.log('Portföy:', portfolio.summary);
    console.log('Uyarılar:', portfolio.critical_alerts);
  });
```

## 🔄 Günlük Kullanım Akışı

### Sabah Rutini

1. **API server'ı başlatın:**
   ```bash
   source venv/bin/activate
   API_PORT=8080 python src/api_server.py
   ```

2. **Portföy durumunu kontrol edin:**
   ```bash
   curl http://localhost:8080/api/portfolio | python -m json.tool
   ```

3. **Kritik uyarıları kontrol edin:**
   ```bash
   curl http://localhost:8080/api/alerts | python -m json.tool
   ```

### Gün İçi İşlemler

- Yeni varlık ekleme
- Fiyat güncellemeleri
- Eşik değeri ayarlamaları
- Portföy raporları

### Akşam Rutini

1. **Günlük raporu export edin:**
   ```bash
   curl -X POST http://localhost:8080/api/export/portfolio \
     -H "Content-Type: application/json" \
     -d '{"format": "json"}'
   ```

2. **Fiyat geçmişini kontrol edin:**
   ```bash
   curl "http://localhost:8080/api/price-history/THYAO?days=30" | python -m json.tool
   ```

## ⏰ Otomatik Kontroller (Scheduler)

Otomatik periyodik kontroller için scheduler kullanın:

```bash
# Scheduler'ı başlat
python src/scheduler.py
```

Scheduler şunları yapar:
- Belirttiğiniz aralıklarla (varsayılan: 60 dakika) kritik uyarıları kontrol eder
- Her gün belirttiğiniz saatte (varsayılan: 09:00) günlük rapor gönderir

**Yapılandırma (.env dosyasına ekleyin):**
```env
ALERT_INTERVAL_MINUTES=60
DAILY_REPORT_TIME=09:00
ENABLE_ALERTS=true
ENABLE_DAILY_REPORT=true
```

## 📊 Komut Satırı Araçları

### Günlük Rapor

```bash
python src/engine.py --report
```

### Kritik Uyarılar

```bash
python src/engine.py --alerts
```

## 🎯 Örnek Kullanım Senaryoları

### Senaryo A: Yeni Başlayan Kullanıcı

1. **İlk kurulum:**
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # .env dosyasını düzenleyin
   ```

2. **API server'ı başlatın:**
   ```bash
   source venv/bin/activate
   API_PORT=8080 python src/api_server.py
   ```

3. **Tarayıcıda http://localhost:8080/docs adresine gidin**

4. **İlk varlığınızı ekleyin:**
   - `POST /api/watchlist` endpoint'ini seçin
   - "Try it out" butonuna tıklayın
   - Örnek:
     ```json
     {
       "symbol": "THYAO",
       "asset_type": "hisse",
       "price": 250.0,
       "threshold": 5.0
     }
     ```
   - "Execute" butonuna tıklayın

5. **Portföy durumunu kontrol edin:**
   - `GET /api/portfolio` endpoint'ini seçin
   - "Execute" butonuna tıklayın

### Senaryo B: Gelişmiş Kullanıcı

1. **Otomatik scheduler kurulumu:**
   ```bash
   # .env dosyasına ekleyin
   ALERT_INTERVAL_MINUTES=30
   DAILY_REPORT_TIME=09:00
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

2. **Scheduler'ı başlatın:**
   ```bash
   python src/scheduler.py
   ```

3. **API ile entegrasyon:**
   - Kendi web uygulamanızdan API'yi çağırın
   - Mobil uygulama geliştirin
   - Dashboard oluşturun

## 🔍 Desteklenen Varlık Türleri

### Hisse Senetleri (BIST)

**Format:** Sadece sembol (örn: THYAO, AKBNK, GARAN)

**Örnekler:**
- THYAO (Türk Hava Yolları)
- AKBNK (Akbank)
- GARAN (Garanti BBVA)
- ISCTR (İş Bankası)

**Not:** Sistem otomatik olarak `.IS` uzantısını ekler.

### Yatırım Fonları (TEFAS)

**Format:** Fon kodu (örn: GMR, YAS, MAC)

**Örnekler:**
- GMR (Güven Menkul Değerler)
- YAS (Yapı Kredi)
- MAC (Midas Menkul Değerler)

**Not:** TEFAS fon kodlarını [TEFAS web sitesinden](https://www.tefas.gov.tr) bulabilirsiniz.

## 🐛 Sorun Giderme

### API Server Başlamıyor

**Sorun:** Port zaten kullanımda
```bash
# Çözüm: Farklı port kullanın
API_PORT=9000 python src/api_server.py
```

### Fiyat Verisi Alınamıyor

**Sorun:** İnternet bağlantısı veya API limiti
- İnternet bağlantınızı kontrol edin
- Sembolün doğru olduğundan emin olun
- Birkaç dakika bekleyip tekrar deneyin

### Virtual Environment Hatası

**Sorun:** `ModuleNotFoundError`
```bash
# Çözüm: Virtual environment'ı aktifleştirin
source venv/bin/activate
```

### TEFAS Fon Hatası

**Sorun:** Fon kodu bulunamıyor
- Fon kodunun doğru olduğundan emin olun
- TEFAS web sitesinden güncel fon kodlarını kontrol edin

## 📚 Ek Kaynaklar

- **API Dokümantasyonu:** http://localhost:8080/docs
- **Proje README:** README.md
- **TEFAS Fon Kodları:** https://www.tefas.gov.tr
- **BIST Hisse Kodları:** https://www.borsaistanbul.com

## 💡 İpuçları

1. **Eşik Değerleri:** Farklı varlıklar için farklı eşik değerleri kullanın
   - Volatil hisseler için: %10-15
   - Stabil hisseler için: %5-7
   - Fonlar için: %3-5

2. **Alış Fiyatı:** Gerçek alış fiyatınızı kullanın, böylece toplam getiri doğru hesaplanır

3. **Günlük Kontroller:** Scheduler kullanarak otomatik kontroller yapın

4. **Export:** Düzenli olarak portföy raporlarını export edin

5. **Bildirimler:** E-posta veya Telegram bildirimlerini aktif edin

## 🎓 Öğrenme Yolu

1. **Başlangıç:** Web arayüzü (Swagger UI) ile temel işlemleri öğrenin
2. **Orta Seviye:** cURL komutları ile komut satırından kullanın
3. **İleri Seviye:** Kendi uygulamanızı geliştirin (Python, JavaScript, vb.)
4. **Uzman:** Scheduler ve bildirimleri yapılandırın

---

**Sorularınız için:** GitHub'da issue açabilir veya dokümantasyonu inceleyebilirsiniz.
