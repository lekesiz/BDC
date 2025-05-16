# BDC (Beneficiary Development Center)

Modern ve kapsamlı bir yetenek değerlendirme (Bilan de Compétence) platformu.

## Proje Açıklaması

BDC, faydalanıcıların (öğrencilerin) gelişim süreçlerini yönetmek, takip etmek ve değerlendirmek için tasarlanmış yapay zeka destekli bir web uygulamasıdır. Sistem, test motoru, değerlendirme, raporlama ve kişiselleştirilmiş öğrenme önerileri sunar.

## Özellikler

- **Kullanıcı Rolleri Yönetimi**: Süper Admin, Kiracı Admin, Eğitmen ve Öğrenci rolleri
- **Eğitim ve Bilan Yönetimi**: Eğitim içeriklerinin oluşturulması ve atanması
- **Test Motoru**: Çeşitli soru tipleri, zaman yönetimi ve sonuçların analizi
- **Yapay Zeka Asistanı**: Kişiselleştirilmiş geri bildirimler ve öneriler
- **Belge Üretici**: PDF raporları ve analizler
- **Dashboard ve Analitik**: Özelleştirilmiş gösterge panelleri
- **Bildirim Sistemi**: Anlık bildirimler ve hatırlatıcılar
- **Harici Entegrasyonlar**: Wedof API, Google Workspace, Pennylane

## Teknolojiler

### Backend
- Python/Flask
- SQLAlchemy (ORM)
- JWT Kimlik Doğrulama
- Redis (Önbellek ve Oturum Yönetimi)
- AI Entegrasyonu

### Frontend
- React
- Tailwind CSS
- Axios
- React Router
- Radix UI Bileşenleri

### Veritabanı
- SQLite (Geliştirme)
- PostgreSQL (Üretim)

## Test Etme

### Backend Test Ortamı

1. Gerekli bağımlılıkları yükleyin
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Veritabanını hazırlayın
```bash
flask db upgrade
python seed_db.py  # Varsayılan kullanıcıları oluşturur
```

3. Backend'i çalıştırın
```bash
flask run
```

Backend http://localhost:5000 adresinde çalışacaktır.

#### Varsayılan Kullanıcılar
- **Super Admin**: admin@bdc.com / Admin123!
- **Tenant Admin**: tenant@bdc.com / Tenant123!
- **Trainer**: trainer@bdc.com / Trainer123!
- **Student**: student@bdc.com / Student123!

### Frontend Test Ortamı

1. Gerekli bağımlılıkları yükleyin
```bash
cd client
npm install
```

2. Frontend'i çalıştırın
```bash
npm run dev
```

Frontend http://localhost:5173 adresinde çalışacaktır.

### API Test Etme

Backend API'lerini test etmek için:

1. Postman veya benzeri bir API test aracı kullanabilirsiniz
2. Thunder Client (VSCode eklentisi) kullanabilirsiniz
3. curl komutları ile test edebilirsiniz

Örnek curl komutu:
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bdc.com","password":"Admin123!"}'
```

### Otomatik Testler

Backend testleri için:
```bash
cd backend
pytest
```

Frontend testleri için:
```bash
cd client
npm run test
```

## Kurulum

### Gereksinimler
- Python 3.8+
- Node.js 18+
- npm/yarn
- Redis
- PostgreSQL (üretim için)

### Geliştirme Ortamı Kurulumu

1. Repoyu klonlayın
```bash
git clone <repo-url>
cd BDC
```

2. Backend kurulumu
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade
python seed_db.py  # Varsayılan kullanıcıları oluştur
```

3. Frontend kurulumu
```bash
cd client
npm install
```

4. Uygulamayı çalıştırma
```bash
# Backend
cd backend
flask run

# Frontend (yeni terminal)
cd client
npm run dev
```

## Docker ile Çalıştırma

Docker kullanarak tüm projeyi çalıştırabilirsiniz:

```bash
docker-compose up
```

Bu komut hem backend hem de frontend'i birlikte çalıştıracaktır.

## Detaylı Kurulum Kılavuzları

- [Backend Kurulum Kılavuzu](backend/README.md)
- [Frontend Kurulum Kılavuzu](client/README.md)

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## Lisans

Bu proje [MIT](LICENSE) lisansı altında lisanslanmıştır.