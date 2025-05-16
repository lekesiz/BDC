# BDC Admin Kullanıcı Kılavuzu

## İçindekiler

1. [Giriş](#giriş)
2. [Sistem Erişimi](#sistem-erişimi)
3. [Ana Panel](#ana-panel)
4. [Kullanıcı Yönetimi](#kullanıcı-yönetimi)
5. [Faydalanıcı Yönetimi](#faydalanıcı-yönetimi)
6. [Değerlendirme Yönetimi](#değerlendirme-yönetimi)
7. [Randevu Yönetimi](#randevu-yönetimi)
8. [Doküman Yönetimi](#doküman-yönetimi)
9. [Raporlama](#raporlama)
10. [Sistem Ayarları](#sistem-ayarları)
11. [İzleme ve Bakım](#izleme-ve-bakım)
12. [Sık Sorulan Sorular](#sık-sorulan-sorular)

## Giriş

BDC (Beneficiary Development Center) yönetici paneli, sistemin tüm yönlerini kontrol etmenizi sağlayan güçlü bir araçtır. Bu kılavuz, yönetici olarak sistemi nasıl kullanacağınızı adım adım açıklamaktadır.

### Sistem Gereksinimleri

- Modern web tarayıcı (Chrome, Firefox, Safari, Edge)
- Stabil internet bağlantısı
- 1366x768 veya üstü ekran çözünürlüğü

### Yönetici Rolleri

- **Süper Admin**: Tüm sistem yetkilerine sahip
- **Kuruluş Admini**: Kendi kuruluşunun yönetimi
- **Sistem Yöneticisi**: Teknik yapılandırma ve bakım

## Sistem Erişimi

### Giriş Yapma

1. Tarayıcınızda `https://yourdomain.com/admin` adresine gidin
2. Email ve şifrenizi girin
3. İki faktörlü doğrulama kodunu girin (eğer aktifse)
4. "Giriş Yap" butonuna tıklayın

![Giriş Ekranı](images/login-screen.png)

### İlk Giriş

İlk girişte şifrenizi değiştirmeniz istenecektir:

1. Mevcut şifrenizi girin
2. Yeni şifrenizi belirleyin (en az 8 karakter, büyük/küçük harf, rakam ve özel karakter içermeli)
3. Yeni şifrenizi tekrar girin
4. "Şifreyi Değiştir" butonuna tıklayın

### Şifremi Unuttum

1. Giriş ekranında "Şifremi Unuttum" linkine tıklayın
2. Email adresinizi girin
3. Emailinize gelen şifre sıfırlama linkine tıklayın
4. Yeni şifrenizi belirleyin

## Ana Panel

### Dashboard Görünümü

Ana panel, sistem durumunu özetleyen widget'lardan oluşur:

- **Genel İstatistikler**
  - Toplam kullanıcı sayısı
  - Aktif faydalanıcı sayısı
  - Bu ayki değerlendirme sayısı
  - Bekleyen randevular

- **Hızlı Erişim**
  - Yeni kullanıcı ekleme
  - Yeni değerlendirme oluşturma
  - Raporları görüntüleme
  - Sistem ayarları

- **Son Aktiviteler**
  - Son giriş yapan kullanıcılar
  - Son tamamlanan değerlendirmeler
  - Yaklaşan randevular

### Özelleştirme

Dashboard'u ihtiyaçlarınıza göre özelleştirebilirsiniz:

1. Sağ üst köşedeki "Düzenle" butonuna tıklayın
2. Widget'ları sürükleyerek yerlerini değiştirin
3. Gereksiz widget'ları gizleyin
4. "Kaydet" butonuna tıklayın

## Kullanıcı Yönetimi

### Kullanıcı Listesi

1. Sol menüden "Kullanıcılar" sekmesine tıklayın
2. Tüm kullanıcıları listeleyen tablo görünecektir
3. Arama kutusunu kullanarak kullanıcı arayabilirsiniz
4. Filtreleme seçenekleri:
   - Role göre (Admin, Eğitmen, Öğrenci)
   - Duruma göre (Aktif, Pasif)
   - Kuruluşa göre

### Yeni Kullanıcı Ekleme

1. "Yeni Kullanıcı Ekle" butonuna tıklayın
2. Gerekli bilgileri doldurun:
   - Ad Soyad
   - Email adresi
   - Telefon numarası
   - Rol seçimi
   - Başlangıç şifresi
3. "Kullanıcıyı Oluştur" butonuna tıklayın
4. Kullanıcıya aktivasyon emaili otomatik olarak gönderilecektir

### Kullanıcı Düzenleme

1. Kullanıcı listesinden düzenlemek istediğiniz kullanıcıya tıklayın
2. "Düzenle" butonuna tıklayın
3. Gerekli değişiklikleri yapın
4. "Değişiklikleri Kaydet" butonuna tıklayın

### Kullanıcı Yetkileri

#### Rol Atama
1. Kullanıcı detay sayfasında "Roller" sekmesine gidin
2. "Rol Ekle" butonuna tıklayın
3. Uygun rolü seçin
4. Gerekirse özel izinler ekleyin

#### Özel İzinler
- Raporları görüntüleme
- Kullanıcı oluşturma/düzenleme
- Sistem ayarlarına erişim
- Veri dışa aktarma

### Toplu İşlemler

1. Listeden birden fazla kullanıcı seçin
2. "Toplu İşlemler" menüsünü açın
3. İşlem seçin:
   - Aktif/Pasif yap
   - Rol değiştir
   - Email gönder
   - Dışa aktar

## Faydalanıcı Yönetimi

### Faydalanıcı Listesi

1. "Faydalanıcılar" menüsüne tıklayın
2. Listeleme seçenekleri:
   - Tüm faydalanıcılar
   - Aktif faydalanıcılar
   - Eğitmen ataması bekleyenler

### Faydalanıcı Profili

Her faydalanıcı profili şunları içerir:

- **Kişisel Bilgiler**
  - Ad soyad
  - İletişim bilgileri
  - Doğum tarihi
  - Acil durum kontağı

- **Eğitim Bilgileri**
  - Atanan eğitmen
  - Başlama tarihi
  - Mevcut durum
  - İlerleme özeti

- **Değerlendirmeler**
  - Tamamlanan testler
  - Ortalama puanlar
  - Gelişim grafiği

### Eğitmen Atama

1. Faydalanıcı profilinde "Eğitmen Ata" butonuna tıklayın
2. Uygun eğitmeni listeden seçin
3. Atama notları ekleyin (opsiyonel)
4. "Atamayı Onayla" butonuna tıklayın

### İlerleme Takibi

1. Faydalanıcı profilinde "İlerleme" sekmesine gidin
2. Görüntüleme seçenekleri:
   - Aylık ilerleme grafiği
   - Beceri bazlı analiz
   - Değerlendirme geçmişi
   - AI önerileri

## Değerlendirme Yönetimi

### Değerlendirme Şablonları

1. "Değerlendirmeler" > "Şablonlar" menüsüne gidin
2. Mevcut şablonları görüntüleyin
3. "Yeni Şablon" oluşturun:
   - Şablon adı
   - Kategori
   - Soru sayısı ve türleri
   - Puanlama kriterleri

### Yeni Değerlendirme Oluşturma

1. "Yeni Değerlendirme" butonuna tıklayın
2. Değerlendirme türünü seçin:
   - Standart test
   - Özel değerlendirme
   - AI destekli değerlendirme
3. Parametreleri belirleyin:
   - Süre limiti
   - Soru sayısı
   - Zorluk seviyesi
   - Geçme puanı

### Değerlendirme Sonuçları

1. "Sonuçlar" sekmesine gidin
2. Filtreleme seçenekleri:
   - Tarih aralığı
   - Faydalanıcı
   - Eğitmen
   - Başarı durumu
3. Detaylı analiz için sonuca tıklayın

### AI Analizi

1. Değerlendirme sonucunda "AI Analizi" butonuna tıklayın
2. Otomatik analiz içeriği:
   - Güçlü yönler
   - Gelişim alanları
   - Önerilen aktiviteler
   - Tahminlenen ilerleme
3. İnsan onayı için "Onayla" veya "Revize Et"

## Randevu Yönetimi

### Takvim Görünümü

1. "Randevular" menüsünden takvime erişin
2. Görünüm seçenekleri:
   - Aylık görünüm
   - Haftalık görünüm
   - Günlük görünüm
   - Liste görünümü

### Randevu Oluşturma

1. Takvimde boş bir zaman dilimini seçin
2. Randevu bilgilerini girin:
   - Başlık
   - Katılımcılar
   - Süre
   - Konum/Oda
   - Notlar
3. Hatırlatma ayarları:
   - Email bildirimi
   - SMS bildirimi
   - Takvim senkronizasyonu

### Toplu Randevu Planlama

1. "Toplu Planlama" özelliğini kullanın
2. Parametreleri belirleyin:
   - Tarih aralığı
   - Tekrar sıklığı
   - Katılımcı grupları
3. Çakışmaları kontrol edin
4. Randevuları oluşturun

### Google Calendar Entegrasyonu

1. "Ayarlar" > "Entegrasyonlar" menüsüne gidin
2. Google Calendar'ı etkinleştirin
3. Yetkilendirme işlemini tamamlayın
4. Senkronizasyon ayarlarını yapılandırın

## Doküman Yönetimi

### Doküman Kategorileri

1. "Dokümanlar" > "Kategoriler" menüsüne gidin
2. Mevcut kategorileri düzenleyin
3. Yeni kategori ekleyin:
   - Kategori adı
   - Açıklama
   - Erişim yetkileri
   - Alt kategoriler

### Doküman Yükleme

1. "Yeni Doküman" butonuna tıklayın
2. Dosyayı seçin veya sürükle-bırak yapın
3. Doküman bilgilerini girin:
   - Başlık
   - Açıklama
   - Kategori
   - Etiketler
4. Paylaşım ayarları:
   - Özel (sadece yüklenen)
   - Belirli kullanıcılar
   - Rol bazlı erişim
   - Herkese açık

### Doküman Arama

1. Üst menüdeki arama kutusunu kullanın
2. Gelişmiş arama filtreleri:
   - Dosya türü
   - Yükleme tarihi
   - Yükleyen kişi
   - Kategori
   - Etiketler

### Versiyonlama

1. Doküman detay sayfasında "Versiyonlar" sekmesine gidin
2. Yeni versiyon yükleyin
3. Versiyon notları ekleyin
4. Eski versiyonları görüntüleyin/geri yükleyin

## Raporlama

### Hazır Raporlar

Sistem aşağıdaki hazır raporları sunar:

1. **Kullanıcı Raporları**
   - Kullanıcı aktivitesi
   - Giriş istatistikleri
   - Rol dağılımı

2. **Faydalanıcı Raporları**  
   - İlerleme raporları
   - Değerlendirme performansı
   - Eğitmen-faydalanıcı eşleşmeleri

3. **Sistem Raporları**
   - Performans metrikleri
   - Hata logları
   - Kullanım istatistikleri

### Özel Rapor Oluşturma

1. "Raporlar" > "Özel Rapor" menüsüne gidin
2. Rapor parametrelerini seçin:
   - Veri kaynağı
   - Tarih aralığı
   - Gruplandırma
   - Sıralama
3. Görselleştirme türü:
   - Tablo
   - Grafik
   - Pasta grafiği
   - Zaman serisi

### Rapor Planlama

1. Raporu kaydedin
2. "Planla" butonuna tıklayın
3. Planlama ayarları:
   - Sıklık (günlük, haftalık, aylık)
   - Gönderim zamanı
   - Alıcılar
   - Format (PDF, Excel, CSV)

### Rapor Dışa Aktarma

1. Rapor görünümünde "Dışa Aktar" butonuna tıklayın
2. Format seçin:
   - PDF (yazdırma için)
   - Excel (analiz için)
   - CSV (veri aktarımı için)
3. Dışa aktarma ayarları:
   - Sayfa yönü
   - Başlıklar
   - Filtreler

## Sistem Ayarları

### Genel Ayarlar

1. "Ayarlar" > "Genel" menüsüne gidin
2. Yapılandırılabilir ayarlar:
   - Site başlığı ve logosu
   - Zaman dilimi
   - Dil seçenekleri
   - Para birimi
   - Tarih formatı

### Güvenlik Ayarları

1. **Şifre Politikaları**
   - Minimum uzunluk
   - Karmaşıklık gereksinimleri
   - Geçerlilik süresi
   - Geçmiş şifre kontrolü

2. **Oturum Yönetimi**
   - Oturum zaman aşımı
   - Eşzamanlı oturum limiti
   - IP kısıtlamaları

3. **İki Faktörlü Doğrulama**
   - SMS doğrulama
   - Authenticator uygulaması
   - Email doğrulama

### Email Ayarları

1. "Ayarlar" > "Email" menüsüne gidin
2. SMTP yapılandırması:
   - Sunucu adresi
   - Port numarası
   - Kullanıcı adı ve şifre
   - Şifreleme türü
3. Email şablonları:
   - Hoş geldin emaili
   - Şifre sıfırlama
   - Randevu hatırlatmaları
   - Sistem bildirimleri

### Entegrasyonlar

1. **Google Workspace**
   - Calendar senkronizasyonu
   - Drive entegrasyonu
   - Gmail bağlantısı

2. **OpenAI**
   - API anahtarı
   - Model seçimi
   - Kullanım limitleri

3. **SMS Servisleri**
   - Twilio entegrasyonu
   - SMS şablonları
   - Gönderim kotaları

### Yedekleme Ayarları

1. "Ayarlar" > "Yedekleme" menüsüne gidin
2. Otomatik yedekleme:
   - Yedekleme sıklığı
   - Saklama süresi
   - Yedekleme konumu
3. Manuel yedekleme:
   - "Şimdi Yedekle" butonu
   - Yedekleme türü seçimi
   - İndirme seçeneği

## İzleme ve Bakım

### Sistem Durumu

1. "İzleme" > "Sistem Durumu" menüsüne gidin
2. Gerçek zamanlı metrikler:
   - CPU kullanımı
   - Bellek kullanımı
   - Disk alanı
   - Ağ trafiği

### Performans İzleme

1. **Yanıt Süreleri**
   - API endpoint performansı
   - Sayfa yükleme süreleri
   - Veritabanı sorgu süreleri

2. **Kullanıcı Metrikleri**
   - Eşzamanlı kullanıcı sayısı
   - Sayfa görüntülemeleri
   - İşlem başarı oranları

### Hata Yönetimi

1. "İzleme" > "Hata Logları" menüsüne gidin
2. Hata filtreleme:
   - Hata türü
   - Önem seviyesi
   - Zaman aralığı
3. Hata detayları:
   - Hata mesajı
   - Stack trace
   - Etkilenen kullanıcılar
   - Çözüm önerileri

### Güvenlik İzleme

1. **Giriş Logları**
   - Başarılı girişler
   - Başarısız denemeler
   - Şüpheli aktiviteler

2. **Erişim Kontrolleri**
   - Yetkisiz erişim denemeleri
   - Rol değişiklikleri
   - İzin güncellemeleri

### Bakım Modu

1. "Ayarlar" > "Bakım Modu" menüsüne gidin
2. Bakım modu ayarları:
   - Başlangıç zamanı
   - Tahmini süre
   - Bakım mesajı
   - Beyaz liste (erişime izin verilenler)

## Sık Sorulan Sorular

### Genel Sorular

**S: Şifremi nasıl değiştirebilirim?**
C: Profil ayarlarından "Güvenlik" sekmesine giderek şifrenizi değiştirebilirsiniz.

**S: Yeni kullanıcı eklediğimde email gitmiyor, ne yapmalıyım?**
C: Email ayarlarını kontrol edin ve SMTP yapılandırmasının doğru olduğundan emin olun.

**S: Sistemde bir hata alıyorum, nasıl raporlayabilirim?**
C: Hata mesajının ekran görüntüsünü alın ve destek ekibine iletin. Hata loglarından detaylı bilgi alabilirsiniz.

### Kullanıcı Yönetimi

**S: Bir kullanıcıyı sistemden tamamen nasıl silerim?**
C: GDPR uyumluluğu nedeniyle kullanıcılar silinmez, sadece pasif yapılır. Veri silme talebi için özel prosedür uygulanır.

**S: Toplu kullanıcı aktarımı yapabilir miyim?**
C: Evet, "Kullanıcılar" > "İçe Aktar" menüsünden CSV dosyası ile toplu kullanıcı ekleyebilirsiniz.

### Raporlama

**S: Özel raporumu nasıl kaydedebilirim?**
C: Raporu oluşturduktan sonra "Kaydet" butonuna tıklayın ve rapor adı verin. Kaydedilen raporlar "Raporlarım" bölümünde görünür.

**S: Raporları otomatik olarak email ile gönderebilir miyim?**
C: Evet, rapor planlama özelliğini kullanarak belirli aralıklarla otomatik gönderim ayarlayabilirsiniz.

### Güvenlik

**S: İki faktörlü doğrulama nasıl etkinleştirilir?**
C: "Ayarlar" > "Güvenlik" > "2FA" bölümünden etkinleştirebilirsiniz. Kullanıcılar kendi profillerinden aktif edebilir.

**S: IP kısıtlaması nasıl uygulanır?**
C: "Ayarlar" > "Güvenlik" > "Erişim Kontrolleri" bölümünden izin verilen IP aralıklarını tanımlayabilirsiniz.

### Performans

**S: Sistem yavaşladı, ne yapmalıyım?**
C: Performans izleme sayfasından metrikleri kontrol edin. Yüksek kullanım varsa önbellek temizlemeyi veya sunucu kaynaklarını artırmayı düşünün.

**S: Veritabanı optimizasyonu ne sıklıkla yapılmalı?**
C: Aylık otomatik optimizasyon planlanmıştır. Manuel optimizasyon için "Bakım" menüsünü kullanabilirsiniz.

## Destek ve İletişim

### Teknik Destek

- Email: destek@yourdomain.com
- Telefon: +90 (212) 123 45 67
- Çalışma Saatleri: Hafta içi 09:00 - 18:00

### Acil Durumlar

7/24 acil destek hattı: +90 (555) 123 45 67

### Eğitim ve Kaynaklar

- Video eğitimler: https://egitim.yourdomain.com
- Kullanıcı forumu: https://forum.yourdomain.com
- API dokümantasyonu: https://api-docs.yourdomain.com

### Güncelleme Bildirimleri

Sistem güncellemeleri ve yeni özellikler hakkında bilgi almak için:
- Sistem içi bildirimler
- Email bülteni
- Blog: https://blog.yourdomain.com

## Ek Bilgiler

### Klavye Kısayolları

- `Ctrl + K`: Hızlı arama
- `Ctrl + N`: Yeni kayıt oluştur
- `Ctrl + S`: Kaydet
- `Esc`: İptal/Kapat
- `?`: Yardım menüsü

### Sistem Gereksinimleri

**Minimum Gereksinimler:**
- İşlemci: Dual Core 2.0 GHz
- RAM: 4 GB
- Disk: 50 GB
- İnternet: 10 Mbps

**Önerilen Gereksinimler:**
- İşlemci: Quad Core 3.0 GHz
- RAM: 8 GB
- Disk: 100 GB SSD
- İnternet: 50 Mbps

### Yasal Uyarılar

- Tüm veriler KVKK ve GDPR uyumlu olarak saklanır
- Sistem logları 90 gün süreyle tutulur
- Kullanıcı verileri şifrelenerek saklanır
- Düzenli güvenlik denetimleri yapılır

### Versiyon Geçmişi

- v2.0.0 (2024-01): Büyük güncelleme, yeni arayüz
- v1.5.0 (2023-09): AI entegrasyonu eklendi
- v1.2.0 (2023-06): Raporlama modülü geliştirildi
- v1.0.0 (2023-01): İlk sürüm

---

*Bu dokümantasyon en son 2024-01 tarihinde güncellenmiştir. En güncel bilgiler için sistem içi yardım menüsünü kontrol edin.*