// TODO: i18n - processed
import { useTranslation } from "react-i18next"; /**
 * Quick Mock Data for All Remaining Components
 * Comprehensive demo data for testing all pages
 */
// Documents Mock Data
export const mockDocuments = Array.from({ length: 30 }, (_, i) => ({
  id: i + 1,
  name: [
  'Kimlik Belgesi', 'Diploma', 'CV', 'Sertifika', 'Transkript',
  'İş Deneyimi Belgesi', 'Dil Belgesi', 'Proje Raporu', 'Sunum',
  'Değerlendirme Formu', 'Katılım Belgesi', 'Başvuru Formu'][
  Math.floor(Math.random() * 12)],
  type: ['pdf', 'doc', 'docx', 'jpg', 'png', 'xlsx'][Math.floor(Math.random() * 6)],
  size: Math.floor(Math.random() * 5000) + 100, // KB
  uploadDate: new Date(Date.now() - Math.floor(Math.random() * 90) * 24 * 60 * 60 * 1000).toISOString(),
  status: ['approved', 'pending', 'rejected'][Math.floor(Math.random() * 3)],
  category: ['identity', 'education', 'employment', 'assessment', 'other'][Math.floor(Math.random() * 5)],
  uploadedBy: {
    id: Math.floor(Math.random() * 10) + 1,
    name: 'Ahmet Yılmaz',
    role: 'student'
  },
  url: `/documents/${i + 1}.pdf`,
  downloadCount: Math.floor(Math.random() * 50),
  isPublic: Math.random() > 0.7,
  tags: ['Önemli', 'Arşiv', 'Güncel'].filter(() => Math.random() > 0.7)
}));
// Programs Mock Data
export const mockPrograms = Array.from({ length: 15 }, (_, i) => ({
  id: i + 1,
  title: [
  'Dijital Beceriler Geliştirme', 'Mesleki İngilizce', 'Girişimcilik Eğitimi',
  'Proje Yönetimi', 'Grafik Tasarım', 'Web Geliştirme', 'Veri Analizi',
  'Pazarlama ve Satış', 'İnsan Kaynakları', 'Muhasebe ve Finans',
  'Liderlik Becerileri', 'İletişim Teknikleri', 'Yaratıcı Düşünce',
  'Problem Çözme', 'Takım Çalışması'][
  i],
  description: 'Bu program katılımcıların mesleki becerilerini geliştirmeyi amaçlamaktadır.',
  duration: Math.floor(Math.random() * 12) + 3, // 3-15 months
  level: ['Başlangıç', 'Orta', 'İleri'][Math.floor(Math.random() * 3)],
  category: ['Teknik', 'İş Becerileri', 'Kişisel Gelişim'][Math.floor(Math.random() * 3)],
  startDate: new Date(2024, Math.floor(Math.random() * 12), 1).toISOString().split('T')[0],
  endDate: new Date(2024, Math.floor(Math.random() * 12) + 6, 28).toISOString().split('T')[0],
  enrollmentCount: Math.floor(Math.random() * 50) + 10,
  maxCapacity: Math.floor(Math.random() * 30) + 50,
  status: ['active', 'upcoming', 'completed'][Math.floor(Math.random() * 3)],
  instructors: [
  { id: 1, name: 'Ahmet Yılmaz', email: 'trainer1@bdc.com' },
  { id: 2, name: 'Ayşe Demir', email: 'trainer2@bdc.com' }].
  slice(0, Math.floor(Math.random() * 2) + 1),
  modules: Array.from({ length: Math.floor(Math.random() * 6) + 4 }, (_, j) => ({
    id: j + 1,
    title: `Modül ${j + 1}`,
    description: 'Modül açıklaması',
    duration: '2 hafta',
    status: ['completed', 'active', 'upcoming'][Math.floor(Math.random() * 3)]
  }))
}));
// Calendar/Events Mock Data
export const mockEvents = Array.from({ length: 20 }, (_, i) => ({
  id: i + 1,
  title: [
  'Matematik Dersi', 'İngilizce Sınavı', 'Proje Sunumu', 'Bireysel Görüşme',
  'Grup Çalışması', 'Vaka Analizi', 'Workshop', 'Seminer', 'Eğitim',
  'Değerlendirme Toplantısı'][
  Math.floor(Math.random() * 10)],
  start: new Date(Date.now() + (Math.floor(Math.random() * 30) - 15) * 24 * 60 * 60 * 1000).toISOString(),
  end: new Date(Date.now() + (Math.floor(Math.random() * 30) - 15) * 24 * 60 * 60 * 1000 + 2 * 60 * 60 * 1000).toISOString(),
  type: ['class', 'exam', 'meeting', 'workshop'][Math.floor(Math.random() * 4)],
  location: ['A101', 'B205', 'Online', 'Konferans Salonu'][Math.floor(Math.random() * 4)],
  attendees: Math.floor(Math.random() * 25) + 5,
  instructor: 'Ahmet Yılmaz',
  description: 'Etkinlik açıklaması buraya gelecek.',
  status: ['scheduled', 'ongoing', 'completed', 'cancelled'][Math.floor(Math.random() * 4)]
}));
// Messages Mock Data
export const mockMessages = Array.from({ length: 25 }, (_, i) => ({
  id: i + 1,
  from: {
    id: Math.floor(Math.random() * 10) + 1,
    name: ['Ahmet Yılmaz', 'Ayşe Demir', 'Mehmet Kaya', 'Fatma Şahin'][Math.floor(Math.random() * 4)],
    avatar: `https://i.pravatar.cc/50?u=${i}`
  },
  to: {
    id: Math.floor(Math.random() * 10) + 1,
    name: 'Mevcut Kullanıcı'
  },
  subject: [
  'Ders programı hakkında', 'Sınav tarihi', 'Proje teslimi', 'Devamsızlık durumu',
  'Başarı durumu', 'Yardım talebi', 'Toplantı daveti', 'Duyuru'][
  Math.floor(Math.random() * 8)],
  content: 'Merhaba, bu mesaj demo amaçlı oluşturulmuştur. Gerçek bir mesaj içeriği burada yer alacaktır.',
  timestamp: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
  isRead: Math.random() > 0.3,
  isImportant: Math.random() > 0.8,
  hasAttachment: Math.random() > 0.7,
  type: ['inbox', 'sent', 'draft'][Math.floor(Math.random() * 3)]
}));
// Notifications Mock Data
export const mockNotifications = Array.from({ length: 15 }, (_, i) => ({
  id: i + 1,
  title: [
  'Yeni sınav atandı', 'Ders iptali', 'Not güncellendi', 'Mesaj alındı',
  'Toplantı hatırlatması', 'Başvuru onaylandı', 'Belge yüklendi',
  'Sistem güncellemesi'][
  Math.floor(Math.random() * 8)],
  message: 'Bu bir demo bildirimidir. Gerçek bildirim içeriği burada yer alacaktır.',
  type: ['info', 'success', 'warning', 'error'][Math.floor(Math.random() * 4)],
  timestamp: new Date(Date.now() - Math.floor(Math.random() * 7) * 24 * 60 * 60 * 1000).toISOString(),
  isRead: Math.random() > 0.4,
  actionUrl: Math.random() > 0.5 ? '/evaluations' : null,
  icon: ['📚', '✅', '⚠️', '📧', '📅'][Math.floor(Math.random() * 5)]
}));
// Analytics Mock Data
export const mockAnalytics = {
  overview: {
    totalStudents: 150,
    activePrograms: 12,
    completedEvaluations: 340,
    averageScore: 78.5,
    growthRate: 12.5
  },
  charts: {
    enrollmentTrend: Array.from({ length: 12 }, (_, i) => ({
      month: ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara'][i],
      enrollments: Math.floor(Math.random() * 50) + 20
    })),
    scoreDistribution: Array.from({ length: 5 }, (_, i) => ({
      range: ['0-20', '21-40', '41-60', '61-80', '81-100'][i],
      count: Math.floor(Math.random() * 30) + 10
    })),
    programPopularity: mockPrograms.slice(0, 5).map((p) => ({
      name: p.title,
      enrollments: p.enrollmentCount
    }))
  }
};
// Reports Mock Data
export const mockReports = Array.from({ length: 10 }, (_, i) => ({
  id: i + 1,
  title: [
  'Aylık Başarı Raporu', 'Program Değerlendirme Raporu', 'Öğrenci İlerleme Raporu',
  'Katılım Analizi', 'Performans Özeti', 'Trend Analizi'][
  Math.floor(Math.random() * 6)],
  type: ['monthly', 'quarterly', 'annual', 'custom'][Math.floor(Math.random() * 4)],
  status: ['generating', 'completed', 'failed'][Math.floor(Math.random() * 3)],
  createdAt: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
  createdBy: 'System Admin',
  fileSize: Math.floor(Math.random() * 1000) + 100, // KB
  downloadUrl: `/reports/report-${i + 1}.pdf`,
  parameters: {
    dateRange: '2024-01-01 to 2024-12-31',
    programs: ['All Programs'],
    metrics: ['Enrollment', 'Completion', 'Scores']
  }
}));
// Settings Mock Data
export const mockSettings = {
  general: {
    siteName: 'BDC Management System',
    siteDescription: 'Beneficiary Development Center',
    language: 'tr',
    timezone: 'Europe/Istanbul',
    dateFormat: 'DD/MM/YYYY',
    currency: 'TRY'
  },
  notifications: {
    emailNotifications: true,
    pushNotifications: false,
    smsNotifications: false,
    weeklyReports: true,
    systemUpdates: true
  },
  security: {
    twoFactorAuth: false,
    sessionTimeout: 30, // minutes
    passwordExpiry: 90, // days
    loginAttempts: 5
  },
  appearance: {
    theme: 'light',
    primaryColor: '#3B82F6',
    fontSize: 'medium',
    sidebar: 'expanded'
  }
};
// Quick setup function for all mock APIs
export const setupQuickMockAPIs = (api, originalGet, originalPost, originalPut, originalDelete) => {
  const get = originalGet || api.get;
  const post = originalPost || api.post;
  const put = originalPut || api.put;
  const del = originalDelete || api.delete;
  // Documents API
  const originalGetMethod = api.get;
  api.get = function (url, config) {
    if (url.includes('/api/documents')) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({ data: { documents: mockDocuments, total: mockDocuments.length } });
        }, 300);
      });
    }
    if (url.includes('/api/programs')) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({ data: { programs: mockPrograms, total: mockPrograms.length } });
        }, 300);
      });
    }
    if (url.includes('/api/calendar') || url.includes('/api/events')) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({ data: { events: mockEvents, total: mockEvents.length } });
        }, 300);
      });
    }
    if (url.includes('/api/messages')) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({ data: { messages: mockMessages, total: mockMessages.length } });
        }, 300);
      });
    }
    if (url.includes('/api/notifications')) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({ data: { notifications: mockNotifications, total: mockNotifications.length } });
        }, 300);
      });
    }
    if (url.includes('/api/analytics')) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({ data: mockAnalytics });
        }, 300);
      });
    }
    if (url.includes('/api/reports')) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({ data: { reports: mockReports, total: mockReports.length } });
        }, 300);
      });
    }
    if (url.includes('/api/settings')) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({ data: mockSettings });
        }, 300);
      });
    }
    return originalGetMethod.call(this, url, config);
  };
};