# BDC Uygulama Test Ortamı - Tam Rehber

Bu belge, BDC uygulamasını farklı şekillerde test etmek için hazırlanan Docker tabanlı test ortamlarının kullanımını açıklamaktadır.

## 1. API Test Arayüzü

### Erişim Bilgileri
- **API Sunucusu**: http://localhost:8888
- **Test Arayüzü**: http://localhost:8091

### Kullanım
Test arayüzüne eriştiğinizde, sağ menüdeki butonları kullanarak API endpointlerini test edebilirsiniz:
1. Health Check butonu: API'nin çalışıp çalışmadığını kontrol eder
2. Login formunu kullanarak giriş yapabilirsiniz
3. Get Me butonu: Oturum açan kullanıcının bilgilerini gösterir
4. Diğer butonlar: Diğer API endpoint'lerini test etmenizi sağlar

## 2. Tam Uygulama Simülasyonu

### Erişim Bilgileri
- **Uygulama Adresi**: http://localhost:5173

### Kullanım
Bu tam özellikli bir SPA (Single Page Application) simülasyonudur:

1. Login ekranında varsayılan kullanıcı bilgilerini kullanın:
   - Email: admin@bdc.com
   - Şifre: Admin123!

2. Giriş yaptıktan sonra:
   - Navigation menüsünü kullanarak farklı bölümlere geçiş yapabilirsiniz
   - Dashboard'da genel bilgileri görebilirsiniz
   - Beneficiaries, Programs ve Evaluations sayfalarında veri tablolarını inceleyebilirsiniz
   - Sağ paneldeki butonlar API verilerini JSON formatında görüntülemenizi sağlar

## Kullanıcı Bilgileri

Tüm test ortamlarında aşağıdaki ön tanımlı kullanıcıları kullanabilirsiniz:

- **Süper Admin**: 
  - Email: `admin@bdc.com`
  - Şifre: `Admin123!`

- **Kiracı Admin**: 
  - Email: `tenant@bdc.com`
  - Şifre: `Tenant123!`

- **Eğitmen**: 
  - Email: `trainer@bdc.com`
  - Şifre: `Trainer123!`

- **Öğrenci**: 
  - Email: `student@bdc.com`
  - Şifre: `Student123!`

## Docker Konteynerlerini Yönetme

Test ortamlarını yönetmek için aşağıdaki komutları kullanabilirsiniz:

### API Test Arayüzü

```bash
# Başlatma
docker-compose -f docker-compose.test.yml up -d

# Durdurma
docker-compose -f docker-compose.test.yml down
```

### Tam Uygulama Simülasyonu

```bash
# Başlatma
docker-compose -f docker-compose.app.yml up -d

# Durdurma
docker-compose -f docker-compose.app.yml down
```

### Diğer Docker Komutları

```bash
# Çalışan konteynerleri görüntüleme
docker ps

# Konteyner loglarını görüntüleme
docker logs bdc_test_api
docker logs bdc_test_app
docker logs bdc_interface

# Tüm konteynerleri durdurma
docker stop $(docker ps -a -q)
```

## API Endpoints

Test ortamında aşağıdaki API endpoint'leri kullanılabilir:

### Kimlik Doğrulama
- `POST /api/auth/login` - Giriş yapma
- `GET /api/auth/me` - Mevcut kullanıcı bilgilerini alma

### Kullanıcılar
- `GET /api/users` - Tüm kullanıcıları listeleme
- `GET /api/users/{id}` - Belirli bir kullanıcının detaylarını görüntüleme

### Faydalanıcılar (Öğrenciler)
- `GET /api/beneficiaries` - Tüm faydalanıcıları listeleme
- `GET /api/beneficiaries/{id}` - Belirli bir faydalanıcının detaylarını görüntüleme

### Programlar
- `GET /api/programs` - Tüm programları listeleme
- `GET /api/programs/{id}` - Belirli bir programın detaylarını görüntüleme

### Değerlendirmeler
- `GET /api/evaluations` - Tüm değerlendirmeleri listeleme
- `GET /api/evaluations/{id}` - Belirli bir değerlendirmenin detaylarını görüntüleme

## Sorun Giderme

Eğer test ortamında sorunlar yaşarsanız:

1. Konteynerlerin çalıştığından emin olun: `docker ps`
2. Konteyner loglarını kontrol edin: `docker logs bdc_test_api`
3. API'nin direkt olarak erişilebilir olduğunu doğrulayın: `curl http://localhost:8888/health`
4. Test ortamını yeniden başlatın: 
   ```bash
   docker-compose -f docker-compose.test.yml down
   docker-compose -f docker-compose.app.yml down
   docker-compose -f docker-compose.app.yml up -d
   ```