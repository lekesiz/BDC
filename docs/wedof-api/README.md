# Wedof API Integration Documentation

## Overview
This documentation provides comprehensive information about integrating Wedof API with the BDC (Beneficiary Development Center) system for managing interns (stagiaires) and competency assessments (bilan de compétences).

## API Structure

### Base Information
- **Base URL**: `https://api.wedof.fr/v2/`
- **Authentication**: Bearer Token (API Key required)
- **Content-Type**: `application/json`
- **Rate Limits**: To be determined based on your subscription

## Documentation Files

1. **authentication.md** - API authentication and security
2. **endpoints/** - Detailed endpoint documentation
   - `stagiaires.md` - Trainee/Intern management
   - `formations.md` - Training program endpoints
   - `bilans.md` - Competency assessment endpoints
   - `documents.md` - Document management
   - `webhooks.md` - Webhook configuration
3. **data-models.md** - Data structures and schemas
4. **integration-guide.md** - Step-by-step integration guide
5. **examples.md** - Code examples and use cases

## Quick Start

1. Obtain your Wedof API key from your Wedof dashboard
2. Configure the API client with your credentials
3. Test the connection with a simple API call
4. Implement the required endpoints for your use case

## Key Features for BDC Integration

- **Stagiaire Management**: Create, update, and track interns
- **Formation Tracking**: Monitor training progress
- **Bilan de Compétences**: Manage competency assessments
- **Document Generation**: Automated certificate and report creation
- **Financial Integration**: Track funding and payments
- **Webhook Support**: Real-time updates for status changes

## Next Steps

1. Review the authentication documentation
2. Explore the endpoint documentation for your specific needs
3. Implement the API client in the BDC backend
4. Set up webhook handlers for real-time updates
5. Configure data synchronization schedules
