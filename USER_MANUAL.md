# BDC Platform - User Manual

## Table of Contents

1. [Getting Started](#getting-started)
2. [User Roles & Permissions](#user-roles--permissions)
3. [Dashboard Overview](#dashboard-overview)
4. [Managing Beneficiaries](#managing-beneficiaries)
5. [Program Management](#program-management)
6. [Evaluations & Tests](#evaluations--tests)
7. [Document Management](#document-management)
8. [Calendar & Appointments](#calendar--appointments)
9. [Reports & Analytics](#reports--analytics)
10. [Communication Tools](#communication-tools)
11. [Settings & Preferences](#settings--preferences)
12. [Mobile App Usage](#mobile-app-usage)
13. [Troubleshooting](#troubleshooting)
14. [FAQ](#faq)

---

## Getting Started

### Accessing the Platform

1. **Web Browser**: Open your preferred web browser (Chrome, Firefox, Safari, Edge)
2. **Navigate**: Go to `https://your-organization.bdc-platform.com`
3. **Login**: Enter your email and password

![Login Screen](docs/images/login-screen.png)

### First-Time Login

When logging in for the first time:

1. **Welcome Screen**: You'll see a welcome message
2. **Password Change**: You may be prompted to change your temporary password
3. **Profile Setup**: Complete your profile information
4. **Onboarding Tutorial**: Follow the interactive tutorial (optional)

### Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character (!@#$%^&*)

---

## User Roles & Permissions

### Role Types

#### Super Admin
- Full system access
- Manage all tenants
- System configuration
- User management across all organizations

#### Tenant Admin
- Manage organization settings
- Create and manage users within organization
- Access all organization data
- Configure organization-specific settings

#### Trainer
- Manage assigned beneficiaries
- Create and conduct evaluations
- Schedule appointments
- Generate reports for assigned beneficiaries

#### Student (Beneficiary)
- View personal information
- Access assigned programs
- Complete evaluations
- View personal documents
- Schedule appointments with trainers

### Permission Matrix

| Feature | Super Admin | Tenant Admin | Trainer | Student |
|---------|------------|--------------|---------|---------|
| System Settings | ✓ | ✗ | ✗ | ✗ |
| User Management | ✓ | ✓ | ✗ | ✗ |
| All Beneficiaries | ✓ | ✓ | Assigned Only | Self Only |
| Program Creation | ✓ | ✓ | ✗ | ✗ |
| Evaluation Creation | ✓ | ✓ | ✓ | ✗ |
| Reports | ✓ | ✓ | Limited | Personal |
| Documents | ✓ | ✓ | Assigned | Personal |

---

## Dashboard Overview

### Main Dashboard Components

![Dashboard Overview](docs/images/dashboard-overview.png)

#### 1. Navigation Sidebar
- **Home**: Return to dashboard
- **Beneficiaries**: Manage beneficiaries
- **Programs**: View and manage programs
- **Evaluations**: Create and review evaluations
- **Calendar**: Schedule and view appointments
- **Documents**: File management
- **Reports**: Analytics and reporting
- **Settings**: Personal and system settings

#### 2. Quick Stats
- Total beneficiaries
- Active programs
- Pending evaluations
- Upcoming appointments

#### 3. Recent Activity
- Latest beneficiary enrollments
- Recent evaluation completions
- Upcoming events
- System notifications

#### 4. Quick Actions
- Add new beneficiary
- Create evaluation
- Schedule appointment
- Generate report

### Customizing Your Dashboard

1. Click the **Settings** icon (⚙️) in the top right
2. Select **Dashboard Preferences**
3. Choose widgets to display
4. Drag and drop to rearrange
5. Click **Save Layout**

---

## Managing Beneficiaries

### Viewing Beneficiaries

1. Navigate to **Beneficiaries** in the sidebar
2. Use the search bar to find specific beneficiaries
3. Apply filters:
   - Status (Active, Inactive, Pending)
   - Program enrollment
   - Age group
   - Location

### Adding a New Beneficiary

1. Click **Add Beneficiary** button
2. Fill in required information:
   - First Name*
   - Last Name*
   - Email
   - Phone Number
   - Date of Birth*
   - Address

3. Add optional information:
   - Emergency contact
   - Medical information
   - Special requirements

4. Click **Save**

### Beneficiary Profile

Each beneficiary profile contains:

#### Personal Information Tab
- Basic details
- Contact information
- Emergency contacts
- Custom fields

#### Programs Tab
- Enrolled programs
- Progress tracking
- Completion certificates

#### Evaluations Tab
- Completed evaluations
- Scores and feedback
- Upcoming tests

#### Documents Tab
- Personal documents
- Certificates
- Reports

#### Activity Timeline
- Enrollment history
- Evaluation results
- Appointment history
- Notes and updates

### Bulk Operations

1. Select multiple beneficiaries using checkboxes
2. Choose bulk action:
   - Export to Excel/CSV
   - Assign to program
   - Send notification
   - Update status

---

## Program Management

### Creating a Program

1. Navigate to **Programs** → **Create Program**
2. Enter program details:
   - **Program Name***
   - **Description**
   - **Category**
   - **Start Date***
   - **End Date***
   - **Capacity**

3. Add program modules:
   - Module name
   - Duration
   - Content description
   - Required materials

4. Set requirements:
   - Prerequisites
   - Age restrictions
   - Documentation needed

5. Click **Create Program**

### Managing Program Enrollment

#### Enrolling Beneficiaries

1. Open program details
2. Click **Manage Enrollment**
3. Search and select beneficiaries
4. Set enrollment details:
   - Start date
   - Custom schedule (if applicable)
   - Special accommodations

5. Click **Enroll Selected**

#### Tracking Progress

1. View program dashboard
2. Monitor:
   - Attendance rates
   - Module completion
   - Evaluation scores
   - Overall progress

### Program Reports

Generate reports showing:
- Enrollment statistics
- Completion rates
- Performance metrics
- Attendance records

---

## Evaluations & Tests

### Creating an Evaluation

1. Navigate to **Evaluations** → **Create New**
2. Choose evaluation type:
   - Quiz
   - Assignment
   - Exam
   - Survey

3. Set basic information:
   - Title*
   - Description
   - Program (if applicable)
   - Duration
   - Passing score

4. Add questions:
   - Multiple choice
   - True/False
   - Short answer
   - Essay
   - File upload

5. Configure settings:
   - Time limit
   - Number of attempts
   - Randomize questions
   - Show results immediately

6. Click **Save & Publish**

### Question Types

#### Multiple Choice
```
Question: What is the capital of France?
Options:
A) London
B) Berlin
C) Paris ✓
D) Madrid

Points: 10
```

#### True/False
```
Question: The Earth is flat.
Answer: False ✓
Points: 5
```

#### Short Answer
```
Question: Name three primary colors.
Expected answers: Red, Blue, Yellow
Points: 15
```

### Managing Evaluations

#### Assigning Evaluations

1. Select evaluation
2. Click **Assign**
3. Choose recipients:
   - Individual beneficiaries
   - Program groups
   - Custom selection

4. Set parameters:
   - Available from
   - Due date
   - Late submission policy

#### Reviewing Results

1. Open evaluation
2. Click **View Results**
3. Review:
   - Individual scores
   - Question analysis
   - Time taken
   - Attempts used

4. Provide feedback:
   - Grade essays
   - Add comments
   - Award partial credit

### Evaluation Analytics

View detailed analytics:
- Score distribution
- Average completion time
- Difficult questions
- Pass/fail rates

---

## Document Management

### Document Organization

#### Folder Structure
```
Documents/
├── Templates/
│   ├── Contracts
│   ├── Certificates
│   └── Forms
├── Beneficiary Files/
│   ├── [Beneficiary Name]/
│   │   ├── Personal Documents
│   │   ├── Evaluations
│   │   └── Certificates
└── Reports/
    ├── Monthly
    ├── Quarterly
    └── Annual
```

### Uploading Documents

1. Navigate to **Documents**
2. Select target folder
3. Click **Upload**
4. Choose files (drag & drop supported)
5. Add metadata:
   - Document type
   - Description
   - Tags
   - Access permissions

### Document Actions

- **View**: Click to preview
- **Download**: Save to device
- **Share**: Generate sharing link
- **Move**: Relocate to different folder
- **Delete**: Remove (requires confirmation)

### Document Security

#### Access Levels
- **Private**: Only you can access
- **Restricted**: Specific users/roles
- **Organization**: All organization members
- **Public**: Anyone with link

#### Version Control
- Automatic versioning
- View version history
- Restore previous versions
- Track changes

---

## Calendar & Appointments

### Calendar Views

#### Month View
- Overview of entire month
- Color-coded events
- Quick event creation

#### Week View
- Detailed weekly schedule
- Hour-by-hour breakdown
- Drag to reschedule

#### Day View
- Detailed daily agenda
- Time slot availability
- Conflict detection

### Creating Appointments

1. Click on calendar date/time
2. Fill appointment details:
   - Title*
   - Participants*
   - Location/Meeting link
   - Duration
   - Description
   - Reminders

3. Check availability
4. Send invitations
5. Click **Schedule**

### Appointment Types

#### One-on-One Session
- Trainer-beneficiary meetings
- Progress reviews
- Counseling sessions

#### Group Sessions
- Class sessions
- Workshops
- Group evaluations

#### Events
- Program launches
- Graduation ceremonies
- Information sessions

### Managing Appointments

#### Rescheduling
1. Click appointment
2. Select **Reschedule**
3. Choose new time
4. Add reason (optional)
5. Notify participants

#### Cancelling
1. Click appointment
2. Select **Cancel**
3. Provide reason
4. Choose notification method
5. Confirm cancellation

### Calendar Integration

Sync with external calendars:
- Google Calendar
- Outlook Calendar
- Apple Calendar

Export options:
- iCal format
- CSV export
- PDF schedule

---

## Reports & Analytics

### Available Reports

#### Beneficiary Reports
- Individual progress reports
- Program participation
- Evaluation history
- Attendance records

#### Program Reports
- Enrollment statistics
- Completion rates
- Performance metrics
- Resource utilization

#### Organizational Reports
- Overall statistics
- Trend analysis
- Comparative reports
- Custom analytics

### Generating Reports

1. Navigate to **Reports**
2. Select report type
3. Configure parameters:
   - Date range
   - Filters
   - Grouping
   - Format

4. Preview report
5. Export options:
   - PDF
   - Excel
   - CSV
   - Print

### Report Builder

Create custom reports:

1. Click **Custom Report**
2. Select data sources
3. Choose fields
4. Apply filters
5. Design layout
6. Save template

### Scheduled Reports

Set up automatic reports:

1. Create report template
2. Click **Schedule**
3. Set frequency:
   - Daily
   - Weekly
   - Monthly
   - Custom

4. Choose recipients
5. Select delivery method:
   - Email
   - Dashboard
   - File storage

### Analytics Dashboard

Interactive analytics featuring:
- Real-time metrics
- Trend visualization
- Comparative analysis
- Predictive insights

Key Metrics:
- Enrollment trends
- Success rates
- Engagement levels
- Resource efficiency

---

## Communication Tools

### Messaging System

#### Sending Messages

1. Click **Messages** icon
2. Compose new message:
   - Select recipients
   - Add subject
   - Write message
   - Attach files (optional)

3. Send or schedule

#### Message Features
- Read receipts
- Priority levels
- Categories/Labels
- Search functionality
- Archive/Delete

### Notifications

#### Notification Types
- System alerts
- Assignment deadlines
- Appointment reminders
- Program updates
- Achievement badges

#### Managing Notifications

1. Click notification bell icon
2. View recent notifications
3. Mark as read/unread
4. Access notification settings:
   - Email preferences
   - Push notifications
   - SMS alerts
   - In-app notifications

### Announcements

Create announcements for:
- Program updates
- Policy changes
- Event invitations
- General information

Steps:
1. Navigate to **Announcements**
2. Click **Create**
3. Set audience
4. Write announcement
5. Schedule or publish

---

## Settings & Preferences

### Personal Settings

#### Profile Information
- Update personal details
- Change profile picture
- Manage contact information
- Set availability status

#### Security Settings
- Change password
- Enable two-factor authentication
- Manage login sessions
- View login history

#### Preferences
- Language selection
- Time zone
- Date format
- Theme (Light/Dark)

### Notification Preferences

Configure how you receive notifications:

| Type | Email | SMS | Push | In-App |
|------|-------|-----|------|--------|
| Appointments | ✓ | ✓ | ✓ | ✓ |
| Evaluations | ✓ | ✗ | ✓ | ✓ |
| Messages | ✓ | ✗ | ✓ | ✓ |
| System Updates | ✓ | ✗ | ✗ | ✓ |

### Accessibility Options

- Font size adjustment
- High contrast mode
- Screen reader support
- Keyboard navigation
- Language preferences

### Data & Privacy

#### Export Your Data
1. Go to **Settings** → **Privacy**
2. Click **Export My Data**
3. Select data types
4. Choose format
5. Receive via email

#### Privacy Controls
- Profile visibility
- Data sharing preferences
- Third-party integrations
- Cookie preferences

---

## Mobile App Usage

### Installation

#### iOS
1. Open App Store
2. Search "BDC Platform"
3. Tap **Get**
4. Sign in with your credentials

#### Android
1. Open Google Play Store
2. Search "BDC Platform"
3. Tap **Install**
4. Sign in with your credentials

### Mobile Features

#### Offline Mode
- View cached data
- Complete downloaded evaluations
- Draft messages
- Sync when connected

#### Mobile-Specific Features
- Push notifications
- Camera integration
- GPS for attendance
- Biometric login
- Voice notes

### Mobile Navigation

Bottom navigation bar:
- **Home**: Dashboard
- **Calendar**: Appointments
- **Messages**: Communications
- **More**: Additional features

Swipe gestures:
- Swipe right: Go back
- Swipe down: Refresh
- Long press: Quick actions

---

## Troubleshooting

### Common Issues

#### Cannot Login
1. Check email/password
2. Clear browser cache
3. Try password reset
4. Contact administrator

#### Slow Performance
1. Check internet connection
2. Clear browser cache
3. Disable browser extensions
4. Try different browser

#### Missing Data
1. Refresh the page
2. Check filters
3. Verify permissions
4. Contact support

### Browser Requirements

| Browser | Minimum Version |
|---------|----------------|
| Chrome | 90+ |
| Firefox | 88+ |
| Safari | 14+ |
| Edge | 90+ |

### Getting Help

#### In-App Help
- Click **?** icon
- Search help topics
- View tutorials
- Contact support

#### Support Channels
- Email: support@bdc-platform.com
- Phone: +1-800-BDC-HELP
- Live Chat: Available 9 AM - 5 PM
- Help Center: help.bdc-platform.com

---

## FAQ

### General Questions

**Q: How do I reset my password?**
A: Click "Forgot Password" on the login page, enter your email, and follow the instructions sent to your email.

**Q: Can I use the platform on multiple devices?**
A: Yes, you can access the platform from any device with an internet connection and compatible browser.

**Q: How often is data backed up?**
A: Data is backed up automatically every 24 hours, with additional real-time replication for critical data.

### Beneficiary Management

**Q: How many beneficiaries can I manage?**
A: There's no hard limit, but performance may vary with very large numbers. Contact support for optimization tips.

**Q: Can I import beneficiaries from Excel?**
A: Yes, use the Import feature in the Beneficiaries section. Download the template first to ensure proper formatting.

### Programs & Evaluations

**Q: Can beneficiaries retake evaluations?**
A: This depends on the evaluation settings. Trainers can configure the number of allowed attempts.

**Q: How do I track program attendance?**
A: Attendance can be tracked through the program dashboard or by using the calendar feature for session check-ins.

### Technical Questions

**Q: Is my data secure?**
A: Yes, we use industry-standard encryption, regular security audits, and comply with data protection regulations.

**Q: What happens if I lose internet connection during an evaluation?**
A: Answers are auto-saved every 30 seconds. You can resume where you left off when connection is restored.

### Billing & Account

**Q: How do I upgrade my account?**
A: Contact your organization administrator or our sales team at sales@bdc-platform.com.

**Q: Can I export all my data?**
A: Yes, you can export your data through Settings → Privacy → Export My Data.

---

## Keyboard Shortcuts

### Global Shortcuts

| Shortcut | Action |
|----------|---------|
| `Ctrl/Cmd + K` | Quick search |
| `Ctrl/Cmd + N` | New (context-aware) |
| `Ctrl/Cmd + S` | Save |
| `Ctrl/Cmd + Z` | Undo |
| `Ctrl/Cmd + /` | Help |

### Navigation Shortcuts

| Shortcut | Navigate to |
|----------|-------------|
| `G then H` | Home |
| `G then B` | Beneficiaries |
| `G then P` | Programs |
| `G then E` | Evaluations |
| `G then C` | Calendar |
| `G then D` | Documents |
| `G then R` | Reports |

### List Shortcuts

| Shortcut | Action |
|----------|---------|
| `J` | Next item |
| `K` | Previous item |
| `X` | Select item |
| `Shift + X` | Select range |
| `Ctrl/Cmd + A` | Select all |

---

## Glossary

- **Beneficiary**: Individual enrolled in programs
- **Program**: Structured learning or assistance plan
- **Evaluation**: Assessment or test
- **Module**: Section within a program
- **Tenant**: Organization using the platform
- **Dashboard**: Main overview screen
- **Widget**: Customizable dashboard component

---

*Last Updated: January 2025*
*Version: 1.0.0*

For additional help, visit our Help Center at help.bdc-platform.com or contact support@bdc-platform.com