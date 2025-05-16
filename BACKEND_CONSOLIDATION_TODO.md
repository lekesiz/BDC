# BDC Projesi Git Entegrasyonu ve Backend Birleştirme TODO Listesi

Bu belge, BDC (Beneficiary Development Center) projesinin Git'e yüklenmesi ve iki ayrı backend dizininin (`server/` ve `backend/`) birleştirilmesi sürecini adım adım takip etmek için oluşturulmuştur.

## Bölüm 1: Git Entegrasyonu

### 1. Git Repository Hazırlığı
- [ ] GitHub, GitLab veya Bitbucket'ta yeni bir repository oluştur
- [ ] Repository'e erişim izinlerini yapılandır (ekip üyeleri için)
- [ ] Lisans türünü belirle (MIT, Apache vb.)
- [ ] Proje açıklamasını ekle

### 2. Yerel Git Hazırlığı
- [ ] Yerel proje dizininde Git başlat
```bash
git init
```
- [ ] `.gitignore` dosyasını kontrol et ve gerekirse güncelle (şunları içerdiğinden emin ol)
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
- [ ] Tüm dosyaları git'e ekle
```bash
git add .
```
- [ ] İlk commit'i oluştur
```bash
git commit -m "İlk commit: BDC Projesi başlangıç kodu"
```

### 3. Uzak Repository Bağlantısı
- [ ] Uzak repository'yi yerel repository'ye bağla
```bash
git remote add origin <REPOSITORY_URL>
```
- [ ] Ana (main) dalı uzak repository'ye gönder
```bash
git push -u origin main
```
- [ ] Push işleminin başarılı olduğunu doğrula (GitHub/GitLab/Bitbucket üzerinden)

### 4. Branching Stratejisi Kurulumu
- [ ] Geliştirme dalı oluştur
```bash
git checkout -b development
git push -u origin development
```
- [ ] Backend birleştirme için özel dal oluştur
```bash
git checkout -b backend-consolidation
git push -u origin backend-consolidation
```

### 5. CI/CD Temel Yapılandırması (opsiyonel)
- [ ] `.github/workflows/` dizini oluştur (GitHub Actions için)
- [ ] Temel CI yapılandırması ekle (test ve linting için)

## Bölüm 2: Backend Birleştirme Süreci

### 1. Mevcut Yapı Analizi
- [ ] `server/` ve `backend/` dizinlerinin detaylı karşılaştırmasını yap
- [ ] Her iki dizindeki dosya ve klasörlerin envanterini çıkar
```bash
find server -type f -name "*.py" | sort > server_files.txt
find backend -type f -name "*.py" | sort > backend_files.txt
```
- [ ] Ortak ve benzersiz modülleri belirle
- [ ] Her iki dizindeki özellikleri listele
- [ ] Aşağıdaki temel bileşenleri belgele:
  - [ ] Veritabanı modelleri
  - [ ] API endpoint'leri
  - [ ] Servisler
  - [ ] Yardımcı işlevler
  - [ ] Middlewares
  - [ ] Test dosyaları

### 2. Birleştirme Stratejisi
- [ ] Hedef yapıyı belirle (tüm kodun `server/` altında olacağını onaylayalım)
- [ ] Kodların nasıl birleştirileceğine dair plan oluştur:
  - [ ] Aynı isimli dosyalar için çözüm yaklaşımını belirle (merge veya biri diğerini değiştirecek)
  - [ ] Dosya ve klasör yapısını tanımla
  - [ ] Birim test yaklaşımını belirle
- [ ] Geçiş süreci için zaman çizelgesi oluştur

### 3. Kod Taşıma İşlemi
- [ ] `backend/` dizininden `server/` dizinine özgün modülleri taşı
  - [ ] Modeller (`models/`)
  - [ ] API rotaları (`api/`)
  - [ ] Servisler (`services/`)
  - [ ] Yardımcı işlevler (`utils/`)
  - [ ] Test dosyaları (`tests/`)
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
- Tarih: __________
- Tamamlanan adımlar: 
- Notlar:

### Backend Analizi
- Tarih: __________
- Tamamlanan adımlar:
- Notlar:

### Kod Taşıma
- Tarih: __________
- Tamamlanan adımlar:
- Notlar:

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