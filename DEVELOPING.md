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

## Realtime İşlevsellik (WebSocket/Socket.IO)

BDC, anlık güncellemeler için Socket.IO tabanlı gerçek zamanlı bildirim sistemi kullanır:

### Backend İmplementasyonu
- `app/socketio_events.py`: Temel Socket.IO olay işleyicileri
- `app/websocket_notifications.py`: Bildirim özel WebSocket işlevleri

### Frontend İmplementasyonu
- `src/contexts/SocketContext.jsx`: Socket.IO bağlantı yönetimi
- `src/providers/NotificationProviderV2.jsx`: Bildirim sistemi

### Desteklenen Olaylar
- `program_created`: Yeni program oluşturulduğunda
- `program_updated`: Program güncellendiğinde
- `program_deleted`: Program silindiğinde
- `notification`: Genel bildirimler için
- `user_joined`: Kullanıcı bağlandığında
- `user_left`: Kullanıcı ayrıldığında
- `message`: Mesajlaşma için

### Nasıl Kullanılır
```jsx
import { useSocket } from '@/contexts/SocketContext';

function MyComponent() {
  const { on, emit } = useSocket();
  
  useEffect(() => {
    // Olay dinleyici ekle
    const cleanup = on('program_updated', (data) => {
      // Program güncellendiğinde state güncelle
      setProgram(data.program);
    });
    
    // Temizleme
    return cleanup;
  }, [on]);
  
  // Olay gönderme
  const sendMessage = () => {
    emit('send_message', { room: 'general', message: 'Merhaba!' });
  };
  
  return <div>...</div>;
}
```

### WebSocket Test Stratejisi

WebSocket işlevselliğini test etmek için aşağıdaki yaklaşımları kullanın:

```jsx
// Örnek WebSocket testi (src/test/websocket/ProgramWebSocket.test.jsx)
import { describe, it, expect, vi } from 'vitest';
import { render, waitFor } from '@testing-library/react';

describe('WebSocket Entegrasyon Testi', () => {
  // Mock socket
  const mockSocket = {
    connected: true,
    on: vi.fn(),
    off: vi.fn(),
    emit: vi.fn()
  };
  
  // Mock handler kaydı
  const savedHandlers = {};
  
  // socket.on mock işlevi ile handler'ları kaydet
  mockSocket.on.mockImplementation((event, handler) => {
    savedHandlers[event] = handler;
    return () => {};
  });
  
  it('program_created olayını doğru işlemeli', async () => {
    // Handler kaydet
    const handler = vi.fn();
    mockSocket.on('program_created', handler);
    
    // Olayı tetikle
    const newProgram = { id: 123, name: 'Test Program' };
    savedHandlers.program_created({ program: newProgram });
    
    // Handler'ın doğru veri ile çağrıldığını doğrula
    expect(handler).toHaveBeenCalledWith({ program: newProgram });
  });
});
```

WebSocket testlerinde dikkat edilmesi gerekenler:
1. Socket.IO istemcisini mock'layın
2. Olay kayıtlarını ve işleyicileri takip edin
3. Gerçek zamanlı güncellemeleri simüle etmek için olayları manuel tetikleyin
4. Bileşenlerin bu olaylara uygun şekilde yanıt verdiğini doğrulayın

## Pull Request Checklist
- [ ] Tüm backend & frontend testleri yeşil.
- [ ] Coverage eşiği aşılmış.
- [ ] Pre-commit hook hatasız.
- [ ] Gerekli dokümantasyon güncellendi.
- [ ] WebSocket testleri eklendi (gerçek zamanlı özellikler için).