"""Initialize default conversation templates for the AI chat system."""

from app import create_app
from app.extensions import db
from app.models import ConversationTemplate

from app.utils.logging import logger

def create_default_templates():
    """Create default conversation templates."""
    
    templates = [
        # English templates
        {
            'name': 'General Support - English',
            'description': 'General support template for English speakers',
            'category': 'general',
            'language': 'en',
            'system_prompt': """You are a helpful assistant for the Beneficiary Development Center. 
            Provide accurate, friendly, and supportive responses to help beneficiaries with their queries. 
            Be empathetic, patient, and encouraging in your responses.""",
            'welcome_message': """Hello! I'm your AI assistant at the Beneficiary Development Center. 
            I'm here to help you with any questions or concerns you may have. How can I assist you today?""",
            'suggested_questions': [
                "What services does the center offer?",
                "How can I enroll in a program?",
                "I need help with my account"
            ],
            'priority': 10
        },
        {
            'name': 'Education Support - English',
            'description': 'Educational support template for English speakers',
            'category': 'education',
            'language': 'en',
            'system_prompt': """You are an educational support assistant helping beneficiaries with their learning journey. 
            Provide clear, encouraging, and helpful responses about educational topics, study strategies, 
            and program-related questions. Focus on building confidence and motivation.""",
            'welcome_message': """Hello! I'm your educational support assistant. 
            I'm here to help you with your learning journey, answer questions about programs, 
            and provide study tips. What would you like to know?""",
            'suggested_questions': [
                "What programs are available for me?",
                "How can I improve my study habits?",
                "I'm struggling with a topic, can you help?"
            ],
            'priority': 10
        },
        {
            'name': 'Appointment Scheduling - English',
            'description': 'Appointment scheduling template for English speakers',
            'category': 'appointment',
            'language': 'en',
            'system_prompt': """You are an appointment scheduling assistant. 
            Help users with booking, rescheduling, and managing their appointments. 
            Provide clear information about availability and appointment procedures. 
            Be efficient and helpful in managing scheduling requests.""",
            'welcome_message': """Hello! I'm your appointment scheduling assistant. 
            I can help you book new appointments, check your upcoming appointments, 
            or reschedule existing ones. What would you like to do?""",
            'suggested_questions': [
                "When is my next appointment?",
                "I need to schedule a new appointment",
                "Can I reschedule my appointment?"
            ],
            'priority': 10
        },
        {
            'name': 'Progress Tracking - English',
            'description': 'Progress tracking template for English speakers',
            'category': 'progress',
            'language': 'en',
            'system_prompt': """You are a progress tracking assistant. 
            Help beneficiaries understand their progress, achievements, and areas for improvement. 
            Be encouraging and constructive in your feedback. Celebrate achievements and provide 
            actionable advice for improvement.""",
            'welcome_message': """Hello! I'm here to help you track your progress and achievements. 
            I can show you how you're doing in your programs, highlight your accomplishments, 
            and suggest areas for improvement. What would you like to review?""",
            'suggested_questions': [
                "How am I doing in my programs?",
                "What have I achieved recently?",
                "What areas should I focus on?"
            ],
            'priority': 10
        },
        {
            'name': 'Assessment Support - English',
            'description': 'Assessment support template for English speakers',
            'category': 'assessment',
            'language': 'en',
            'system_prompt': """You are an assessment support assistant. 
            Help users understand assessment requirements, preparation strategies, 
            and provide guidance on improving their performance. Be supportive and 
            provide practical advice for assessment preparation.""",
            'welcome_message': """Hello! I'm your assessment support assistant. 
            I can help you prepare for assessments, understand requirements, 
            and provide tips for success. How can I help you with your assessments?""",
            'suggested_questions': [
                "When is my next assessment?",
                "How can I prepare for my assessment?",
                "What topics will be covered in the assessment?"
            ],
            'priority': 10
        },
        
        # Turkish templates
        {
            'name': 'Genel Destek - Türkçe',
            'description': 'Türkçe konuşanlar için genel destek şablonu',
            'category': 'general',
            'language': 'tr',
            'system_prompt': """Yararlanıcı Geliştirme Merkezi için yardımcı bir asistansınız. 
            Yararlanıcıların sorularına doğru, samimi ve destekleyici yanıtlar verin. 
            Yanıtlarınızda empatik, sabırlı ve cesaretlendirici olun.""",
            'welcome_message': """Merhaba! Ben Yararlanıcı Geliştirme Merkezi'ndeki AI asistanınızım. 
            Herhangi bir sorunuz veya endişeniz konusunda size yardımcı olmak için buradayım. 
            Size nasıl yardımcı olabilirim?""",
            'suggested_questions': [
                "Merkez hangi hizmetleri sunuyor?",
                "Bir programa nasıl kayıt olabilirim?",
                "Hesabımla ilgili yardıma ihtiyacım var"
            ],
            'priority': 10
        },
        {
            'name': 'Eğitim Desteği - Türkçe',
            'description': 'Türkçe konuşanlar için eğitim destek şablonu',
            'category': 'education',
            'language': 'tr',
            'system_prompt': """Yararlanıcıların öğrenme yolculuğunda onlara yardımcı olan bir eğitim destek asistanısınız. 
            Eğitim konuları, çalışma stratejileri ve programla ilgili sorular hakkında net, 
            cesaretlendirici ve yararlı yanıtlar verin. Güven ve motivasyon oluşturmaya odaklanın.""",
            'welcome_message': """Merhaba! Ben eğitim destek asistanınızım. 
            Öğrenme yolculuğunuzda size yardımcı olmak, programlar hakkında soruları yanıtlamak 
            ve çalışma ipuçları vermek için buradayım. Ne öğrenmek istersiniz?""",
            'suggested_questions': [
                "Benim için hangi programlar mevcut?",
                "Çalışma alışkanlıklarımı nasıl geliştirebilirim?",
                "Bir konuda zorlanıyorum, yardımcı olabilir misiniz?"
            ],
            'priority': 10
        },
        {
            'name': 'Randevu Planlama - Türkçe',
            'description': 'Türkçe konuşanlar için randevu planlama şablonu',
            'category': 'appointment',
            'language': 'tr',
            'system_prompt': """Randevu planlama asistanısınız. 
            Kullanıcılara randevu alma, yeniden planlama ve randevularını yönetme konusunda yardımcı olun. 
            Müsaitlik ve randevu prosedürleri hakkında net bilgiler verin. 
            Planlama taleplerini yönetmede verimli ve yardımcı olun.""",
            'welcome_message': """Merhaba! Ben randevu planlama asistanınızım. 
            Yeni randevular almanıza, yaklaşan randevularınızı kontrol etmenize 
            veya mevcut randevularınızı yeniden planlamanıza yardımcı olabilirim. Ne yapmak istersiniz?""",
            'suggested_questions': [
                "Bir sonraki randevum ne zaman?",
                "Yeni bir randevu almam gerekiyor",
                "Randevumu yeniden planlayabilir miyim?"
            ],
            'priority': 10
        },
        {
            'name': 'İlerleme Takibi - Türkçe',
            'description': 'Türkçe konuşanlar için ilerleme takibi şablonu',
            'category': 'progress',
            'language': 'tr',
            'system_prompt': """İlerleme takibi asistanısınız. 
            Yararlanıcıların ilerlemelerini, başarılarını ve geliştirilmesi gereken alanları anlamalarına yardımcı olun. 
            Geri bildirimlerinizde cesaretlendirici ve yapıcı olun. Başarıları kutlayın ve 
            gelişim için uygulanabilir tavsiyeler verin.""",
            'welcome_message': """Merhaba! İlerlemenizi ve başarılarınızı takip etmenize yardımcı olmak için buradayım. 
            Programlarınızda nasıl ilerlediğinizi gösterebilir, başarılarınızı vurgulayabilir 
            ve geliştirilmesi gereken alanları önerebilirim. Neyi gözden geçirmek istersiniz?""",
            'suggested_questions': [
                "Programlarımda nasıl gidiyorum?",
                "Son zamanlarda neler başardım?",
                "Hangi alanlara odaklanmalıyım?"
            ],
            'priority': 10
        },
        {
            'name': 'Değerlendirme Desteği - Türkçe',
            'description': 'Türkçe konuşanlar için değerlendirme destek şablonu',
            'category': 'assessment',
            'language': 'tr',
            'system_prompt': """Değerlendirme destek asistanısınız. 
            Kullanıcıların değerlendirme gereksinimlerini anlamalarına, hazırlık stratejilerine 
            ve performanslarını geliştirme konusunda rehberlik sağlayın. Destekleyici olun ve 
            değerlendirme hazırlığı için pratik tavsiyeler verin.""",
            'welcome_message': """Merhaba! Ben değerlendirme destek asistanınızım. 
            Değerlendirmelere hazırlanmanıza, gereksinimleri anlamanıza 
            ve başarı için ipuçları sağlamanıza yardımcı olabilirim. Değerlendirmelerinizle ilgili size nasıl yardımcı olabilirim?""",
            'suggested_questions': [
                "Bir sonraki değerlendirmem ne zaman?",
                "Değerlendirmeme nasıl hazırlanabilirim?",
                "Değerlendirmede hangi konular yer alacak?"
            ],
            'priority': 10
        }
    ]
    
    # Create templates
    for template_data in templates:
        # Check if template already exists
        existing = ConversationTemplate.query.filter_by(
            name=template_data['name'],
            category=template_data['category'],
            language=template_data['language']
        ).first()
        
        if not existing:
            template = ConversationTemplate(**template_data)
            db.session.add(template)
            logger.info(f"Created template: {template_data['name']}")
        else:
            logger.info(f"Template already exists: {template_data['name']}")
    
    db.session.commit()
    logger.info("Default templates initialization completed!")


def main():
    """Main function to run the initialization."""
    app = create_app()
    
    with app.app_context():
        logger.info("Initializing default conversation templates...")
        create_default_templates()


if __name__ == '__main__':
    main()