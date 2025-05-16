# BDC Frontend

## Kurulum

1. Bağımlılıkları yükle:
```bash
npm install
```

2. Ortam değişkenlerini ayarla:
```bash
cp .env.example .env
# .env dosyasını düzenle
```

3. Backend API URL'ini ayarla (.env dosyasında):
```
VITE_API_URL=http://localhost:5000
```

## Çalıştırma

### Development ortamında:
```bash
npm run dev
```

Frontend http://localhost:5173 adresinde çalışacaktır.

### Production build:
```bash
npm run build
npm run preview
```

## Test

```bash
# Birim testleri çalıştır
npm test

# E2E testleri çalıştır
npm run test:e2e

# Coverage raporu
npm run test:coverage
```

## Kullanım

1. Tarayıcıda http://localhost:5173 adresine git
2. Varsayılan kullanıcılardan biriyle giriş yap:
   - admin@bdc.com / Admin123!
   - trainer@bdc.com / Trainer123!
   - student@bdc.com / Student123!

## Özellikler

- Rol bazlı yetkilendirme
- Gerçek zamanlı bildirimler
- AI destekli analizler
- Responsive tasarım
- Dark/Light tema desteği