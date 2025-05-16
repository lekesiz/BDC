# BDC Projesi Git Entegrasyonu ve Backend Birleştirme TODO Listesi

Bu belge, BDC (Beneficiary Development Center) projesinin Git'e yüklenmesi ve iki ayrı backend dizininin (`server/` ve `backend/`) birleştirilmesi sürecini adım adım takip etmek için oluşturulmuştur.

## Bölüm 1: Git Entegrasyonu

### 1. Git Repository Hazırlığı
- [x] GitHub, GitLab veya Bitbucket'ta yeni bir repository oluştur
- [x] Repository'e erişim izinlerini yapılandır (ekip üyeleri için)
- [x] Lisans türünü belirle (MIT, Apache vb.)
- [x] Proje açıklamasını ekle

### 2. Yerel Git Hazırlığı
- [x] Yerel proje dizininde Git başlat
```bash
git init
```
- [x] `.gitignore` dosyasını kontrol et ve gerekirse güncelle (şunları içerdiğinden emin ol)
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
coverage_html/
.env
venv/
.venv/

# JavaScript/Node.js
node_modules/
npm-debug.log
yarn-debug.log
yarn-error.log
.pnpm-debug.log
dist/
dist-ssr/
*.local
.env.local
.env.development.local
.env.test.local
.env.production.local

# Database
*.db
*.sqlite
*.sqlite3

# IDE/Editors
.idea/
.vscode/
*.swp
*.swo
.DS_Store
*.sublime-project
*.sublime-workspace

# Logs
logs/
*.log

# Uploads
uploads/
```
- [x] Tüm dosyaları git'e ekle
```bash
git add .
```
- [x] İlk commit'i oluştur
```bash
git commit -m "İlk commit: BDC Projesi başlangıç kodu"
```

### 3. Uzak Repository Bağlantısı
- [x] Uzak repository'yi yerel repository'ye bağla
```bash
git remote add origin <REPOSITORY_URL>
```
- [x] Ana (main) dalı uzak repository'ye gönder
```bash
git push -u origin main
```
- [x] Push işleminin başarılı olduğunu doğrula (GitHub/GitLab/Bitbucket üzerinden)

### 4. Branching Stratejisi Kurulumu
- [x] Geliştirme dalı oluştur
```bash
git checkout -b development
git push -u origin development
```
- [x] Backend birleştirme için özel dal oluştur
```bash
git checkout -b backend-consolidation
git push -u origin backend-consolidation
```

### 5. CI/CD Temel Yapılandırması (opsiyonel)
- [ ] `.github/workflows/` dizini oluştur (GitHub Actions için)
- [ ] Temel CI yapılandırması ekle (test ve linting için)

## Bölüm 2: Backend Birleştirme Süreci

### 1. Mevcut Yapı Analizi
- [x] `server/` ve `backend/` dizinlerinin detaylı karşılaştırmasını yap
- [x] Her iki dizindeki dosya ve klasörlerin envanterini çıkar
```bash
find server -type f -name "*.py" | sort > server_files.txt
find backend -type f -name "*.py" | sort > backend_files.txt
```
- [x] Ortak ve benzersiz modülleri belirle
- [x] Her iki dizindeki özellikleri listele
- [x] Aşağıdaki temel bileşenleri belgele:
  - [x] Veritabanı modelleri
  - [x] API endpoint'leri
  - [x] Servisler
  - [x] Yardımcı işlevler
  - [x] Middlewares
  - [x] Test dosyaları

### 2. Birleştirme Stratejisi
- [x] Hedef yapıyı belirle (tüm kodun `server/` altında olacağını onaylayalım)
- [x] Kodların nasıl birleştirileceğine dair plan oluştur:
  - [x] Aynı isimli dosyalar için çözüm yaklaşımını belirle (merge veya biri diğerini değiştirecek)
  - [x] Dosya ve klasör yapısını tanımla
  - [x] Birim test yaklaşımını belirle
- [x] Geçiş süreci için zaman çizelgesi oluştur

### 3. Kod Taşıma İşlemi
- [ ] `backend/` dizininden `server/` dizinine özgün modülleri taşı
  - [ ] AI Servisleri
    - [x] `backend/app/services/ai_verification.py` -> `server/app/services/ai_verification.py`
    - [x] `backend/app/services/ai/content_recommendations.py` -> `server/app/services/ai/content_recommendations.py`
    - [x] `backend/app/services/ai/human_review_workflow.py` -> `server/app/services/ai/human_review_workflow.py`
    - [x] `backend/app/services/ai/note_analysis.py` -> `server/app/services/ai/note_analysis.py` 
    - [x] `backend/app/services/ai/recommendations.py` -> `server/app/services/ai/recommendations.py`
    - [x] `backend/app/services/ai/report_synthesis.py` -> `server/app/services/ai/report_synthesis.py`
    - [x] `backend/app/services/ai/test_analysis.py` -> `server/app/services/ai/test_analysis.py`
  - [ ] Optimizasyon Servisleri
    - [x] `backend/app/services/optimization/api_optimizer.py` -> `server/app/services/optimization/api_optimizer.py`
    - [x] `backend/app/services/optimization/cache_strategy.py` -> `server/app/services/optimization/cache_strategy.py`
    - [x] `backend/app/services/optimization/db_indexing.py` -> `server/app/services/optimization/db_indexing.py`
    - [x] `backend/app/services/optimization/query_optimizer.py` -> `server/app/services/optimization/query_optimizer.py`
  - [ ] Veritabanı Yardımcı Modülleri
    - [ ] `backend/database/backup.py` -> `server/app/utils/database/backup.py`
    - [ ] `backend/database/indexing_strategy.py` -> `server/app/utils/database/indexing_strategy.py` 
    - [ ] `backend/database/migrations.py` -> `server/app/utils/database/migrations.py`
    - [ ] `backend/database/optimization.py` -> `server/app/utils/database/optimization.py`
  - [ ] İzleme/Monitör Modülleri
    - [x] `backend/app/models/monitoring.py` -> `server/app/models/monitoring.py`
    - [ ] `backend/monitoring/alarm_system.py` -> `server/app/utils/monitoring/alarm_system.py`
    - [ ] `backend/monitoring/app_monitoring.py` -> `server/app/utils/monitoring/app_monitoring.py`
    - [ ] `backend/monitoring/error_tracking.py` -> `server/app/utils/monitoring/error_tracking.py`
    - [ ] `backend/monitoring/performance_metrics.py` -> `server/app/utils/monitoring/performance_metrics.py`
  - [ ] Test Modülleri
    - [ ] `backend/tests/test_performance.py` -> `server/tests/test_performance.py`
    - [ ] `backend/tests/test_security_auth.py` -> `server/tests/test_security_auth.py`
    - [ ] `backend/tests/test_security_encryption.py` -> `server/tests/test_security_encryption.py`
    - [ ] `backend/tests/test_security_input_validation.py` -> `server/tests/test_security_input_validation.py`
    - [ ] `backend/tests/test_security_xss_csrf.py` -> `server/tests/test_security_xss_csrf.py`
  - [ ] API Endpoint'leri
    - [ ] `backend/app/api/beneficiaries/dashboard.py` -> `server/app/api/beneficiaries/dashboard.py`
- [ ] İsimlendirme çakışmaları için dosya adı değişiklikleri yap
- [ ] Import ifadelerini güncelle
- [ ] Taşınan kodları test et
- [ ] Her taşıma işleminden sonra ara commit oluştur
```bash
git add .
git commit -m "Backend birleştirme: <MODUL_ADI> taşındı"
```

### 4. Entegrasyon ve Test
- [ ] Veritabanı şemasını güncellenmiş modellere göre uyarla
- [ ] Taşınan tüm modülleri mevcut sistem ile entegre et
- [ ] Birim testleri çalıştır
```bash
cd server && python run_tests.py
```
- [ ] Entegrasyon testleri çalıştır
- [ ] Performans testleri yap
- [ ] Hataları gider ve tekrar test et

### 5. Temizlik ve Dokümantasyon
- [ ] `backend/` dizinini arşivle
```bash
mkdir -p archived
git mv backend archived/backend_archive
```
- [ ] README ve diğer dokümantasyonu güncelle
- [ ] API dokümantasyonunu güncelle (varsa)
- [ ] Yeni yapı için geliştiricilere yönelik kılavuz oluştur
- [ ] Değişiklik günlüğünü (CHANGELOG.md) güncelle

### 6. Gözden Geçirme ve Birleştirme
- [ ] Yapılan değişiklikleri gözden geçir
- [ ] Son testleri çalıştır
- [ ] Pull Request oluştur
- [ ] Code review süreci
- [ ] Onay sonrası development dalına birleştir
```bash
git checkout development
git merge backend-consolidation
git push origin development
```
- [ ] Daha sonra main dalına birleştir
```bash
git checkout main
git merge development
git push origin main
```

## Bölüm 3: İlerleme Takibi

Her adımı tamamladıkça, bu dosyaya yapılan işi ve tarih ekleyerek ilerlemeyi takip et.

### Git Entegrasyonu
- Tarih: 2024-05-14
- Tamamlanan adımlar: 
  - Yerel proje dizininde Git başlatıldı
  - .gitignore dosyası kontrol edildi (zaten uygun şekilde yapılandırılmıştı)
  - Tüm dosyalar git'e eklendi
  - İlk commit oluşturuldu
  - GitHub'da repository oluşturuldu (https://github.com/lekesiz/BDC.git)
  - Uzak repository bağlantısı kuruldu
  - Ana dal (main) GitHub'a gönderildi
  - Development ve backend-consolidation dalları oluşturuldu ve GitHub'a gönderildi
- Notlar: Git kullanıcı bilgileri yapılandırıldı (user.name "BDC Developer", user.email "mikail@lekesiz.org")

### Backend Analizi
- Tarih: 2024-05-14
- Tamamlanan adımlar:
  - Server ve backend dizinlerinde Python dosyalarının envanteri çıkarıldı
  - Modüllerin analizi yapıldı
  - Taşınması gereken özgün modüller tespit edildi
  - Backend'den server'a taşınacak dosyaların listesi oluşturuldu
  - Hedef klasör yapısı için organizasyonel iyileştirmeler tanımlandı
- Notlar: Backend dizini temel olarak AI hizmetleri, optimizasyon, izleme, ve güvenlik test modülleri içeriyor. Server dizini ile önemli bir fonksiyonel örtüşme yok.

### Kod Taşıma
- Tarih: 2024-05-15
- Tamamlanan adımlar:
  - Gerekli dizin yapısı oluşturuldu
  - Paket __init__.py dosyaları eklendi
  - İlk modüller taşındı:
    - ai_verification.py
    - monitoring.py modeli (AIAnalysis ve HumanVerification eklemeleriyle)
  - Import ifadeleri düzeltildi ve taşınan kod uyumlu hale getirildi
- Notlar: Şimdilik geçici çözümler kullanarak bazı eksik model tanımlarını ele aldık. Diğer modüller taşındıkça bu kısımlar daha temiz hale getirilecek.

- Tarih: 2024-05-16
- Tamamlanan adımlar:
  - AI servisleri taşındı:
    - content_recommendations.py
    - human_review_workflow.py
    - note_analysis.py
    - recommendations.py
    - report_synthesis.py
    - test_analysis.py
  - Taşınan servislerde import ifadeleri düzenlendi
  - Henüz taşınmamış modeller için geçici sınıflar oluşturuldu
- Notlar: AI servisleri başarıyla taşındı. Geçici sınıflar, kodun hata vermeden çalışmasını sağlamak için oluşturuldu. İlerleyen adımlarda eksik modellerin taşınmasıyla bu geçici sınıflar kaldırılacak.

### Test ve Entegrasyon
- Tarih: __________
- Tamamlanan adımlar:
- Notlar:

### Dokümantasyon
- Tarih: __________
- Tamamlanan adımlar:
- Notlar:

## Kaynaklar ve Referanslar

- [Git Başlangıç Kılavuzu](https://git-scm.com/book/tr/v2/Başlangıç-Git-Temelleri)
- [Flask Belgeleri](https://flask.palletsprojects.com/)
- [React Belgeleri](https://react.dev/) 