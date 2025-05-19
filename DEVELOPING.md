# Developing BDC

Bu dosya, proje geliştirme sürecinde takip edilmesi gereken adımları ve en iyi uygulamaları özetler.

## Ortam Kurulumu

1. Depoyu klonlayın ve dizine girin.
2. `server/` dizininde Python venv oluşturun ve `requirements.txt` + `requirements-test.txt` yükleyin.
3. `client/` dizininde `npm ci` çalıştırın.
4. Redis & PostgreSQL servislerini docker-compose.dev.yml ile ayağa kaldırın.

## Pre-commit Hook'lar

Aşağıdaki komut ile hook'ları yükleyin:
```bash
pre-commit install
```
Bu sayede commit öncesi black, isort, flake8, bandit, eslint, prettier otomatik çalışır.

## Test & Coverage

Backend:
```bash
cd server
python run_tests.py  # pytest + coverage, eşik ≥50 %
```

Frontend:
```bash
cd client
npm run test:coverage  # vitest + coverage, eşik ≥50 %
```

CI'de coverage Codecov'a gönderilir. Coverage badge README'de gösterilir.

## Branch Stratejisi
- `main`: production
- `develop`: staging
- `feature/*`: yeni özellikler

## Pull Request Checklist
- [ ] Tüm backend & frontend testleri yeşil.
- [ ] Coverage eşiği aşılmış.
- [ ] Pre-commit hook hatasız.
- [ ] Gerekli dokümantasyon güncellendi. 