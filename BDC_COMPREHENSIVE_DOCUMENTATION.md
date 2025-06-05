# BDC (Beneficiary Development Center) - Kapsamlı Sistem Dokümantasyonu

## İçindekiler
1. [Genel Bakış](#genel-bakış)
2. [Sistem Amacı ve Hedefleri](#sistem-amacı-ve-hedefleri)
3. [Kullanıcı Türleri ve Rolleri](#kullanıcı-türleri-ve-rolleri)
4. [Sistem Mimarisi](#sistem-mimarisi)
5. [Özellikler ve Modüller](#özellikler-ve-modüller)
6. [İş Akışları](#iş-akışları)
7. [Veritabanı Yapısı](#veritabanı-yapısı)
8. [API Endpoints](#api-endpoints)
9. [Kullanıcı Arayüzü](#kullanıcı-arayüzü)
10. [Güvenlik ve Yetkilendirme](#güvenlik-ve-yetkilendirme)
11. [Entegrasyonlar](#entegrasyonlar)
12. [Yapay Zeka Özellikleri](#yapay-zeka-özellikleri)
13. [Teknik Özellikler](#teknik-özellikler)

---

## Genel Bakış

BDC (Beneficiary Development Center), modern bir yetenek değerlendirme ve gelişim platformudur. Fransa'daki "Bilan de Compétence" (yetenek değerlendirme) sürecini dijitalleştirerek, kişiselleştirilmiş öğrenme yolları ve yapay zeka destekli öneriler sunar.

### Temel Özellikler:
- 🎯 **Multi-tenant mimari**: Birden fazla organizasyonu destekler
- 🤖 **AI-destekli değerlendirmeler**: GPT-4 ile otomatik analiz
- 📊 **Kapsamlı raporlama**: PDF ve dijital raporlar
- 🔄 **Gerçek zamanlı bildirimler**: WebSocket entegrasyonu
- 🌍 **Çok dilli destek**: Fransızca ve İngilizce arayüz

---

## Sistem Amacı ve Hedefleri

### Ana Amaç
BDC, bireylerin mesleki yeterliliklerini değerlendirmek, güçlü ve gelişim alanlarını belirlemek ve kişiselleştirilmiş kariyer gelişim planları oluşturmak için tasarlanmıştır.

### Hedefler
1. **Dijitalleştirme**: Geleneksel kağıt tabanlı değerlendirme süreçlerini dijitalleştirmek
2. **Otomasyon**: Değerlendirme ve raporlama süreçlerini otomatikleştirmek
3. **Kişiselleştirme**: AI ile kişiye özel öneriler sunmak
4. **Takip**: Gelişim sürecini sürekli izlemek ve raporlamak
5. **Erişilebilirlik**: Web tabanlı, her yerden erişilebilir platform

---

## Kullanıcı Türleri ve Rolleri

### 1. 🔴 Super Admin (Süper Yönetici)
**Amaç**: Tüm sistemi yönetmek ve kontrol etmek

**Yetkiler**:
- ✅ Tüm kiracıları (tenant) yönetme
- ✅ Sistem ayarlarını yapılandırma
- ✅ Kullanıcı rollerini atama/değiştirme
- ✅ Platform genelinde raporları görüntüleme
- ✅ AI ayarlarını yapılandırma
- ✅ Sistem bakım işlemleri

**Ana İşlevler**:
- Kiracı oluşturma ve yönetimi
- Sistem genelinde kullanıcı yönetimi
- Platform performans izleme
- Güvenlik ayarları yönetimi

### 2. 🟠 Tenant Admin (Kiracı Yöneticisi)
**Amaç**: Kendi organizasyonunu yönetmek

**Yetkiler**:
- ✅ Organizasyon içi kullanıcı yönetimi
- ✅ Program ve eğitim oluşturma
- ✅ Organizasyon raporlarını görüntüleme
- ✅ Eğitmen atama
- ✅ Organizasyon ayarları

**Ana İşlevler**:
- Eğitmen ve öğrenci hesapları oluşturma
- Program takvimi yönetimi
- Organizasyon içi raporlama
- Faydalanıcı yönetimi

### 3. 🟡 Trainer (Eğitmen)
**Amaç**: Eğitim ve değerlendirme süreçlerini yürütmek

**Yetkiler**:
- ✅ Değerlendirme oluşturma ve yönetme
- ✅ Öğrenci performansını izleme
- ✅ Geri bildirim verme
- ✅ Rapor oluşturma
- ✅ Randevu yönetimi

**Ana İşlevler**:
- Test ve değerlendirme oluşturma
- Öğrenci gelişimini takip etme
- Bireysel ve grup seansları yönetme
- Performans raporları hazırlama

### 4. 🟢 Student/Beneficiary (Öğrenci/Faydalanıcı)
**Amaç**: Eğitim ve değerlendirme süreçlerine katılmak

**Yetkiler**:
- ✅ Testlere katılma
- ✅ Kişisel gelişim takibi
- ✅ Belge yükleme/indirme
- ✅ Randevu talep etme
- ✅ Raporları görüntüleme

**Ana İşlevler**:
- Değerlendirmelere katılma
- Ödevleri tamamlama
- İlerleme raporlarını görüntüleme
- Eğitmenlerle iletişim

---

## Sistem Mimarisi

### Backend Teknolojileri
- **Framework**: Flask 3.0.0 (Python)
- **ORM**: SQLAlchemy 2.0.25
- **Veritabanı**: PostgreSQL (Production), SQLite (Development)
- **Cache**: Redis
- **Authentication**: JWT (JSON Web Tokens)
- **WebSocket**: Socket.IO
- **Task Queue**: Celery (planned)

### Frontend Teknolojileri
- **Framework**: React 18.2.0
- **Build Tool**: Vite 6.3.5
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI
- **State Management**: Context API
- **HTTP Client**: Axios
- **Charts**: Chart.js, Recharts

### Deployment ve DevOps
- **Containerization**: Docker (Multi-stage builds)
- **Orchestration**: Docker Compose
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger
- **CI/CD**: GitHub Actions

---

## Özellikler ve Modüller

### 1. 👥 Kullanıcı Yönetimi Modülü
- Kullanıcı oluşturma, düzenleme, silme
- Rol tabanlı yetkilendirme
- Profil yönetimi
- Şifre sıfırlama
- İki faktörlü kimlik doğrulama (2FA) - planlanıyor

### 2. 🎯 Faydalanıcı Yönetimi Modülü
- Faydalanıcı kayıt ve onboarding
- Kişisel bilgi yönetimi
- Belge yönetimi (CV, diplomalar vb.)
- İlerleme takibi
- Geçmiş değerlendirmeler

### 3. 📚 Program Yönetimi Modülü
- Program oluşturma ve yapılandırma
- Modül ve içerik yönetimi
- Katılımcı kayıt ve yönetimi
- Program takvimi
- Otomatik hatırlatıcılar

### 4. 📝 Değerlendirme ve Test Modülü
- Çoklu soru tipleri (çoktan seçmeli, açık uçlu, eşleştirme)
- Zaman yönetimi
- Otomatik puanlama
- AI destekli analiz
- Adaptif test sistemi (planlanıyor)

### 5. 📄 Belge Yönetimi Modülü
- Güvenli dosya yükleme
- Klasör organizasyonu
- Versiyon kontrolü
- Paylaşım yönetimi
- Otomatik belge sınıflandırma

### 6. 📅 Takvim ve Randevu Modülü
- Randevu oluşturma ve yönetimi
- Müsaitlik takvimi
- Otomatik hatırlatıcılar
- Google Calendar entegrasyonu
- Toplu randevu planlaması

### 7. 💬 İletişim Modülü
- Anlık mesajlaşma
- E-posta bildirimleri
- SMS entegrasyonu (planlanıyor)
- Video konferans (planlanıyor)
- Grup iletişimi

### 8. 🔔 Bildirim Sistemi
- Gerçek zamanlı bildirimler (WebSocket)
- E-posta bildirimleri
- Uygulama içi bildirimler
- Bildirim tercihleri yönetimi
- Toplu bildirim gönderimi

### 9. 📊 Analitik ve Raporlama Modülü
- Dashboard'lar (rol bazlı)
- Performans raporları
- İlerleme analizleri
- PDF rapor üretimi
- Veri dışa aktarma (Excel, CSV)

### 10. 🤖 Yapay Zeka Modülü
- Otomatik değerlendirme analizi
- Kişiselleştirilmiş öneriler
- İçerik üretimi
- Chatbot asistan
- Tahminsel analitik

---

## İş Akışları

### 1. Faydalanıcı Kayıt Süreci
```
1. Eğitmen/Admin faydalanıcı davet eder
2. Faydalanıcı e-posta ile davet alır
3. Kayıt formunu doldurur
4. Profil bilgilerini tamamlar
5. Programa otomatik atanır
6. Hoşgeldin e-postası gönderilir
```

### 2. Değerlendirme Süreci
```
1. Eğitmen test oluşturur
2. Test faydalanıcılara atanır
3. Bildirim gönderilir
4. Faydalanıcı testi tamamlar
5. Otomatik puanlama yapılır
6. AI analiz raporu üretilir
7. Eğitmen gözden geçirir
8. Final rapor oluşturulur
```

### 3. Program Akışı
```
1. Admin program oluşturur
2. Modüller ve içerik eklenir
3. Eğitmenler atanır
4. Faydalanıcılar kaydedilir
5. Otomatik takvim oluşturulur
6. Seanslar gerçekleştirilir
7. İlerleme takip edilir
8. Sertifika üretilir
```

---

## Veritabanı Yapısı

### Ana Tablolar

#### Users (Kullanıcılar)
```sql
- id: Primary Key
- email: Unique, Not Null
- password_hash: Encrypted
- first_name, last_name
- role: Enum (super_admin, tenant_admin, trainer, student)
- tenant_id: Foreign Key
- is_active: Boolean
- created_at, updated_at
```

#### Beneficiaries (Faydalanıcılar)
```sql
- id: Primary Key
- user_id: Foreign Key (Users)
- date_of_birth
- phone_number
- address
- emergency_contact
- education_level
- professional_status
- created_at, updated_at
```

#### Tenants (Kiracılar)
```sql
- id: Primary Key
- name: Unique
- domain
- settings: JSON
- subscription_plan
- is_active: Boolean
- created_at, updated_at
```

#### Programs (Programlar)
```sql
- id: Primary Key
- tenant_id: Foreign Key
- name, description
- start_date, end_date
- max_participants
- status: Enum
- created_by: Foreign Key (Users)
```

#### Tests/Evaluations (Testler/Değerlendirmeler)
```sql
- id: Primary Key
- program_id: Foreign Key
- name, description
- test_type
- duration_minutes
- passing_score
- questions: JSON
- created_by: Foreign Key
```

#### Test_Results (Test Sonuçları)
```sql
- id: Primary Key
- test_id: Foreign Key
- beneficiary_id: Foreign Key
- score, percentage
- answers: JSON
- ai_analysis: JSON
- completed_at
```

### İlişkiler
- One-to-Many: Tenant → Users, Program → Tests
- Many-to-Many: Programs ↔ Beneficiaries, Users ↔ Programs
- One-to-One: User → Beneficiary

---

## API Endpoints

### Authentication Endpoints
```
POST   /api/auth/register          # Yeni kullanıcı kaydı
POST   /api/auth/login            # Giriş yapma
POST   /api/auth/logout           # Çıkış yapma
POST   /api/auth/refresh          # Token yenileme
POST   /api/auth/forgot-password  # Şifre sıfırlama
POST   /api/auth/reset-password   # Yeni şifre belirleme
GET    /api/auth/me              # Mevcut kullanıcı bilgisi
```

### User Management
```
GET    /api/users                # Kullanıcı listesi
GET    /api/users/:id           # Kullanıcı detayı
POST   /api/users               # Kullanıcı oluştur
PUT    /api/users/:id           # Kullanıcı güncelle
DELETE /api/users/:id           # Kullanıcı sil
PUT    /api/users/:id/password  # Şifre değiştir
```

### Beneficiary Management
```
GET    /api/beneficiaries        # Faydalanıcı listesi
GET    /api/beneficiaries/:id   # Faydalanıcı detayı
POST   /api/beneficiaries       # Faydalanıcı oluştur
PUT    /api/beneficiaries/:id   # Faydalanıcı güncelle
DELETE /api/beneficiaries/:id   # Faydalanıcı sil
GET    /api/beneficiaries/:id/progress  # İlerleme raporu
```

### Program Management
```
GET    /api/programs            # Program listesi
GET    /api/programs/:id       # Program detayı
POST   /api/programs           # Program oluştur
PUT    /api/programs/:id       # Program güncelle
DELETE /api/programs/:id       # Program sil
POST   /api/programs/:id/enroll      # Programa kayıt
GET    /api/programs/:id/participants # Katılımcı listesi
```

### Evaluation/Test Management
```
GET    /api/evaluations         # Test listesi
GET    /api/evaluations/:id    # Test detayı
POST   /api/evaluations        # Test oluştur
PUT    /api/evaluations/:id    # Test güncelle
DELETE /api/evaluations/:id    # Test sil
POST   /api/evaluations/:id/submit   # Test gönder
GET    /api/evaluations/:id/results  # Test sonuçları
POST   /api/evaluations/:id/analyze  # AI analizi
```

### Document Management
```
GET    /api/documents           # Belge listesi
GET    /api/documents/:id      # Belge detayı
POST   /api/documents/upload   # Belge yükle
PUT    /api/documents/:id      # Belge güncelle
DELETE /api/documents/:id      # Belge sil
GET    /api/documents/:id/download  # Belge indir
POST   /api/documents/:id/share     # Belge paylaş
```

### Analytics & Reports
```
GET    /api/analytics/dashboard      # Dashboard verileri
GET    /api/analytics/performance    # Performans metrikleri
GET    /api/reports/beneficiary/:id # Faydalanıcı raporu
GET    /api/reports/program/:id     # Program raporu
POST   /api/reports/generate        # Rapor oluştur
GET    /api/reports/:id/download    # Rapor indir
```

### AI Integration
```
POST   /api/ai/analyze-evaluation   # Değerlendirme analizi
POST   /api/ai/generate-recommendations # Öneri üretimi
POST   /api/ai/chat                # AI chat
GET    /api/ai/settings            # AI ayarları
PUT    /api/ai/settings            # AI ayarları güncelle
```

---

## Kullanıcı Arayüzü

### Ana Sayfalar

#### 1. Giriş ve Kimlik Doğrulama
- `/login` - Giriş sayfası
- `/register` - Kayıt sayfası
- `/forgot-password` - Şifre sıfırlama
- `/reset-password` - Yeni şifre belirleme

#### 2. Dashboard'lar (Rol Bazlı)
- `/dashboard` - Ana kontrol paneli
- `/admin/dashboard` - Admin paneli
- `/trainer/dashboard` - Eğitmen paneli
- `/student/dashboard` - Öğrenci paneli

#### 3. Kullanıcı Yönetimi
- `/users` - Kullanıcı listesi
- `/users/new` - Yeni kullanıcı
- `/users/:id` - Kullanıcı detayı
- `/profile` - Profil sayfası

#### 4. Faydalanıcı Yönetimi
- `/beneficiaries` - Faydalanıcı listesi
- `/beneficiaries/new` - Yeni faydalanıcı
- `/beneficiaries/:id` - Faydalanıcı detayı
- `/beneficiaries/:id/progress` - İlerleme takibi

#### 5. Program Yönetimi
- `/programs` - Program listesi
- `/programs/new` - Yeni program
- `/programs/:id` - Program detayı
- `/programs/:id/modules` - Program modülleri

#### 6. Değerlendirme Yönetimi
- `/evaluations` - Değerlendirme listesi
- `/evaluations/new` - Yeni değerlendirme
- `/evaluations/:id` - Değerlendirme detayı
- `/evaluations/:id/take` - Test alma sayfası
- `/evaluations/:id/results` - Sonuçlar

#### 7. Belge Yönetimi
- `/documents` - Belge listesi
- `/documents/upload` - Belge yükleme
- `/documents/:id` - Belge detayı

#### 8. Takvim ve Randevular
- `/calendar` - Takvim görünümü
- `/appointments` - Randevu listesi
- `/appointments/new` - Yeni randevu

#### 9. Raporlar
- `/reports` - Rapor merkezi
- `/reports/generate` - Rapor oluştur
- `/analytics` - Analitik dashboard

#### 10. Ayarlar
- `/settings` - Genel ayarlar
- `/settings/profile` - Profil ayarları
- `/settings/notifications` - Bildirim ayarları
- `/settings/ai` - AI ayarları
- `/settings/security` - Güvenlik ayarları

### UI/UX Özellikleri
- **Responsive Design**: Mobil uyumlu
- **Dark Mode**: Karanlık tema desteği
- **Accessibility**: WCAG 2.1 AA uyumlu
- **Multi-language**: Fransızca ve İngilizce
- **Real-time Updates**: WebSocket ile anlık güncellemeler
- **Progressive Web App**: Offline çalışma desteği

---

## Güvenlik ve Yetkilendirme

### Kimlik Doğrulama
- **JWT Token Tabanlı**: Access token + Refresh token
- **Token Süreleri**: Access (15 dk), Refresh (7 gün)
- **Secure Cookie**: HttpOnly, Secure, SameSite
- **Password Policy**: Min 8 karakter, büyük/küçük harf, rakam, özel karakter

### Yetkilendirme
- **RBAC (Role-Based Access Control)**: Rol tabanlı erişim
- **Resource-Level Permissions**: Kaynak bazlı izinler
- **Multi-Tenant Isolation**: Kiracı izolasyonu
- **API Rate Limiting**: Hız sınırlaması

### Güvenlik Önlemleri
- **HTTPS Zorunlu**: SSL/TLS şifreleme
- **CORS Policy**: Kontrollü cross-origin erişim
- **SQL Injection Koruması**: Parametreli sorgular
- **XSS Koruması**: Input sanitization
- **CSRF Koruması**: CSRF token kullanımı
- **Security Headers**: Helmet.js entegrasyonu
- **Audit Logging**: Tüm kritik işlemler loglanır

---

## Entegrasyonlar

### 1. Wedof API
- **Amaç**: Eğitim verilerini senkronize etme
- **Özellikler**:
  - Eğitim kataloğu senkronizasyonu
  - Katılımcı verisi aktarımı
  - Sertifika doğrulama
  - Raporlama entegrasyonu

### 2. Google Workspace
- **Google Calendar**: Randevu senkronizasyonu
- **Google Drive**: Belge depolama
- **Google Meet**: Video konferans (planlanıyor)

### 3. Pennylane
- **Amaç**: Finansal yönetim
- **Özellikler**:
  - Fatura oluşturma
  - Ödeme takibi
  - Finansal raporlama

### 4. E-posta Servisleri
- **SendGrid/Mailgun**: Transactional emails
- **SMTP**: Basit e-posta gönderimi

### 5. SMS Servisleri (Planlanıyor)
- **Twilio**: SMS bildirimleri
- **Nexmo**: Alternatif SMS sağlayıcı

### 6. Ödeme Sistemleri (Planlanıyor)
- **Stripe**: Kredi kartı ödemeleri
- **PayPal**: Alternatif ödeme yöntemi

### 7. AI Sağlayıcıları
- **OpenAI**: GPT-4 entegrasyonu
- **Anthropic Claude**: Alternatif AI
- **Local LLM**: Ollama entegrasyonu

---

## Yapay Zeka Özellikleri

### 1. Değerlendirme Analizi
- **Otomatik Puanlama**: AI destekli puanlama
- **Güçlü Yön Tespiti**: Kişinin güçlü alanları
- **Gelişim Alanları**: İyileştirme önerileri
- **Detaylı Feedback**: Soru bazlı geri bildirim

### 2. Kişiselleştirilmiş Öneriler
- **Öğrenme Yolu**: Customized learning path
- **Kaynak Önerileri**: İlgili materyaller
- **Beceri Boşluk Analizi**: Skill gap analysis
- **Kariyer Önerileri**: Career recommendations

### 3. İçerik Üretimi
- **Rapor Sentezi**: Otomatik rapor oluşturma
- **Soru Üretimi**: Adaptif soru oluşturma
- **Özet Çıkarma**: Belge özetleme
- **Çeviri**: Çok dilli içerik

### 4. Chatbot Asistan
- **7/24 Destek**: Anlık yardım
- **Soru-Cevap**: FAQ otomasyonu
- **Yönlendirme**: Doğru kaynaklara yönlendirme
- **Öğrenme Desteği**: Konu anlatımı

### 5. Tahminsel Analitik
- **Başarı Tahmini**: Success prediction
- **Risk Analizi**: Dropout risk
- **Performans Projeksiyonu**: Future performance
- **Önleyici Müdahale**: Preventive actions

---

## Teknik Özellikler

### Performans
- **Page Load Time**: < 3 saniye
- **API Response Time**: < 200ms (avg)
- **Concurrent Users**: 10,000+
- **Database Queries**: Optimized with indexes
- **Caching**: Redis for session/data caching
- **CDN**: Static asset delivery

### Scalability
- **Horizontal Scaling**: Docker Swarm/K8s ready
- **Load Balancing**: Nginx reverse proxy
- **Database Replication**: Master-slave setup
- **Microservices Ready**: Service separation
- **Queue System**: Celery for async tasks

### Monitoring
- **Application Monitoring**: Sentry
- **Performance Monitoring**: Prometheus + Grafana
- **Log Management**: ELK Stack
- **Distributed Tracing**: Jaeger
- **Uptime Monitoring**: UptimeRobot
- **Real User Monitoring**: Google Analytics

### Backup & Recovery
- **Database Backup**: Daily automated backups
- **File Backup**: Incremental file backups
- **Disaster Recovery**: 24-hour RPO
- **Backup Testing**: Monthly restore tests
- **Version Control**: Git with tagged releases

### Development Workflow
- **Version Control**: Git (GitHub)
- **CI/CD**: GitHub Actions
- **Code Quality**: ESLint, Pylint
- **Testing**: Jest, Pytest (>60% coverage)
- **Documentation**: Inline + External docs
- **API Documentation**: OpenAPI/Swagger

---

## Proje Durumu ve Roadmap

### Mevcut Durum (Mayıs 2025)
- **Tamamlanma Oranı**: %94
- **Production Ready**: ✅
- **Docker Deployment**: ✅
- **Core Features**: ✅
- **Security Hardening**: ✅

### Yakın Gelecek (Q2-Q3 2025)
- [ ] İki faktörlü kimlik doğrulama (2FA)
- [ ] Video konferans entegrasyonu
- [ ] SMS bildirimleri
- [ ] Ödeme sistemi entegrasyonu
- [ ] Mobile app (React Native)

### Orta Vade (Q4 2025 - Q1 2026)
- [ ] Advanced AI features
- [ ] Blockchain sertifikalar
- [ ] API marketplace
- [ ] White-label çözümü
- [ ] Advanced analytics

### Uzun Vade (2026+)
- [ ] VR/AR eğitim modülleri
- [ ] IoT entegrasyonları
- [ ] Global expansion
- [ ] AI-powered coaching
- [ ] Predictive career planning

---

## Sonuç

BDC, modern teknolojiler kullanılarak geliştirilmiş, ölçeklenebilir ve güvenli bir yetenek değerlendirme platformudur. Multi-tenant mimarisi sayesinde birden fazla organizasyonu destekleyebilir, AI entegrasyonu ile kişiselleştirilmiş deneyimler sunabilir. 

Platform, kullanıcı dostu arayüzü, kapsamlı özellikleri ve güçlü altyapısı ile profesyonel yetenek değerlendirme süreçlerini baştan sona dijitalleştirmekte ve otomatikleştirmektedir.

### İletişim ve Destek
- **Dokümantasyon**: `/docs` klasörü
- **API Dokümantasyonu**: `/api/docs` endpoint
- **Sorun Bildirimi**: GitHub Issues
- **E-posta**: support@bdc-platform.com

---

*Bu dokümantasyon, BDC platformunun v1.0 sürümü için hazırlanmıştır.*
*Son güncelleme: 31 Mayıs 2025*