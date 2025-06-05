# 🤖 AI Konfigürasyon Kılavuzu

Bu kılavuz, BDC (Beneficiary Development Center) sisteminde AI özelliklerini yapılandırmak için gerekli bilgileri içerir.

## 📋 Desteklenen AI Sağlayıcıları

### 1. **OpenAI GPT**
- **Model Seçenekleri**:
  - `gpt-3.5-turbo` - Hızlı ve ekonomik
  - `gpt-4` - Gelişmiş akıl yürütme
  - `gpt-4-turbo` - Optimize edilmiş performans
  - `gpt-4o` - En son model

- **API Key**: OpenAI hesabınızdan alın
  - [OpenAI API Keys](https://platform.openai.com/api-keys) sayfasına gidin
  - "Create new secret key" butonuna tıklayın
  - Key'i güvenli bir yerde saklayın

- **Base URL**: `https://api.openai.com/v1`

### 2. **Anthropic Claude**
- **Model Seçenekleri**:
  - `claude-3-haiku-20240307` - Hızlı ve hafif
  - `claude-3-sonnet-20240229` - Dengeli performans
  - `claude-3-opus-20240229` - En güçlü model

- **API Key**: Anthropic hesabınızdan alın
  - [Anthropic Console](https://console.anthropic.com/) sayfasına gidin
  - API Keys bölümünden yeni key oluşturun

- **Base URL**: `https://api.anthropic.com/v1`

### 3. **Local LLM (Ollama)**
- **Model Seçenekleri**:
  - `llama2` - Meta'nın açık kaynak modeli
  - `mistral` - Mistral AI modeli
  - `codellama` - Kod üretimi için optimize edilmiş

- **Kurulum**:
  ```bash
  # Ollama'yı yükleyin
  curl -fsSL https://ollama.ai/install.sh | sh
  
  # Model indirin
  ollama pull llama2
  ollama pull mistral
  ```

- **Base URL**: `http://localhost:11434/v1`

## 🔧 Konfigürasyon Adımları

### 1. Settings Sayfasına Erişim
1. BDC sistemine admin veya trainer hesabıyla giriş yapın
2. Sağ üst köşedeki profil menüsünden "Settings" seçin
3. "AI" sekmesine tıklayın

### 2. API Key Yapılandırması
1. Kullanmak istediğiniz AI sağlayıcısını seçin
2. "API Key" alanına key'inizi girin
3. "Test Connection" butonu ile bağlantıyı test edin
4. "Save Settings" ile kaydedin

### 3. Model Ayarları
- **Temperature**: 0.0-1.0 arası (yaratıcılık seviyesi)
  - 0.1-0.3: Deterministik, faktüel cevaplar
  - 0.7-0.9: Yaratıcı, çeşitli cevaplar

- **Max Tokens**: Maksimum response uzunluğu
  - 500-1000: Kısa cevaplar
  - 1000-2000: Orta uzunluk
  - 2000+: Uzun içerik

## 🎯 AI Özellikler ve Kullanım Alanları

### 1. **Content Generation (İçerik Üretimi)**
- Eğitim materyalleri oluşturma
- Test soruları yazma
- Müfredat geliştirme
- **Önerilen Sağlayıcı**: OpenAI GPT-4

### 2. **Evaluation Insights (Değerlendirme Analizi)**
- Test sonuçlarını analiz etme
- Öğrenci performans raporları
- Gelişim önerileri
- **Önerilen Sağlayıcı**: Claude-3 Sonnet

### 3. **Chatbot (AI Asistan)**
- Öğrenci sorularını yanıtlama
- Rehberlik ve destek
- 7/24 yardım masası
- **Önerilen Sağlayıcı**: GPT-3.5-turbo

### 4. **Recommendations (Öneriler)**
- Kişiselleştirilmiş öğrenme yolları
- İlerleme önerileri
- Kaynak tavsiyeleri
- **Önerilen Sağlayıcı**: GPT-4

## 💰 Maliyet Yönetimi

### API Ücretlendirme (Tahmini)
- **OpenAI GPT-3.5**: $0.0015/1K token
- **OpenAI GPT-4**: $0.03/1K token
- **Claude-3 Haiku**: $0.00025/1K token
- **Claude-3 Sonnet**: $0.003/1K token
- **Local Models**: Ücretsiz (kendi donanımınız)

### Kullanım Takibi
- Aylık token limitleri ayarlayın
- Günlük kullanım raporlarını izleyin
- Maliyet uyarıları aktifleştirin

## 🔒 Güvenlik En İyi Uygulamaları

### 1. API Key Güvenliği
- API key'leri asla paylaşmayın
- Düzenli olarak rotate edin
- Environment variables kullanın
- Sadmin/Admin rolleri yönetebilir

### 2. Veri Gizliliği
- Kişisel bilgileri AI'ya göndermeyin
- GDPR/KVKK uyumluluğunu kontrol edin
- Veri maskeleme kullanın

### 3. Rate Limiting
- API limitlerini aşmayın
- Retry logic implementasyonu
- Graceful degradation

## 🛠️ Teknik Konfigürasyon

### Environment Variables
```bash
# .env dosyasına ekleyin
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
AI_ENABLED=true
AI_DEFAULT_PROVIDER=openai
AI_MAX_TOKENS_PER_REQUEST=1000
AI_MONTHLY_TOKEN_LIMIT=1000000
```

### Database Schema
```sql
-- AI settings tablosu
CREATE TABLE ai_settings (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    api_key_encrypted TEXT,
    model VARCHAR(100),
    temperature DECIMAL(3,2),
    max_tokens INTEGER,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI kullanım takibi
CREATE TABLE ai_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    provider VARCHAR(50),
    feature VARCHAR(50),
    tokens_used INTEGER,
    cost DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📊 Monitoring ve Analytics

### Usage Dashboard
- Günlük/aylık kullanım grafikler
- Özellik bazında dağılım
- Maliyet analizi
- Performans metrikleri

### Error Tracking
- API hata logları
- Response time monitoring
- Success/failure oranları

## 🚀 Production Deployment

### 1. Scaling Considerations
- Load balancing for AI requests
- Queue system for heavy tasks
- Caching for repeated queries

### 2. Backup Strategy
- AI settings backup
- Usage data export
- Configuration versioning

## 📞 Destek ve Sorun Giderme

### Yaygın Sorunlar
1. **API Key Invalid**: Key'i kontrol edin, yenileyin
2. **Rate Limit Exceeded**: Kullanım limitlerini artırın
3. **Connection Timeout**: Network ve firewall kontrol edin
4. **High Costs**: Token usage patterns analiz edin

### Log Files
- `/var/log/bdc/ai.log` - AI request logs
- `/var/log/bdc/error.log` - Error logs
- `/var/log/bdc/usage.log` - Usage tracking

### Support Channels
- GitHub Issues
- System Admin
- AI Provider Support (OpenAI, Anthropic)

---

**Not**: Bu konfigürasyon kılavuzu sürekli güncellenmektedir. Yeni AI sağlayıcıları ve özellikler eklendikçe dokümantasyon da güncellenecektir.