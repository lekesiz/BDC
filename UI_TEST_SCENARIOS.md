# BDC UI Test Senaryoları

## Test Tarihi: 16/05/2025

### 🎯 Test Amaçları
- Login fonksiyonelliğini doğrulamak
- Rol bazlı yönlendirmeleri test etmek
- Dashboard erişimini kontrol etmek
- Menü görünürlüğünü doğrulamak

### 🧪 Test Senaryoları

#### 1. Super Admin Login Testi
**Kullanıcı:** admin@bdc.com / Admin123!

**Beklentiler:**
- ✅ Başarılı login
- ✅ /dashboard yönlendirmesi
- ✅ Tüm menü öğeleri görünür:
  - Users
  - Tenants
  - Beneficiaries
  - Evaluations
  - Calendar
  - Documents
  - Analytics
  - Reports
  - Settings
  - Admin

**Test Adımları:**
1. http://localhost:5173/login adresine git
2. Email ve şifre gir
3. Login butonuna tıkla
4. Dashboard'a yönlendirilmeyi doğrula
5. Tüm menü öğelerini kontrol et

#### 2. Tenant Admin Login Testi
**Kullanıcı:** tenant@bdc.com / Tenant123!

**Beklentiler:**
- ✅ Başarılı login
- ✅ /dashboard yönlendirmesi
- ✅ Görünür menüler:
  - Dashboard
  - Users
  - Beneficiaries
  - Evaluations
  - Calendar
  - Documents
  - Reports
  - Settings
- ❌ Gizli menüler:
  - Tenants
  - Admin

#### 3. Trainer Login Testi
**Kullanıcı:** trainer@bdc.com / Trainer123!

**Beklentiler:**
- ✅ Başarılı login
- ✅ /dashboard yönlendirmesi
- ✅ Görünür menüler:
  - Dashboard
  - My Beneficiaries
  - Evaluations
  - Calendar
  - Documents
  - Reports
  - Settings
- ❌ Gizli menüler:
  - Users
  - Tenants
  - Admin

#### 4. Student Login Testi
**Kullanıcı:** student@bdc.com / Student123!

**Beklentiler:**
- ✅ Başarılı login
- ✅ /portal yönlendirmesi
- ✅ Görünür menüler:
  - Dashboard
  - My Progress
  - My Evaluations
  - My Documents
  - Calendar
  - Settings
- ❌ Gizli menüler:
  - Users
  - Tenants
  - Beneficiaries
  - Admin

### 📋 Test Kontrol Listesi

#### Login Sayfası
- [ ] Sayfa düzgün yükleniyor
- [ ] Form elemanları görünür
- [ ] Validation mesajları çalışıyor
- [ ] Remember me checkbox'ı var
- [ ] Forgot password linki aktif

#### Dashboard/Portal
- [ ] Sayfa yükleniyor
- [ ] Header doğru kullanıcı bilgisini gösteriyor
- [ ] Sidebar menüleri role göre filtreleniyor
- [ ] Logout butonu çalışıyor
- [ ] Ana içerik alanı yükleniyor

#### Navigasyon
- [ ] Menü linkleri çalışıyor
- [ ] URL'ler doğru
- [ ] Back/forward butonları çalışıyor
- [ ] Refresh sonrası oturum korunuyor

#### Hata Durumları
- [ ] Yanlış şifre mesajı
- [ ] Kullanıcı bulunamadı mesajı
- [ ] Network hatası mesajı
- [ ] Session timeout yönlendirmesi

### 🔍 Dikkat Edilecek Noktalar

1. **Console Hataları:** Tarayıcı console'unda hata olmamalı
2. **Network Tab:** API çağrıları başarılı olmalı (200/201)
3. **CORS:** CORS hataları olmamalı
4. **Token Storage:** LocalStorage'da token saklanmalı
5. **Route Protection:** Yetkisiz sayfalara erişim engellenmeli

### 📊 Test Sonuç Tablosu

| Kullanıcı | Login | Yönlendirme | Menü Görünürlüğü | Logout | Notlar |
|-----------|-------|-------------|------------------|---------|--------|
| Super Admin | [ ] | [ ] | [ ] | [ ] | - |
| Tenant Admin | [ ] | [ ] | [ ] | [ ] | - |
| Trainer | [ ] | [ ] | [ ] | [ ] | - |
| Student | [ ] | [ ] | [ ] | [ ] | - |

### 🐛 Tespit Edilen Sorunlar

1. **Sorun:** 
   - **Detay:** 
   - **Çözüm:** 

2. **Sorun:** 
   - **Detay:** 
   - **Çözüm:** 

### 📝 Ek Notlar

- Test sırasında cache temizlenmelidir
- Farklı tarayıcılarda test edilmelidir (Chrome, Firefox, Safari)
- Mobil görünüm de kontrol edilmelidir