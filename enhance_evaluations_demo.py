#!/usr/bin/env python3
"""
Enhanced demo evaluation data for BDC system.
Updates existing evaluations with rich content.
"""

import sys
import random
from datetime import datetime, timedelta

# Set up Flask app context
sys.path.append('./server')
from server.app import create_app
from server.app.extensions import db
from server.app.models.test import TestSet, Question, TestSession, Response, AIFeedback
from server.app.models.user import User
from server.app.models.beneficiary import Beneficiary

def enhance_evaluations():
    """Enhance existing evaluations with better data."""
    
    app = create_app()
    
    with app.app_context():
        print("🚀 Enhancing evaluations with rich demo data...")
        
        # Get existing data
        trainer = User.query.filter_by(role='trainer').first()
        beneficiaries = Beneficiary.query.limit(15).all()
        
        # Enhanced evaluation data
        enhanced_data = [
            {
                'id': 1,
                'title': 'JavaScript Temel Bilgiler Testi',
                'description': 'JavaScript programlama dilinin temel kavramlarını ve syntax\'ını değerlendiren kapsamlı test.',
                'type': 'assessment',
                'category': 'programming',
                'questions': [
                    {
                        'text': 'JavaScript\'te değişken tanımlamak için kullanılan anahtar kelimeler hangileridir?',
                        'type': 'multiple_choice',
                        'options': [
                            {'text': 'var, let, const', 'is_correct': True},
                            {'text': 'variable, declare, define', 'is_correct': False},
                            {'text': 'int, string, boolean', 'is_correct': False},
                            {'text': 'dim, set, new', 'is_correct': False}
                        ],
                        'points': 5.0,
                        'difficulty': 'easy',
                        'explanation': 'JavaScript\'te değişken tanımlamak için var, let ve const anahtar kelimeleri kullanılır.'
                    },
                    {
                        'text': 'Aşağıdaki JavaScript veri tiplerinden hangisi primitif değildir?',
                        'type': 'multiple_choice',
                        'options': [
                            {'text': 'string', 'is_correct': False},
                            {'text': 'number', 'is_correct': False},
                            {'text': 'object', 'is_correct': True},
                            {'text': 'boolean', 'is_correct': False}
                        ],
                        'points': 5.0,
                        'difficulty': 'medium'
                    }
                ]
            },
            {
                'id': 2,
                'title': 'Python Programlama Beceri Değerlendirmesi',
                'description': 'Python programlama becerileri ve temel kavramların kapsamlı değerlendirilmesi.',
                'type': 'quiz',
                'category': 'programming',
                'questions': [
                    {
                        'text': 'Python\'da liste (list) ve tuple arasındaki temel fark nedir?',
                        'type': 'multiple_choice',
                        'options': [
                            {'text': 'Liste mutable, tuple immutable\'dır', 'is_correct': True},
                            {'text': 'Liste string, tuple sayı tutar', 'is_correct': False},
                            {'text': 'Liste hızlı, tuple yavaştır', 'is_correct': False},
                            {'text': 'Hiçbir fark yoktur', 'is_correct': False}
                        ],
                        'points': 8.0,
                        'difficulty': 'medium'
                    }
                ]
            },
            {
                'id': 3,
                'title': 'Web Geliştirme Temel Kavramları',
                'description': 'HTML, CSS ve web teknolojileri hakkında temel bilgi değerlendirmesi.',
                'type': 'assessment',
                'category': 'web-development',
                'questions': [
                    {
                        'text': 'HTML\'de bir bağlantı (link) oluşturmak için hangi etiket kullanılır?',
                        'type': 'multiple_choice',
                        'options': [
                            {'text': '<link>', 'is_correct': False},
                            {'text': '<a>', 'is_correct': True},
                            {'text': '<href>', 'is_correct': False},
                            {'text': '<url>', 'is_correct': False}
                        ],
                        'points': 4.0,
                        'difficulty': 'easy'
                    }
                ]
            },
            {
                'id': 4,
                'title': 'Veri Analizi ve İstatistik Testi',
                'description': 'Veri analizi teknikleri ve temel istatistik kavramları değerlendirmesi.',
                'type': 'assessment',
                'category': 'data-analysis',
                'questions': [
                    {
                        'text': 'Veri setinin merkezi eğilim ölçüleri hangileridir?',
                        'type': 'multiple_choice',
                        'options': [
                            {'text': 'Ortalama, medyan, mod', 'is_correct': True},
                            {'text': 'Varyans, standart sapma, aralık', 'is_correct': False},
                            {'text': 'Minimum, maksimum, çeyreklik', 'is_correct': False},
                            {'text': 'Korelasyon, regresyon, kovaryans', 'is_correct': False}
                        ],
                        'points': 10.0,
                        'difficulty': 'medium'
                    }
                ]
            },
            {
                'id': 5,
                'title': 'Dijital Pazarlama Temelleri',
                'description': 'Dijital pazarlama stratejileri ve araçları hakkında değerlendirme.',
                'type': 'quiz',
                'category': 'marketing',
                'questions': [
                    {
                        'text': 'SEO\'nun açılımı nedir?',
                        'type': 'text',
                        'points': 5.0,
                        'difficulty': 'easy',
                        'explanation': 'Search Engine Optimization (Arama Motoru Optimizasyonu)'
                    }
                ]
            },
            {
                'id': 6,
                'title': 'Proje Yönetimi Beceri Testi',
                'description': 'Proje yönetimi metodolojileri ve araçları değerlendirmesi.',
                'type': 'assessment',
                'category': 'project-management',
                'questions': [
                    {
                        'text': 'Agile metodolojisinin temel prensipleri nelerdir?',
                        'type': 'text',
                        'points': 15.0,
                        'difficulty': 'hard',
                        'explanation': 'Müşteri işbirliği, değişime yanıt verme, çalışan yazılım, bireyler ve etkileşimler.'
                    },
                    {
                        'text': 'Scrum metodolojisinde sprint süresi genellikle kaç haftadır?',
                        'type': 'multiple_choice',
                        'options': [
                            {'text': '1-2 hafta', 'is_correct': True},
                            {'text': '3-4 hafta', 'is_correct': False},
                            {'text': '5-6 hafta', 'is_correct': False},
                            {'text': '7-8 hafta', 'is_correct': False}
                        ],
                        'points': 8.0,
                        'difficulty': 'medium'
                    }
                ]
            },
            {
                'id': 7,
                'title': 'Database ve SQL Temel Bilgiler',
                'description': 'Veritabanı tasarımı ve SQL sorguları hakkında değerlendirme.',
                'type': 'assessment',
                'category': 'database',
                'questions': [
                    {
                        'text': 'SQL\'de tablolardan veri seçmek için hangi komut kullanılır?',
                        'type': 'multiple_choice',
                        'options': [
                            {'text': 'GET', 'is_correct': False},
                            {'text': 'SELECT', 'is_correct': True},
                            {'text': 'FETCH', 'is_correct': False},
                            {'text': 'RETRIEVE', 'is_correct': False}
                        ],
                        'points': 5.0,
                        'difficulty': 'easy'
                    }
                ]
            },
            {
                'id': 8,
                'title': 'React.js Frontend Geliştirme',
                'description': 'React.js kütüphanesi ve modern frontend geliştirme teknikleri.',
                'type': 'quiz',
                'category': 'frontend',
                'questions': [
                    {
                        'text': 'React\'te component state\'i yönetmek için hangi hook kullanılır?',
                        'type': 'multiple_choice',
                        'options': [
                            {'text': 'useEffect', 'is_correct': False},
                            {'text': 'useState', 'is_correct': True},
                            {'text': 'useContext', 'is_correct': False},
                            {'text': 'useReducer', 'is_correct': False}
                        ],
                        'points': 6.0,
                        'difficulty': 'medium'
                    }
                ]
            }
        ]
        
        # Update existing evaluations
        for eval_data in enhanced_data:
            try:
                test_set = TestSet.query.get(eval_data['id'])
                if test_set:
                    # Update test set properties
                    test_set.title = eval_data['title']
                    test_set.description = eval_data['description']
                    test_set.type = eval_data['type']
                    test_set.category = eval_data['category']
                    
                    # Delete existing questions
                    Question.query.filter_by(test_set_id=test_set.id).delete()
                    
                    # Create new questions
                    for i, q_data in enumerate(eval_data['questions']):
                        question = Question(
                            test_set_id=test_set.id,
                            text=q_data['text'],
                            type=q_data['type'],
                            points=q_data['points'],
                            difficulty=q_data['difficulty'],
                            order=i + 1,
                            explanation=q_data.get('explanation', '')
                        )
                        
                        # Set question options and correct answers
                        if q_data['type'] == 'multiple_choice':
                            question.options = q_data['options']
                            # Find correct answer index
                            for idx, option in enumerate(q_data['options']):
                                if option['is_correct']:
                                    question.correct_answer = idx
                                    break
                        elif q_data['type'] == 'text':
                            question.correct_answer = q_data.get('sample_answer', 'Sample answer')
                        
                        db.session.add(question)
                    
                    print(f"✅ Enhanced evaluation: {eval_data['title']}")
                
            except Exception as e:
                print(f"❌ Error enhancing evaluation {eval_data['id']}: {str(e)}")
                continue
        
        # Create test sessions for some evaluations
        if beneficiaries:
            print("\n📝 Creating test sessions...")
            
            for eval_id in [1, 2, 3, 4, 5]:  # Create sessions for first 5 evaluations
                test_set = TestSet.query.get(eval_id)
                if not test_set:
                    continue
                    
                # Create sessions for random beneficiaries
                session_count = random.randint(4, min(10, len(beneficiaries)))
                selected_beneficiaries = random.sample(beneficiaries, session_count)
                
                for beneficiary in selected_beneficiaries:
                    try:
                        # Create test session
                        session_start = datetime.utcnow() - timedelta(
                            days=random.randint(1, 30),
                            hours=random.randint(0, 23),
                            minutes=random.randint(0, 59)
                        )
                        
                        session_duration = random.randint(20, test_set.time_limit or 60)
                        
                        session = TestSession(
                            test_set_id=test_set.id,
                            beneficiary_id=beneficiary.id,
                            start_time=session_start,
                            end_time=session_start + timedelta(minutes=session_duration),
                            time_spent=session_duration * 60,
                            status='completed'
                        )
                        
                        db.session.add(session)
                        db.session.flush()
                        
                        # Create responses
                        questions = Question.query.filter_by(test_set_id=test_set.id).all()
                        total_score = 0
                        max_possible_score = sum(q.points for q in questions)
                        
                        for question in questions:
                            # 70-90% accuracy simulation
                            is_correct = random.random() < random.uniform(0.70, 0.90)
                            score = question.points if is_correct else 0
                            total_score += score
                            
                            # Generate answer based on type
                            if question.type == 'multiple_choice':
                                if is_correct:
                                    answer = question.correct_answer
                                else:
                                    options_count = len(question.options) if question.options else 4
                                    wrong_options = [i for i in range(options_count) if i != question.correct_answer]
                                    answer = random.choice(wrong_options) if wrong_options else 0
                            elif question.type == 'text':
                                sample_answers = [
                                    'Detaylı bir açıklama yazısı.',
                                    'Kısa ve öz bir cevap.',
                                    'Kapsamlı bir yanıt metni.',
                                    'Uygun bir açıklama.'
                                ]
                                answer = random.choice(sample_answers)
                            else:
                                answer = question.correct_answer
                            
                            response = Response(
                                session_id=session.id,
                                question_id=question.id,
                                answer=answer,
                                is_correct=is_correct,
                                score=score,
                                start_time=session_start + timedelta(minutes=random.randint(0, session_duration-1)),
                                time_spent=random.randint(45, 300)
                            )
                            
                            db.session.add(response)
                        
                        # Update session scores
                        session.score = total_score
                        session.max_score = max_possible_score
                        session.passed = total_score >= (max_possible_score * test_set.passing_score / 100.0)
                        
                        # Create AI feedback (60% chance)
                        if random.random() < 0.6:
                            feedback = AIFeedback(
                                session_id=session.id,
                                summary=f"Genel performans {'başarılı' if session.passed else 'geliştirilmesi gereken'} seviyededir.",
                                strengths=[
                                    "Temel kavramları iyi anlıyor",
                                    "Sistematik düşünme becerisi",
                                    "Problem çözme yaklaşımı"
                                ] if session.passed else [
                                    "Çaba gösteriyor",
                                    "Temel motivasyon var"
                                ],
                                areas_to_improve=[
                                    "İleri seviye konular",
                                    "Uygulama becerileri"
                                ] if session.passed else [
                                    "Temel kavramlar",
                                    "Konu tekrarı",
                                    "Pratik yapma"
                                ],
                                recommendations=[
                                    "İleri düzey eğitimlere katılım",
                                    "Pratik projeler yapma",
                                    "Mentoring programına katılım"
                                ] if session.passed else [
                                    "Temel konuları tekrar etme",
                                    "Ek kaynaklar kullanma",
                                    "Bireysel destek alma"
                                ],
                                next_steps=[
                                    "Sonraki seviye modüllere geçiş",
                                    "Sertifikasyon programları"
                                ] if session.passed else [
                                    "Temel eğitimleri tamamlama",
                                    "Konu tekrarı yapma"
                                ],
                                status='approved',
                                approved_by=trainer.id if trainer else None
                            )
                            
                            db.session.add(feedback)
                        
                        print(f"  ✅ Session: {beneficiary.first_name} {beneficiary.last_name} - {total_score:.1f}/{max_possible_score:.1f}")
                        
                    except Exception as e:
                        print(f"  ❌ Error creating session: {str(e)}")
                        continue
        
        # Commit changes
        try:
            db.session.commit()
            print(f"\n🎉 Successfully enhanced evaluations with rich demo data!")
            
            # Print summary
            print("\n📊 Enhanced Evaluations Summary:")
            for eval_data in enhanced_data:
                test_set = TestSet.query.get(eval_data['id'])
                if test_set:
                    question_count = Question.query.filter_by(test_set_id=test_set.id).count()
                    session_count = TestSession.query.filter_by(test_set_id=test_set.id).count()
                    print(f"  • {test_set.title}")
                    print(f"    - Questions: {question_count}")
                    print(f"    - Sessions: {session_count}")
                    print(f"    - Category: {test_set.category}")
                    
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error committing changes: {str(e)}")

if __name__ == '__main__':
    enhance_evaluations()