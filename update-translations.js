const fs = require('fs');
const path = require('path');

// Read the new translations from en.json
const enPath = path.join(__dirname, 'client/src/i18n/locales/en.json');
const enTranslations = JSON.parse(fs.readFileSync(enPath, 'utf8'));

// Language files to update
const languages = {
  es: {
    settings: {
      ai: {
        title: "Configuración de IA",
        subtitle: "Configurar proveedores de IA y claves API para funciones inteligentes",
        providers: {
          openai: {
            name: "OpenAI",
            description: "Modelos GPT para generación y análisis de texto",
            apiKey: "Clave API",
            apiKeyPlaceholder: "sk-...",
            getApiKey: "Obtén tu clave API de",
            platform: "Plataforma OpenAI",
            model: "Modelo",
            models: {
              gpt4: "GPT-4",
              gpt4Turbo: "GPT-4 Turbo",
              gpt35Turbo: "GPT-3.5 Turbo"
            },
            temperature: "Temperatura",
            maxTokens: "Tokens Máximos"
          },
          anthropic: {
            name: "Anthropic Claude",
            description: "Asistente de IA avanzado para tareas complejas",
            apiKey: "Clave API",
            apiKeyPlaceholder: "sk-ant-...",
            getApiKey: "Obtén tu clave API de",
            platform: "Consola Anthropic",
            model: "Modelo",
            models: {
              claude3Opus: "Claude 3 Opus",
              claude3Sonnet: "Claude 3 Sonnet",
              claude3Haiku: "Claude 3 Haiku",
              claude21: "Claude 2.1"
            }
          },
          google: {
            name: "Google AI",
            description: "Modelos Gemini para tareas de IA multimodal",
            apiKey: "Clave API",
            apiKeyPlaceholder: "AIza...",
            getApiKey: "Obtén tu clave API de",
            platform: "Google AI Studio",
            model: "Modelo",
            models: {
              geminiPro: "Gemini Pro",
              geminiProVision: "Gemini Pro Vision"
            }
          }
        },
        customEndpoints: {
          title: "Endpoints de IA Personalizados",
          description: "Agregar endpoints de IA personalizados para modelos especializados",
          namePlaceholder: "Nombre del endpoint",
          urlPlaceholder: "URL del endpoint",
          apiKeyPlaceholder: "Clave API (opcional)",
          addEndpoint: "Agregar Endpoint"
        },
        features: {
          title: "Funciones de IA",
          description: "Configurar qué funciones de IA están habilitadas",
          evaluationAnalysis: "Habilitar análisis de evaluación con IA",
          recommendations: "Habilitar recomendaciones de IA",
          contentGeneration: "Habilitar generación de contenido con IA",
          chatbotAssistance: "Habilitar asistencia de chatbot con IA"
        },
        actions: {
          test: "Probar",
          save: "Guardar Configuración"
        },
        messages: {
          saveSuccess: "La configuración de IA se ha actualizado correctamente",
          saveFailed: "Error al guardar la configuración de IA",
          connectionSuccess: "Conectado exitosamente a la API de {{provider}}",
          connectionFailed: "Error al conectar con la API de {{provider}}"
        }
      },
      page: {
        title: "Configuración",
        accountSettings: "Configuración de Cuenta",
        accountSettingsDescription: "Administra tus preferencias y configuración de cuenta",
        tabs: {
          notifications: "Notificaciones",
          privacy: "Privacidad",
          preferences: "Preferencias",
          ai: "IA",
          integrations: "Integraciones"
        },
        notifications: {
          email: {
            title: "Notificaciones por Email",
            description: "Recibir notificaciones por email para actualizaciones importantes",
            marketing: "Emails de Marketing",
            marketingDescription: "Recibir emails sobre nuevas funciones y ofertas"
          },
          push: {
            title: "Notificaciones Push",
            description: "Recibir notificaciones push en tu navegador",
            newMessages: "Nuevos Mensajes",
            newMessagesDescription: "Recibir notificaciones cuando recibas nuevos mensajes",
            sessionReminders: "Recordatorios de Sesión",
            sessionRemindersDescription: "Recibir recordatorios para próximas sesiones",
            evaluationResults: "Resultados de Evaluación",
            evaluationResultsDescription: "Recibir notificaciones cuando tus resultados de evaluación estén listos"
          },
          sms: {
            title: "Notificaciones SMS",
            description: "Recibir notificaciones por mensaje de texto (pueden aplicar cargos del operador)"
          },
          saveButton: "Guardar Configuración de Notificaciones"
        },
        privacy: {
          title: "Configuración de Privacidad",
          profileVisibility: {
            title: "Visibilidad del Perfil",
            description: "Controla quién puede ver tu información de perfil",
            everyone: "Todos",
            connections: "Solo conexiones",
            private: "Privado"
          },
          onlineStatus: {
            title: "Mostrar Estado En Línea",
            description: "Permitir que otros vean cuando estás en línea"
          },
          activitySharing: {
            title: "Compartir Actividad",
            description: "Compartir tu progreso de aprendizaje y logros"
          },
          dataCollection: {
            title: "Recopilación de Datos",
            allowCollection: "Permitir Recopilación de Datos",
            description: "Ayúdanos a mejorar nuestra plataforma compartiendo datos de uso"
          },
          dataPrivacyNotice: {
            title: "Privacidad de Datos",
            message: "Tus datos siempre están protegidos y nunca se comparten con terceros sin tu consentimiento.",
            privacyPolicyLink: "Política de Privacidad"
          },
          saveButton: "Guardar Configuración de Privacidad"
        },
        preferences: {
          appearance: {
            title: "Apariencia",
            theme: {
              title: "Tema",
              description: "Elige tu tema preferido",
              light: "Claro",
              dark: "Oscuro",
              system: "Sistema"
            }
          },
          language: {
            title: "Idioma",
            displayLanguage: "Idioma de Visualización",
            description: "Elige tu idioma preferido para la interfaz"
          },
          themeSupport: {
            title: "Soporte de Tema",
            message: "La configuración de tema está actualmente en beta y puede no aplicarse a todas las partes de la aplicación."
          },
          saveButton: "Guardar Preferencias"
        },
        integrations: {
          title: "Integraciones de Servicios Externos",
          description: "Configurar conexiones a servicios externos y APIs",
          wedof: {
            name: "API Wedof",
            description: "Sincronizar datos de beneficiarios y programas",
            configure: "Configurar"
          },
          google: {
            name: "Google Workspace",
            description: "Integración de Calendar, Drive y Gmail",
            calendar: {
              name: "Google Calendar",
              description: "Sincronizar citas y sesiones",
              setup: "Configurar"
            },
            drive: {
              name: "Google Drive",
              description: "Almacenar y compartir documentos",
              clientId: "ID de Cliente",
              clientIdPlaceholder: "ID de Cliente OAuth de Google",
              clientSecret: "Secreto de Cliente",
              clientSecretPlaceholder: "Secreto de Cliente OAuth de Google"
            },
            gmail: {
              name: "Integración Gmail",
              description: "Enviar emails automatizados y notificaciones",
              smtpSettings: "Configuración SMTP",
              usernamePlaceholder: "smtp-username@gmail.com",
              passwordPlaceholder: "Contraseña de Aplicación"
            }
          },
          other: {
            title: "Otras Integraciones",
            pennylane: {
              name: "Pennylane",
              description: "Integración de gestión financiera"
            },
            sms: {
              name: "Servicio SMS",
              description: "Enviar notificaciones SMS",
              provider: "Proveedor",
              selectProvider: "Seleccionar Proveedor SMS",
              providers: {
                twilio: "Twilio",
                messageBird: "MessageBird",
                orangeSms: "Orange SMS"
              },
              apiKeyPlaceholder: "Clave API"
            },
            webhooks: {
              name: "URLs de Webhook",
              description: "Configurar notificaciones de servicios externos",
              manage: "Administrar"
            }
          },
          health: {
            title: "Estado de Integración",
            connected: "Conectado",
            partial: "Parcial",
            active: "Activo",
            notConfigured: "No Configurado"
          },
          saveButton: "Guardar Configuración de Integraciones"
        },
        accessRestricted: {
          title: "Acceso Restringido",
          privacyMessage: "La configuración avanzada de privacidad solo está disponible para administradores y capacitadores.",
          aiMessage: "La configuración de IA solo está disponible para administradores y capacitadores.",
          integrationsMessage: "La configuración de integraciones solo está disponible para administradores.",
          currentRole: "Rol actual:"
        },
        messages: {
          updateSuccess: "Tu configuración de {{type}} ha sido guardada.",
          updateFailed: "Error al actualizar la configuración. Por favor intenta de nuevo.",
          settingsSaved: "Configuración guardada",
          integrationsSaved: "La configuración de integraciones ha sido guardada."
        }
      }
    },
    portal: {
      notifications: {
        title: "Notificaciones",
        subtitle: "Mantente actualizado con anuncios y notificaciones importantes",
        settings: "Configuración",
        markAllAsRead: "Marcar Todo como Leído",
        settingsPanel: {
          title: "Configuración de Notificaciones",
          deliveryMethods: {
            title: "Métodos de Entrega",
            email: "Notificaciones por email",
            push: "Notificaciones push (navegador)"
          },
          categories: {
            title: "Categorías de Notificación",
            schedule: "Actualizaciones de horario",
            messages: "Mensajes de instructores",
            progress: "Actualizaciones de progreso",
            reminders: "Recordatorios",
            alerts: "Alertas y anuncios importantes"
          },
          saveButton: "Guardar Configuración"
        },
        search: {
          placeholder: "Buscar notificaciones..."
        },
        filters: {
          all: "Todas",
          schedule: "Horario",
          messages: "Mensajes",
          progress: "Progreso"
        },
        empty: {
          title: "No se encontraron notificaciones",
          searchMessage: "Intenta ajustar tu búsqueda o filtro para encontrar lo que buscas",
          defaultMessage: "Aún no tienes notificaciones"
        },
        actions: {
          viewDetails: "Ver Detalles",
          markAsRead: "Marcar como leída",
          markAsUnread: "Marcar como no leída",
          delete: "Eliminar"
        },
        dateFormats: {
          today: "Hoy a las {{time}}",
          yesterday: "Ayer a las {{time}}"
        },
        messages: {
          loadError: "Error al cargar notificaciones",
          markAsReadError: "Error al marcar notificación como leída",
          markAllAsReadSuccess: "Todas las notificaciones marcadas como leídas",
          markAllAsReadError: "Error al marcar todas las notificaciones como leídas",
          deleteSuccess: "Notificación eliminada",
          deleteError: "Error al eliminar notificación",
          settingsUpdateSuccess: "Configuración de notificaciones actualizada",
          settingsUpdateError: "Error al actualizar configuración de notificaciones"
        }
      },
      dashboard: {
        welcome: "¡Bienvenido de nuevo, {{name}}!",
        subtitle: "Sigue tu progreso y alcanza tus metas",
        currentLevel: "Nivel Actual",
        defaultLevel: "Principiante",
        defaultStudent: "Estudiante",
        retry: "Reintentar",
        stats: {
          enrolledPrograms: "Programas Inscritos",
          enrolledProgramsSubtitle: "{{count}} completados",
          averageProgress: "Progreso Promedio",
          averageProgressSubtitle: "En todos los programas",
          attendanceRate: "Tasa de Asistencia",
          attendanceRateSubtitle: "¡Sigue así!",
          achievements: "Logros",
          achievementsSubtitle: "Insignias ganadas"
        },
        sections: {
          activePrograms: {
            title: "Programas Activos",
            viewAll: "Ver Todos",
            empty: "No hay programas activos",
            moduleProgress: "Módulo {{current}} de {{total}}"
          },
          recentAssessments: {
            title: "Evaluaciones Recientes",
            viewAll: "Ver Todas",
            empty: "No hay evaluaciones recientes",
            defaultTitle: "Evaluación",
            inProgress: "En Progreso"
          },
          performanceTrend: {
            title: "Tendencia de Rendimiento",
            empty: "No hay datos de rendimiento disponibles",
            assessmentScore: "Puntuación de Evaluación",
            completionRate: "Tasa de Finalización",
            attendanceRate: "Tasa de Asistencia"
          },
          upcomingSchedule: {
            title: "Próximo Horario",
            viewCalendar: "Ver Calendario",
            empty: "No hay sesiones próximas",
            defaultSession: "Sesión de Entrenamiento"
          },
          skillsDevelopment: {
            title: "Desarrollo de Habilidades",
            empty: "No hay datos de habilidades disponibles",
            viewDetailed: "Ver Progreso Detallado"
          },
          recentAchievements: {
            title: "Logros Recientes",
            viewAll: "Ver Todos",
            empty: "Aún no hay logros"
          },
          quickActions: {
            title: "Acciones Rápidas",
            resources: "Recursos",
            takeTest: "Tomar Prueba",
            progress: "Progreso",
            profile: "Perfil"
          }
        },
        dateFormats: {
          today: "Hoy a las {{time}}",
          tomorrow: "Mañana a las {{time}}"
        },
        scoreLabels: {
          excellent: "Excelente",
          veryGood: "Muy Bueno",
          good: "Bueno",
          satisfactory: "Satisfactorio",
          needsImprovement: "Necesita Mejorar"
        }
      }
    }
  },
  fr: {
    settings: {
      ai: {
        title: "Paramètres IA",
        subtitle: "Configurer les fournisseurs IA et les clés API pour les fonctionnalités intelligentes",
        providers: {
          openai: {
            name: "OpenAI",
            description: "Modèles GPT pour la génération et l'analyse de texte",
            apiKey: "Clé API",
            apiKeyPlaceholder: "sk-...",
            getApiKey: "Obtenez votre clé API depuis",
            platform: "Plateforme OpenAI",
            model: "Modèle",
            models: {
              gpt4: "GPT-4",
              gpt4Turbo: "GPT-4 Turbo",
              gpt35Turbo: "GPT-3.5 Turbo"
            },
            temperature: "Température",
            maxTokens: "Jetons Max"
          },
          anthropic: {
            name: "Anthropic Claude",
            description: "Assistant IA avancé pour les tâches complexes",
            apiKey: "Clé API",
            apiKeyPlaceholder: "sk-ant-...",
            getApiKey: "Obtenez votre clé API depuis",
            platform: "Console Anthropic",
            model: "Modèle",
            models: {
              claude3Opus: "Claude 3 Opus",
              claude3Sonnet: "Claude 3 Sonnet",
              claude3Haiku: "Claude 3 Haiku",
              claude21: "Claude 2.1"
            }
          },
          google: {
            name: "Google AI",
            description: "Modèles Gemini pour les tâches IA multimodales",
            apiKey: "Clé API",
            apiKeyPlaceholder: "AIza...",
            getApiKey: "Obtenez votre clé API depuis",
            platform: "Google AI Studio",
            model: "Modèle",
            models: {
              geminiPro: "Gemini Pro",
              geminiProVision: "Gemini Pro Vision"
            }
          }
        },
        customEndpoints: {
          title: "Points de terminaison IA personnalisés",
          description: "Ajouter des points de terminaison IA personnalisés pour des modèles spécialisés",
          namePlaceholder: "Nom du point de terminaison",
          urlPlaceholder: "URL du point de terminaison",
          apiKeyPlaceholder: "Clé API (optionnel)",
          addEndpoint: "Ajouter un point de terminaison"
        },
        features: {
          title: "Fonctionnalités IA",
          description: "Configurer les fonctionnalités IA activées",
          evaluationAnalysis: "Activer l'analyse d'évaluation par IA",
          recommendations: "Activer les recommandations IA",
          contentGeneration: "Activer la génération de contenu par IA",
          chatbotAssistance: "Activer l'assistance chatbot IA"
        },
        actions: {
          test: "Tester",
          save: "Enregistrer les paramètres"
        },
        messages: {
          saveSuccess: "Les paramètres IA ont été mis à jour avec succès",
          saveFailed: "Échec de l'enregistrement des paramètres IA",
          connectionSuccess: "Connexion réussie à l'API {{provider}}",
          connectionFailed: "Échec de la connexion à l'API {{provider}}"
        }
      }
    },
    portal: {
      notifications: {
        title: "Notifications",
        subtitle: "Restez informé des annonces et notifications importantes",
        settings: "Paramètres",
        markAllAsRead: "Tout marquer comme lu"
      },
      dashboard: {
        welcome: "Bon retour, {{name}} !",
        subtitle: "Suivez vos progrès et atteignez vos objectifs",
        currentLevel: "Niveau actuel",
        defaultLevel: "Débutant",
        defaultStudent: "Étudiant",
        retry: "Réessayer"
      }
    }
  },
  de: {
    settings: {
      ai: {
        title: "KI-Einstellungen",
        subtitle: "KI-Anbieter und API-Schlüssel für intelligente Funktionen konfigurieren"
      }
    },
    portal: {
      notifications: {
        title: "Benachrichtigungen",
        subtitle: "Bleiben Sie über wichtige Ankündigungen und Benachrichtigungen auf dem Laufenden"
      },
      dashboard: {
        welcome: "Willkommen zurück, {{name}}!",
        subtitle: "Verfolgen Sie Ihren Fortschritt und erreichen Sie Ihre Ziele"
      }
    }
  },
  tr: {
    settings: {
      ai: {
        title: "Yapay Zeka Ayarları",
        subtitle: "Akıllı özellikler için yapay zeka sağlayıcılarını ve API anahtarlarını yapılandırın"
      }
    },
    portal: {
      notifications: {
        title: "Bildirimler",
        subtitle: "Önemli duyurular ve bildirimlerden haberdar olun"
      },
      dashboard: {
        welcome: "Tekrar hoş geldiniz, {{name}}!",
        subtitle: "İlerlemenizi takip edin ve hedeflerinize ulaşın"
      }
    }
  },
  ar: {
    settings: {
      ai: {
        title: "إعدادات الذكاء الاصطناعي",
        subtitle: "تكوين موفري الذكاء الاصطناعي ومفاتيح API للميزات الذكية"
      }
    },
    portal: {
      notifications: {
        title: "الإشعارات",
        subtitle: "ابق على اطلاع بالإعلانات والإشعارات المهمة"
      },
      dashboard: {
        welcome: "مرحباً بعودتك، {{name}}!",
        subtitle: "تتبع تقدمك وحقق أهدافك"
      }
    }
  }
};

// Update each language file
Object.entries(languages).forEach(([lang, translations]) => {
  const filePath = path.join(__dirname, `client/src/i18n/locales/${lang}.json`);
  
  try {
    // Read existing translations
    const existingTranslations = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    
    // Deep merge function
    function deepMerge(target, source) {
      for (const key in source) {
        if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
          if (!target[key]) {
            target[key] = {};
          }
          deepMerge(target[key], source[key]);
        } else {
          target[key] = source[key];
        }
      }
      return target;
    }
    
    // Merge new translations
    const updatedTranslations = deepMerge(existingTranslations, translations);
    
    // Write back to file
    fs.writeFileSync(filePath, JSON.stringify(updatedTranslations, null, 2));
    console.log(`✅ Updated ${lang}.json`);
    
  } catch (error) {
    console.error(`❌ Error updating ${lang}.json:`, error.message);
  }
});

console.log('\n✨ Translation update complete!');