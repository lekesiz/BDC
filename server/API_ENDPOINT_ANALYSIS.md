# BDC Backend API Endpoint Analysis

## Overview

This document provides a comprehensive catalog of all existing API endpoints in the BDC backend system, identifying duplicates, conflicts, and inconsistencies across different files and versions.

## Authentication Endpoints

### File: `app/api/auth.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/debug` | Debug auth status | No | Any |
| POST | `/login` | User login | No | Any |
| POST | `/register` | User registration | No | Any |
| POST | `/refresh` | Refresh JWT token | Yes (Refresh) | Any |
| POST | `/logout` | User logout | Yes | Any |
| POST | `/reset-password/request` | Request password reset | No | Any |
| POST | `/reset-password` | Reset password with token | No | Any |
| POST | `/change-password` | Change user password | Yes | Any |

### File: `app/api/improved_auth.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| POST | `/login` | User login (improved) | No | Any |
| POST | `/register` | User registration (improved) | No | Any |
| POST | `/refresh` | Refresh JWT token | Yes (Refresh) | Any |
| POST | `/logout` | User logout | Yes | Any |
| POST | `/change-password` | Change password | Yes | Any |
| POST | `/reset-password` | Reset password | No | Any |

### File: `app/api/v2/auth.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| POST | `/api/v2/auth/login` | User login | No | Any |
| POST | `/api/v2/auth/register` | User registration | No | Any |
| POST | `/api/v2/auth/refresh` | Refresh token | No | Any |
| POST | `/api/v2/auth/logout` | User logout | Yes | Any |
| POST | `/api/v2/auth/forgot-password` | Forgot password | No | Any |
| POST | `/api/v2/auth/reset-password` | Reset password | No | Any |
| POST | `/api/v2/auth/change-password` | Change password | Yes | Any |
| GET | `/api/v2/auth/verify` | Verify token | Yes | Any |

**Conflicts Identified:**
- 3 different implementations of login endpoint
- Inconsistent URL patterns (with/without `/api/v2/`)
- Different parameter handling for registration
- Varying response formats

## User Management Endpoints

### File: `app/api/users.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/me` | Get current user | Yes | Any |
| GET | `` | Get all users | Yes | super_admin, tenant_admin |
| POST | `/profile-picture` | Upload profile picture | Yes | Any |
| GET | `/me/profile` | Get current user profile | Yes | Any |
| PUT/PATCH | `/me/profile` | Update current user profile | Yes | Any |
| GET | `/{user_id}` | Get user by ID | Yes | Any |
| POST | `` | Create new user | Yes | super_admin, tenant_admin |
| PUT | `/{user_id}` | Update user | Yes | Any (with restrictions) |
| DELETE | `/{user_id}` | Delete user (soft delete) | Yes | super_admin, tenant_admin |
| GET | `/{user_id}/profile` | Get user profile | Yes | Any |

### File: `app/api/users_v2.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/api/v2/users/me` | Get current user | Yes | Any |
| GET | `/api/v2/users/` | Get all users | Yes | admin |
| POST | `/api/v2/users/` | Create user | Yes | admin |
| GET | `/api/v2/users/{user_id}` | Get user by ID | Yes | Any (with access control) |
| PUT | `/api/v2/users/{user_id}` | Update user | Yes | Any (with access control) |
| DELETE | `/api/v2/users/{user_id}` | Delete user | Yes | admin |
| GET | `/api/v2/users/{user_id}/profile` | Get user profile | Yes | Any (with access control) |
| PUT | `/api/v2/users/{user_id}/profile` | Update user profile | Yes | Any (with access control) |
| POST | `/api/v2/users/{user_id}/profile/picture` | Upload profile picture | Yes | Any (with access control) |
| PUT | `/api/v2/users/{user_id}/password` | Update password | Yes | Any (with access control) |

### File: `app/api/users_profile.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/users/me/profile` | Get current user profile | Yes | Any |
| PUT/PATCH | `/users/me/profile` | Update current user profile | Yes | Any |
| POST | `/users/me/profile/avatar` | Upload avatar | Yes | Any |
| GET | `/users/me/profile/privacy` | Get privacy settings | Yes | Any |
| PUT | `/users/me/profile/privacy` | Update privacy settings | Yes | Any |
| PUT | `/users/me/profile/social` | Update social links | Yes | Any |
| GET | `/users/me/profile/skills` | Get user skills | Yes | Any |
| PUT | `/users/me/profile/skills` | Update user skills | Yes | Any |

**Conflicts Identified:**
- Profile endpoints duplicated across multiple files
- Different URL patterns (`/me/profile` vs `/users/me/profile`)
- Async vs sync implementations
- Different role checking mechanisms

## Beneficiary Management Endpoints

### File: `app/api/beneficiaries_dashboard.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/beneficiaries/{id}/dashboard` | Get beneficiary dashboard | Yes | Based on beneficiary access |
| POST | `/beneficiaries/{id}/progress` | Update beneficiary progress | Yes | super_admin, tenant_admin, trainer |

### File: `app/api/beneficiaries_v2/list_routes.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `` | Get beneficiaries list | Yes | super_admin, tenant_admin, trainer |

### File: `app/api/v2/beneficiaries.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/api/v2/beneficiaries` | List beneficiaries | Yes | beneficiaries.view |
| POST | `/api/v2/beneficiaries` | Create beneficiary | Yes | beneficiaries.create |
| GET | `/api/v2/beneficiaries/{id}` | Get beneficiary | Yes | beneficiaries.view |
| PUT | `/api/v2/beneficiaries/{id}` | Update beneficiary | Yes | beneficiaries.edit |
| DELETE | `/api/v2/beneficiaries/{id}` | Delete beneficiary | Yes | beneficiaries.delete |
| GET | `/api/v2/beneficiaries/statistics` | Get statistics | Yes | beneficiaries.view |
| GET | `/api/v2/beneficiaries/{id}/notes` | Get notes | Yes | beneficiaries.view |
| POST | `/api/v2/beneficiaries/{id}/notes` | Add note | Yes | beneficiaries.edit |
| PUT | `/api/v2/beneficiaries/notes/{note_id}` | Update note | Yes | beneficiaries.edit |
| DELETE | `/api/v2/beneficiaries/notes/{note_id}` | Delete note | Yes | beneficiaries.edit |
| GET | `/api/v2/beneficiaries/{id}/documents` | Get documents | Yes | beneficiaries.view |
| POST | `/api/v2/beneficiaries/{id}/documents` | Upload document | Yes | beneficiaries.edit |
| GET | `/api/v2/beneficiaries/documents/{id}` | Download document | Yes | beneficiaries.view |
| DELETE | `/api/v2/beneficiaries/documents/{id}` | Delete document | Yes | beneficiaries.edit |
| GET | `/api/v2/beneficiaries/{id}/appointments` | Get appointments | Yes | beneficiaries.view |
| POST | `/api/v2/beneficiaries/{id}/appointments` | Schedule appointment | Yes | appointments.create |
| PUT | `/api/v2/beneficiaries/appointments/{id}` | Update appointment | Yes | appointments.edit |
| POST | `/api/v2/beneficiaries/appointments/{id}/cancel` | Cancel appointment | Yes | appointments.edit |
| GET | `/api/v2/beneficiaries/{id}/export` | Export beneficiary | Yes | beneficiaries.export |
| GET | `/api/v2/beneficiaries/export` | Export beneficiaries | Yes | beneficiaries.export |

**Conflicts Identified:**
- Multiple implementations scattered across different files
- Inconsistent permission system (role-based vs permission-based)
- Different caching strategies
- Scattered functionality (notes, documents, appointments mixed in)

## Evaluation System Endpoints

### File: `app/api/evaluations.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `` | Get evaluations list | Yes | Based on role |
| POST | `` | Create evaluation | Yes | trainer, admin |
| GET | `/{id}` | Get evaluation by ID | Yes | Based on access |
| PUT | `/{id}` | Update evaluation | Yes | creator or admin |
| DELETE | `/{id}` | Delete evaluation | Yes | creator or admin |
| POST | `/{id}/start` | Start evaluation session | Yes | beneficiary |
| POST | `/{id}/submit` | Submit evaluation | Yes | beneficiary |
| GET | `/{id}/results` | Get evaluation results | Yes | trainer, admin, beneficiary |
| POST | `/{id}/questions` | Add question | Yes | creator or admin |
| PUT | `/questions/{id}` | Update question | Yes | creator or admin |
| DELETE | `/questions/{id}` | Delete question | Yes | creator or admin |

### File: `app/api/improved_evaluations.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `` | Get evaluations (improved) | Yes | Based on role |
| POST | `` | Create evaluation | Yes | trainer, admin |
| GET | `/{id}` | Get evaluation | Yes | Based on access |
| PUT | `/{id}` | Update evaluation | Yes | creator or admin |
| DELETE | `/{id}` | Delete evaluation | Yes | creator or admin |

**Conflicts Identified:**
- Duplicate CRUD operations
- Different question management approaches
- Inconsistent access control logic

## Document Management Endpoints

### File: `app/api/documents.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/documents` | Get documents list | Yes | Based on role |
| GET | `/documents/evaluation-report/{id}` | Get evaluation report | Yes | trainer, admin |
| GET | `/documents/beneficiary-report/{id}` | Get beneficiary report | Yes | trainer, admin |
| POST | `/documents/generate-evaluation-report` | Generate evaluation report | Yes | trainer, admin |
| POST | `/documents/generate-beneficiary-report` | Generate beneficiary report | Yes | trainer, admin |
| POST | `/documents/upload` | Upload document | Yes | trainer, admin |
| GET | `/documents/{id}/download` | Download document | Yes | Based on permissions |
| DELETE | `/documents/{id}` | Delete document | Yes | uploader or admin |

### File: `app/api/improved_documents.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `` | Get documents (improved) | Yes | Based on role |
| POST | `` | Upload document | Yes | trainer, admin |
| GET | `/{id}` | Get document | Yes | Based on permissions |
| PUT | `/{id}` | Update document | Yes | uploader or admin |
| DELETE | `/{id}` | Delete document | Yes | uploader or admin |

**Conflicts Identified:**
- Different URL patterns for same functionality
- Duplicate upload/download logic
- Inconsistent permission checking

## Appointment/Calendar Endpoints

### File: `app/api/appointments.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/appointments` | Get appointments | Yes | Any |
| POST | `/appointments` | Create appointment | Yes | trainer |
| PUT | `/appointments/{id}` | Update appointment | Yes | trainer, beneficiary |
| DELETE | `/appointments/{id}` | Cancel appointment | Yes | trainer, beneficiary |
| GET | `/appointments/{id}` | Get appointment | Yes | trainer, beneficiary |

### File: `app/api/calendar.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/calendar/events` | Get calendar events | Yes | Any |
| POST | `/calendar/events` | Create calendar event | Yes | trainer |
| GET | `/calendar/availability` | Get availability | Yes | trainer |
| POST | `/calendar/availability` | Set availability | Yes | trainer |

### File: `app/api/improved_calendar.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `` | Get calendar events (improved) | Yes | Any |
| POST | `` | Create event | Yes | trainer |
| PUT | `/{id}` | Update event | Yes | trainer |
| DELETE | `/{id}` | Delete event | Yes | trainer |

### File: `app/api/calendars_availability.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/calendars/availability` | Get availability slots | Yes | Any |
| POST | `/calendars/availability` | Set availability | Yes | trainer |
| PUT | `/calendars/availability/{id}` | Update availability | Yes | trainer |
| DELETE | `/calendars/availability/{id}` | Delete availability | Yes | trainer |

**Conflicts Identified:**
- Calendar vs appointment functionality overlap
- Multiple availability management endpoints
- Inconsistent event vs appointment terminology

## Notification System Endpoints

### File: `app/api/notifications.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/notifications` | Get notifications | Yes | Any |
| GET | `/notifications/unread-count` | Get unread count | Yes | Any |
| POST | `/notifications/{id}/read` | Mark as read | Yes | Any |
| POST | `/notifications/read-all` | Mark all as read | Yes | Any |
| DELETE | `/notifications/{id}` | Delete notification | Yes | Any |

### File: `app/api/improved_notifications.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `` | Get notifications (improved) | Yes | Any |
| POST | `` | Create notification | Yes | admin |
| PUT | `/{id}` | Update notification | Yes | admin |
| DELETE | `/{id}` | Delete notification | Yes | admin |
| POST | `/{id}/read` | Mark as read | Yes | Any |

### File: `app/api/notifications_fixed.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `` | Get notifications (fixed) | Yes | Any |
| POST | `/send` | Send notification | Yes | admin |
| POST | `/{id}/read` | Mark as read | Yes | Any |

### File: `app/api/notifications_unread.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/unread` | Get unread notifications | Yes | Any |
| GET | `/unread/count` | Get unread count | Yes | Any |
| POST | `/unread/mark-all-read` | Mark all unread as read | Yes | Any |

**Conflicts Identified:**
- 4 different files handling notifications
- Duplicate read/unread functionality
- Inconsistent notification creation patterns

## Program Management Endpoints

### File: `app/api/programs.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/programs` | Get programs list | Yes | Any |
| POST | `/programs` | Create program | Yes | super_admin, tenant_admin |
| GET | `/programs/{id}` | Get program details | Yes | Any |
| PUT | `/programs/{id}` | Update program | Yes | super_admin, tenant_admin |
| DELETE | `/programs/{id}` | Delete program | Yes | super_admin, tenant_admin |
| POST | `/programs/{id}/enroll` | Enroll beneficiary | Yes | trainer, admin |
| POST | `/programs/{id}/modules` | Add module | Yes | admin |
| GET | `/programs/{id}/sessions` | Get sessions | Yes | trainer, admin |
| POST | `/programs/{id}/sessions` | Create session | Yes | trainer, admin |

### File: `app/api/improved_programs.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `` | Get programs (improved) | Yes | Any |
| POST | `` | Create program | Yes | admin |
| GET | `/{id}` | Get program | Yes | Any |
| PUT | `/{id}` | Update program | Yes | admin |
| DELETE | `/{id}` | Delete program | Yes | admin |

**Conflicts Identified:**
- Duplicate CRUD operations
- Different enrollment logic
- Inconsistent module/session management

## Settings Management Endpoints

### File: `app/api/settings.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/settings/general` | Get general settings | Yes | Any |
| PUT | `/settings/general` | Update general settings | Yes | Any |

### File: `app/api/settings_general.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/general` | Get general settings | Yes | Any |
| PUT | `/general` | Update general settings | Yes | Any |
| GET | `/system` | Get system settings | Yes | admin |
| PUT | `/system` | Update system settings | Yes | admin |

### File: `app/api/settings_appearance.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/appearance` | Get appearance settings | Yes | Any |
| PUT | `/appearance` | Update appearance settings | Yes | Any |
| GET | `/themes` | Get available themes | Yes | Any |
| POST | `/themes` | Create custom theme | Yes | Any |

**Conflicts Identified:**
- Split settings functionality across multiple files
- Inconsistent URL patterns
- Overlapping general settings endpoints

## Additional Endpoints Found

### File: `app/api/analytics.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/analytics/dashboard` | Get analytics dashboard | Yes | admin |
| GET | `/analytics/reports` | Get analytics reports | Yes | admin |

### File: `app/api/health.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/health` | Health check | No | Any |
| GET | `/health/detailed` | Detailed health check | Yes | admin |

### File: `app/api/portal.py`
| Method | Path | Description | Auth Required | Roles |
|--------|------|-------------|---------------|-------|
| GET | `/portal/dashboard` | Get portal dashboard | Yes | Any |
| GET | `/portal/quick-stats` | Get quick statistics | Yes | Any |

## Summary of Issues

### Critical Issues
1. **Multiple Authentication Systems**: 3 different auth implementations
2. **Fragmented User Management**: Core functionality spread across 3 files
3. **Scattered Beneficiary Logic**: Related functionality in multiple locations
4. **Inconsistent URL Patterns**: Mix of `/api/v2/`, no prefix, and various patterns
5. **Role vs Permission Systems**: Inconsistent access control mechanisms

### Major Issues
1. **Duplicate CRUD Operations**: Most resources have 2-3 implementations
2. **Response Format Inconsistency**: Different JSON structures across endpoints
3. **Error Handling Variations**: Multiple error response patterns
4. **Pagination Inconsistency**: Different pagination implementations

### Minor Issues
1. **Naming Conventions**: Mix of singular/plural resource names
2. **HTTP Method Usage**: Some non-RESTful patterns
3. **Documentation Gaps**: Missing or inconsistent API documentation

## Recommendations

1. **Immediate Actions**:
   - Standardize on v2 URL pattern: `/api/v2/{resource}`
   - Implement consistent response formatting
   - Consolidate authentication into single implementation

2. **Short-term Goals**:
   - Merge duplicate endpoint implementations
   - Standardize error handling across all endpoints
   - Implement consistent pagination

3. **Long-term Goals**:
   - Complete API consolidation as per consolidation plan
   - Implement comprehensive API documentation
   - Establish API governance and versioning strategy

This analysis provides the foundation for the comprehensive API consolidation outlined in the accompanying consolidation plan.