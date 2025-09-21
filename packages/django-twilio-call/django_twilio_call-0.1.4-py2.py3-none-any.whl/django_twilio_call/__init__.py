"""Django-Twilio-Call: Enterprise-grade Django package for call center functionality using Twilio."""

__version__ = "0.1.4"
__author__ = "Gojjo Tech"
__email__ = "admin@gojjotech.com"
__license__ = "MIT"

# Set default app config for Django
default_app_config = "django_twilio_call.apps.DjangoTwilioCallConfig"

# Note: Model and service imports are available after Django app initialization
# Usage:
#   from django_twilio_call.models import Agent, Call, CallLog
#   from django_twilio_call.services import call_service, queue_service
