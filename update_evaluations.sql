-- Update existing evaluations with rich demo data

-- Update test set 1 - JavaScript
UPDATE test_sets SET 
    title = 'JavaScript Temel Bilgiler Testi',
    description = 'JavaScript programlama dilinin temel kavramlarını ve syntax''ını değerlendiren kapsamlı test.',
    type = 'assessment',
    category = 'programming'
WHERE id = 1;

-- Update test set 2 - Python
UPDATE test_sets SET 
    title = 'Python Programlama Beceri Değerlendirmesi',
    description = 'Python programlama becerileri ve temel kavramların kapsamlı değerlendirilmesi.',
    type = 'quiz',
    category = 'programming'
WHERE id = 2;

-- Update test set 3 - Web Development
UPDATE test_sets SET 
    title = 'Web Geliştirme Temel Kavramları',
    description = 'HTML, CSS ve web teknolojileri hakkında temel bilgi değerlendirmesi.',
    type = 'assessment',
    category = 'web-development'
WHERE id = 3;

-- Update test set 4 - Data Analysis
UPDATE test_sets SET 
    title = 'Veri Analizi ve İstatistik Testi',
    description = 'Veri analizi teknikleri ve temel istatistik kavramları değerlendirmesi.',
    type = 'assessment',
    category = 'data-analysis'
WHERE id = 4;

-- Update test set 5 - Digital Marketing
UPDATE test_sets SET 
    title = 'Dijital Pazarlama Temelleri',
    description = 'Dijital pazarlama stratejileri ve araçları hakkında değerlendirme.',
    type = 'quiz',
    category = 'marketing'
WHERE id = 5;

-- Update test set 6 - Project Management
UPDATE test_sets SET 
    title = 'Proje Yönetimi Beceri Testi',
    description = 'Proje yönetimi metodolojileri ve araçları değerlendirmesi.',
    type = 'assessment',
    category = 'project-management'
WHERE id = 6;

-- Update test set 7 - Database
UPDATE test_sets SET 
    title = 'Database ve SQL Temel Bilgiler',
    description = 'Veritabanı tasarımı ve SQL sorguları hakkında değerlendirme.',
    type = 'assessment',
    category = 'database'
WHERE id = 7;

-- Update test set 8 - React
UPDATE test_sets SET 
    title = 'React.js Frontend Geliştirme',
    description = 'React.js kütüphanesi ve modern frontend geliştirme teknikleri.',
    type = 'quiz',
    category = 'frontend'
WHERE id = 8;

-- Update test set 9 - UI/UX Design
UPDATE test_sets SET 
    title = 'UI/UX Tasarım Prensipleri',
    description = 'Kullanıcı arayüzü ve kullanıcı deneyimi tasarımı hakkında değerlendirme.',
    type = 'assessment',
    category = 'design',
    status = 'active'
WHERE id = 9;

-- Update test set 10 - Cloud Computing
UPDATE test_sets SET 
    title = 'Cloud Computing ve DevOps',
    description = 'Bulut bilişim teknolojileri ve DevOps metodolojileri değerlendirmesi.',
    type = 'quiz',
    category = 'cloud'
WHERE id = 10;

-- Delete existing questions first
DELETE FROM questions WHERE test_set_id IN (1,2,3,4,5,6,7,8,9,10);

-- Insert enhanced questions

-- JavaScript Test (id=1)
INSERT INTO questions (test_set_id, text, type, options, correct_answer, points, difficulty, "order", explanation, created_at, updated_at) VALUES
(1, 'JavaScript''te değişken tanımlamak için kullanılan anahtar kelimeler hangileridir?', 'multiple_choice', 
 '[{"text": "var, let, const", "is_correct": true}, {"text": "variable, declare, define", "is_correct": false}, {"text": "int, string, boolean", "is_correct": false}, {"text": "dim, set, new", "is_correct": false}]',
 '0', 5.0, 'easy', 1, 'JavaScript''te değişken tanımlamak için var, let ve const anahtar kelimeleri kullanılır.', NOW(), NOW()),

(1, 'Aşağıdaki JavaScript veri tiplerinden hangisi primitif değildir?', 'multiple_choice',
 '[{"text": "string", "is_correct": false}, {"text": "number", "is_correct": false}, {"text": "object", "is_correct": true}, {"text": "boolean", "is_correct": false}]',
 '2', 5.0, 'medium', 2, 'Object bir referans tipidir, primitif değildir.', NOW(), NOW()),

(1, 'JavaScript''te bir array''in uzunluğunu nasıl öğrenirsiniz?', 'multiple_choice',
 '[{"text": "array.size", "is_correct": false}, {"text": "array.length", "is_correct": true}, {"text": "array.count", "is_correct": false}, {"text": "array.total", "is_correct": false}]',
 '1', 4.0, 'easy', 3, 'JavaScript''te array uzunluğu .length property''si ile öğrenilir.', NOW(), NOW());

-- Python Test (id=2)
INSERT INTO questions (test_set_id, text, type, options, correct_answer, points, difficulty, "order", explanation, created_at, updated_at) VALUES
(2, 'Python''da liste (list) ve tuple arasındaki temel fark nedir?', 'multiple_choice',
 '[{"text": "Liste mutable, tuple immutable''dır", "is_correct": true}, {"text": "Liste string, tuple sayı tutar", "is_correct": false}, {"text": "Liste hızlı, tuple yavaştır", "is_correct": false}, {"text": "Hiçbir fark yoktur", "is_correct": false}]',
 '0', 8.0, 'medium', 1, 'Liste değiştirilebilir (mutable), tuple değiştirilemez (immutable) veri yapılarıdır.', NOW(), NOW()),

(2, 'Python''da bir dictionary''den değer almak için kullanılan yöntemlerden hangisi güvenlidir?', 'multiple_choice',
 '[{"text": "dict[key]", "is_correct": false}, {"text": "dict.get(key)", "is_correct": true}, {"text": "dict.value(key)", "is_correct": false}, {"text": "dict.find(key)", "is_correct": false}]',
 '1', 6.0, 'medium', 2, 'get() metodu key yoksa KeyError vermez, None döner.', NOW(), NOW());

-- Web Development Test (id=3)
INSERT INTO questions (test_set_id, text, type, options, correct_answer, points, difficulty, "order", explanation, created_at, updated_at) VALUES
(3, 'HTML''de bir bağlantı (link) oluşturmak için hangi etiket kullanılır?', 'multiple_choice',
 '[{"text": "<link>", "is_correct": false}, {"text": "<a>", "is_correct": true}, {"text": "<href>", "is_correct": false}, {"text": "<url>", "is_correct": false}]',
 '1', 4.0, 'easy', 1, '<a> etiketi hyperlink oluşturmak için kullanılır.', NOW(), NOW()),

(3, 'CSS''de bir elementin arka plan rengini değiştirmek için hangi özellik kullanılır?', 'multiple_choice',
 '[{"text": "color", "is_correct": false}, {"text": "background-color", "is_correct": true}, {"text": "bg-color", "is_correct": false}, {"text": "background", "is_correct": false}]',
 '1', 4.0, 'easy', 2, 'background-color CSS özelliği arka plan rengini belirler.', NOW(), NOW()),

(3, 'Responsive web tasarımda hangi CSS özelliği en yaygın kullanılır?', 'multiple_choice',
 '[{"text": "media queries", "is_correct": true}, {"text": "flexbox", "is_correct": false}, {"text": "grid", "is_correct": false}, {"text": "float", "is_correct": false}]',
 '0', 6.0, 'medium', 3, 'Media queries farklı ekran boyutları için stil tanımlar.', NOW(), NOW());

-- Data Analysis Test (id=4)
INSERT INTO questions (test_set_id, text, type, options, correct_answer, points, difficulty, "order", explanation, created_at, updated_at) VALUES
(4, 'Veri setinin merkezi eğilim ölçüleri hangileridir?', 'multiple_choice',
 '[{"text": "Ortalama, medyan, mod", "is_correct": true}, {"text": "Varyans, standart sapma, aralık", "is_correct": false}, {"text": "Minimum, maksimum, çeyreklik", "is_correct": false}, {"text": "Korelasyon, regresyon, kovaryans", "is_correct": false}]',
 '0', 10.0, 'medium', 1, 'Merkezi eğilim ölçüleri: ortalama, medyan ve mod''dur.', NOW(), NOW()),

(4, 'Pearson korelasyon katsayısının değer aralığı nedir?', 'multiple_choice',
 '[{"text": "0 ile 1 arası", "is_correct": false}, {"text": "-1 ile 1 arası", "is_correct": true}, {"text": "0 ile 100 arası", "is_correct": false}, {"text": "Sınırı yoktur", "is_correct": false}]',
 '1', 8.0, 'medium', 2, 'Pearson korelasyon katsayısı -1 ile +1 arasında değer alır.', NOW(), NOW());

-- Digital Marketing Test (id=5)
INSERT INTO questions (test_set_id, text, type, options, correct_answer, points, difficulty, "order", explanation, created_at, updated_at) VALUES
(5, 'SEO''nun açılımı nedir?', 'multiple_choice',
 '[{"text": "Search Engine Optimization", "is_correct": true}, {"text": "Social Engine Optimization", "is_correct": false}, {"text": "Search Email Optimization", "is_correct": false}, {"text": "Site Engine Optimization", "is_correct": false}]',
 '0', 5.0, 'easy', 1, 'SEO: Search Engine Optimization (Arama Motoru Optimizasyonu)', NOW(), NOW()),

(5, 'Dijital pazarlamada CTR neyi ifade eder?', 'multiple_choice',
 '[{"text": "Cost To Revenue", "is_correct": false}, {"text": "Click Through Rate", "is_correct": true}, {"text": "Customer Trust Rating", "is_correct": false}, {"text": "Content Traffic Ratio", "is_correct": false}]',
 '1', 6.0, 'medium', 2, 'CTR: Click Through Rate (Tıklama Oranı)', NOW(), NOW());

-- Project Management Test (id=6)
INSERT INTO questions (test_set_id, text, type, options, correct_answer, points, difficulty, "order", explanation, created_at, updated_at) VALUES
(6, 'Scrum metodolojisinde sprint süresi genellikle kaç haftadır?', 'multiple_choice',
 '[{"text": "1-2 hafta", "is_correct": true}, {"text": "3-4 hafta", "is_correct": false}, {"text": "5-6 hafta", "is_correct": false}, {"text": "7-8 hafta", "is_correct": false}]',
 '0', 8.0, 'medium', 1, 'Scrum sprint''leri genellikle 1-2 hafta sürer.', NOW(), NOW()),

(6, 'Kanban metodolojisinin temel prensibi nedir?', 'multiple_choice',
 '[{"text": "İş akışını görselleştirmek", "is_correct": true}, {"text": "Kod yazmak", "is_correct": false}, {"text": "Test yapmak", "is_correct": false}, {"text": "Dokümantasyon", "is_correct": false}]',
 '0', 7.0, 'medium', 2, 'Kanban iş akışını görselleştirerek süreç yönetimi sağlar.', NOW(), NOW());

-- Database Test (id=7)
INSERT INTO questions (test_set_id, text, type, options, correct_answer, points, difficulty, "order", explanation, created_at, updated_at) VALUES
(7, 'SQL''de tablolardan veri seçmek için hangi komut kullanılır?', 'multiple_choice',
 '[{"text": "GET", "is_correct": false}, {"text": "SELECT", "is_correct": true}, {"text": "FETCH", "is_correct": false}, {"text": "RETRIEVE", "is_correct": false}]',
 '1', 5.0, 'easy', 1, 'SELECT komutu veritabanından veri seçmek için kullanılır.', NOW(), NOW()),

(7, 'SQL''de birincil anahtar (Primary Key) ne işe yarar?', 'multiple_choice',
 '[{"text": "Tablodaki her satırı benzersiz tanımlar", "is_correct": true}, {"text": "Tabloyu sıralar", "is_correct": false}, {"text": "Tabloyu güvenli tutar", "is_correct": false}, {"text": "Tabloya renk verir", "is_correct": false}]',
 '0', 6.0, 'medium', 2, 'Primary Key her satırı benzersiz şekilde tanımlar.', NOW(), NOW());

-- React Test (id=8)
INSERT INTO questions (test_set_id, text, type, options, correct_answer, points, difficulty, "order", explanation, created_at, updated_at) VALUES
(8, 'React''te component state''i yönetmek için hangi hook kullanılır?', 'multiple_choice',
 '[{"text": "useEffect", "is_correct": false}, {"text": "useState", "is_correct": true}, {"text": "useContext", "is_correct": false}, {"text": "useReducer", "is_correct": false}]',
 '1', 6.0, 'medium', 1, 'useState hook''u component state''ini yönetmek için kullanılır.', NOW(), NOW()),

(8, 'React''te prop''lar neyi ifade eder?', 'multiple_choice',
 '[{"text": "Component''e geçilen parametreler", "is_correct": true}, {"text": "Component''in state''i", "is_correct": false}, {"text": "Component''in style''ı", "is_correct": false}, {"text": "Component''in adı", "is_correct": false}]',
 '0', 5.0, 'easy', 2, 'Props, parent component''ten child component''e geçilen parametrelerdir.', NOW(), NOW());

-- UI/UX Design Test (id=9)
INSERT INTO questions (test_set_id, text, type, options, correct_answer, points, difficulty, "order", explanation, created_at, updated_at) VALUES
(9, 'UI tasarımında ''wireframe'' neyi ifade eder?', 'multiple_choice',
 '[{"text": "Sayfanın iskelet planı", "is_correct": true}, {"text": "Sayfanın renk paleti", "is_correct": false}, {"text": "Sayfanın yazı tipleri", "is_correct": false}, {"text": "Sayfanın animasyonları", "is_correct": false}]',
 '0', 6.0, 'medium', 1, 'Wireframe, sayfanın temel yapısını gösteren iskelet plandır.', NOW(), NOW()),

(9, 'UX tasarımında ''user persona'' nedir?', 'multiple_choice',
 '[{"text": "Hedef kullanıcı profili", "is_correct": true}, {"text": "Tasarımcının profili", "is_correct": false}, {"text": "Uygulamanın profili", "is_correct": false}, {"text": "Şirketin profili", "is_correct": false}]',
 '0', 7.0, 'medium', 2, 'User persona, hedef kullanıcı grubunu temsil eden kurgusal profil''dir.', NOW(), NOW());

-- Cloud Computing Test (id=10)
INSERT INTO questions (test_set_id, text, type, options, correct_answer, points, difficulty, "order", explanation, created_at, updated_at) VALUES
(10, 'AWS''nin açılımı nedir?', 'multiple_choice',
 '[{"text": "Amazon Web Services", "is_correct": true}, {"text": "Advanced Web Services", "is_correct": false}, {"text": "Automated Web Services", "is_correct": false}, {"text": "Application Web Services", "is_correct": false}]',
 '0', 5.0, 'easy', 1, 'AWS: Amazon Web Services', NOW(), NOW()),

(10, 'Docker konteynerlerinin temel avantajı nedir?', 'multiple_choice',
 '[{"text": "Uygulamaları izole eder", "is_correct": true}, {"text": "Uygulamaları yavaşlatır", "is_correct": false}, {"text": "Uygulamaları siler", "is_correct": false}, {"text": "Uygulamaları karıştırır", "is_correct": false}]',
 '0', 7.0, 'medium', 2, 'Docker, uygulamaları izole edilmiş ortamlarda çalıştırır.', NOW(), NOW());