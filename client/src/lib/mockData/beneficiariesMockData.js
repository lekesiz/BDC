// TODO: i18n - processed
import { useTranslation } from "react-i18next"; /**
 * Comprehensive Beneficiaries Mock Data for Demo and Testing
 */
// Status options
export const BENEFICIARY_STATUS = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  PENDING: 'pending',
  GRADUATED: 'graduated',
  DROPPED_OUT: 'dropped_out'
};
// Program types
export const PROGRAM_TYPES = {
  VOCATIONAL: 'vocational',
  ACADEMIC: 'academic',
  LANGUAGE: 'language',
  DIGITAL_SKILLS: 'digital_skills',
  ENTREPRENEURSHIP: 'entrepreneurship',
  LIFE_SKILLS: 'life_skills'
};
// Generate realistic Turkish names
const firstNames = [
'Ahmet', 'Mehmet', 'Mustafa', 'Ali', 'Hüseyin', 'İbrahim', 'İsmail', 'Süleyman', 'Ömer', 'Yusuf',
'Fatma', 'Ayşe', 'Emine', 'Hatice', 'Zeynep', 'Elif', 'Meryem', 'Büşra', 'Esra', 'Seda',
'Emre', 'Burak', 'Serkan', 'Oğuz', 'Deniz', 'Kaan', 'Arda', 'Berk', 'Efe', 'Kerem',
'Selin', 'Ceren', 'Defne', 'Derin', 'İpek', 'Nil', 'Pınar', 'Ezgi', 'Gizem', 'Melis'];

const lastNames = [
'Yılmaz', 'Kaya', 'Demir', 'Şahin', 'Çelik', 'Yıldız', 'Yıldırım', 'Öztürk', 'Aydin', 'Özdemir',
'Arslan', 'Doğan', 'Kilic', 'Aslan', 'Çetin', 'Kara', 'Koç', 'Kurt', 'Özkan', 'Şimşek',
'Erdoğan', 'Güler', 'Türk', 'Uçar', 'Acar', 'Polat', 'Korkmaz', 'Bulut', 'Güneş', 'Ak'];

const cities = [
'İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya', 'Adana', 'Konya', 'Gaziantep', 'Mersin', 'Diyarbakır',
'Kayseri', 'Eskişehir', 'Urfa', 'Malatya', 'Erzurum', 'Van', 'Batman', 'Elazığ', 'Trabzon', 'Samsun'];

const skills = [
'Microsoft Office', 'İngilizce', 'Almanca', 'Fransızca', 'Muhasebe', 'Grafik Tasarım', 'Web Tasarım',
'Pazarlama', 'Satış', 'Müşteri Hizmetleri', 'Proje Yönetimi', 'Veri Analizi', 'Sosyal Medya',
'Fotoğrafçılık', 'Video Editing', 'Çeviri', 'Öğretmenlik', 'Hemşirelik', 'Aşçılık', 'Berberlik',
'Elektrik', 'Tesisatçılık', 'Marangozluk', 'Kaynakçılık', 'Dikış-Terzilik', 'Kuaförlük', 'Estetisyenlik'];

const interests = [
'Teknoloji', 'Sanat', 'Müzik', 'Spor', 'Okuma', 'Yazma', 'Seyahat', 'Fotoğrafçılık', 'Sinema',
'Tiyatro', 'Dans', 'Resim', 'El Sanatları', 'Bahçıvanlık', 'Yemek Yapma', 'Dil Öğrenme',
'Gönüllü Çalışma', 'Çevre', 'Eğitim', 'Sağlık', 'Sosyal Medya', 'Oyun', 'Müzecilik'];

// Generate random beneficiary
export const generateBeneficiary = (id) => {
  const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
  const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
  const city = cities[Math.floor(Math.random() * cities.length)];
  const age = 18 + Math.floor(Math.random() * 47); // 18-65 yaş arası
  const phone = `0${Math.floor(Math.random() * 900000000) + 100000000}`;
  const email = `${firstName.toLowerCase()}.${lastName.toLowerCase()}@example.com`;
  // Random skills (1-5 tane)
  const numSkills = 1 + Math.floor(Math.random() * 5);
  const userSkills = [];
  for (let i = 0; i < numSkills; i++) {
    const skill = skills[Math.floor(Math.random() * skills.length)];
    if (!userSkills.includes(skill)) {
      userSkills.push(skill);
    }
  }
  // Random interests (1-4 tane)
  const numInterests = 1 + Math.floor(Math.random() * 4);
  const userInterests = [];
  for (let i = 0; i < numInterests; i++) {
    const interest = interests[Math.floor(Math.random() * interests.length)];
    if (!userInterests.includes(interest)) {
      userInterests.push(interest);
    }
  }
  const statuses = Object.values(BENEFICIARY_STATUS);
  const status = statuses[Math.floor(Math.random() * statuses.length)];
  const programs = Object.values(PROGRAM_TYPES);
  const currentProgram = programs[Math.floor(Math.random() * programs.length)];
  const createdDate = new Date(2024, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28));
  const lastActive = new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000);
  return {
    id,
    personalInfo: {
      firstName,
      lastName,
      fullName: `${firstName} ${lastName}`,
      email,
      phone,
      dateOfBirth: new Date(1958 + Math.floor(Math.random() * 47), Math.floor(Math.random() * 12), Math.floor(Math.random() * 28)).toISOString().split('T')[0],
      age,
      gender: Math.random() > 0.5 ? 'Kadın' : 'Erkek',
      nationality: 'Türk',
      idNumber: `${Math.floor(Math.random() * 90000000000) + 10000000000}`,
      profilePhoto: `https://i.pravatar.cc/150?u=${id}`
    },
    contactInfo: {
      address: `${Math.floor(Math.random() * 999) + 1}. Sokak No:${Math.floor(Math.random() * 99) + 1}`,
      district: `${Math.floor(Math.random() * 20) + 1}. İlçe`,
      city,
      postalCode: `${Math.floor(Math.random() * 90000) + 10000}`,
      emergencyContact: {
        name: firstNames[Math.floor(Math.random() * firstNames.length)] + ' ' + lastNames[Math.floor(Math.random() * lastNames.length)],
        relationship: ['Anne', 'Baba', 'Eş', 'Kardeş', 'Çocuk'][Math.floor(Math.random() * 5)],
        phone: `0${Math.floor(Math.random() * 900000000) + 100000000}`
      }
    },
    educationInfo: {
      highestDegree: ['İlkokul', 'Ortaokul', 'Lise', 'Ön Lisans', 'Lisans', 'Yüksek Lisans'][Math.floor(Math.random() * 6)],
      university: Math.random() > 0.5 ? ['İstanbul Üniversitesi', 'Ankara Üniversitesi', 'İzmir Üniversitesi', 'Bursa Üniversitesi'][Math.floor(Math.random() * 4)] : null,
      graduationYear: Math.random() > 0.3 ? 2000 + Math.floor(Math.random() * 24) : null,
      gpa: Math.random() > 0.5 ? (2.0 + Math.random() * 2).toFixed(2) : null,
      languages: ['Türkçe', ...(Math.random() > 0.6 ? ['İngilizce'] : []), ...(Math.random() > 0.8 ? ['Almanca'] : [])]
    },
    employmentInfo: {
      currentStatus: ['Çalışıyor', 'İşsiz', 'Öğrenci', 'Emekli', 'Ev Hanımı'][Math.floor(Math.random() * 5)],
      previousJobs: [
      {
        company: `${lastNames[Math.floor(Math.random() * lastNames.length)]} Ltd. Şti.`,
        position: ['Uzman', 'Asistan', 'Müdür', 'Tekniker', 'Operatör'][Math.floor(Math.random() * 5)],
        duration: `${1 + Math.floor(Math.random() * 5)} yıl`,
        startDate: '2020-01-15',
        endDate: Math.random() > 0.5 ? '2023-06-30' : null
      }],

      skills: userSkills,
      desiredField: currentProgram,
      salaryExpectation: 3000 + Math.floor(Math.random() * 7000) + ' TL'
    },
    programInfo: {
      currentProgram,
      enrollmentDate: createdDate.toISOString().split('T')[0],
      expectedGraduation: new Date(createdDate.getTime() + (6 + Math.floor(Math.random() * 18)) * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      progress: Math.floor(Math.random() * 100),
      attendance: 75 + Math.floor(Math.random() * 25), // 75-100%
      gpa: (2.5 + Math.random() * 1.5).toFixed(2),
      credits: {
        completed: Math.floor(Math.random() * 120),
        total: 120 + Math.floor(Math.random() * 60)
      },
      status: status
    },
    assessmentInfo: {
      totalAssessments: Math.floor(Math.random() * 15) + 5,
      completedAssessments: Math.floor(Math.random() * 12) + 3,
      averageScore: (60 + Math.random() * 35).toFixed(1),
      lastAssessment: {
        date: lastActive.toISOString().split('T')[0],
        score: (50 + Math.random() * 45).toFixed(1),
        subject: ['Genel Yetenek', 'Mesleki Bilgi', 'İngilizce', 'Bilgisayar'][Math.floor(Math.random() * 4)]
      },
      strengths: userSkills.slice(0, 3),
      weaknesses: ['Zaman Yönetimi', 'Stres Yönetimi', 'İletişim', 'Teknik Bilgi'][Math.floor(Math.random() * 4)]
    },
    socialInfo: {
      maritalStatus: ['Bekar', 'Evli', 'Boşanmış', 'Dul'][Math.floor(Math.random() * 4)],
      children: Math.floor(Math.random() * 4),
      householdSize: 1 + Math.floor(Math.random() * 6),
      monthlyIncome: 2000 + Math.floor(Math.random() * 8000) + ' TL',
      hasDisability: Math.random() > 0.9,
      veteranStatus: Math.random() > 0.95,
      interests: userInterests
    },
    notes: [
    {
      id: 1,
      date: lastActive.toISOString().split('T')[0],
      author: 'Ahmet Yılmaz',
      content: 'Öğrenci derse düzenli katılıyor ve başarılı. İletişim becerileri geliştirilmeli.',
      type: 'progress'
    },
    {
      id: 2,
      date: new Date(lastActive.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      author: 'Ayşe Demir',
      content: 'Teknik konularda yardıma ihtiyaç duyuyor. Ek destek sağlanacak.',
      type: 'support'
    }],

    documents: [
    { id: 1, name: 'Kimlik Fotokopisi', type: 'identity', uploadDate: createdDate.toISOString().split('T')[0], status: 'approved' },
    { id: 2, name: 'Diploma', type: 'education', uploadDate: createdDate.toISOString().split('T')[0], status: 'approved' },
    { id: 3, name: 'CV', type: 'employment', uploadDate: lastActive.toISOString().split('T')[0], status: 'pending' }],

    metadata: {
      createdAt: createdDate.toISOString(),
      updatedAt: lastActive.toISOString(),
      lastLogin: lastActive.toISOString(),
      source: ['Website', 'Referral', 'Social Media', 'Walk-in'][Math.floor(Math.random() * 4)],
      tags: ['Aktif', ...(Math.random() > 0.7 ? ['Öncelikli'] : []), ...(Math.random() > 0.8 ? ['Risk Altında'] : [])],
      assignedTrainer: {
        id: Math.floor(Math.random() * 10) + 1,
        name: `${firstNames[Math.floor(Math.random() * firstNames.length)]} ${lastNames[Math.floor(Math.random() * lastNames.length)]}`,
        email: 'trainer@bdc.com'
      }
    }
  };
};
// Generate array of beneficiaries
export const generateBeneficiaries = (count = 50) => {
  const beneficiaries = [];
  for (let i = 1; i <= count; i++) {
    beneficiaries.push(generateBeneficiary(i));
  }
  return beneficiaries;
};
// Sample data with 50 beneficiaries
export const mockBeneficiaries = generateBeneficiaries(50);
// Statistics derived from mock data
export const beneficiaryStats = {
  total: mockBeneficiaries.length,
  active: mockBeneficiaries.filter((b) => b.programInfo.status === 'active').length,
  graduated: mockBeneficiaries.filter((b) => b.programInfo.status === 'graduated').length,
  pending: mockBeneficiaries.filter((b) => b.programInfo.status === 'pending').length,
  averageAge: Math.round(mockBeneficiaries.reduce((sum, b) => sum + b.personalInfo.age, 0) / mockBeneficiaries.length),
  averageProgress: Math.round(mockBeneficiaries.reduce((sum, b) => sum + b.programInfo.progress, 0) / mockBeneficiaries.length),
  programDistribution: {
    vocational: mockBeneficiaries.filter((b) => b.programInfo.currentProgram === 'vocational').length,
    academic: mockBeneficiaries.filter((b) => b.programInfo.currentProgram === 'academic').length,
    language: mockBeneficiaries.filter((b) => b.programInfo.currentProgram === 'language').length,
    digital_skills: mockBeneficiaries.filter((b) => b.programInfo.currentProgram === 'digital_skills').length,
    entrepreneurship: mockBeneficiaries.filter((b) => b.programInfo.currentProgram === 'entrepreneurship').length,
    life_skills: mockBeneficiaries.filter((b) => b.programInfo.currentProgram === 'life_skills').length
  }
};
export default mockBeneficiaries;