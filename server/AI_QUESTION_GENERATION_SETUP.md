# AI-Powered Question Generation System Setup

## Overview

This comprehensive AI-powered question generation system enhances the assessment capabilities of the BDC system by automatically generating high-quality educational questions from various content sources.

## Features

### 🎯 Question Generation Capabilities
- **Multiple Question Types**: Multiple choice, true/false, fill-in-the-blank, short answer, essay, matching, and ordering questions
- **AI-Powered Generation**: Uses OpenAI GPT models for intelligent question creation
- **Quality Assessment**: Automatic scoring for clarity, relevance, and educational value
- **Difficulty Scaling**: Questions rated on 1-10 difficulty scale
- **Bloom's Taxonomy**: Questions categorized by cognitive levels (remember, understand, apply, analyze, evaluate, create)

### 📚 Content Processing
- **Multiple Input Types**: 
  - Text documents (PDF, Word, TXT)
  - Audio files (MP3, WAV, M4A) with transcription
  - Video files (MP4, AVI, MOV) with audio extraction
  - Web pages/URLs with content extraction
  - Direct text input
- **Content Analysis**: Automatic keyword extraction, topic identification, and readability assessment
- **NLP Enhancement**: Advanced text processing with spaCy and NLTK

### 🔍 Quality Assurance
- **Duplicate Detection**: AI-powered detection of similar questions using multiple algorithms
- **Human Review Workflow**: Approval/rejection system with reviewer notes
- **Performance Tracking**: Question usage analytics and performance metrics
- **Quality Scoring**: Multi-dimensional quality assessment

### 📊 Organization & Management
- **Question Banks**: Organize questions into categorized collections
- **Learning Objectives**: Align questions with specific educational goals
- **Advanced Filtering**: Search and filter by difficulty, topic, quality, and more
- **Export Capabilities**: Export questions in various formats (JSON, CSV)

### 📈 Analytics & Insights
- **Generation Analytics**: Track question creation success rates and costs
- **Usage Metrics**: Monitor question performance in assessments
- **Quality Trends**: Analyze quality improvements over time
- **Cost Tracking**: Monitor AI API usage and associated costs

## Installation & Setup

### 1. Dependencies

Add the following packages to your `requirements.txt`:

```txt
# AI and NLP Libraries
openai>=1.0.0
spacy>=3.6.0
nltk>=3.8.0
textstat>=0.7.0
scikit-learn>=1.3.0

# Content Processing
PyPDF2>=3.0.0
python-docx>=0.8.11
openai-whisper>=20231117
requests>=2.31.0
beautifulsoup4>=4.12.0

# File Handling
pathlib2>=2.3.7
mimetypes
```

Install the dependencies:
```bash
pip install -r requirements.txt
```

### 2. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### 3. Environment Variables

Add to your `.env` file:

```env
# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ORGANIZATION=your_openai_org_id_here  # Optional

# Question Generation Settings
AI_QUESTION_MAX_FILE_SIZE=52428800  # 50MB
AI_QUESTION_UPLOAD_FOLDER=/tmp/question_generation_uploads
AI_QUESTION_DEFAULT_MODEL=gpt-4
AI_QUESTION_MAX_CONTENT_LENGTH=50000

# Processing Settings
AI_QUESTION_MIN_WORD_COUNT=50
AI_QUESTION_MAX_WORD_COUNT=50000
AI_QUESTION_MIN_SENTENCES=3
```

### 4. Database Migration

Run the migration to create the necessary tables:

```bash
# Apply the migration
flask db upgrade

# Or manually run the migration script
python migrations/add_ai_question_generation.py
```

### 5. Initialize Default Data

Run the initialization to set up default question types and Bloom's taxonomy:

```bash
# Using the API endpoint (requires admin access)
curl -X POST http://localhost:5000/api/ai-questions/initialize \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json"

# Or using Python shell
python -c "
from app import create_app
from app.services.ai_question_generator_service import AIQuestionGeneratorService

app = create_app()
with app.app_context():
    service = AIQuestionGeneratorService()
    service.initialize_default_data()
    print('Default data initialized successfully')
"
```

## API Endpoints

### Content Management
- `GET /api/ai-questions/content-types` - Get available content types
- `POST /api/ai-questions/source-content` - Upload/create content
- `GET /api/ai-questions/source-content` - List source content
- `GET /api/ai-questions/source-content/{id}` - Get content details
- `POST /api/ai-questions/source-content/{id}/process` - Reprocess content

### Question Generation
- `GET /api/ai-questions/question-types` - Get available question types
- `GET /api/ai-questions/blooms-taxonomy` - Get Bloom's taxonomy levels
- `POST /api/ai-questions/generate` - Generate questions
- `GET /api/ai-questions/generation-status/{request_id}` - Check generation status
- `GET /api/ai-questions/questions` - List generated questions
- `GET /api/ai-questions/questions/{id}` - Get question details

### Review & Approval
- `POST /api/ai-questions/questions/{id}/approve` - Approve question
- `POST /api/ai-questions/questions/{id}/reject` - Reject question

### Question Banks
- `GET /api/ai-questions/question-banks` - List question banks
- `POST /api/ai-questions/question-banks` - Create question bank
- `POST /api/ai-questions/question-banks/{id}/questions` - Add question to bank
- `GET /api/ai-questions/question-banks/{id}/questions` - Get bank questions

### Analytics
- `GET /api/ai-questions/analytics` - Get analytics data
- `GET /api/ai-questions/analytics/summary` - Get summary statistics

### Quality Assurance
- `GET /api/ai-questions/duplicates` - Get detected duplicates
- `POST /api/ai-questions/duplicates/{id}/resolve` - Resolve duplicate

## Usage Examples

### 1. Upload and Process Content

```python
import requests

# Upload a PDF file
files = {'file': open('document.pdf', 'rb')}
data = {
    'title': 'Biology Chapter 1',
    'description': 'Introduction to Cell Biology',
    'content_type': 'document'
}

response = requests.post(
    'http://localhost:5000/api/ai-questions/source-content',
    files=files,
    data=data,
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

content = response.json()
print(f"Content ID: {content['content']['id']}")
```

### 2. Generate Questions

```python
import requests

# Generate questions from processed content
generation_request = {
    'source_content_id': 123,
    'question_count': 10,
    'question_types': [1, 2, 3],  # Multiple choice, true/false, short answer
    'difficulty_range': [3, 7],
    'language': 'en',
    'topic_focus': ['cells', 'biology'],
    'custom_instructions': 'Focus on fundamental concepts suitable for high school students'
}

response = requests.post(
    'http://localhost:5000/api/ai-questions/generate',
    json=generation_request,
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

result = response.json()
request_id = result['request_id']
print(f"Generation started with request ID: {request_id}")
```

### 3. Check Generation Status

```python
import requests
import time

# Poll for completion
while True:
    response = requests.get(
        f'http://localhost:5000/api/ai-questions/generation-status/{request_id}',
        headers={'Authorization': 'Bearer YOUR_TOKEN'}
    )
    
    status = response.json()
    print(f"Status: {status['status']}, Progress: {status['progress']:.1%}")
    
    if status['status'] == 'completed':
        print(f"Generated {status['questions_generated']} questions!")
        break
    elif status['status'] == 'failed':
        print(f"Generation failed: {status['error_message']}")
        break
    
    time.sleep(5)
```

### 4. Retrieve and Review Questions

```python
import requests

# Get generated questions
response = requests.get(
    f'http://localhost:5000/api/ai-questions/questions?request_id={request_id}',
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

questions = response.json()['questions']

for question in questions:
    print(f"Question: {question['question_text']}")
    print(f"Type: {question['question_type_id']}")
    print(f"Difficulty: {question['difficulty_level']}")
    print(f"Quality Score: {question['quality_score']}")
    print("---")
```

### 5. Approve Questions

```python
import requests

# Approve a high-quality question
question_id = 456
response = requests.post(
    f'http://localhost:5000/api/ai-questions/questions/{question_id}/approve',
    json={'notes': 'Excellent question with clear explanation'},
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

print("Question approved!")
```

## Integration with Existing Systems

### 1. Evaluation System Integration

```python
# In your evaluation service
from app.services.ai_question_generator_service import AIQuestionGeneratorService
from app.models.ai_question_generation import GeneratedQuestion

class EvaluationService:
    def create_test_from_question_bank(self, bank_id, question_count=10):
        """Create a test using questions from an AI-generated question bank."""
        
        # Get approved questions from bank
        questions = db.session.query(GeneratedQuestion).join(
            QuestionBankQuestion
        ).filter(
            QuestionBankQuestion.question_bank_id == bank_id,
            GeneratedQuestion.status == 'approved'
        ).order_by(func.random()).limit(question_count).all()
        
        # Convert to test format
        test_questions = []
        for q in questions:
            test_question = {
                'text': q.question_text,
                'type': q.question_type.name,
                'options': q.question_options,
                'correct_answer': q.correct_answer,
                'explanation': q.explanation,
                'difficulty': q.difficulty_level,
                'points': max(1.0, q.difficulty_level / 2)
            }
            test_questions.append(test_question)
        
        return test_questions
```

### 2. Content Management Integration

```python
# Automatically generate questions when new course materials are uploaded
from app.services.ai_question_generator_service import AIQuestionGeneratorService

class DocumentService:
    def upload_course_material(self, file_path, title, course_id):
        """Upload course material and automatically generate questions."""
        
        # Save document
        document = self.save_document(file_path, title, course_id)
        
        # Create source content for question generation
        ai_service = AIQuestionGeneratorService()
        source_content = ai_service.create_source_content(
            tenant_id=self.current_tenant_id,
            creator_id=self.current_user_id,
            title=f"Questions from {title}",
            description=f"Auto-generated from course material: {title}",
            content_type_name='document',
            file_path=file_path
        )
        
        # Schedule question generation
        self.schedule_question_generation(source_content.id, course_id)
        
        return document
```

### 3. Performance Analytics Integration

```python
# Track question performance in assessments
class TestSessionService:
    def complete_test_session(self, session_id):
        """Complete test session and update question performance."""
        
        session = TestSession.query.get(session_id)
        
        # Update AI-generated question performance
        for response in session.responses:
            if hasattr(response.question, 'generated_question_id'):
                generated_question = GeneratedQuestion.query.get(
                    response.question.generated_question_id
                )
                
                if generated_question:
                    # Update usage count
                    generated_question.times_used += 1
                    
                    # Update performance data
                    perf_data = generated_question.performance_data or {}
                    perf_data.setdefault('response_rates', []).append({
                        'correct': response.is_correct,
                        'time_spent': response.time_spent,
                        'session_id': session_id
                    })
                    
                    generated_question.performance_data = perf_data
        
        db.session.commit()
```

## Configuration Options

### Question Generation Settings

```python
# In your app configuration
class Config:
    # AI Question Generation
    AI_QUESTION_GENERATION_ENABLED = True
    AI_QUESTION_DEFAULT_MODEL = 'gpt-4'
    AI_QUESTION_BACKUP_MODEL = 'gpt-3.5-turbo'
    AI_QUESTION_MAX_TOKENS = 3000
    AI_QUESTION_TEMPERATURE = 0.7
    
    # Content Processing
    AI_QUESTION_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    AI_QUESTION_ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'docx', 'doc', 'mp3', 'wav', 'm4a', 'mp4', 'avi', 'mov'
    }
    
    # Quality Thresholds
    AI_QUESTION_MIN_QUALITY_SCORE = 0.6
    AI_QUESTION_DUPLICATE_THRESHOLD = 0.8
    AI_QUESTION_AUTO_APPROVE_THRESHOLD = 0.9
    
    # Rate Limiting
    AI_QUESTION_RATE_LIMIT = "10 per hour"
    AI_QUESTION_DAILY_LIMIT = 100
```

## Security Considerations

### 1. API Key Security
- Store OpenAI API keys securely using environment variables
- Rotate keys regularly
- Monitor API usage for unusual activity

### 2. Content Validation
- Validate uploaded content for malicious files
- Sanitize extracted text content
- Implement file size and type restrictions

### 3. Access Control
- Implement role-based access for question generation features
- Restrict admin functions to authorized users
- Log all question generation activities

### 4. Data Privacy
- Ensure compliance with data protection regulations
- Implement data retention policies
- Provide options for content deletion

## Monitoring & Maintenance

### 1. Health Checks
```bash
# Check system health
curl http://localhost:5000/api/ai-questions/health

# Get analytics summary
curl -H "Authorization: Bearer TOKEN" \
     http://localhost:5000/api/ai-questions/analytics/summary
```

### 2. Performance Monitoring
- Monitor API response times
- Track OpenAI API usage and costs
- Monitor question generation success rates
- Alert on high failure rates

### 3. Regular Maintenance
- Clean up old generated questions
- Archive completed generation requests
- Update AI models as needed
- Review and update question quality thresholds

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Check API key validity
   - Verify sufficient API credits
   - Check rate limiting

2. **Content Processing Failures**
   - Verify file format support
   - Check file corruption
   - Ensure sufficient disk space

3. **Low Question Quality**
   - Review source content quality
   - Adjust generation parameters
   - Update prompt templates

4. **Duplicate Detection Issues**
   - Tune similarity thresholds
   - Review detection algorithms
   - Check for content repetition

### Logs and Debugging

Enable detailed logging:
```python
import logging
logging.getLogger('app.services.ai_question_generator_service').setLevel(logging.DEBUG)
logging.getLogger('app.utils.content_processing').setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features
- Support for additional AI models (Claude, Gemini)
- Advanced question templates and customization
- Collaborative question review workflows
- Machine learning-based quality prediction
- Integration with external content sources
- Multi-language support
- Voice-to-question generation
- Image-based question generation

### API Extensions
- Batch question generation
- Question similarity search
- Advanced analytics and reporting
- Question recommendation engine
- Automated quality improvement suggestions

## Support

For technical support or questions about the AI Question Generation system:

1. Check the logs for error messages
2. Review the API documentation
3. Test with the health check endpoint
4. Verify all dependencies are installed correctly
5. Ensure OpenAI API access is working

The system is designed to be robust and handle various edge cases, but proper configuration and monitoring are essential for optimal performance.