# Wedof API Implementation Guide for BDC

## Overview
This guide provides step-by-step instructions for implementing Wedof API integration in the BDC (Beneficiary Development Center) system.

## 1. Backend Implementation

### 1.1 Create Wedof API Client

Create a new file: `/server/integrations/wedof/client.py`

```python
import requests
from typing import Dict, List, Optional
import hmac
import hashlib
from datetime import datetime
import os
from flask import current_app

class WedofAPIClient:
    """Client for interacting with Wedof API"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv('WEDOF_API_KEY')
        self.base_url = base_url or os.getenv('WEDOF_API_URL', 'https://api.wedof.fr/v2')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request to Wedof API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Wedof API error: {str(e)}")
            raise
    
    # Stagiaires methods
    def get_stagiaires(self, page: int = 1, per_page: int = 20, **filters) -> Dict:
        """Get list of stagiaires"""
        params = {'page': page, 'per_page': per_page, **filters}
        return self._make_request('GET', '/stagiaires', params=params)
    
    def get_stagiaire(self, stagiaire_id: str) -> Dict:
        """Get single stagiaire by ID"""
        return self._make_request('GET', f'/stagiaires/{stagiaire_id}')
    
    def create_stagiaire(self, data: Dict) -> Dict:
        """Create new stagiaire"""
        return self._make_request('POST', '/stagiaires', json=data)
    
    def update_stagiaire(self, stagiaire_id: str, data: Dict) -> Dict:
        """Update stagiaire"""
        return self._make_request('PUT', f'/stagiaires/{stagiaire_id}', json=data)
    
    def update_progression(self, stagiaire_id: str, module_id: str, data: Dict) -> Dict:
        """Update stagiaire progression"""
        return self._make_request('POST', f'/stagiaires/{stagiaire_id}/progression', json=data)
    
    # Formations methods
    def get_formations(self, **filters) -> Dict:
        """Get list of formations"""
        return self._make_request('GET', '/formations', params=filters)
    
    def get_formation(self, formation_id: str) -> Dict:
        """Get single formation"""
        return self._make_request('GET', f'/formations/{formation_id}')
    
    def register_stagiaire_to_formation(self, formation_id: str, data: Dict) -> Dict:
        """Register stagiaire to formation"""
        return self._make_request('POST', f'/formations/{formation_id}/inscriptions', json=data)
    
    # Bilans methods
    def get_bilans(self, **filters) -> Dict:
        """Get list of bilans"""
        return self._make_request('GET', '/bilans', params=filters)
    
    def create_bilan(self, data: Dict) -> Dict:
        """Create new bilan"""
        return self._make_request('POST', '/bilans', json=data)
    
    def update_bilan(self, bilan_id: str, data: Dict) -> Dict:
        """Update bilan"""
        return self._make_request('PUT', f'/bilans/{bilan_id}', json=data)
    
    def generate_ai_analysis(self, bilan_id: str, options: Dict) -> Dict:
        """Generate AI analysis for bilan"""
        return self._make_request('POST', f'/bilans/{bilan_id}/ai-analysis', json=options)
    
    # Webhook verification
    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        expected = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected)
```

### 1.2 Create Sync Service

Create `/server/integrations/wedof/sync_service.py`:

```python
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from server.models import Beneficiary, Program, User, db
from server.integrations.wedof.client import WedofAPIClient
import logging

logger = logging.getLogger(__name__)

class WedofSyncService:
    """Service for syncing data between BDC and Wedof"""
    
    def __init__(self, api_client: WedofAPIClient):
        self.client = api_client
    
    def sync_stagiaire_to_beneficiary(self, stagiaire_data: Dict) -> Beneficiary:
        """Sync Wedof stagiaire to BDC beneficiary"""
        
        # Check if beneficiary exists
        beneficiary = Beneficiary.query.filter_by(
            external_id=stagiaire_data['id']
        ).first()
        
        if not beneficiary:
            beneficiary = Beneficiary()
            beneficiary.external_id = stagiaire_data['id']
        
        # Update beneficiary data
        beneficiary.first_name = stagiaire_data.get('prenom', '')
        beneficiary.last_name = stagiaire_data.get('nom', '')
        beneficiary.email = stagiaire_data.get('email', '')
        beneficiary.phone = stagiaire_data.get('telephone', '')
        beneficiary.date_of_birth = datetime.strptime(
            stagiaire_data.get('date_naissance', '2000-01-01'), 
            '%Y-%m-%d'
        ).date()
        
        # Update address
        if 'adresse' in stagiaire_data:
            addr = stagiaire_data['adresse']
            beneficiary.address = f"{addr.get('rue', '')}, {addr.get('code_postal', '')} {addr.get('ville', '')}"
        
        # Map status
        wedof_status = stagiaire_data.get('status', 'active')
        beneficiary.status = self._map_status(wedof_status)
        
        # Update metadata
        beneficiary.metadata = beneficiary.metadata or {}
        beneficiary.metadata['wedof_data'] = {
            'id': stagiaire_data['id'],
            'formation_id': stagiaire_data.get('formation', {}).get('id'),
            'progression': stagiaire_data.get('progression', {}),
            'last_sync': datetime.utcnow().isoformat()
        }
        
        db.session.add(beneficiary)
        db.session.commit()
        
        logger.info(f"Synced stagiaire {stagiaire_data['id']} to beneficiary {beneficiary.id}")
        
        return beneficiary
    
    def sync_beneficiary_to_stagiaire(self, beneficiary: Beneficiary) -> Dict:
        """Sync BDC beneficiary to Wedof stagiaire"""
        
        data = {
            'nom': beneficiary.last_name,
            'prenom': beneficiary.first_name,
            'email': beneficiary.email,
            'telephone': beneficiary.phone,
            'date_naissance': beneficiary.date_of_birth.strftime('%Y-%m-%d')
        }
        
        if beneficiary.external_id:
            # Update existing
            result = self.client.update_stagiaire(beneficiary.external_id, data)
        else:
            # Create new
            result = self.client.create_stagiaire(data)
            beneficiary.external_id = result['id']
            db.session.commit()
        
        return result
    
    def sync_all_stagiaires(self, formation_id: Optional[str] = None) -> Dict:
        """Sync all stagiaires from Wedof"""
        
        synced = 0
        failed = 0
        page = 1
        
        while True:
            try:
                filters = {}
                if formation_id:
                    filters['formation_id'] = formation_id
                
                response = self.client.get_stagiaires(page=page, per_page=50, **filters)
                
                for stagiaire in response['data']:
                    try:
                        self.sync_stagiaire_to_beneficiary(stagiaire)
                        synced += 1
                    except Exception as e:
                        logger.error(f"Failed to sync stagiaire {stagiaire['id']}: {str(e)}")
                        failed += 1
                
                if page >= response['meta']['total_pages']:
                    break
                    
                page += 1
                
            except Exception as e:
                logger.error(f"Error during sync: {str(e)}")
                break
        
        return {
            'synced': synced,
            'failed': failed,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def sync_formation_to_program(self, formation_data: Dict) -> Program:
        """Sync Wedof formation to BDC program"""
        
        program = Program.query.filter_by(
            external_id=formation_data['id']
        ).first()
        
        if not program:
            program = Program()
            program.external_id = formation_data['id']
        
        program.name = formation_data.get('nom', '')
        program.description = formation_data.get('description', '')
        program.category = formation_data.get('categorie', '')
        program.duration_weeks = formation_data.get('duree', {}).get('semaines', 0)
        
        # Parse dates
        if 'dates' in formation_data:
            dates = formation_data['dates']
            if 'debut' in dates:
                program.start_date = datetime.strptime(dates['debut'], '%Y-%m-%d').date()
            if 'fin' in dates:
                program.end_date = datetime.strptime(dates['fin'], '%Y-%m-%d').date()
        
        # Update capacity
        if 'places' in formation_data:
            program.capacity = formation_data['places'].get('total', 0)
            program.enrolled = formation_data['places'].get('total', 0) - formation_data['places'].get('disponibles', 0)
        
        program.status = 'active' if formation_data.get('status') == 'active' else 'inactive'
        
        db.session.add(program)
        db.session.commit()
        
        return program
    
    def _map_status(self, wedof_status: str) -> str:
        """Map Wedof status to BDC status"""
        mapping = {
            'active': 'active',
            'completed': 'completed',
            'suspended': 'inactive',
            'abandoned': 'inactive'
        }
        return mapping.get(wedof_status, 'active')

    def update_progression(self, beneficiary_id: int, module_id: str, 
                          score: float, status: str) -> Dict:
        """Update progression in Wedof"""
        
        beneficiary = Beneficiary.query.get(beneficiary_id)
        if not beneficiary or not beneficiary.external_id:
            raise ValueError("Beneficiary not linked to Wedof")
        
        data = {
            'module_id': module_id,
            'status': status,
            'score': score,
            'commentaire': f'Updated from BDC on {datetime.utcnow().isoformat()}'
        }
        
        return self.client.update_progression(beneficiary.external_id, module_id, data)
```

### 1.3 Create Webhook Handler

Create `/server/integrations/wedof/webhooks.py`:

```python
from flask import Blueprint, request, jsonify
from server.integrations.wedof.client import WedofAPIClient
from server.integrations.wedof.sync_service import WedofSyncService
from server.models import db
import os
import logging

logger = logging.getLogger(__name__)
wedof_webhook_bp = Blueprint('wedof_webhooks', __name__)

@wedof_webhook_bp.route('/webhooks/wedof', methods=['POST'])
def handle_wedof_webhook():
    """Handle incoming Wedof webhooks"""
    
    # Verify signature
    signature = request.headers.get('X-Wedof-Signature')
    secret = os.getenv('WEDOF_WEBHOOK_SECRET')
    
    if not signature or not secret:
        return jsonify({'error': 'Missing signature or secret'}), 401
    
    if not WedofAPIClient.verify_webhook_signature(
        request.data, 
        signature, 
        secret
    ):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Process event
    event = request.json
    event_type = event.get('type')
    
    logger.info(f"Received Wedof webhook: {event_type}")
    
    # Initialize services
    api_client = WedofAPIClient()
    sync_service = WedofSyncService(api_client)
    
    try:
        if event_type == 'stagiaire.created':
            handle_stagiaire_created(event['data'], sync_service)
        
        elif event_type == 'stagiaire.updated':
            handle_stagiaire_updated(event['data'], sync_service)
        
        elif event_type == 'stagiaire.progression.updated':
            handle_progression_updated(event['data'])
        
        elif event_type == 'formation.inscription':
            handle_formation_inscription(event['data'])
        
        elif event_type == 'bilan.completed':
            handle_bilan_completed(event['data'])
        
        else:
            logger.warning(f"Unhandled webhook event type: {event_type}")
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'error': 'Processing failed'}), 500

def handle_stagiaire_created(data: dict, sync_service: WedofSyncService):
    """Handle new stagiaire creation"""
    
    # Fetch full stagiaire data
    api_client = WedofAPIClient()
    stagiaire = api_client.get_stagiaire(data['id'])
    
    # Sync to BDC
    beneficiary = sync_service.sync_stagiaire_to_beneficiary(stagiaire)
    
    # TODO: Send welcome email, assign trainer, etc.
    logger.info(f"Created beneficiary {beneficiary.id} from stagiaire {data['id']}")

def handle_stagiaire_updated(data: dict, sync_service: WedofSyncService):
    """Handle stagiaire update"""
    
    # Fetch updated data
    api_client = WedofAPIClient()
    stagiaire = api_client.get_stagiaire(data['id'])
    
    # Sync updates
    beneficiary = sync_service.sync_stagiaire_to_beneficiary(stagiaire)
    
    logger.info(f"Updated beneficiary {beneficiary.id} from stagiaire {data['id']}")

def handle_progression_updated(data: dict):
    """Handle progression update"""
    
    from server.models import Beneficiary, Evaluation
    
    # Find beneficiary
    beneficiary = Beneficiary.query.filter_by(
        external_id=data['stagiaire_id']
    ).first()
    
    if not beneficiary:
        logger.warning(f"Beneficiary not found for stagiaire {data['stagiaire_id']}")
        return
    
    # Update or create evaluation
    evaluation = Evaluation.query.filter_by(
        beneficiary_id=beneficiary.id,
        external_id=data['module_id']
    ).first()
    
    if not evaluation:
        evaluation = Evaluation(
            beneficiary_id=beneficiary.id,
            external_id=data['module_id'],
            title=f"Module {data['module_id']}"
        )
    
    evaluation.score = data.get('new_progression', 0)
    evaluation.status = 'completed' if data.get('module_completed') else 'in_progress'
    
    db.session.add(evaluation)
    db.session.commit()
    
    logger.info(f"Updated progression for beneficiary {beneficiary.id}")

def handle_formation_inscription(data: dict):
    """Handle new formation inscription"""
    
    from server.models import Beneficiary, Program
    
    # Find beneficiary and program
    beneficiary = Beneficiary.query.filter_by(
        external_id=data['stagiaire_id']
    ).first()
    
    program = Program.query.filter_by(
        external_id=data['formation_id']
    ).first()
    
    if beneficiary and program:
        # Add beneficiary to program
        if program not in beneficiary.programs:
            beneficiary.programs.append(program)
            db.session.commit()
            
        logger.info(f"Added beneficiary {beneficiary.id} to program {program.id}")

def handle_bilan_completed(data: dict):
    """Handle completed bilan"""
    
    from server.models import Beneficiary, Document
    
    # Find beneficiary
    beneficiary = Beneficiary.query.filter_by(
        external_id=data['stagiaire_id']
    ).first()
    
    if not beneficiary:
        return
    
    # Create document record for the bilan report
    document = Document(
        name=f"Bilan {data['type']} - {beneficiary.full_name}",
        type='bilan_report',
        beneficiary_id=beneficiary.id,
        external_id=data['bilan_id'],
        metadata={
            'bilan_type': data['type'],
            'evaluateur_id': data['evaluateur_id'],
            'synthese': data.get('synthese', {}),
            'rapport_url': data.get('rapport_url')
        }
    )
    
    db.session.add(document)
    db.session.commit()
    
    # TODO: Notify trainer, schedule follow-up, etc.
    logger.info(f"Processed completed bilan for beneficiary {beneficiary.id}")
```

### 1.4 Create API Routes

Create `/server/api/integrations/wedof.py`:

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from server.integrations.wedof.client import WedofAPIClient
from server.integrations.wedof.sync_service import WedofSyncService
from server.models import User
import os

wedof_api_bp = Blueprint('wedof_api', __name__)

@wedof_api_bp.route('/integrations/wedof/status', methods=['GET'])
@jwt_required()
def get_wedof_status():
    """Get Wedof integration status"""
    
    # Check if API key is configured
    api_key_configured = bool(os.getenv('WEDOF_API_KEY'))
    
    # Try to make a test request
    if api_key_configured:
        try:
            client = WedofAPIClient()
            # Make a simple request to check connectivity
            client.get_formations(per_page=1)
            api_connected = True
            error_message = None
        except Exception as e:
            api_connected = False
            error_message = str(e)
    else:
        api_connected = False
        error_message = "API key not configured"
    
    return jsonify({
        'configured': api_key_configured,
        'connected': api_connected,
        'error': error_message,
        'webhook_url': request.host_url + 'api/webhooks/wedof'
    })

@wedof_api_bp.route('/integrations/wedof/sync', methods=['POST'])
@jwt_required()
def sync_wedof_data():
    """Manually trigger data sync"""
    
    user = User.query.get(get_jwt_identity())
    if user.role not in ['admin', 'tenant_admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    sync_type = request.json.get('type', 'all')
    
    try:
        client = WedofAPIClient()
        sync_service = WedofSyncService(client)
        
        if sync_type == 'stagiaires':
            result = sync_service.sync_all_stagiaires()
        elif sync_type == 'formations':
            # Implement formation sync
            result = {'message': 'Formation sync not implemented yet'}
        else:
            # Sync all
            stagiaires_result = sync_service.sync_all_stagiaires()
            result = {
                'stagiaires': stagiaires_result,
                'formations': {'message': 'Not implemented'}
            }
        
        return jsonify({
            'status': 'success',
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@wedof_api_bp.route('/integrations/wedof/stagiaires', methods=['GET'])
@jwt_required()
def get_wedof_stagiaires():
    """Get stagiaires from Wedof"""
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    try:
        client = WedofAPIClient()
        result = client.get_stagiaires(page=page, per_page=per_page)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wedof_api_bp.route('/integrations/wedof/formations', methods=['GET'])
@jwt_required()
def get_wedof_formations():
    """Get formations from Wedof"""
    
    try:
        client = WedofAPIClient()
        result = client.get_formations()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wedof_api_bp.route('/integrations/wedof/bilans/ai-analysis', methods=['POST'])
@jwt_required()
def create_ai_analysis():
    """Create AI analysis for a bilan"""
    
    bilan_id = request.json.get('bilan_id')
    if not bilan_id:
        return jsonify({'error': 'bilan_id required'}), 400
    
    options = {
        'analysis_types': request.json.get('analysis_types', [
            'competency_prediction',
            'learning_recommendations',
            'career_matching'
        ]),
        'include_market_data': request.json.get('include_market_data', True),
        'projection_months': request.json.get('projection_months', 12)
    }
    
    try:
        client = WedofAPIClient()
        result = client.generate_ai_analysis(bilan_id, options)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 1.5 Update Environment Configuration

Add to `.env` files:

```env
# Wedof API Configuration
WEDOF_API_KEY=your_api_key_here
WEDOF_API_URL=https://api.wedof.fr/v2
WEDOF_ORG_ID=your_organization_id
WEDOF_WEBHOOK_SECRET=your_webhook_secret

# Sync Configuration
WEDOF_SYNC_ENABLED=true
WEDOF_SYNC_INTERVAL=3600  # seconds
```

## 2. Frontend Implementation

### 2.1 Create Wedof API Service

Create `/client/src/services/wedofService.js`:

```javascript
import axios from 'axios';

class WedofService {
  constructor() {
    this.baseURL = '/api/integrations/wedof';
  }

  async getStatus() {
    const response = await axios.get(`${this.baseURL}/status`);
    return response.data;
  }

  async syncData(type = 'all') {
    const response = await axios.post(`${this.baseURL}/sync`, { type });
    return response.data;
  }

  async getStagiaires(page = 1, perPage = 20) {
    const response = await axios.get(`${this.baseURL}/stagiaires`, {
      params: { page, per_page: perPage }
    });
    return response.data;
  }

  async getFormations() {
    const response = await axios.get(`${this.baseURL}/formations`);
    return response.data;
  }

  async createAIAnalysis(bilanId, options = {}) {
    const response = await axios.post(`${this.baseURL}/bilans/ai-analysis`, {
      bilan_id: bilanId,
      ...options
    });
    return response.data;
  }
}

export default new WedofService();
```

### 2.2 Update Integration Page

Update the existing `/client/src/pages/integrations/WedofIntegrationPage.jsx` to use the real API.

## 3. Database Updates

### 3.1 Add External ID Fields

Create migration to add external_id fields:

```python
"""Add external_id fields for Wedof integration

Revision ID: xxx
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('beneficiaries', sa.Column('external_id', sa.String(100), nullable=True))
    op.add_column('programs', sa.Column('external_id', sa.String(100), nullable=True))
    op.add_column('evaluations', sa.Column('external_id', sa.String(100), nullable=True))
    op.add_column('documents', sa.Column('external_id', sa.String(100), nullable=True))
    
    op.create_index('idx_beneficiaries_external_id', 'beneficiaries', ['external_id'])
    op.create_index('idx_programs_external_id', 'programs', ['external_id'])

def downgrade():
    op.drop_index('idx_beneficiaries_external_id', 'beneficiaries')
    op.drop_index('idx_programs_external_id', 'programs')
    
    op.drop_column('beneficiaries', 'external_id')
    op.drop_column('programs', 'external_id')
    op.drop_column('evaluations', 'external_id')
    op.drop_column('documents', 'external_id')
```

## 4. Testing

### 4.1 Test Wedof Client

Create `/server/tests/test_wedof_integration.py`:

```python
import pytest
from unittest.mock import Mock, patch
from server.integrations.wedof.client import WedofAPIClient
from server.integrations.wedof.sync_service import WedofSyncService

class TestWedofClient:
    def test_api_client_initialization(self):
        client = WedofAPIClient(api_key='test_key')
        assert client.api_key == 'test_key'
        assert 'Bearer test_key' in client.session.headers['Authorization']
    
    @patch('requests.Session.request')
    def test_get_stagiaires(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [{'id': 'stag_123', 'nom': 'Test'}],
            'meta': {'total_count': 1}
        }
        mock_request.return_value = mock_response
        
        client = WedofAPIClient(api_key='test_key')
        result = client.get_stagiaires()
        
        assert len(result['data']) == 1
        assert result['data'][0]['id'] == 'stag_123'

class TestSyncService:
    # Add sync service tests
    pass
```

## 5. Deployment Checklist

- [ ] Set up Wedof API credentials in production environment
- [ ] Configure webhook URL in Wedof dashboard
- [ ] Test webhook signature verification
- [ ] Set up monitoring for sync failures
- [ ] Configure sync schedule (cron job or scheduler)
- [ ] Test full sync process with sample data
- [ ] Document API rate limits and implement throttling
- [ ] Set up error alerting for failed syncs
- [ ] Create backup strategy for synced data
- [ ] Test rollback procedures

## 6. Security Considerations

1. **API Key Storage**: Never commit API keys to version control
2. **Webhook Security**: Always verify webhook signatures
3. **Data Privacy**: Ensure GDPR compliance when syncing personal data
4. **Access Control**: Limit API access to authorized users only
5. **Audit Logging**: Log all sync operations for compliance
6. **Encryption**: Use HTTPS for all API communications
7. **Rate Limiting**: Implement rate limiting to prevent abuse

## 7. Monitoring & Maintenance

1. **Health Checks**: Regular API connectivity tests
2. **Sync Monitoring**: Track success/failure rates
3. **Performance Metrics**: Monitor API response times
4. **Error Tracking**: Log and alert on sync errors
5. **Data Integrity**: Regular validation of synced data
6. **Version Updates**: Monitor Wedof API changes
