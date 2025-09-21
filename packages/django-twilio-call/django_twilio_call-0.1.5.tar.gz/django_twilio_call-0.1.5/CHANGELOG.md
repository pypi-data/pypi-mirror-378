# Changelog

All notable changes to django-twilio-call will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.5] - 2024-01-19

### Fixed
- **CRITICAL**: Fixed migration error "Indexes passed to ModelState require a name attribute"
- Added names to all database indexes in the initial migration
- Fixed indexes for CallLog, AgentActivity, TaskExecution, and WebhookLog models

## [0.1.4] - 2024-01-19

### Fixed
- **CRITICAL**: Fixed incorrect CallLog model structure in migration
- CallLog now correctly has a ForeignKey to Call model (was missing in v0.1.3)
- Fixed "CallLog has no field named 'call'" error
- Corrected all model fields to match actual models.py definitions

### Added
- Complete model definitions for all 9 models (Agent, Call, Queue, CallLog, CallRecording, PhoneNumber, AgentActivity, TaskExecution, WebhookLog)

## [0.1.3] - 2024-01-19

### Fixed
- **CRITICAL**: Added missing initial migration (0001_initial.py) that creates database tables
- Added missing __init__.py in migrations directory
- Fixed "App 'django_twilio_call' does not have migrations" error
- Fixed database table creation issues

### Added
- Complete initial migration with all model definitions
- Proper migration dependencies

## [0.1.2] - 2024-01-19

### Fixed
- Fixed Django admin error: Removed invalid `filter_horizontal` for reverse relation in QueueAdmin
- QueueAdmin was trying to use `filter_horizontal` with 'agents' which is a reverse ManyToMany relation

## [0.1.1] - 2024-01-19

### Fixed
- **CRITICAL**: Fixed Django AppRegistryNotReady error when importing package
- Removed model and service imports from `__init__.py` that were causing initialization issues
- Models and services must now be imported from their respective modules after Django initialization

### Changed
- Updated import documentation to reflect proper usage patterns

## [0.1.0] - 2024-01-19

### Added
- Initial release of django-twilio-call package
- Complete call center functionality with Twilio integration
- Agent management system with queue routing
- Inbound and outbound call handling
- IVR (Interactive Voice Response) support
- Call recording and transcription capabilities
- Queue management with priority routing
- Real-time call monitoring and analytics
- WebSocket support for live updates
- Comprehensive REST API with Django REST Framework
- JWT authentication with djangorestframework-simplejwt
- Rate limiting and throttling for API endpoints
- Role-Based Access Control (RBAC) for agents
- Webhook handling for Twilio callbacks
- Celery integration for asynchronous tasks
- Redis caching for performance optimization
- Comprehensive observability with Prometheus metrics
- Health check endpoints for monitoring
- Docker and Kubernetes deployment configurations
- Production-ready settings with security hardening
- Extensive documentation and examples
- Test suite with factory-based test data
- Support for Django 4.2, 5.0, and 5.1
- Support for Python 3.8, 3.9, 3.10, 3.11, and 3.12

### Security
- JWT authentication implementation
- Rate limiting on all API endpoints
- Input validation and sanitization
- Webhook signature verification
- Replay attack prevention
- Object-level permission checks
- Encrypted secrets management
- Security headers middleware
- Session security configuration
- CORS properly configured

### Infrastructure
- Multi-stage Docker build
- Docker Compose configuration for local development
- Kubernetes manifests with HorizontalPodAutoscaler
- GitHub Actions CI/CD pipeline
- Multiple environment configurations (dev, staging, prod)
- Comprehensive monitoring and alerting setup

[0.1.0]: https://github.com/hmesfin/django-twilio-call/releases/tag/v0.1.0