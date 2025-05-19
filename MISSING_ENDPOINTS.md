# BDC - Eksik API Endpoint'leri

## Tespit Edilen 404 Hatası Veren Endpoint'ler

### 1. Calendar/Availability Endpoint'leri
- `/api/calendars/availability` - 404
- Amaç: Kullanıcı müsaitlik bilgilerini yönetme

### 2. Settings Endpoint'leri
- `/api/settings/general` - 404
- `/api/settings/appearance` - 404
- Amaç: Kullanıcı ve sistem ayarlarını yönetme

### 3. Assessment Templates Endpoint'i
- `/api/assessment/templates` - 404
- Amaç: Değerlendirme şablonlarını yönetme

### 4. Logout Endpoint'i (Yanlış Path)
- `/auth/logout` - 404 (Doğru path: `/api/auth/logout`)
- Test script'te yanlış path kullanılıyor

### 5. User Profile Endpoint'i
- `/api/users/me/profile` - 404
- Amaç: Kullanıcı profil bilgilerini görüntüleme/güncelleme

## Çözüm Planı

### Öncelik 1: Logout Path Düzeltmesi
Test script'teki `/auth/logout` path'ini `/api/auth/logout` olarak düzelt.

### Öncelik 2: Settings Endpoint'leri
```python
# app/api/settings.py
@settings_bp.route('/general', methods=['GET', 'PUT'])
@jwt_required()
def general_settings():
    # Genel ayarlar endpoint'i
    pass

@settings_bp.route('/appearance', methods=['GET', 'PUT'])
@jwt_required()
def appearance_settings():
    # Görünüm ayarları endpoint'i
    pass
```

### Öncelik 3: Calendar Availability Endpoint'i
```python
# app/api/calendars.py
@calendars_bp.route('/availability', methods=['GET', 'POST', 'PUT'])
@jwt_required()
def availability():
    # Müsaitlik yönetimi endpoint'i
    pass
```

### Öncelik 4: Assessment Templates Endpoint'i
```python
# app/api/assessment.py
@assessment_bp.route('/templates', methods=['GET', 'POST'])
@jwt_required()
@admin_required
def templates():
    # Değerlendirme şablonları endpoint'i
    pass
```

### Öncelik 5: User Profile Endpoint'i
```python
# app/api/users.py
@users_bp.route('/me/profile', methods=['GET', 'PUT'])
@jwt_required()
def user_profile():
    # Kullanıcı profili endpoint'i
    pass
```

## Implementation Notları

1. Her endpoint için:
   - Schema tanımla (request/response validation)
   - Service layer oluştur
   - Proper error handling ekle
   - Role-based access control uygula

2. Database modelleri:
   - Settings tablosu eklenebilir
   - Assessment templates tablosu gerekli
   - Calendar/availability için model güncellenmeli

3. Test Coverage:
   - Her endpoint için unit test yazılmalı
   - Integration testler eklenmeli
   - Permission testleri önemli