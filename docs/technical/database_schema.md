# BDC Database Schema Documentation

## Overview

The BDC application uses a relational database (PostgreSQL in production, SQLite in development) with the following schema design principles:

- Normalized structure to minimize data redundancy
- Foreign key constraints to ensure referential integrity
- Indexes on frequently queried columns
- JSON columns for flexible metadata storage
- Timestamp columns for audit trails

## Entity Relationship Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Users    │────<│Beneficiaries│>────│  Trainers   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Profiles  │     │ Assessments │     │Appointments │
└─────────────┘     └─────────────┘     └─────────────┘
                          │                   │
                          ▼                   │
                    ┌─────────────┐           │
                    │  Questions  │           │
                    └─────────────┘           │
                          │                   │
                          ▼                   ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  Responses  │     │   Messages  │
                    └─────────────┘     └─────────────┘
```

## Tables

### users
Core user table for authentication and authorization.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| email | VARCHAR(120) | UNIQUE, NOT NULL | User email address |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| name | VARCHAR(100) | NOT NULL | User full name |
| role | VARCHAR(20) | NOT NULL | User role (super_admin, admin, trainer, student) |
| is_active | BOOLEAN | DEFAULT TRUE | Account active status |
| is_verified | BOOLEAN | DEFAULT FALSE | Email verification status |
| last_login | TIMESTAMP | | Last login timestamp |
| created_at | TIMESTAMP | DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- idx_users_email (email)
- idx_users_role (role)
- idx_users_is_active (is_active)

### profiles
Extended user profile information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| user_id | INTEGER | FOREIGN KEY | Reference to users table |
| phone | VARCHAR(20) | | Phone number |
| address | TEXT | | Physical address |
| city | VARCHAR(100) | | City |
| state | VARCHAR(100) | | State/Province |
| country | VARCHAR(100) | | Country |
| postal_code | VARCHAR(20) | | Postal/ZIP code |
| date_of_birth | DATE | | Date of birth |
| emergency_contact | VARCHAR(100) | | Emergency contact name |
| emergency_phone | VARCHAR(20) | | Emergency contact phone |
| preferences | JSON | | User preferences |
| metadata | JSON | | Additional metadata |
| created_at | TIMESTAMP | DEFAULT NOW() | Profile creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- idx_profiles_user_id (user_id)

### organizations
Multi-tenant organization support.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| name | VARCHAR(100) | NOT NULL | Organization name |
| slug | VARCHAR(100) | UNIQUE | URL slug |
| admin_id | INTEGER | FOREIGN KEY | Organization admin user |
| settings | JSON | | Organization settings |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- idx_organizations_slug (slug)
- idx_organizations_admin_id (admin_id)

### beneficiaries
Beneficiary-specific information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| user_id | INTEGER | FOREIGN KEY | Reference to users table |
| trainer_id | INTEGER | FOREIGN KEY | Assigned trainer |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| enrollment_date | DATE | | Enrollment date |
| status | VARCHAR(20) | DEFAULT 'active' | Status (active, inactive, completed) |
| notes | TEXT | | Internal notes |
| metadata | JSON | | Additional metadata |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- idx_beneficiaries_user_id (user_id)
- idx_beneficiaries_trainer_id (trainer_id)
- idx_beneficiaries_organization_id (organization_id)
- idx_beneficiaries_status (status)

### assessments
Assessment definitions and metadata.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| title | VARCHAR(200) | NOT NULL | Assessment title |
| description | TEXT | | Assessment description |
| type | VARCHAR(50) | NOT NULL | Assessment type |
| beneficiary_id | INTEGER | FOREIGN KEY | Target beneficiary |
| trainer_id | INTEGER | FOREIGN KEY | Creating trainer |
| status | VARCHAR(20) | DEFAULT 'draft' | Status (draft, published, in_progress, completed) |
| scheduled_for | TIMESTAMP | | Scheduled time |
| completed_at | TIMESTAMP | | Completion time |
| time_limit | INTEGER | | Time limit in minutes |
| passing_score | INTEGER | | Minimum passing score |
| attempts_allowed | INTEGER | DEFAULT 1 | Maximum attempts |
| settings | JSON | | Assessment settings |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- idx_assessments_beneficiary_id (beneficiary_id)
- idx_assessments_trainer_id (trainer_id)
- idx_assessments_status (status)
- idx_assessments_type (type)

### questions
Assessment questions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| assessment_id | INTEGER | FOREIGN KEY | Parent assessment |
| text | TEXT | NOT NULL | Question text |
| type | VARCHAR(50) | NOT NULL | Question type (multiple_choice, true_false, short_answer, essay) |
| options | JSON | | Answer options (for multiple choice) |
| correct_answer | TEXT | | Correct answer |
| points | INTEGER | DEFAULT 1 | Point value |
| order | INTEGER | | Display order |
| required | BOOLEAN | DEFAULT TRUE | Is required |
| metadata | JSON | | Additional metadata |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- idx_questions_assessment_id (assessment_id)
- idx_questions_order (order)

### responses
User responses to assessment questions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| assessment_id | INTEGER | FOREIGN KEY | Parent assessment |
| beneficiary_id | INTEGER | FOREIGN KEY | Responding beneficiary |
| question_id | INTEGER | FOREIGN KEY | Question being answered |
| answer | TEXT | | User's answer |
| is_correct | BOOLEAN | | Whether answer is correct |
| points_earned | INTEGER | | Points earned |
| time_spent | INTEGER | | Time spent in seconds |
| attempt_number | INTEGER | DEFAULT 1 | Attempt number |
| created_at | TIMESTAMP | DEFAULT NOW() | Response timestamp |

**Indexes:**
- idx_responses_assessment_id (assessment_id)
- idx_responses_beneficiary_id (beneficiary_id)
- idx_responses_question_id (question_id)

### assessment_results
Aggregated assessment results and analysis.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| assessment_id | INTEGER | FOREIGN KEY | Parent assessment |
| beneficiary_id | INTEGER | FOREIGN KEY | Beneficiary |
| score | FLOAT | | Total score |
| percentage | FLOAT | | Score percentage |
| passed | BOOLEAN | | Whether passed |
| time_taken | INTEGER | | Total time in seconds |
| ai_analysis | JSON | | AI-generated analysis |
| recommendations | JSON | | AI recommendations |
| created_at | TIMESTAMP | DEFAULT NOW() | Result timestamp |

**Indexes:**
- idx_assessment_results_assessment_id (assessment_id)
- idx_assessment_results_beneficiary_id (beneficiary_id)

### appointments
Scheduled appointments between trainers and beneficiaries.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| title | VARCHAR(200) | NOT NULL | Appointment title |
| description | TEXT | | Appointment description |
| beneficiary_id | INTEGER | FOREIGN KEY | Beneficiary |
| trainer_id | INTEGER | FOREIGN KEY | Trainer |
| start_time | TIMESTAMP | NOT NULL | Start time |
| end_time | TIMESTAMP | NOT NULL | End time |
| location | VARCHAR(200) | | Location/Room |
| type | VARCHAR(50) | | Appointment type |
| status | VARCHAR(20) | DEFAULT 'scheduled' | Status (scheduled, completed, cancelled) |
| notes | TEXT | | Appointment notes |
| reminder_sent | BOOLEAN | DEFAULT FALSE | Reminder sent flag |
| google_event_id | VARCHAR(100) | | Google Calendar event ID |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- idx_appointments_beneficiary_id (beneficiary_id)
- idx_appointments_trainer_id (trainer_id)
- idx_appointments_start_time (start_time)
- idx_appointments_status (status)

### documents
Document management and storage.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| filename | VARCHAR(255) | NOT NULL | Original filename |
| file_path | VARCHAR(500) | | Storage path |
| file_size | INTEGER | | File size in bytes |
| mime_type | VARCHAR(100) | | MIME type |
| category | VARCHAR(50) | | Document category |
| description | TEXT | | Document description |
| uploaded_by | INTEGER | FOREIGN KEY | Uploading user |
| beneficiary_id | INTEGER | FOREIGN KEY | Associated beneficiary |
| is_public | BOOLEAN | DEFAULT FALSE | Public visibility |
| tags | JSON | | Document tags |
| metadata | JSON | | Additional metadata |
| created_at | TIMESTAMP | DEFAULT NOW() | Upload timestamp |

**Indexes:**
- idx_documents_uploaded_by (uploaded_by)
- idx_documents_beneficiary_id (beneficiary_id)
- idx_documents_category (category)

### document_shares
Document sharing permissions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| document_id | INTEGER | FOREIGN KEY | Shared document |
| shared_with | INTEGER | FOREIGN KEY | User shared with |
| shared_by | INTEGER | FOREIGN KEY | Sharing user |
| permission | VARCHAR(20) | DEFAULT 'view' | Permission level (view, edit) |
| expires_at | TIMESTAMP | | Share expiration |
| created_at | TIMESTAMP | DEFAULT NOW() | Share timestamp |

**Indexes:**
- idx_document_shares_document_id (document_id)
- idx_document_shares_shared_with (shared_with)

### messages
Internal messaging system.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| sender_id | INTEGER | FOREIGN KEY | Sending user |
| recipient_id | INTEGER | FOREIGN KEY | Receiving user |
| subject | VARCHAR(200) | | Message subject |
| content | TEXT | NOT NULL | Message content |
| is_read | BOOLEAN | DEFAULT FALSE | Read status |
| read_at | TIMESTAMP | | Read timestamp |
| parent_id | INTEGER | FOREIGN KEY | Parent message (for threads) |
| attachments | JSON | | Attachment metadata |
| created_at | TIMESTAMP | DEFAULT NOW() | Send timestamp |

**Indexes:**
- idx_messages_sender_id (sender_id)
- idx_messages_recipient_id (recipient_id)
- idx_messages_is_read (is_read)
- idx_messages_parent_id (parent_id)

### notifications
System notifications.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| user_id | INTEGER | FOREIGN KEY | Target user |
| type | VARCHAR(50) | NOT NULL | Notification type |
| title | VARCHAR(200) | NOT NULL | Notification title |
| message | TEXT | | Notification message |
| data | JSON | | Additional data |
| is_read | BOOLEAN | DEFAULT FALSE | Read status |
| read_at | TIMESTAMP | | Read timestamp |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |

**Indexes:**
- idx_notifications_user_id (user_id)
- idx_notifications_is_read (is_read)
- idx_notifications_type (type)

### activity_logs
User activity tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| user_id | INTEGER | FOREIGN KEY | Acting user |
| action | VARCHAR(100) | NOT NULL | Action performed |
| resource_type | VARCHAR(50) | | Resource type |
| resource_id | INTEGER | | Resource ID |
| details | JSON | | Action details |
| ip_address | VARCHAR(45) | | User IP address |
| user_agent | TEXT | | User agent string |
| created_at | TIMESTAMP | DEFAULT NOW() | Action timestamp |

**Indexes:**
- idx_activity_logs_user_id (user_id)
- idx_activity_logs_action (action)
- idx_activity_logs_resource_type (resource_type)

### settings
Application settings and preferences.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| key | VARCHAR(100) | UNIQUE, NOT NULL | Setting key |
| value | TEXT | | Setting value |
| type | VARCHAR(20) | | Value type |
| category | VARCHAR(50) | | Setting category |
| description | TEXT | | Setting description |
| is_public | BOOLEAN | DEFAULT FALSE | Public visibility |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- idx_settings_key (key)
- idx_settings_category (category)

### sessions
User session management.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| user_id | INTEGER | FOREIGN KEY | Session user |
| token | VARCHAR(255) | UNIQUE | Session token |
| ip_address | VARCHAR(45) | | Client IP |
| user_agent | TEXT | | User agent |
| last_activity | TIMESTAMP | | Last activity time |
| expires_at | TIMESTAMP | | Session expiration |
| created_at | TIMESTAMP | DEFAULT NOW() | Session start |

**Indexes:**
- idx_sessions_token (token)
- idx_sessions_user_id (user_id)
- idx_sessions_expires_at (expires_at)

### error_logs
Error tracking and monitoring.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique identifier |
| timestamp | TIMESTAMP | DEFAULT NOW() | Error timestamp |
| error_type | VARCHAR(100) | NOT NULL | Error type/class |
| error_message | TEXT | NOT NULL | Error message |
| traceback | TEXT | | Stack trace |
| severity | VARCHAR(20) | NOT NULL | Severity level |
| context | JSON | | Error context |
| request_id | VARCHAR(36) | | Request ID |
| user_id | INTEGER | FOREIGN KEY | Affected user |

**Indexes:**
- idx_error_logs_timestamp (timestamp)
- idx_error_logs_error_type (error_type)
- idx_error_logs_severity (severity)
- idx_error_logs_user_id (user_id)

## Relationships

### One-to-Many Relationships

- users → profiles (1:1)
- users → beneficiaries (1:1)
- users → assessments (1:N as trainer)
- users → appointments (1:N as trainer)
- users → documents (1:N as uploader)
- users → messages (1:N as sender/recipient)
- users → notifications (1:N)
- users → activity_logs (1:N)
- users → sessions (1:N)
- organizations → users (1:N)
- assessments → questions (1:N)
- assessments → responses (1:N)
- assessments → assessment_results (1:N)
- questions → responses (1:N)
- documents → document_shares (1:N)

### Many-to-Many Relationships

- beneficiaries ↔ trainers (through beneficiaries table)
- documents ↔ users (through document_shares)
- messages ↔ users (sender/recipient)

## Data Types

- **VARCHAR**: Variable-length character strings
- **TEXT**: Long text content
- **INTEGER**: Whole numbers
- **FLOAT**: Decimal numbers
- **BOOLEAN**: True/False values
- **TIMESTAMP**: Date and time values
- **DATE**: Date values only
- **JSON**: JSON data for flexible storage

## Constraints

### Foreign Keys
All foreign key relationships include ON DELETE CASCADE or ON DELETE SET NULL as appropriate.

### Check Constraints
- role IN ('super_admin', 'admin', 'trainer', 'student')
- status values are restricted to predefined sets
- percentage BETWEEN 0 AND 100
- points >= 0

### Unique Constraints
- users.email
- organizations.slug
- settings.key
- sessions.token

## Performance Considerations

1. **Indexing Strategy**
   - Primary keys are automatically indexed
   - Foreign keys have indexes for join performance
   - Frequently queried columns are indexed
   - Composite indexes for common query patterns

2. **Partitioning**
   - Consider partitioning large tables (activity_logs, error_logs) by date
   - Archive old data periodically

3. **Query Optimization**
   - Use explain plans to optimize complex queries
   - Avoid N+1 query problems
   - Use database views for complex reports

4. **Data Archival**
   - Move old activity logs to archive tables
   - Compress or delete old error logs
   - Archive completed assessments after retention period

## Migration Strategy

1. **Version Control**
   - All schema changes tracked in migration files
   - Rollback scripts for each migration
   - Test migrations in staging environment

2. **Zero-Downtime Migrations**
   - Add columns as nullable first
   - Populate data in background
   - Add constraints after data migration
   - Remove old columns in separate migration

3. **Backup Strategy**
   - Daily automated backups
   - Point-in-time recovery capability
   - Test restore procedures regularly

## Security Considerations

1. **Data Encryption**
   - Sensitive data encrypted at rest
   - Use database-level encryption where available
   - Encrypt backups

2. **Access Control**
   - Principle of least privilege
   - Separate read/write database users
   - Audit database access

3. **Data Privacy**
   - PII data clearly identified
   - Implement data retention policies
   - Support data export/deletion for GDPR compliance

## Monitoring

1. **Performance Metrics**
   - Query execution time
   - Connection pool usage
   - Table sizes and growth
   - Index usage statistics

2. **Health Checks**
   - Database connectivity
   - Replication lag (if applicable)
   - Disk space usage
   - Long-running queries

## Future Considerations

1. **Scalability**
   - Consider read replicas for reporting
   - Implement caching layer
   - Evaluate NoSQL for specific use cases

2. **Multi-tenancy**
   - Row-level security for tenant isolation
   - Consider schema-per-tenant for large clients
   - Implement tenant-aware indexing

3. **Analytics**
   - Consider separate analytics database
   - Implement data warehouse for reporting
   - Use materialized views for dashboards