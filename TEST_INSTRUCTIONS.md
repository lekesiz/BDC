# BDC Uygulama Test Ortamı

Bu belgede, BDC uygulamasını test etmek için hazırlanan Docker tabanlı test ortamının kullanımı açıklanmaktadır.

## Test Ortamı Erişim Bilgileri

Test ortamı iki ana bileşenden oluşmaktadır:

1. **Test API Sunucusu**: `http://localhost:8888`
   - BDC API'sinin basitleştirilmiş bir versiyonu
   - JWT token tabanlı kimlik doğrulama
   - Test verileriyle doldurulmuş

2. **Test Arayüzü**: `http://localhost:8091`
   - BDC uygulamasını test etmek için basit web arayüzü
   - API endpoint'lerini kolayca test etmenizi sağlar
   - Oturum yönetimi özelliği

## Kullanıcı Bilgileri

Test ortamında aşağıdaki ön tanımlı kullanıcıları kullanabilirsiniz:

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

## Test Yapılabilecek API Endpoint'leri

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

## API'yi Doğrudan Test Etme

Test arayüzü dışında, API'yi doğrudan test etmek isterseniz, Postman veya `curl` gibi araçları kullanabilirsiniz.

### Örnek curl Komutları

#### Health Check
```bash
curl http://localhost:8888/health
```

#### Login
```bash
curl -X POST http://localhost:8888/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bdc.com","password":"Admin123!"}'
```

#### Get Users (Token gerektiriyor)
```bash
curl http://localhost:8888/api/users \
  -H "Authorization: Bearer BURAYA_TOKEN_GELECEK"
```

## Docker Konteynerlerini Yönetme

Test ortamının Docker konteynerlerini yönetmek için aşağıdaki komutları kullanabilirsiniz:

### Konteynerleri Başlatma
```bash
docker-compose -f docker-compose.test.yml up -d
```

### Konteynerleri Durdurma
```bash
docker-compose -f docker-compose.test.yml down
```

### Konteyner Loglarını Görüntüleme
```bash
docker logs bdc_test_api    # API konteyneri için
docker logs bdc_interface   # Arayüz konteyneri için
```

## Test Ortamını Teyit Etme

Test ortamının doğru çalıştığından emin olmak için:

1. Tarayıcıda `http://localhost:8091` adresine gidin
2. "Health Check" butonuna tıklayın - "healthy" yanıtı almanız gerekir
3. Kullanıcı bilgileriyle giriş yapın
4. Diğer API endpoint'lerini test edin

## Sorun Giderme

Eğer test ortamında sorunlar yaşarsanız:

1. Konteynerlerin çalıştığından emin olun: `docker ps`
2. Konteyner loglarını kontrol edin: `docker logs bdc_test_api`
3. API'nin direkt olarak erişilebilir olduğunu doğrulayın: `curl http://localhost:8888/health`
4. Test ortamını yeniden başlatın: `docker-compose -f docker-compose.test.yml restart`