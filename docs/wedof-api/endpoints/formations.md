# Formations (Training Programs) API Endpoints

## Overview
These endpoints manage training programs (formations) in the Wedof system.

## Endpoints

### List All Formations
```http
GET /api/v2/formations
```

#### Query Parameters
| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| page | integer | Page number (default: 1) | No |
| per_page | integer | Items per page (default: 20) | No |
| search | string | Search by name or code | No |
| status | string | Filter by status (active, completed, upcoming) | No |
| categorie | string | Filter by category | No |
| date_debut_min | date | Filter by start date (from) | No |
| date_debut_max | date | Filter by start date (to) | No |
| cpf_eligible | boolean | Filter CPF eligible formations | No |

#### Response
```json
{
  "data": [
    {
      "id": "form_789",
      "code": "DEV-WEB-2024",
      "nom": "Développement Web Full Stack",
      "description": "Formation complète en développement web",
      "categorie": "Informatique",
      "niveau": "Intermédiaire",
      "duree": {
        "heures": 490,
        "jours": 70,
        "semaines": 14
      },
      "dates": {
        "debut": "2024-01-15",
        "fin": "2024-07-15",
        "inscription_limite": "2024-01-05"
      },
      "lieu": {
        "type": "presentiel",
        "adresse": "123 Rue de la Formation, 75001 Paris"
      },
      "tarif": {
        "montant": 8000,
        "devise": "EUR",
        "cpf_eligible": true,
        "opco_eligible": true
      },
      "places": {
        "total": 20,
        "disponibles": 5,
        "reservees": 15
      },
      "formateurs": [
        {
          "id": "form_456",
          "nom": "Martin",
          "prenom": "Pierre",
          "specialite": "Frontend Development"
        }
      ],
      "modules": [
        {
          "id": "mod_001",
          "nom": "HTML/CSS Fundamentals",
          "duree_heures": 35,
          "ordre": 1
        },
        {
          "id": "mod_002",
          "nom": "JavaScript Basics",
          "duree_heures": 42,
          "ordre": 2
        }
      ],
      "certifications": [
        {
          "nom": "Certification Développeur Web",
          "organisme": "France Compétences",
          "code_rncp": "RNCP31114"
        }
      ],
      "prerequis": "Connaissance de base en informatique",
      "objectifs": [
        "Maîtriser les langages web",
        "Développer des applications full stack",
        "Déployer des applications en production"
      ],
      "status": "active"
    }
  ],
  "meta": {
    "current_page": 1,
    "total_pages": 3,
    "total_count": 45
  }
}
```

### Get Single Formation
```http
GET /api/v2/formations/{id}
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Formation ID |

#### Response
```json
{
  "id": "form_789",
  "code": "DEV-WEB-2024",
  "nom": "Développement Web Full Stack",
  "description_complete": "Formation intensive...",
  "programme_detaille": {
    "modules": [
      {
        "id": "mod_001",
        "nom": "HTML/CSS Fundamentals",
        "description": "Apprentissage des bases du web",
        "duree_heures": 35,
        "ordre": 1,
        "competences": [
          "Créer des pages HTML sémantiques",
          "Styliser avec CSS moderne",
          "Responsive design"
        ],
        "evaluations": [
          {
            "type": "QCM",
            "duree_minutes": 60,
            "coefficient": 1
          },
          {
            "type": "Projet",
            "duree_jours": 3,
            "coefficient": 2
          }
        ]
      }
    ]
  },
  "stagiaires_inscrits": [
    {
      "id": "stag_123",
      "nom": "Dupont",
      "prenom": "Marie",
      "date_inscription": "2023-12-15",
      "status": "active"
    }
  ],
  "sessions": [
    {
      "id": "sess_001",
      "date": "2024-01-15",
      "heure_debut": "09:00",
      "heure_fin": "17:00",
      "formateur_id": "form_456",
      "salle": "Salle A204"
    }
  ],
  "documents_pedagogiques": [
    {
      "id": "doc_ped_001",
      "nom": "Support de cours HTML/CSS",
      "type": "pdf",
      "taille": "2.5MB",
      "url": "/api/v2/documents/doc_ped_001/download"
    }
  ],
  "statistiques": {
    "taux_reussite": 85,
    "taux_satisfaction": 92,
    "taux_insertion": 78,
    "nombre_sessions": 12,
    "total_stagiaires": 240
  }
}
```

### Create Formation
```http
POST /api/v2/formations
```

#### Request Body
```json
{
  "code": "AI-ML-2024",
  "nom": "Intelligence Artificielle et Machine Learning",
  "description": "Formation en IA et ML",
  "categorie": "Informatique",
  "niveau": "Avancé",
  "duree_heures": 350,
  "date_debut": "2024-09-01",
  "date_fin": "2024-12-15",
  "lieu": {
    "type": "hybride",
    "adresse": "456 Avenue Tech, 75002 Paris",
    "url_visio": "https://meet.wedof.fr/ai-ml-2024"
  },
  "tarif": 12000,
  "cpf_eligible": true,
  "places_disponibles": 15,
  "prerequis": "Connaissances en Python et mathématiques",
  "objectifs": [
    "Comprendre les fondamentaux de l'IA",
    "Implémenter des modèles de ML",
    "Déployer des solutions IA"
  ],
  "formateurs_ids": ["form_789", "form_790"],
  "modules": [
    {
      "nom": "Introduction à l'IA",
      "duree_heures": 28,
      "ordre": 1
    },
    {
      "nom": "Machine Learning Basics",
      "duree_heures": 42,
      "ordre": 2
    }
  ]
}
```

### Update Formation
```http
PUT /api/v2/formations/{id}
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Formation ID |

#### Request Body
```json
{
  "places_disponibles": 10,
  "status": "complet",
  "date_inscription_limite": "2024-08-15"
}
```

### Delete Formation
```http
DELETE /api/v2/formations/{id}
```

### Add Module to Formation
```http
POST /api/v2/formations/{id}/modules
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Formation ID |

#### Request Body
```json
{
  "nom": "Deep Learning Advanced",
  "description": "Techniques avancées de deep learning",
  "duree_heures": 56,
  "ordre": 5,
  "competences": [
    "Réseaux de neurones profonds",
    "CNN et RNN",
    "Transformers"
  ]
}
```

### Register Stagiaire to Formation
```http
POST /api/v2/formations/{id}/inscriptions
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Formation ID |

#### Request Body
```json
{
  "stagiaire_id": "stag_123",
  "date_debut_souhaitee": "2024-09-01",
  "financement": {
    "type": "CPF",
    "montant": 8000,
    "numero_dossier": "CPF123456"
  },
  "motivation": "Je souhaite me reconvertir dans l'IA"
}
```

### Get Formation Planning
```http
GET /api/v2/formations/{id}/planning
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Formation ID |

#### Query Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| date_debut | date | Start date for planning |
| date_fin | date | End date for planning |

#### Response
```json
{
  "formation_id": "form_789",
  "planning": [
    {
      "date": "2024-09-01",
      "sessions": [
        {
          "heure_debut": "09:00",
          "heure_fin": "12:30",
          "module": "Introduction à l'IA",
          "formateur": "Dr. Smith",
          "salle": "Lab AI-01",
          "type": "cours"
        },
        {
          "heure_debut": "14:00",
          "heure_fin": "17:30",
          "module": "TP Python pour l'IA",
          "formateur": "Mme. Johnson",
          "salle": "Lab Info-02",
          "type": "travaux_pratiques"
        }
      ]
    }
  ]
}
```

### Generate Formation Report
```http
POST /api/v2/formations/{id}/rapports
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Formation ID |

#### Request Body
```json
{
  "type": "bilan_pedagogique",
  "periode": {
    "debut": "2024-01-01",
    "fin": "2024-06-30"
  },
  "inclure": [
    "statistiques",
    "evaluations",
    "satisfaction",
    "insertion_professionnelle"
  ],
  "format": "pdf"
}
```

### Update Formation Status
```http
PUT /api/v2/formations/{id}/status
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Formation ID |

#### Request Body
```json
{
  "status": "completed",
  "commentaire": "Formation terminée avec succès"
}
```

## Webhook Events

### formation.created
Triggered when a new formation is created

### formation.updated
Triggered when formation information is updated

### formation.inscription
Triggered when a stagiaire registers

### formation.started
Triggered when formation starts

### formation.completed
Triggered when formation ends

### formation.cancelled
Triggered when formation is cancelled

## Error Responses

### 404 Not Found
```json
{
  "error": {
    "code": "FORMATION_NOT_FOUND",
    "message": "Formation with ID form_789 not found"
  }
}
```

### 409 Conflict
```json
{
  "error": {
    "code": "FORMATION_FULL",
    "message": "Formation is full, no places available"
  }
}
```

### 422 Validation Error
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "date_debut": ["Start date must be in the future"],
      "duree_heures": ["Duration must be positive"]
    }
  }
}
```
