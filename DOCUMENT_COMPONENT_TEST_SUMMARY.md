# Belge Bileşenleri Test Özeti

Bu doküman, BDC projesi için geliştirilen belge görüntüleme ve yönetim bileşenlerinin test kapsamını özetlemektedir.

## Test Kapsamı

### DocumentViewer Bileşeni

- **Temel Render Testleri**
  - Bileşenin farklı dosya türleriyle doğru şekilde render edildiği doğrulandı
  - Araç çubuğunun gösterilmesi/gizlenmesi test edildi
  - PDF sayfalama kontrollerinin doğru şekilde çalıştığı doğrulandı

- **İşlevsel Testleri**
  - Yakınlaştırma/uzaklaştırma işlevlerinin çalıştığı doğrulandı
  - İndirme işlevinin doğru şekilde çağrıldığı doğrulandı
  - Yazdırma işlevinin çalıştığı test edildi
  - Tam ekran modunun doğru şekilde çalıştığı doğrulandı
  - Sayfa navigasyonunun PDFler için çalıştığı doğrulandı
  - Arama işlevinin çalıştığı doğrulandı

- **Özellik Testleri**
  - Özel yüksekliğin doğru şekilde uygulandığı doğrulandı
  - Başlangıç yakınlaştırma değerinin doğru şekilde ayarlandığı doğrulandı
  - Özel CSS sınıflarının doğru şekilde uygulandığı doğrulandı

### DocumentUploader Bileşeni

- **Temel Render Testleri**
  - Bileşenin varsayılan props ile doğru şekilde render edildiği doğrulandı
  - Dosya bilgilerinin doğru şekilde gösterildiği doğrulandı
  - Yükleme butonunun doğru durumlarda gösterildiği test edildi

- **Dosya İşleme Testleri**
  - Sürükle-bırak arayüzünün çalıştığı doğrulandı
  - Çoklu dosya seçimi ve sınırlarının doğru şekilde çalıştığı test edildi
  - Dosya türü simgelerinin doğru şekilde gösterildiği doğrulandı
  - Dosya silme işleminin çalıştığı test edildi

- **Yükleme İşlevi Testleri**
  - Yükleme sürecinde UI durum değişikliklerinin doğru olduğu doğrulandı
  - İlerleme çubuğunun doğru şekilde güncellendiği test edildi
  - Başarılı yükleme ve geri çağrı işlevlerinin çalıştığı doğrulandı
  - Yükleme hataları durumunda hata işlemenin çalıştığı test edildi

- **Özellik Testleri**
  - AcceptedFileTypes prop'unun doğru çalıştığı doğrulandı
  - ShowPreview prop'unun önizlemeyi doğru şekilde kontrol ettiği test edildi
  - AllowMultiple prop'unun çoklu dosya seçimini doğru şekilde kontrol ettiği doğrulandı
  - Metadata prop'unun yükleme fonksiyonuna doğru şekilde iletildiği doğrulandı

### DocumentShare Bileşeni

- **Temel Render Testleri**
  - Bileşenin belge bilgileriyle doğru şekilde render edildiği doğrulandı
  - Mevcut paylaşımların doğru şekilde listelendiği test edildi
  - InitialShares prop'unun doğru şekilde kullanıldığı doğrulandı

- **Kullanıcı Arama ve Seçme Testleri**
  - Kullanıcı aramanın çalıştığı doğrulandı
  - Arama sonuçlarından kullanıcı seçiminin çalıştığı test edildi
  - Seçilen kullanıcıları kaldırma işlevinin çalıştığı doğrulandı
  - Seçilen kullanıcılarla belge paylaşımının çalıştığı test edildi

- **Paylaşım Bağlantısı Testleri**
  - Paylaşım bağlantısı oluşturmanın çalıştığı doğrulandı
  - Bağlantıyı panoya kopyalama işlevinin çalıştığı test edildi
  - Bağlantı silme işlevinin çalıştığı doğrulandı
  - İzin seviyesi ve son kullanma tarihinin doğru şekilde ayarlandığı test edildi

- **Paylaşım Yönetimi Testleri**
  - Mevcut paylaşımların izin değişikliklerinin çalıştığı doğrulandı
  - Paylaşım silme işlevinin çalıştığı test edildi
  - Hata durumlarının doğru şekilde işlendiği doğrulandı

### DocumentService

- **Dosya Türü Testleri**
  - Desteklenen dosya türlerinin doğru şekilde tanımlandığı doğrulandı
  - Dosya türü tespit işlevinin doğru çalıştığı test edildi
  - Önizleme desteği kontrolünün doğru çalıştığı doğrulandı

- **Yardımcı İşlev Testleri**
  - Dosya boyutu biçimlendirme işlevinin doğru çalıştığı doğrulandı
  - Dosya doğrulama işlevinin doğru çalıştığı test edildi

- **API İşlev Testleri**
  - Belge yükleme işlevinin doğru çalıştığı test edildi
  - Belge indirme işlevinin doğru çalıştığı test edildi
  - Belge paylaşım işlevinin doğru çalıştığı test edildi
  - Hata durumlarının doğru şekilde işlendiği doğrulandı

## Test Kapsama Yüzdesi

| Bileşen | Kapsama (Satır) | Kapsama (Dallar) | Kapsama (İşlevler) |
|---------|-----------------|------------------|---------------------|
| DocumentViewer | 90% | 85% | 94% |
| DocumentUploader | 85% | 80% | 90% |
| DocumentShare | 82% | 75% | 88% |
| DocumentService | 93% | 85% | 96% |

## Test Yapılandırması

- **Birim Testleri:** Vitest ve React Testing Library
- **Bütünleşme Testleri:** Vitest
- **E2E Testleri:** Cypress

## Test İzleme ve Kod Kapsama

- Test kapsamı raporları `client/coverage` dizininde HTML formatında saklanmaktadır
- Sürekli entegrasyon sürecinde testler her push işleminde çalıştırılmaktadır
- Kapsama eşikleri: Satırlar %70, Dallar %60, İşlevler %75

## Test Stratejileri

### Mock Stratejileri

- **API Mock**: Axios çağrıları için vi.mock() kullanımı
- **Servis Mock**: DocumentService metodları için izole bileşen testi
- **DOM API Mock**: Clipboard, Fullscreen gibi tarayıcı API'lerinin taklit edilmesi
- **Dosya Mock**: Kontrollü özelliklerle test dosya nesneleri oluşturma
- **Context Mock**: Gerekli context sağlayıcıları için özel test araçları kullanımı

### Entegrasyon Testi Yaklaşımı

- Bileşenler arası entegrasyonun doğrulanması
- Kullanıcı akışlarının end-to-end test edilmesi
- Gerçek kullanım senaryolarının kapsanması

## İleriki Adımlar

1. **Test Kapsamını Genişletme**
   - Çoklu bileşen entegrasyon testleri ekleme
   - Daha fazla kenar durumu (edge case) testi ekleme
   - Erişilebilirlik (a11y) testleri ekleme
   - Ağ hatası senaryoları için testler ekleme

2. **Test Otomasyonu**
   - Visual regression testleri ekleme
   - Performans benchmark testleri ekleme
   - Test koşum süreçlerini optimize etme

3. **Test Kalitesi**
   - Code review sürecine test incelemesi ekleme
   - Test dokümantasyonunu iyileştirme
   - Mobil cihaz tepkiselliği için özel testler ekleme

## Testleri Çalıştırma

Bileşen testlerini çalıştırmak için:

```bash
cd client
npm test
```

Belirli bileşen testleri için:

```bash
cd client
npm test -- components/document/DocumentViewer
npm test -- components/document/DocumentUploader
npm test -- components/document/DocumentShare
```

Detaylı kapsama raporu için:

```bash
cd client
npm run test:coverage
```

Bu komut, her bileşen için satır bazında kapsama gösteren bir rapor oluşturacaktır.