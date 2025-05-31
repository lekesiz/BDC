# Stagiaires (Trainees/Interns) API Endpoints

## Overview
These endpoints allow you to manage trainees/interns (stagiaires) in the Wedof system.

## Endpoints

### List All Stagiaires
```http
GET /api/v2/stagiaires
```

#### Query Parameters
| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| page | integer | Page number (default: 1) | No |
| per_page | integer | Items per page (default: 20, max: 100) | No |
| search | string | Search by name, email, or ID | No |
| formation_id | string | Filter by formation ID | No |
| status | string | Filter by status (active, completed, suspended) | No |
| date_debut_min | date | Filter by start date (from) | No |
| date_debut_max | date | Filter by start date (to) | No |

#### Response
```json
{
  "data": [
    {
      "id": "stag_123456",
      "nom": "Dupont",
      "prenom": "Marie",
      "email": "marie.dupont@example.com",
      "telephone": "+33612345678",
      "date_naissance": "1995-03-15",
      "adresse": {
        "rue": "123 Rue de la Paix",
        "code_postal": "75001",
        "ville": "Paris",
        "pays": "France"
      },
      "formation": {
        "id": "form_789",
        "nom": "Développement Web Full Stack",
        "date_debut": "2024-01-15",
        "date_fin": "2024-07-15"
      },
      "status": "active",
      "progression": {
        "pourcentage": 45,
        "modules_completes": 5,
        "modules_total": 12
      },
      "financements": [
        {
          "type": "CPF",
          "montant": 5000,
          "status": "valide"
        }
      ],
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2024-03-20T14:30:00Z"
    }
  ],
  "meta": {
    "current_page": 1,
    "total_pages": 5,
    "total_count": 95,
    "per_page": 20
  }
}
```

### Get Single Stagiaire
```http
GET /api/v2/stagiaires/{id}
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Stagiaire ID |

#### Response
```json
{
  "id": "stag_123456",
  "nom": "Dupont",
  "prenom": "Marie",
  "email": "marie.dupont@example.com",
  "telephone": "+33612345678",
  "date_naissance": "1995-03-15",
  "numero_secu": "1950375001234",
  "adresse": {
    "rue": "123 Rue de la Paix",
    "code_postal": "75001",
    "ville": "Paris",
    "pays": "France"
  },
  "contact_urgence": {
    "nom": "Dupont Jean",
    "telephone": "+33698765432",
    "relation": "Père"
  },
  "formation": {
    "id": "form_789",
    "nom": "Développement Web Full Stack",
    "date_debut": "2024-01-15",
    "date_fin": "2024-07-15",
    "formateur": {
      "id": "form_456",
      "nom": "Martin",
      "prenom": "Pierre"
    }
  },
  "bilans": [
    {
      "id": "bilan_001",
      "type": "initial",
      "date": "2024-01-20",
      "status": "complete"
    },
    {
      "id": "bilan_002",
      "type": "intermediaire",
      "date": "2024-04-15",
      "status": "planifie"
    }
  ],
  "documents": [
    {
      "id": "doc_001",
      "type": "cv",
      "nom": "CV_Marie_Dupont.pdf",
      "url": "https://api.wedof.fr/v2/documents/doc_001/download"
    }
  ],
  "competences": {
    "acquises": [
      {
        "id": "comp_001",
        "nom": "HTML/CSS",
        "niveau": "intermediaire",
        "date_validation": "2024-02-15"
      }
    ],
    "en_cours": [
      {
        "id": "comp_002",
        "nom": "JavaScript",
        "niveau_vise": "avance",
        "progression": 60
      }
    ]
  },
  "assiduity": {
    "taux_presence": 92,
    "heures_presentes": 320,
    "heures_totales": 350,
    "absences": [
      {
        "date": "2024-03-10",
        "duree_heures": 7,
        "justifiee": true,
        "motif": "Maladie"
      }
    ]
  },
  "evaluations": [
    {
      "id": "eval_001",
      "module": "HTML/CSS Basics",
      "date": "2024-02-10",
      "note": 16,
      "note_max": 20,
      "commentaire": "Très bon travail"
    }
  ]
}
```

### Create Stagiaire
```http
POST /api/v2/stagiaires
```

#### Request Body
```json
{
  "nom": "Nouveau",
  "prenom": "Stagiaire",
  "email": "nouveau.stagiaire@example.com",
  "telephone": "+33612345678",
  "date_naissance": "1998-05-20",
  "numero_secu": "1980575001234",
  "adresse": {
    "rue": "456 Avenue des Champs",
    "code_postal": "75008",
    "ville": "Paris",
    "pays": "France"
  },
  "formation_id": "form_789",
  "date_debut": "2024-04-01",
  "financements": [
    {
      "type": "CPF",
      "montant": 3000
    }
  ],
  "contact_urgence": {
    "nom": "Nouveau Parent",
    "telephone": "+33698765432",
    "relation": "Parent"
  }
}
```

#### Response
```json
{
  "id": "stag_789012",
  "nom": "Nouveau",
  "prenom": "Stagiaire",
  "status": "active",
  "created_at": "2024-03-25T10:00:00Z"
}
```

### Update Stagiaire
```http
PUT /api/v2/stagiaires/{id}
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Stagiaire ID |

#### Request Body
```json
{
  "telephone": "+33612345679",
  "adresse": {
    "rue": "789 Boulevard Nouveau",
    "code_postal": "75009",
    "ville": "Paris"
  },
  "status": "completed"
}
```

### Delete Stagiaire
```http
DELETE /api/v2/stagiaires/{id}
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Stagiaire ID |

#### Response
```json
{
  "message": "Stagiaire successfully deleted",
  "id": "stag_123456"
}
```

### Update Progression
```http
POST /api/v2/stagiaires/{id}/progression
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Stagiaire ID |

#### Request Body
```json
{
  "module_id": "mod_123",
  "status": "complete",
  "score": 85,
  "commentaire": "Module complété avec succès"
}
```

### Add Document
```http
POST /api/v2/stagiaires/{id}/documents
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Stagiaire ID |

#### Request Body (multipart/form-data)
```
file: [binary]
type: "attestation"
description: "Attestation de formation"
```

### Update Attendance
```http
POST /api/v2/stagiaires/{id}/assiduite
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Stagiaire ID |

#### Request Body
```json
{
  "date": "2024-03-25",
  "present": true,
  "heures": 7,
  "commentaire": "Présent toute la journée"
}
```

### Generate Bilan
```http
POST /api/v2/stagiaires/{id}/bilans
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Stagiaire ID |

#### Request Body
```json
{
  "type": "intermediaire",
  "date": "2024-04-15",
  "evaluateur_id": "eval_123",
  "competences_evaluees": [
    {
      "competence_id": "comp_001",
      "niveau": "acquis",
      "commentaire": "Maîtrise complète"
    }
  ],
  "synthese": "Progression satisfaisante",
  "recommandations": "Continuer sur cette voie"
}
```

## Webhook Events

### stagiaire.created
Triggered when a new stagiaire is created

### stagiaire.updated
Triggered when stagiaire information is updated

### stagiaire.progression.updated
Triggered when progression is updated

### stagiaire.bilan.created
Triggered when a new bilan is created

### stagiaire.document.added
Triggered when a document is added

## Error Responses

### 404 Not Found
```json
{
  "error": {
    "code": "STAGIAIRE_NOT_FOUND",
    "message": "Stagiaire with ID stag_123456 not found"
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
      "email": ["Email is already taken"],
      "date_naissance": ["Must be a valid date"]
    }
  }
}
```
