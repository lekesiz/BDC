# BDC (Beneficiary Development Center) - Bileşen İmplementasyonu

Bu doküman, BDC projesi için geliştirilen belge görüntüleme ve yönetim bileşenlerinin implementasyonunu detaylandırmaktadır.

## 1. İmplementasyonu Yapılan Bileşenler

### Belge Görüntüleyici (DocumentViewer)

Belge görüntüleyici bileşeni, çeşitli dosya türlerini (PDF, görsel, ofis dokümanları, metin dosyaları) web arayüzünde göstermek için geliştirilmiştir. Bu bileşen:

- PDF sayfalamasını ve navigasyonunu destekler
- Yakınlaştırma/uzaklaştırma işlevselliği sunar
- Arama işlevi içerir
- Tam ekran desteği sağlar
- Dosya indirme işlevselliği içerir
- Çeşitli dosya türleri için özelleştirilmiş görüntüleme sunar

**Arayüz:**
```jsx
<DocumentViewer
  document={document}
  onDownload={handleDownload}
  showToolbar={true}
  initialZoom={100}
  height="800px"
  className="custom-class"
/>
```

### Belge Yükleyici (DocumentUploader)

Belge yükleme bileşeni, kullanıcıların sürükle-bırak veya dosya seçici ile belge yüklemelerini sağlar. Özellikler:

- Sürükle-bırak desteği
- Çoklu dosya seçimi
- Dosya türü doğrulama
- Boyut doğrulama
- Yükleme ilerleme göstergesi
- Önizleme desteği

**Arayüz:**
```jsx
<DocumentUploader
  onUploadComplete={handleUploadComplete}
  onUploadError={handleUploadError}
  metadata={metadata}
  maxFileSize={100 * 1024 * 1024}
  allowMultiple={true}
  maxFiles={10}
  acceptedFileTypes={['pdf', 'office', 'image', 'text', 'archive']}
  onPreview={handlePreviewDocument}
/>
```

### Belge Paylaşım (DocumentShare)

Belge paylaşım bileşeni, kullanıcıların belgeleri diğer kullanıcılarla paylaşmasını ve paylaşım izinlerini yönetmesini sağlar. Özellikler:

- Kullanıcı arama
- İzin yönetimi (görüntüleme, indirme, düzenleme)
- Paylaşım bağlantısı oluşturma
- Şifreli paylaşım
- Geçerlilik süresi belirleme
- E-posta gönderme

**Arayüz:**
```jsx
<DocumentShare
  documentId={id}
  initialShares={shares}
  onShareComplete={handleShareComplete}
  onClose={handleClose}
/>
```

### Belge Hizmeti (DocumentService)

Belge işlemlerini merkezi olarak yönetmek için bir hizmet modülü. İşlevler:

- Dosya yükleme
- Dosya indirme
- Paylaşım oluşturma/yönetme
- Dosya türü doğrulama
- Boyut doğrulama
- Dosya biçimlendirme

## 2. Bileşen Yapısı

Bileşenler `/client/src/components/document/` dizininde yer almaktadır:

```
/client/src/components/document/
  ├── DocumentViewer.jsx  - Belge görüntüleme bileşeni
  ├── DocumentUploader.jsx - Belge yükleme bileşeni
  ├── DocumentShare.jsx - Belge paylaşım bileşeni
  ├── DocumentService.js - Belge işlemleri hizmeti
  └── index.js - Dışa aktarma
```

## 3. Entegrasyon

Bileşenler, mevcut projede şu sayfalarda entegre edilmiştir:

1. **Belge Görüntüleme Sayfası**: `DocumentViewerPageV2.jsx`
2. **Belge Yükleme Sayfası**: `DocumentUploadPageV2.jsx`
3. **Belge Paylaşım Sayfası**: `DocumentSharePageV2.jsx`

## 4. Props ve Yapılandırma

### DocumentViewer Özellikleri

| Prop | Tür | Açıklama |
|------|-----|----------|
| document | Object | Belge nesnesi (url, type, name vs.) |
| onDownload | Function | İndirme işlevi (isteğe bağlı) |
| showToolbar | Boolean | Araç çubuğunu göster/gizle |
| initialZoom | Number | Başlangıç yakınlaştırma seviyesi |
| height | String | Görüntüleyici yüksekliği |
| className | String | Ek CSS sınıfları |

### DocumentUploader Özellikleri

| Prop | Tür | Açıklama |
|------|-----|----------|
| onUploadComplete | Function | Yükleme tamamlandığında çağrılır |
| onUploadError | Function | Yükleme hatası durumunda çağrılır |
| acceptedFileTypes | Array/Object | Kabul edilen dosya türleri |
| maxFileSize | Number | Maksimum dosya boyutu (byte) |
| maxFiles | Number | Maksimum dosya sayısı |
| allowMultiple | Boolean | Çoklu dosya seçimine izin ver |
| showPreview | Boolean | Dosya önizlemesini göster/gizle |
| metadata | Object | Dosyayla birlikte gönderilecek meta veriler |

### DocumentShare Özellikleri

| Prop | Tür | Açıklama |
|------|-----|----------|
| documentId | String/Number | Paylaşılacak belge ID'si |
| initialShares | Array | Mevcut paylaşımlar |
| onShareComplete | Function | Paylaşım tamamlandığında çağrılır |
| onClose | Function | Kapatma işlevi |
| className | String | Ek CSS sınıfları |

## 5. Örnek Kullanım

```jsx
import { DocumentViewer, DocumentUploader, DocumentShare } from '../../components/document';

// Belge görüntüleyici kullanımı
<DocumentViewer
  document={{
    id: '123',
    url: 'http://example.com/document.pdf',
    type: 'pdf',
    name: 'Example Document.pdf',
    page_count: 5
  }}
  height="600px"
/>

// Belge yükleyici kullanımı
<DocumentUploader
  onUploadComplete={(documents) => {
    console.log('Uploaded:', documents);
  }}
  onUploadError={(errors) => {
    console.error('Upload errors:', errors);
  }}
  maxFileSize={50 * 1024 * 1024} // 50MB
  acceptedFileTypes={['pdf', 'image']}
/>

// Belge paylaşım kullanımı
<DocumentShare
  documentId="123"
  onShareComplete={(shares) => {
    console.log('New shares:', shares);
  }}
/>
```

## 6. İyileştirme ve Gelecek Geliştirmeler

1. **Belge Görüntüleyici**:
   - PDF.js entegrasyonu ile daha kapsamlı PDF görüntüleme
   - Not alma ve işaretleme özellikleri
   - Dijital imza desteği

2. **Belge Yükleyici**:
   - Toplu meta veri düzenleme
   - Sıkıştırılmış dosya (zip) içerik önizleme
   - Yükleme kuyruğu yönetimi

3. **Belge Paylaşım**:
   - Kapsamlı izin rolleri
   - Otomatik paylaşım zamanlama
   - Paylaşım analitiği

## 7. Test Durumu

Tüm bileşenler için temel birim testleri oluşturuldu:

- Bileşen render testleri
- Özellik testleri
- Hata işleme testleri
- Entegrasyon testleri

End-to-end testler, Cypress ile yapılandırıldı.

## 8. Sonuç

Belge yönetim bileşenleri, modern web teknolojileri kullanılarak, kullanıcı deneyimini en üst düzeye çıkaracak şekilde tasarlanmıştır. Modüler yapı, projenin farklı yerlerinde yeniden kullanılabilirlik sağlarken, kapsamlı özellik seti kurumsal belge yönetim ihtiyaçlarını karşılamaktadır.