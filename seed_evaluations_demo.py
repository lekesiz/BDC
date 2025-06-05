#!/usr/bin/env python3
"""
Demo evaluation and test data seeder for BDC system.
Creates comprehensive test data for evaluations page.
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Set environment to avoid conflicts
os.environ['FLASK_ENV'] = 'development'

# Direct database connection approach
import psycopg2
from psycopg2.extras import RealDictCursor
import json

def create_demo_evaluations():
    """Create comprehensive demo evaluations and test data."""
    
    # Database connection
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            database=os.getenv('POSTGRES_DB', 'bdc_test'),
            user=os.getenv('POSTGRES_USER', 'bdc_user'),
            password=os.getenv('POSTGRES_PASSWORD'),
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        print("🚀 Creating demo evaluations and test data...")
        
        # Get existing data
        cursor.execute("SELECT * FROM tenants LIMIT 1")
        tenant = cursor.fetchone()
        if not tenant:
            print("❌ No tenant found. Please run the main demo data seeder first.")
            return
            
        cursor.execute("SELECT * FROM users WHERE role = 'trainer' LIMIT 1")
        trainer = cursor.fetchone()
        cursor.execute("SELECT * FROM users WHERE role = 'tenant_admin' LIMIT 1") 
        admin = cursor.fetchone()
        cursor.execute("SELECT * FROM beneficiaries LIMIT 10")
        beneficiaries = cursor.fetchall()
        
        if not trainer or not admin:
            print("❌ No trainer or admin found. Please run the main demo data seeder first.")
            return
            
        print(f"📊 Found {len(beneficiaries)} beneficiaries for test data")
        
        # Demo evaluation templates
        evaluation_templates = [
            {
                'title': 'JavaScript Temel Bilgi Testi',
                'description': 'JavaScript programlama dilinin temel kavramlarını değerlendiren kapsamlı test.',
                'type': 'assessment',
                'category': 'programming',
                'time_limit': 45,
                'passing_score': 70.0,
                'is_randomized': True,
                'max_attempts': 2,
                'status': 'active',
                'questions': [
                    {
                        'text': 'JavaScript\'te değişken tanımlamak için hangi anahtar kelimeler kullanılır?',
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
                        'difficulty': 'medium',
                        'explanation': 'Object bir referans tipidir, primitif değildir.'
                    },
                    {
                        'text': 'JavaScript\'te bir fonksiyon nasıl tanımlanır?',
                        'type': 'text',
                        'points': 10.0,
                        'difficulty': 'medium',
                        'explanation': 'function fonksiyonAdı() {...} veya const fonksiyonAdı = () => {...} şeklinde tanımlanır.'
                    },
                    {
                        'text': 'JavaScript bir dinamik tipli dildir.',
                        'type': 'true_false',
                        'correct_answer': True,
                        'points': 3.0,
                        'difficulty': 'easy',
                        'explanation': 'JavaScript dinamik tipli bir dildir, değişken tipleri runtime\'da belirlenir.'
                    }
                ]
            },
            {
                'title': 'Python Programlama Değerlendirmesi',
                'description': 'Python programlama becerileri ve temel kavramların değerlendirilmesi.',
                'type': 'quiz',
                'category': 'programming',
                'time_limit': 60,
                'passing_score': 75.0,
                'is_randomized': False,
                'max_attempts': 3,
                'status': 'active',
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
                        'difficulty': 'medium',
                        'explanation': 'Liste değiştirilebilir (mutable), tuple değiştirilemez (immutable) veri yapılarıdır.'
                    },
                    {
                        'text': 'Python\'da bir dictionary nasıl oluşturulur?',
                        'type': 'text',
                        'points': 12.0,
                        'difficulty': 'easy',
                        'explanation': 'dict = {\"key\": \"value\"} veya dict = dict() şeklinde oluşturulur.'
                    }
                ]
            },
            {
                'title': 'Web Geliştirme Temel Kavramları',
                'description': 'HTML, CSS ve web teknolojileri hakkında temel bilgi değerlendirmesi.',
                'type': 'assessment',
                'category': 'web-development',
                'time_limit': 30,
                'passing_score': 65.0,
                'is_randomized': True,
                'max_attempts': 1,
                'status': 'active',
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
                    },
                    {
                        'text': 'CSS\'de bir elementin arka plan rengini değiştirmek için hangi özellik kullanılır?',
                        'type': 'text',
                        'points': 6.0,
                        'difficulty': 'easy',
                        'explanation': 'background-color özelliği kullanılır.'
                    }
                ]
            },
            {
                'title': 'Veri Analizi ve İstatistik Testi',
                'description': 'Veri analizi teknikleri ve temel istatistik kavramları değerlendirmesi.',
                'type': 'assessment',
                'category': 'data-analysis',
                'time_limit': 90,
                'passing_score': 80.0,
                'is_randomized': False,
                'max_attempts': 2,
                'status': 'active',
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
                'title': 'Dijital Pazarlama Temelleri',
                'description': 'Dijital pazarlama stratejileri ve araçları hakkında değerlendirme.',
                'type': 'quiz',
                'category': 'marketing',
                'time_limit': 40,
                'passing_score': 70.0,
                'is_randomized': True,
                'max_attempts': 3,
                'status': 'active',
                'questions': [
                    {
                        'text': 'SEO\'nun açılımı nedir?',
                        'type': 'text',
                        'points': 5.0,
                        'difficulty': 'easy',
                        'explanation': 'Search Engine Optimization (Arama Motoru Optimizasyonu)'
                    },
                    {
                        'text': 'Sosyal medya pazarlaması B2B şirketler için önemli değildir.',
                        'type': 'true_false',
                        'correct_answer': False,
                        'points': 5.0,
                        'difficulty': 'medium',
                        'explanation': 'Sosyal medya pazarlaması B2B şirketler için de çok önemlidir.'
                    }
                ]
            },
            {
                'title': 'Proje Yönetimi Beceri Testi',
                'description': 'Proje yönetimi metodolojileri ve araçları değerlendirmesi.',
                'type': 'assessment',
                'category': 'project-management',
                'time_limit': 50,
                'passing_score': 75.0,
                'is_randomized': False,
                'max_attempts': 2,
                'status': 'draft',
                'questions': [
                    {
                        'text': 'Agile metodolojisinin temel prensipleri nelerdir?',
                        'type': 'text',
                        'points': 15.0,
                        'difficulty': 'hard',
                        'explanation': 'Müşteri işbirliği, değişime yanıt verme, çalışan yazılım, bireyler ve etkileşimler.'
                    }
                ]
            }
        ]
        
        created_evaluations = []
        
        # Create evaluations
        for eval_data in evaluation_templates:
            try:
                # Create test set
                cursor.execute("""
                    INSERT INTO test_sets (title, description, type, category, time_limit, passing_score, 
                                         is_randomized, max_attempts, status, tenant_id, creator_id, 
                                         created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    eval_data['title'], eval_data['description'], eval_data['type'],
                    eval_data['category'], eval_data['time_limit'], eval_data['passing_score'],
                    eval_data['is_randomized'], eval_data['max_attempts'], eval_data['status'],
                    tenant['id'], trainer['id'], datetime.utcnow(), datetime.utcnow()
                ))
                
                test_set_id = cursor.fetchone()['id']
                
                # Create questions
                for i, q_data in enumerate(eval_data['questions']):
                    options = None
                    correct_answer = None
                    
                    # Set question options and correct answers based on type
                    if q_data['type'] == 'multiple_choice':
                        options = json.dumps(q_data['options'])
                        # Find correct answer index
                        for idx, option in enumerate(q_data['options']):
                            if option['is_correct']:
                                correct_answer = json.dumps(idx)
                                break
                    elif q_data['type'] == 'true_false':
                        options = json.dumps([{'text': 'Doğru'}, {'text': 'Yanlış'}])
                        correct_answer = json.dumps(0 if q_data['correct_answer'] else 1)
                    elif q_data['type'] == 'text':
                        correct_answer = json.dumps(q_data.get('sample_answer', 'Sample answer'))
                    
                    cursor.execute("""
                        INSERT INTO questions (test_set_id, text, type, options, correct_answer, 
                                             explanation, points, difficulty, "order", created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        test_set_id, q_data['text'], q_data['type'], options, correct_answer,
                        q_data.get('explanation', ''), q_data['points'], q_data['difficulty'],
                        i + 1, datetime.utcnow(), datetime.utcnow()
                    ))
                
                created_evaluations.append({'id': test_set_id, 'title': eval_data['title'], 
                                          'status': eval_data['status'], 'time_limit': eval_data['time_limit'],
                                          'passing_score': eval_data['passing_score']})
                print(f"✅ Created evaluation: {eval_data['title']}")
                
            except Exception as e:
                print(f"❌ Error creating evaluation {eval_data['title']}: {str(e)}")
                continue
        
        # Create test sessions and responses for some evaluations
        if beneficiaries and created_evaluations:
            print("\n📝 Creating test sessions and responses...")
            
            # Create completed test sessions
            for eval in created_evaluations[:4]:  # Only for first 4 evaluations
                if eval['status'] != 'active':
                    continue
                    
                # Create sessions for random beneficiaries
                session_count = random.randint(3, min(8, len(beneficiaries)))
                selected_beneficiaries = random.sample(beneficiaries, session_count)
                
                for beneficiary in selected_beneficiaries:
                    try:
                        # Create test session
                        session_start = datetime.utcnow() - timedelta(
                            days=random.randint(1, 30),
                            hours=random.randint(0, 23),
                            minutes=random.randint(0, 59)
                        )
                        
                        session_duration = random.randint(
                            int(eval['time_limit'] * 0.5) if eval['time_limit'] else 20,
                            eval['time_limit'] if eval['time_limit'] else 60
                        )
                        
                        session_end = session_start + timedelta(minutes=session_duration)
                        
                        cursor.execute("""
                            INSERT INTO test_sessions (test_set_id, beneficiary_id, start_time, end_time, 
                                                     time_spent, status, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id
                        """, (
                            eval['id'], beneficiary['id'], session_start, session_end,
                            session_duration * 60, 'completed', datetime.utcnow(), datetime.utcnow()
                        ))
                        
                        session_id = cursor.fetchone()['id']
                        
                        # Get questions for this evaluation
                        cursor.execute("SELECT * FROM questions WHERE test_set_id = %s ORDER BY \"order\"", (eval['id'],))
                        questions = cursor.fetchall()
                        
                        total_score = 0
                        max_possible_score = sum(float(q['points']) for q in questions)
                        
                        for question in questions:
                            # Simulate answer accuracy (70-95% chance of correct answer)
                            is_correct = random.random() < random.uniform(0.70, 0.95)
                            score = float(question['points']) if is_correct else 0
                            total_score += score
                            
                            # Generate realistic answer based on question type
                            answer = None
                            if question['type'] == 'multiple_choice':
                                correct_idx = json.loads(question['correct_answer']) if question['correct_answer'] else 0
                                if is_correct:
                                    answer = correct_idx
                                else:
                                    # Random wrong answer
                                    options = json.loads(question['options']) if question['options'] else []
                                    wrong_options = [i for i in range(len(options)) if i != correct_idx]
                                    answer = random.choice(wrong_options) if wrong_options else 0
                            elif question['type'] == 'true_false':
                                correct_answer = json.loads(question['correct_answer']) if question['correct_answer'] else 0
                                answer = correct_answer if is_correct else (1 - correct_answer)
                            elif question['type'] == 'text':
                                sample_answers = [
                                    'Bu bir örnek cevaptır.',
                                    'Kısa ve öz bir açıklama.',
                                    'Detaylı bir cevap metni.',
                                    'Uygun bir yanıt örneği.'
                                ]
                                answer = random.choice(sample_answers)
                            
                            cursor.execute("""
                                INSERT INTO responses (session_id, question_id, answer, is_correct, score,
                                                     start_time, time_spent, created_at, updated_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                session_id, question['id'], json.dumps(answer), is_correct, score,
                                session_start + timedelta(minutes=random.randint(0, session_duration-1)),
                                random.randint(30, 180), datetime.utcnow(), datetime.utcnow()
                            ))
                        
                        # Update session with final scores
                        passed = total_score >= (max_possible_score * eval['passing_score'] / 100.0)
                        
                        cursor.execute("""
                            UPDATE test_sessions 
                            SET score = %s, max_score = %s, passed = %s, updated_at = %s
                            WHERE id = %s
                        """, (total_score, max_possible_score, passed, datetime.utcnow(), session_id))
                        
                        # Create AI feedback for some sessions
                        if random.random() < 0.6:  # 60% chance of AI feedback
                            strengths = [
                                "Temel kavramların iyi anlaşılması",
                                "Sistematik yaklaşım", 
                                "Zaman yönetimi"
                            ] if passed else [
                                "Çaba gösterme",
                                "Temel anlayış"
                            ]
                            
                            areas_to_improve = [
                                "İleri düzey konular",
                                "Pratik uygulamalar"
                            ] if passed else [
                                "Temel kavramlar",
                                "Konu anlaşılması",
                                "Daha fazla çalışma"
                            ]
                            
                            recommendations = [
                                "İleri düzey kurslara katılım",
                                "Pratik projeler yapma",
                                "Peer learning gruplarına katılım"
                            ] if passed else [
                                "Temel konuları tekrar etme",
                                "Ek kaynaklardan çalışma",
                                "Mentor desteği alma"
                            ]
                            
                            next_steps = [
                                "Sonraki seviye eğitimlere geçiş",
                                "Uzmanlık alanı seçimi"
                            ] if passed else [
                                "Temel eğitimleri tamamlama",
                                "Konu tekrarı yapme"
                            ]
                            
                            cursor.execute("""
                                INSERT INTO ai_feedback (session_id, summary, strengths, areas_to_improve,
                                                       recommendations, next_steps, status, approved_by,
                                                       created_at, updated_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                session_id,
                                f"Genel performans {'başarılı' if passed else 'geliştirilmesi gereken'} düzeydedir.",
                                json.dumps(strengths),
                                json.dumps(areas_to_improve),
                                json.dumps(recommendations),
                                json.dumps(next_steps),
                                'approved',
                                trainer['id'],
                                datetime.utcnow(),
                                datetime.utcnow()
                            ))
                        
                        print(f"  ✅ Created session for {beneficiary['first_name']} {beneficiary['last_name']} - Score: {total_score:.1f}/{max_possible_score:.1f}")
                        
                    except Exception as e:
                        print(f"  ❌ Error creating session for {beneficiary['first_name']}: {str(e)}")
                        continue
        
        # Commit all changes
        try:
            conn.commit()
            print(f"\n🎉 Successfully created {len(created_evaluations)} evaluations with test data!")
            
            # Print summary
            print("\n📊 Demo Evaluations Summary:")
            for eval in created_evaluations:
                cursor.execute("SELECT COUNT(*) as count FROM questions WHERE test_set_id = %s", (eval['id'],))
                question_count = cursor.fetchone()['count']
                cursor.execute("SELECT COUNT(*) as count FROM test_sessions WHERE test_set_id = %s", (eval['id'],))
                session_count = cursor.fetchone()['count']
                print(f"  • {eval['title']}")
                print(f"    - Questions: {question_count}")
                print(f"    - Test Sessions: {session_count}")
                print(f"    - Status: {eval['status']}")
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Error committing changes: {str(e)}")
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")

if __name__ == '__main__':
    create_demo_evaluations()