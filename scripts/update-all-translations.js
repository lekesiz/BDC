#!/usr/bin/env node

/**
 * Script to update all translation files with comprehensive keys
 * Maintains existing translations while adding new keys with English fallbacks
 */

const fs = require('fs').promises;
const path = require('path');

const LOCALES_DIR = path.join(__dirname, '../client/src/i18n/locales');
const LANGUAGES = ['tr', 'ar', 'es', 'fr', 'de', 'ru', 'he'];

// Translation mappings for common terms
const commonTranslations = {
  tr: {
    'common.welcome': 'Hoş geldiniz',
    'common.logout': 'Çıkış',
    'common.login': 'Giriş',
    'common.save': 'Kaydet',
    'common.cancel': 'İptal',
    'common.delete': 'Sil',
    'common.edit': 'Düzenle',
    'common.submit': 'Gönder',
    'common.search': 'Ara',
    'common.filter': 'Filtrele',
    'common.loading': 'Yükleniyor...',
    'common.error': 'Hata',
    'common.success': 'Başarılı',
    'common.yes': 'Evet',
    'common.no': 'Hayır',
    'navigation.dashboard': 'Kontrol Paneli',
    'navigation.beneficiaries': 'Yararlanıcılar',
    'navigation.programs': 'Programlar',
    'navigation.evaluations': 'Değerlendirmeler',
    'navigation.calendar': 'Takvim',
    'navigation.documents': 'Belgeler',
    'navigation.reports': 'Raporlar',
    'navigation.settings': 'Ayarlar',
    'navigation.users': 'Kullanıcılar',
    'navigation.profile': 'Profil',
    'auth.loginTitle': 'Giriş Yap',
    'auth.email': 'E-posta',
    'auth.password': 'Şifre',
    'auth.rememberMe': 'Beni hatırla',
    'auth.forgotPassword': 'Şifremi unuttum',
    'auth.signIn': 'Giriş Yap',
    'auth.signOut': 'Çıkış Yap',
    'auth.register': 'Kayıt Ol',
    'auth.loginError': 'Geçersiz e-posta veya şifre'
  },
  ar: {
    'common.welcome': 'مرحبا',
    'common.logout': 'تسجيل خروج',
    'common.login': 'تسجيل دخول',
    'common.save': 'حفظ',
    'common.cancel': 'إلغاء',
    'common.delete': 'حذف',
    'common.edit': 'تعديل',
    'common.submit': 'إرسال',
    'common.search': 'بحث',
    'common.filter': 'تصفية',
    'common.loading': 'جاري التحميل...',
    'common.error': 'خطأ',
    'common.success': 'نجاح',
    'common.yes': 'نعم',
    'common.no': 'لا',
    'navigation.dashboard': 'لوحة القيادة',
    'navigation.beneficiaries': 'المستفيدون',
    'navigation.programs': 'البرامج',
    'navigation.evaluations': 'التقييمات',
    'navigation.calendar': 'التقويم',
    'navigation.documents': 'المستندات',
    'navigation.reports': 'التقارير',
    'navigation.settings': 'الإعدادات',
    'navigation.users': 'المستخدمون',
    'navigation.profile': 'الملف الشخصي',
    'auth.loginTitle': 'تسجيل الدخول',
    'auth.email': 'البريد الإلكتروني',
    'auth.password': 'كلمة المرور',
    'auth.rememberMe': 'تذكرني',
    'auth.forgotPassword': 'نسيت كلمة المرور؟',
    'auth.signIn': 'تسجيل الدخول',
    'auth.signOut': 'تسجيل الخروج',
    'auth.register': 'التسجيل',
    'auth.loginError': 'البريد الإلكتروني أو كلمة المرور غير صحيحة'
  },
  es: {
    'common.welcome': 'Bienvenido',
    'common.logout': 'Cerrar sesión',
    'common.login': 'Iniciar sesión',
    'common.save': 'Guardar',
    'common.cancel': 'Cancelar',
    'common.delete': 'Eliminar',
    'common.edit': 'Editar',
    'common.submit': 'Enviar',
    'common.search': 'Buscar',
    'common.filter': 'Filtrar',
    'common.loading': 'Cargando...',
    'common.error': 'Error',
    'common.success': 'Éxito',
    'common.yes': 'Sí',
    'common.no': 'No',
    'navigation.dashboard': 'Panel de control',
    'navigation.beneficiaries': 'Beneficiarios',
    'navigation.programs': 'Programas',
    'navigation.evaluations': 'Evaluaciones',
    'navigation.calendar': 'Calendario',
    'navigation.documents': 'Documentos',
    'navigation.reports': 'Informes',
    'navigation.settings': 'Configuración',
    'navigation.users': 'Usuarios',
    'navigation.profile': 'Perfil',
    'auth.loginTitle': 'Iniciar sesión',
    'auth.email': 'Correo electrónico',
    'auth.password': 'Contraseña',
    'auth.rememberMe': 'Recuérdame',
    'auth.forgotPassword': '¿Olvidaste tu contraseña?',
    'auth.signIn': 'Iniciar sesión',
    'auth.signOut': 'Cerrar sesión',
    'auth.register': 'Registrarse',
    'auth.loginError': 'Correo o contraseña inválidos'
  },
  fr: {
    'common.welcome': 'Bienvenue',
    'common.logout': 'Déconnexion',
    'common.login': 'Connexion',
    'common.save': 'Enregistrer',
    'common.cancel': 'Annuler',
    'common.delete': 'Supprimer',
    'common.edit': 'Modifier',
    'common.submit': 'Soumettre',
    'common.search': 'Rechercher',
    'common.filter': 'Filtrer',
    'common.loading': 'Chargement...',
    'common.error': 'Erreur',
    'common.success': 'Succès',
    'common.yes': 'Oui',
    'common.no': 'Non',
    'navigation.dashboard': 'Tableau de bord',
    'navigation.beneficiaries': 'Bénéficiaires',
    'navigation.programs': 'Programmes',
    'navigation.evaluations': 'Évaluations',
    'navigation.calendar': 'Calendrier',
    'navigation.documents': 'Documents',
    'navigation.reports': 'Rapports',
    'navigation.settings': 'Paramètres',
    'navigation.users': 'Utilisateurs',
    'navigation.profile': 'Profil',
    'auth.loginTitle': 'Se connecter',
    'auth.email': 'Email',
    'auth.password': 'Mot de passe',
    'auth.rememberMe': 'Se souvenir de moi',
    'auth.forgotPassword': 'Mot de passe oublié?',
    'auth.signIn': 'Se connecter',
    'auth.signOut': 'Se déconnecter',
    'auth.register': "S'inscrire",
    'auth.loginError': 'Email ou mot de passe invalide'
  },
  de: {
    'common.welcome': 'Willkommen',
    'common.logout': 'Abmelden',
    'common.login': 'Anmelden',
    'common.save': 'Speichern',
    'common.cancel': 'Abbrechen',
    'common.delete': 'Löschen',
    'common.edit': 'Bearbeiten',
    'common.submit': 'Senden',
    'common.search': 'Suchen',
    'common.filter': 'Filtern',
    'common.loading': 'Wird geladen...',
    'common.error': 'Fehler',
    'common.success': 'Erfolg',
    'common.yes': 'Ja',
    'common.no': 'Nein',
    'navigation.dashboard': 'Dashboard',
    'navigation.beneficiaries': 'Begünstigte',
    'navigation.programs': 'Programme',
    'navigation.evaluations': 'Bewertungen',
    'navigation.calendar': 'Kalender',
    'navigation.documents': 'Dokumente',
    'navigation.reports': 'Berichte',
    'navigation.settings': 'Einstellungen',
    'navigation.users': 'Benutzer',
    'navigation.profile': 'Profil',
    'auth.loginTitle': 'Anmelden',
    'auth.email': 'E-Mail',
    'auth.password': 'Passwort',
    'auth.rememberMe': 'Angemeldet bleiben',
    'auth.forgotPassword': 'Passwort vergessen?',
    'auth.signIn': 'Anmelden',
    'auth.signOut': 'Abmelden',
    'auth.register': 'Registrieren',
    'auth.loginError': 'Ungültige E-Mail oder Passwort'
  },
  ru: {
    'common.welcome': 'Добро пожаловать',
    'common.logout': 'Выйти',
    'common.login': 'Войти',
    'common.save': 'Сохранить',
    'common.cancel': 'Отмена',
    'common.delete': 'Удалить',
    'common.edit': 'Редактировать',
    'common.submit': 'Отправить',
    'common.search': 'Поиск',
    'common.filter': 'Фильтр',
    'common.loading': 'Загрузка...',
    'common.error': 'Ошибка',
    'common.success': 'Успешно',
    'common.yes': 'Да',
    'common.no': 'Нет',
    'navigation.dashboard': 'Панель управления',
    'navigation.beneficiaries': 'Бенефициары',
    'navigation.programs': 'Программы',
    'navigation.evaluations': 'Оценки',
    'navigation.calendar': 'Календарь',
    'navigation.documents': 'Документы',
    'navigation.reports': 'Отчеты',
    'navigation.settings': 'Настройки',
    'navigation.users': 'Пользователи',
    'navigation.profile': 'Профиль',
    'auth.loginTitle': 'Вход',
    'auth.email': 'Электронная почта',
    'auth.password': 'Пароль',
    'auth.rememberMe': 'Запомнить меня',
    'auth.forgotPassword': 'Забыли пароль?',
    'auth.signIn': 'Войти',
    'auth.signOut': 'Выйти',
    'auth.register': 'Регистрация',
    'auth.loginError': 'Неверный email или пароль'
  },
  he: {
    'common.welcome': 'ברוך הבא',
    'common.logout': 'יציאה',
    'common.login': 'כניסה',
    'common.save': 'שמור',
    'common.cancel': 'ביטול',
    'common.delete': 'מחק',
    'common.edit': 'ערוך',
    'common.submit': 'שלח',
    'common.search': 'חיפוש',
    'common.filter': 'סנן',
    'common.loading': 'טוען...',
    'common.error': 'שגיאה',
    'common.success': 'הצלחה',
    'common.yes': 'כן',
    'common.no': 'לא',
    'navigation.dashboard': 'לוח בקרה',
    'navigation.beneficiaries': 'מוטבים',
    'navigation.programs': 'תוכניות',
    'navigation.evaluations': 'הערכות',
    'navigation.calendar': 'לוח שנה',
    'navigation.documents': 'מסמכים',
    'navigation.reports': 'דוחות',
    'navigation.settings': 'הגדרות',
    'navigation.users': 'משתמשים',
    'navigation.profile': 'פרופיל',
    'auth.loginTitle': 'התחברות',
    'auth.email': 'דואר אלקטרוני',
    'auth.password': 'סיסמה',
    'auth.rememberMe': 'זכור אותי',
    'auth.forgotPassword': 'שכחת סיסמה?',
    'auth.signIn': 'התחבר',
    'auth.signOut': 'התנתק',
    'auth.register': 'הרשמה',
    'auth.loginError': 'דואר אלקטרוני או סיסמה לא תקינים'
  }
};

/**
 * Deep merge two objects
 */
function deepMerge(target, source) {
  const output = Object.assign({}, target);
  if (isObject(target) && isObject(source)) {
    Object.keys(source).forEach(key => {
      if (isObject(source[key])) {
        if (!(key in target))
          Object.assign(output, { [key]: source[key] });
        else
          output[key] = deepMerge(target[key], source[key]);
      } else {
        Object.assign(output, { [key]: source[key] });
      }
    });
  }
  return output;
}

function isObject(item) {
  return item && typeof item === 'object' && !Array.isArray(item);
}

/**
 * Flatten nested object to dot notation
 */
function flattenObject(obj, prefix = '') {
  return Object.keys(obj).reduce((acc, k) => {
    const pre = prefix.length ? prefix + '.' : '';
    if (typeof obj[k] === 'object' && obj[k] !== null && !Array.isArray(obj[k])) {
      Object.assign(acc, flattenObject(obj[k], pre + k));
    } else {
      acc[pre + k] = obj[k];
    }
    return acc;
  }, {});
}

/**
 * Unflatten dot notation to nested object
 */
function unflattenObject(obj) {
  const result = {};
  for (const key in obj) {
    const keys = key.split('.');
    keys.reduce((acc, k, i) => {
      if (i === keys.length - 1) {
        acc[k] = obj[key];
      } else {
        acc[k] = acc[k] || {};
      }
      return acc[k];
    }, result);
  }
  return result;
}

/**
 * Apply known translations to a language
 */
function applyKnownTranslations(enFlat, lang) {
  const translations = commonTranslations[lang] || {};
  const result = { ...enFlat };
  
  Object.keys(translations).forEach(key => {
    if (key in result) {
      result[key] = translations[key];
    }
  });
  
  return result;
}

async function updateTranslations() {
  try {
    // Read English translations as the base
    const enPath = path.join(LOCALES_DIR, 'en.json');
    const enContent = await fs.readFile(enPath, 'utf8');
    const enTranslations = JSON.parse(enContent);
    const enFlat = flattenObject(enTranslations);
    
    console.log('Loaded English translations with', Object.keys(enFlat).length, 'keys');
    
    // Update each language file
    for (const lang of LANGUAGES) {
      const langPath = path.join(LOCALES_DIR, `${lang}.json`);
      
      try {
        // Read existing translations
        const existingContent = await fs.readFile(langPath, 'utf8');
        const existingTranslations = JSON.parse(existingContent);
        const existingFlat = flattenObject(existingTranslations);
        
        // Apply known translations
        const withKnownTranslations = applyKnownTranslations(enFlat, lang);
        
        // Merge with existing translations (existing takes precedence)
        const mergedFlat = { ...withKnownTranslations, ...existingFlat };
        
        // Convert back to nested structure
        const mergedNested = unflattenObject(mergedFlat);
        
        // Write updated translations
        await fs.writeFile(langPath, JSON.stringify(mergedNested, null, 2));
        
        const existingCount = Object.keys(existingFlat).length;
        const newCount = Object.keys(mergedFlat).length;
        const addedCount = newCount - existingCount;
        
        console.log(`✓ Updated ${lang}.json: ${existingCount} → ${newCount} keys (+${addedCount})`);
      } catch (error) {
        console.error(`✗ Error updating ${lang}.json:`, error.message);
      }
    }
    
    console.log('\nTranslation update complete!');
    
    // Generate translation status report
    console.log('\nTranslation Coverage Report:');
    console.log('===========================');
    
    for (const lang of LANGUAGES) {
      const langPath = path.join(LOCALES_DIR, `${lang}.json`);
      const langContent = await fs.readFile(langPath, 'utf8');
      const langTranslations = JSON.parse(langContent);
      const langFlat = flattenObject(langTranslations);
      
      const totalKeys = Object.keys(enFlat).length;
      const translatedKeys = Object.keys(langFlat).filter(key => 
        langFlat[key] !== enFlat[key]
      ).length;
      
      const percentage = ((translatedKeys / totalKeys) * 100).toFixed(1);
      console.log(`${lang}: ${translatedKeys}/${totalKeys} (${percentage}%)`);
    }
    
  } catch (error) {
    console.error('Error updating translations:', error);
    process.exit(1);
  }
}

// Run the update
updateTranslations();