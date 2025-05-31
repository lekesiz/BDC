# Bilans de Compétences API Endpoints

## Overview
These endpoints manage competency assessments (bilans de compétences) in the Wedof system, with AI-powered analysis capabilities.

## Endpoints

### List All Bilans
```http
GET /api/v2/bilans
```

#### Query Parameters
| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| page | integer | Page number (default: 1) | No |
| per_page | integer | Items per page (default: 20) | No |
| stagiaire_id | string | Filter by stagiaire | No |
| formation_id | string | Filter by formation | No |
| evaluateur_id | string | Filter by evaluator | No |
| type | string | Filter by type (initial, intermediaire, final) | No |
| status | string | Filter by status (planifie, en_cours, complete) | No |
| date_min | date | Filter by date (from) | No |
| date_max | date | Filter by date (to) | No |

#### Response
```json
{
  "data": [
    {
      "id": "bilan_001",
      "stagiaire": {
        "id": "stag_123",
        "nom": "Dupont",
        "prenom": "Marie"
      },
      "formation": {
        "id": "form_789",
        "nom": "Développement Web Full Stack"
      },
      "type": "intermediaire",
      "date": "2024-04-15",
      "status": "complete",
      "evaluateur": {
        "id": "eval_456",
        "nom": "Martin",
        "prenom": "Sophie"
      },
      "duree_minutes": 90,
      "synthese": {
        "points_forts": [
          "Excellente maîtrise du HTML/CSS",
          "Bonne compréhension des concepts JavaScript"
        ],
        "points_amelioration": [
          "Approfondir les frameworks React/Vue",
          "Pratiquer davantage les tests unitaires"
        ],
        "progression_generale": 75
      },
      "competences_evaluees": 12,
      "competences_validees": 8,
      "ai_insights": {
        "confidence_score": 0.87,
        "recommendations": [
          "Focus sur les projets pratiques",
          "Mentorat recommandé pour React"
        ]
      }
    }
  ],
  "meta": {
    "current_page": 1,
    "total_pages": 10,
    "total_count": 198
  }
}
```

### Get Single Bilan
```http
GET /api/v2/bilans/{id}
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Bilan ID |

#### Response
```json
{
  "id": "bilan_001",
  "stagiaire": {
    "id": "stag_123",
    "nom": "Dupont",
    "prenom": "Marie",
    "email": "marie.dupont@example.com",
    "formation_actuelle": "Développement Web Full Stack"
  },
  "formation": {
    "id": "form_789",
    "nom": "Développement Web Full Stack",
    "progression": 45
  },
  "type": "intermediaire",
  "date": "2024-04-15",
  "heure": "14:00",
  "duree_minutes": 90,
  "lieu": "Salle d'entretien B12",
  "status": "complete",
  "evaluateur": {
    "id": "eval_456",
    "nom": "Martin",
    "prenom": "Sophie",
    "qualification": "Psychologue du travail"
  },
  "contexte": {
    "objectif_bilan": "Évaluation mi-parcours",
    "situation_actuelle": "En formation depuis 3 mois",
    "projet_professionnel": "Devenir développeur full stack"
  },
  "competences": {
    "techniques": [
      {
        "id": "comp_001",
        "nom": "HTML/CSS",
        "niveau_initial": "debutant",
        "niveau_actuel": "intermediaire",
        "niveau_vise": "avance",
        "progression": 60,
        "evaluation": {
          "note": 15,
          "max": 20,
          "commentaire": "Très bonne maîtrise des bases"
        },
        "preuves": [
          "Projet portfolio personnel",
          "3 sites web responsive créés"
        ]
      },
      {
        "id": "comp_002",
        "nom": "JavaScript",
        "niveau_initial": "aucun",
        "niveau_actuel": "debutant",
        "niveau_vise": "intermediaire",
        "progression": 30,
        "evaluation": {
          "note": 12,
          "max": 20,
          "commentaire": "En progression, bases acquises"
        }
      }
    ],
    "transversales": [
      {
        "id": "comp_trans_001",
        "nom": "Travail en équipe",
        "evaluation": "excellent",
        "exemples": [
          "Leadership sur projet groupe",
          "Bonne communication avec pairs"
        ]
      },
      {
        "id": "comp_trans_002",
        "nom": "Autonomie",
        "evaluation": "bon",
        "exemples": [
          "Auto-formation sur React",
          "Gestion autonome des projets"
        ]
      }
    ]
  },
  "evaluations_detaillees": {
    "tests_psychotechniques": {
      "logique": 85,
      "verbal": 78,
      "numerique": 82,
      "spatial": 90
    },
    "questionnaires": {
      "personnalite": {
        "type": "MBTI",
        "resultat": "INTJ",
        "traits_dominants": [
          "Analytique",
          "Stratégique",
          "Indépendant"
        ]
      },
      "interets_professionnels": {
        "domaines": [
          {
            "nom": "Technologie",
            "score": 95
          },
          {
            "nom": "Innovation",
            "score": 88
          }
        ]
      }
    },
    "mises_en_situation": [
      {
        "scenario": "Résolution bug complexe",
        "performance": "très bien",
        "observations": "Approche méthodique et efficace"
      }
    ]
  },
  "synthese": {
    "points_forts": [
      "Forte capacité d'apprentissage",
      "Excellente logique de programmation",
      "Motivation élevée",
      "Bonne culture technique"
    ],
    "points_amelioration": [
      "Approfondir JavaScript avancé",
      "Développer expertise frameworks",
      "Améliorer gestion du stress"
    ],
    "potentiel": {
      "evaluation": "élevé",
      "justification": "Progression rapide et régulière"
    }
  },
  "plan_action": {
    "objectifs_court_terme": [
      {
        "objectif": "Maîtriser React basics",
        "delai": "2 mois",
        "actions": [
          "Suivre cours React officiel",
          "Créer 3 projets React"
        ]
      }
    ],
    "objectifs_moyen_terme": [
      {
        "objectif": "Obtenir certification développeur",
        "delai": "6 mois",
        "actions": [
          "Préparer portfolio complet",
          "Passer examens blancs"
        ]
      }
    ],
    "preconisations_formation": [
      "Module avancé JavaScript",
      "Workshop React/Vue",
      "Stage en entreprise"
    ]
  },
  "ai_analysis": {
    "competency_prediction": {
      "6_months": {
        "javascript": 75,
        "react": 60,
        "node_js": 50
      },
      "confidence": 0.82
    },
    "learning_style": {
      "type": "visuel-pratique",
      "recommandations": [
        "Privilégier tutoriels vidéo",
        "Multiplier projets pratiques"
      ]
    },
    "career_matching": {
      "roles": [
        {
          "titre": "Développeur Frontend Junior",
          "compatibilite": 85,
          "delai_estimé": "6-8 mois"
        },
        {
          "titre": "Développeur Full Stack Junior",
          "compatibilite": 70,
          "delai_estimé": "10-12 mois"
        }
      ]
    },
    "personalized_recommendations": [
      "Focus sur React pour employabilité rapide",
      "Participer à hackathons pour réseau",
      "Contribuer à projets open source"
    ]
  },
  "documents": [
    {
      "id": "doc_bilan_001",
      "type": "rapport_complet",
      "nom": "Bilan_Marie_Dupont_2024-04-15.pdf",
      "taille": "1.2MB",
      "url": "/api/v2/documents/doc_bilan_001/download"
    },
    {
      "id": "doc_bilan_002",
      "type": "synthese",
      "nom": "Synthese_Marie_Dupont.pdf",
      "taille": "245KB"
    }
  ],
  "signatures": {
    "stagiaire": {
      "signe": true,
      "date": "2024-04-15T16:30:00Z"
    },
    "evaluateur": {
      "signe": true,
      "date": "2024-04-15T16:35:00Z"
    }
  }
}
```

### Create Bilan
```http
POST /api/v2/bilans
```

#### Request Body
```json
{
  "stagiaire_id": "stag_123",
  "formation_id": "form_789",
  "type": "intermediaire",
  "date": "2024-04-15",
  "heure": "14:00",
  "duree_prevue_minutes": 90,
  "evaluateur_id": "eval_456",
  "lieu": "Salle B12",
  "objectifs": [
    "Évaluer progression technique",
    "Identifier axes d'amélioration",
    "Définir plan d'action"
  ],
  "questionnaires_prevus": [
    "competences_techniques",
    "soft_skills",
    "projet_professionnel"
  ],
  "enable_ai_analysis": true
}
```

### Update Bilan
```http
PUT /api/v2/bilans/{id}
```

#### Request Body
```json
{
  "competences": {
    "techniques": [
      {
        "competence_id": "comp_001",
        "niveau_actuel": "intermediaire",
        "progression": 60,
        "evaluation": {
          "note": 15,
          "commentaire": "Très bonne progression"
        }
      }
    ]
  },
  "synthese": {
    "points_forts": ["Apprentissage rapide"],
    "points_amelioration": ["Gestion du temps"]
  },
  "status": "complete"
}
```

### Generate AI Analysis
```http
POST /api/v2/bilans/{id}/ai-analysis
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Bilan ID |

#### Request Body
```json
{
  "analysis_types": [
    "competency_prediction",
    "learning_recommendations",
    "career_matching",
    "skill_gap_analysis"
  ],
  "include_market_data": true,
  "projection_months": 12
}
```

#### Response
```json
{
  "analysis_id": "ai_analysis_789",
  "bilan_id": "bilan_001",
  "generated_at": "2024-04-15T17:00:00Z",
  "insights": {
    "competency_trajectory": {
      "current_level": 45,
      "projected_levels": {
        "3_months": 65,
        "6_months": 78,
        "12_months": 88
      },
      "confidence_interval": [0.75, 0.92]
    },
    "skill_gaps": [
      {
        "skill": "React Framework",
        "current": 20,
        "required": 70,
        "priority": "high",
        "estimated_time_to_close": "3-4 months"
      }
    ],
    "personalized_learning_path": [
      {
        "phase": 1,
        "duration": "2 months",
        "focus": "JavaScript Advanced",
        "resources": [
          "Course: Advanced JS Patterns",
          "Project: Build a SPA"
        ]
      }
    ],
    "market_alignment": {
      "demand_score": 0.85,
      "salary_projection": {
        "junior": "35-40k EUR",
        "after_1_year": "40-45k EUR"
      },
      "top_matching_companies": [
        "Tech startups",
        "Digital agencies"
      ]
    }
  }
}
```

### Add Competency Evaluation
```http
POST /api/v2/bilans/{id}/competences
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Bilan ID |

#### Request Body
```json
{
  "competence_id": "comp_003",
  "type": "technique",
  "nom": "Node.js Backend",
  "niveau_actuel": "debutant",
  "evaluation": {
    "methode": "projet_pratique",
    "resultat": "API REST fonctionnelle créée",
    "note": 14,
    "max": 20
  },
  "preuves": [
    "Github repo: api-project",
    "Démo live sur Heroku"
  ]
}
```

### Generate Bilan Report
```http
POST /api/v2/bilans/{id}/rapport
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Bilan ID |

#### Request Body
```json
{
  "format": "pdf",
  "template": "standard",
  "sections": [
    "synthese",
    "competences",
    "progression",
    "plan_action",
    "ai_insights"
  ],
  "include_graphs": true,
  "language": "fr"
}
```

### Schedule Follow-up
```http
POST /api/v2/bilans/{id}/suivi
```

#### Request Body
```json
{
  "date": "2024-06-15",
  "type": "point_etape",
  "objectifs": [
    "Vérifier progression React",
    "Ajuster plan d'action"
  ],
  "rappel_jours_avant": 7
}
```

## Webhook Events

### bilan.created
Triggered when a new bilan is scheduled

### bilan.started
Triggered when bilan begins

### bilan.completed
Triggered when bilan is completed

### bilan.signed
Triggered when bilan is signed by parties

### bilan.ai_analysis.completed
Triggered when AI analysis is ready

## Error Responses

### 404 Not Found
```json
{
  "error": {
    "code": "BILAN_NOT_FOUND",
    "message": "Bilan with ID bilan_001 not found"
  }
}
```

### 409 Conflict
```json
{
  "error": {
    "code": "BILAN_IN_PROGRESS",
    "message": "Another bilan is already in progress for this stagiaire"
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
      "date": ["Date cannot be in the past"],
      "evaluateur_id": ["Evaluator not qualified for this type"]
    }
  }
}
```
