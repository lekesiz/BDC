# BDC (Beneficiary Development Center) Proje Yapısı

## 1. Proje Genel Bakış

### 1.1 Proje Amacı
BDC, faydalanıcıların gelişim süreçlerini yönetmek, takip etmek ve değerlendirmek için tasarlanmış kapsamlı bir web uygulamasıdır.

### 1.2 Temel Özellikler
- Kullanıcı Rolleri ve Yönetimi
- Eğitim ve Bilan Yönetimi
- Test Motoru
- Yapay Zeka Asistan Modülü
- Belge Üretici
- Dashboard ve Analitik
- Bildirim Sistemi
- Harici Entegrasyonlar

## 2. Klasör Yapısı

```
BDC/
├── server/                        # Backend (Flask)
│   ├── app/
│   │   ├── api/                    # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py             # Kimlik doğrulama API
│   │   │   ├── users.py            # Kullanıcı API
│   │   │   ├── beneficiaries.py    # Faydalanıcı API
│   │   │   ├── evaluations.py      # Değerlendirme API
│   │   │   ├── test_engine.py      # Test motoru API
│   │   │   ├── documents.py        # Belge API
│   │   │   ├── messaging.py        # Mesajlaşma API
│   │   │   ├── notifications.py    # Bildirim API
│   │   │   └── integrations.py     # Entegrasyon API
│   │   ├── middleware/             # Middleware components
│   │   │   ├── __init__.py
│   │   │   ├── auth.py             # Kimlik doğrulama middleware
│   │   │   ├── error_handlers.py   # Hata yakalama
│   │   │   ├── logging.py          # Loglama
│   │   │   ├── validation.py       # Veri doğrulama
│   │   │   └── rate_limit.py       # Rate limiting
│   │   ├── models/                 # Veritabanı modelleri
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── beneficiary.py
│   │   │   ├── evaluation.py
│   │   │   ├── test.py
│   │   │   ├── response.py
│   │   │   ├── document.py
│   │   │   ├── message.py
│   │   │   └── notification.py
│   │   ├── schemas/                # Marshmallow şemaları
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── beneficiary.py
│   │   │   ├── evaluation.py
│   │   │   ├── test.py
│   │   │   ├── document.py
│   │   │   └── notification.py
│   │   ├── services/               # İş mantığı
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── beneficiary_service.py
│   │   │   ├── evaluation_service.py
│   │   │   ├── test_service.py
│   │   │   ├── document_service.py
│   │   │   ├── ai_service.py       # AI servisleri
│   │   │   └── integration_service.py
│   │   ├── utils/                  # Yardımcı fonksiyonlar
│   │   │   ├── __init__.py
│   │   │   ├── security.py
│   │   │   ├── validation.py
│   │   │   ├── formatters.py
│   │   │   └── generators.py
│   │   ├── config.py               # Yapılandırma
│   │   ├── extensions.py           # Flask eklentileri
│   │   └── __init__.py             # Ana uygulama
│   ├── migrations/                 # Veritabanı migrasyonları
│   ├── tests/                      # Test dosyaları
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_users.py
│   │   ├── test_beneficiaries.py
│   │   ├── test_evaluations.py
│   │   └── test_tests.py
│   ├── requirements.txt            # Python bağımlılıkları
│   ├── config.py                   # Yapılandırma
│   └── wsgi.py                     # WSGI giriş noktası
│
├── client/                        # Frontend (React)
│   ├── public/                     # Statik dosyalar
│   ├── src/
│   │   ├── assets/                 # Resimler, fontlar vb.
│   │   ├── components/             # Paylaşılan bileşenler
│   │   │   ├── common/             # Genel bileşenler
│   │   │   ├── layout/             # Düzen bileşenleri
│   │   │   ├── auth/               # Kimlik doğrulama bileşenleri
│   │   │   ├── dashboard/          # Dashboard bileşenleri
│   │   │   ├── beneficiary/        # Faydalanıcı bileşenleri
│   │   │   ├── evaluation/         # Değerlendirme bileşenleri
│   │   │   ├── test-engine/        # Test motoru bileşenleri
│   │   │   ├── document/           # Belge bileşenleri
│   │   │   ├── ui/                 # UI bileşenleri
│   │   │   └── forms/              # Form bileşenleri
│   │   ├── context/                # React context'leri
│   │   │   ├── AuthContext.jsx
│   │   │   ├── UserContext.jsx
│   │   │   └── NotificationContext.jsx
│   │   ├── hooks/                  # Custom hooks
│   │   │   ├── useAuth.js
│   │   │   ├── useFetch.js
│   │   │   ├── useForm.js
│   │   │   └── useToast.js
│   │   ├── lib/                    # Yardımcı kütüphaneler
│   │   │   ├── api.js              # API istekleri
│   │   │   ├── utils.js            # Yardımcı fonksiyonlar
│   │   │   └── constants.js        # Sabitler
│   │   ├── pages/                  # Sayfa bileşenleri
│   │   │   ├── auth/               # Kimlik doğrulama sayfaları
│   │   │   ├── dashboard/          # Dashboard sayfaları
│   │   │   ├── admin/              # Admin sayfaları
│   │   │   ├── beneficiary/        # Faydalanıcı sayfaları
│   │   │   ├── evaluation/         # Değerlendirme sayfaları
│   │   │   ├── test/               # Test sayfaları
│   │   │   └── settings/           # Ayarlar sayfaları
│   │   ├── store/                  # Durum yönetimi
│   │   ├── App.jsx                 # Ana uygulama bileşeni
│   │   ├── main.jsx                # Uygulama giriş noktası
│   │   └── index.css               # Global CSS
│   ├── .eslintrc.js                # ESLint yapılandırması
│   ├── package.json                # npm paketi ve scriptler
│   └── vite.config.js              # Vite yapılandırması
│
├── docs/                          # Dokümantasyon
│   ├── api/                        # API dokümantasyonu
│   ├── development/                # Geliştirici dokümantasyonu
│   └── user/                       # Kullanıcı dokümantasyonu
│
├── docker/                        # Docker yapılandırması
│   ├── docker-compose.yml
│   ├── Dockerfile.server
│   └── Dockerfile.client
│
├── scripts/                       # Yardımcı scriptler
│   ├── setup.sh
│   └── deploy.sh
│
├── .env.example                   # Örnek çevre değişkenleri
├── .gitignore                     # Git tarafından yok sayılacak dosyalar
├── README.md                      # Proje açıklaması
└── LICENSE                        # Lisans bilgisi
```

## 3. Uygulama Akışı

### 3.1 Kullanıcı Kimlik Doğrulama
1. Kullanıcı giriş yapar
2. Backend JWT token üretir
3. Token istemcide saklanır
4. Tüm API isteklerinde token gönderilir

### 3.2 Test Çözme
1. Öğrenci teste başlar
2. Sorular adım adım sunulur
3. Öğrenci yanıtları kaydedilir
4. Test tamamlandığında sonuçlar analiz edilir
5. AI servisi geri bildirim ve öneriler üretir
6. Eğitmen geri bildirimi inceler ve onaylar
7. Öğrenci geri bildirim ve önerileri görüntüler

### 3.3 Rapor Oluşturma
1. Eğitmen rapor oluşturma isteği gönderir
2. Backend rapor şablonu hazırlar
3. AI servisi içerik önerileri üretir
4. Eğitmen içeriği düzenler/onaylar
5. PDF raporu oluşturulur
6. Öğrenciye bildirim gönderilir

## 4. Teknik Kararlar

### 4.1 Backend
- Flask: Hafif ve modüler yapısı nedeniyle tercih edildi
- SQLAlchemy: ORM desteği için
- Marshmallow: Veri doğrulama ve serileştirme
- JWT: Stateless kimlik doğrulama
- Redis: Önbellek ve oturum yönetimi
- OpenAI/LangChain: AI özellikleri için

### 4.2 Frontend
- React: Bileşen tabanlı UI geliştirme
- Vite: Hızlı geliştirme deneyimi
- Tailwind CSS: Stil ve düzen
- React Router: Sayfa yönlendirme
- Axios: HTTP istekleri
- Radix UI: Erişilebilir UI bileşenleri

### 4.3 Veritabanı
- SQLite: Geliştirme
- PostgreSQL: Üretim
- Alembic: Veritabanı migrasyonları

## 5. Güvenlik Önlemleri

- HTTPS zorunlu
- JWT kimlik doğrulama
- Role-based access control
- Input sanitization
- Rate limiting
- CSRF koruması
- Security headers
- Veri şifreleme
- Audit logging