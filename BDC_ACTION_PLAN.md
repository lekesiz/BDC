# BDC Projesi - Eksik ve Hataların Giderilmesi Aksiyon Planı

## Özet
BDC projesinin dokümantasyon doğrulama sürecinde tespit edilen eksik ve hataların giderilmesi için hazırlanmış detaylı aksiyon planıdır.

## Öncelik Seviyeleri
- 🔴 **KRİTİK**: İşlevselliği engelleyen, acil çözülmesi gereken
- 🟠 **YÜKSEK**: Önemli özellik eksikleri
- 🟡 **ORTA**: İyileştirme gerektiren alanlar
- 🟢 **DÜŞÜK**: Nice-to-have özellikler

---

## 1. KRİTİK SEVİYE DÜZELTMELER 🔴

### 1.1 Beneficiary Creation Endpoint Eksikliği
**Problem**: Frontend beneficiary oluşturma formu var ama `/api/beneficiaries` POST endpoint yok
**Çözüm**:
```python
# /server/app/api/beneficiaries_v2/__init__.py içine eklenecek
@bp.route('', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def create_beneficiary():
    # Implementation
```
**Tahmini Süre**: 2 saat

### 1.2 Model-API Field Mismatch
**Problem**: MessageThread modelinde `title` field yok ama API bekliyor
**Çözüm**:
```python
# /server/app/models/notification.py - MessageThread modeline eklenecek
title = db.Column(db.String(255))
thread_type = db.Column(db.String(50))

# Message modeline eklenecek
is_edited = db.Column(db.Boolean, default=False)
edited_at = db.Column(db.DateTime)
```
**Tahmini Süre**: 1 saat + migration

### 1.3 Test Submission Flow Eksikliği
**Problem**: Test submission, results ve AI analysis endpoint'leri eksik
**Çözüm**:
```python
# /server/app/api/evaluations.py içine eklenecek
@bp.route('/<int:id>/submit', methods=['POST'])
@bp.route('/<int:id>/results', methods=['GET'])
@bp.route('/<int:id>/analyze', methods=['POST'])
```
**Tahmini Süre**: 4 saat

---

## 2. YÜKSEK ÖNCELİKLİ DÜZELTMELER 🟠

### 2.1 Background Task Scheduler Implementasyonu
**Problem**: Otomatik hatırlatıcılar için scheduler yok
**Çözüm**: Celery ve Redis entegrasyonu
```python
# requirements.txt
celery==5.3.0
redis==5.0.0

# /server/app/tasks.py oluştur
from celery import Celery
# Email reminder tasks
# Notification tasks
```
**Tahmini Süre**: 8 saat

### 2.2 Document Management CRUD Tamamlama
**Problem**: Document GET/PUT/DELETE ve download endpoint'leri eksik
**Çözüm**:
```python
# /server/app/api/documents.py içine eklenecek
@bp.route('/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@bp.route('/<int:id>/download', methods=['GET'])
@bp.route('/<int:id>/share', methods=['POST'])
```
**Tahmini Süre**: 3 saat

### 2.3 Real-time Messaging WebSocket Bağlantısı
**Problem**: WebSocket altyapısı var ama messaging'e bağlı değil
**Çözüm**:
```python
# /server/app/websocket_notifications.py içine eklenecek
@socketio.on('message_sent', namespace='/notifications')
@socketio.on('typing', namespace='/notifications')
```
**Tahmini Süre**: 4 saat

---

## 3. ORTA ÖNCELİKLİ DÜZELTMELER 🟡

### 3.1 Two-Factor Authentication (2FA)
**Problem**: 2FA hiç implemente edilmemiş
**Çözüm**: 
- pyotp kütüphanesi ile TOTP implementasyonu
- QR kod üretimi
- Backup codes
**Tahmini Süre**: 12 saat

### 3.2 Document Versioning System
**Problem**: Belge versiyonlama yok
**Çözüm**:
```python
# Yeni model: DocumentVersion
class DocumentVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
    version_number = db.Column(db.Integer)
    file_path = db.Column(db.String(500))
    # ...
```
**Tahmini Süre**: 6 saat

### 3.3 Recurring Appointments
**Problem**: Tekrarlayan randevu desteği yok
**Çözüm**: 
- Appointment modeline recurrence pattern ekle
- Recurrence logic implementasyonu
**Tahmini Süre**: 8 saat

### 3.4 AI Features - Placeholder'ları Gerçek Implementasyona Çevirme
**Problem**: Birçok AI özelliği placeholder
**Çözüm**:
- Report synthesis gerçek implementasyonu
- Chatbot assistant tamamlama
- Performance predictions aktif etme
**Tahmini Süre**: 16 saat

---

## 4. DÜŞÜK ÖNCELİKLİ DÜZELTMELER 🟢

### 4.1 SMS Integration
**Problem**: SMS bildirimleri yok
**Çözüm**: Twilio entegrasyonu
**Tahmini Süre**: 4 saat

### 4.2 Video Conferencing
**Problem**: Video konferans özelliği yok
**Çözüm**: Jitsi Meet veya Zoom API entegrasyonu
**Tahmini Süre**: 8 saat

### 4.3 Field Naming Standardization
**Problem**: Model field isimleri dokümantasyondan farklı
**Çözüm**: Migration ile field isimlerini güncelle veya alias ekle
**Tahmini Süre**: 2 saat

---

## İMPLEMENTASYON SIRASI

### Hafta 1 (40 saat)
1. ✅ Beneficiary Creation Endpoint (2 saat) - COMPLETED (3 Haziran 2025)
2. ✅ Model-API Field Mismatch (1 saat) - COMPLETED (3 Haziran 2025)
3. ✅ Test Submission Flow (4 saat) - COMPLETED (3 Haziran 2025)
4. ✅ Document Management CRUD (3 saat) - COMPLETED (3 Haziran 2025)
5. ✅ Real-time Messaging WebSocket (4 saat) - COMPLETED (3 Haziran 2025)
6. ✅ Background Task Scheduler kurulum (8 saat) - COMPLETED (3 Haziran 2025)
7. ✅ Document Versioning başlangıç (6 saat) - COMPLETED (3 Haziran 2025)
8. ✅ Emergency contact field ekleme (1 saat) - COMPLETED (3 Haziran 2025)
9. ✅ API documentation güncelleme (3 saat) - COMPLETED (3 Haziran 2025)
10. ✅ Unit test yazımı (8 saat) - COMPLETED (3 Haziran 2025)

### Hafta 2 (40 saat)
1. ✅ Two-Factor Authentication (12 saat) - COMPLETED (3 Haziran 2025)
2. ✅ Recurring Appointments (8 saat) - COMPLETED (3 Haziran 2025)
3. ✅ AI Report Synthesis implementasyonu (8 saat) - COMPLETED (3 Haziran 2025)
4. ✅ Message search endpoints (4 saat) - COMPLETED (3 Haziran 2025)
5. ✅ Archive/unarchive endpoints (2 saat) - COMPLETED (3 Haziran 2025)
6. ⏱️ Integration testleri (6 saat)

### Hafta 3 (40 saat)
1. ⏱️ AI Chatbot Assistant tamamlama (8 saat)
2. ⏱️ Performance Predictions aktif etme (8 saat)
3. ⏱️ SMS Integration (4 saat)
4. ⏱️ Adaptive test system tasarım (8 saat)
5. ⏱️ Question randomization (4 saat)
6. ⏱️ Performance optimization (8 saat)

### Hafta 4 (40 saat)
1. ⏱️ Video Conferencing entegrasyonu (8 saat)
2. ⏱️ Field naming standardization (2 saat)
3. ⏱️ Bulk operations implementasyonu (6 saat)
4. ⏱️ End-to-end testler (8 saat)
5. ⏱️ Security audit ve düzeltmeler (8 saat)
6. ⏱️ Documentation finalization (8 saat)

---

## TEST STRATEJİSİ

### Her Feature İçin:
1. Unit testler yazılacak
2. Integration testler eklenecek
3. Frontend-backend entegrasyon testleri
4. Performance testleri (kritik endpoint'ler için)

### Test Coverage Hedefi:
- Backend: %80+
- Frontend: %70+

---

## RİSKLER VE MİTİGASYON

### Risk 1: Migration Sorunları
**Mitigation**: 
- Staging environment'da test
- Rollback planı hazırlama
- Database backup

### Risk 2: Performance Degradation
**Mitigation**:
- Load testing
- Caching strategy
- Database indexing

### Risk 3: Breaking Changes
**Mitigation**:
- API versioning
- Backward compatibility
- Deprecation notices

---

## BAŞARI KRİTERLERİ

1. ✅ Tüm kritik eksikler giderilmiş
2. ✅ Test coverage hedeflerine ulaşılmış
3. ✅ Performance benchmarks sağlanmış
4. ✅ Security audit geçilmiş
5. ✅ Documentation güncel

---

## SONUÇ

Bu plan takip edildiğinde, BDC projesi dokümantasyonda belirtilen tüm özelliklere sahip, production-ready bir platform haline gelecektir. Toplam tahmini süre: 4 hafta (160 saat).

Priority Matrix:
- Hafta 1: Kritik fonksiyonel eksikler
- Hafta 2: Authentication ve core features
- Hafta 3: AI ve advanced features
- Hafta 4: Nice-to-have ve polish

---

*Bu doküman, BDC projesinin eksiklerini gidermek için hazırlanmış detaylı bir yol haritasıdır.*
*Oluşturulma Tarihi: 3 Haziran 2025*