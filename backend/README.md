# BDC Backend

## Kurulum

1. Sanal ortam oluştur ve aktif et:
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# veya
venv\Scripts\activate  # Windows
```

2. Bağımlılıkları yükle:
```bash
pip install -r requirements.txt
```

3. Ortam değişkenlerini ayarla:
```bash
cp .env.example .env
# .env dosyasını düzenle ve gerekli değerleri gir
```

4. Veritabanını oluştur:
```bash
python init_db.py
```

5. Redis'i başlat (Docker ile):
```bash
docker run -d -p 6379:6379 redis:alpine
```

## Çalıştırma

### Development ortamında:
```bash
python run.py
```

Backend http://localhost:5000 adresinde çalışacaktır.

### Production ortamında:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## Test

```bash
# Tüm testleri çalıştır
pytest

# Coverage ile testleri çalıştır
pytest --cov=app tests/
```

## API Dokümantasyonu

API dokümantasyonu http://localhost:5000/docs adresinde bulunabilir.

## Varsayılan Kullanıcılar

Sistem başlatıldığında aşağıdaki kullanıcılar otomatik oluşturulur:

- **Super Admin**: admin@bdc.com / Admin123!
- **Tenant Admin**: tenant@bdc.com / Tenant123!
- **Trainer**: trainer@bdc.com / Trainer123!
- **Student**: student@bdc.com / Student123!