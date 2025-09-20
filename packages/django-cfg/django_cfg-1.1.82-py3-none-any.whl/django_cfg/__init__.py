"""
Django-CFG: Developer-First Django Configuration with Pydantic v2

A revolutionary Django configuration system that provides type-safe, intelligent,
and zero-boilerplate configuration management through Pydantic v2 models.

Key Features:
- 90% reduction in settings.py boilerplate
- 100% type safety with Pydantic v2 models
- Environment-aware smart defaults
- Seamless third-party integrations
- Zero raw dictionary usage

Example:
    ```python
    from django_cfg import DjangoConfig, DatabaseConnection
    
    class MyConfig(DjangoConfig):
        project_name: str = "My Project"
        databases: Dict[str, DatabaseConnection] = {
            "default": DatabaseConnection(
                engine="django.db.backends.postgresql",
                name="${DATABASE_URL:mydb}",
            )
        }
    
    config = MyConfig()
    ```
"""

# Check Python version immediately on import
from .version_check import check_python_version
check_python_version("django-cfg")

# Configure Django app
default_app_config = "django_cfg.apps.DjangoCfgConfig"

from typing import TYPE_CHECKING

# Version information
__version__ = "1.1.82"
__author__ = "Unrealos Team"
__email__ = "info@unrealos.com"
__license__ = "MIT"

# Core exports - only import when needed to avoid circular imports
if TYPE_CHECKING:
    from django_cfg.core.config import DjangoConfig
    from django_cfg.models.database import DatabaseConnection, DatabaseRoutingRule
    from django_cfg.models.cache import CacheBackend
    from django_cfg.models.security import SecuritySettings
    from django_cfg.models.services import EmailConfig, TelegramConfig
    from django_cfg.models.jwt import JWTConfig
    from django_cfg.modules.django_twilio.models import TwilioConfig
    from django_cfg.modules.django_twilio.service import DjangoTwilioService
    from django_cfg.models.logging import LoggingConfig
    from django_cfg.models.limits import LimitsConfig
    from django_cfg.models.ngrok import NgrokConfig, NgrokAuthConfig, NgrokTunnelConfig
    from django_cfg.models.third_party.revolution import RevolutionConfig, APIZone
    from django_cfg.models.unfold import UnfoldConfig, UnfoldColors, UnfoldSidebar
    from django_cfg.models.constance import ConstanceConfig, ConstanceField
    # LLM models are deprecated - use direct LLMClient injection instead

    # Dashboard models are now part of unfold module
    from django_cfg.models.environment import EnvironmentConfig
    from django_cfg.exceptions import DjangoCfgException, ConfigurationError, ValidationError


# Lazy imports to avoid import time overhead
def __getattr__(name: str):
    """Lazy import mechanism to avoid circular imports and improve startup time."""

    # Core classes
    if name == "DjangoConfig":
        from django_cfg.core.config import DjangoConfig

        return DjangoConfig

    # Database models
    elif name == "DatabaseConnection":
        from django_cfg.models.database import DatabaseConnection

        return DatabaseConnection

    # Cache models
    elif name == "CacheBackend":
        from django_cfg.models.cache import CacheBackend

        return CacheBackend

    # Security models
    elif name == "SecuritySettings":
        from django_cfg.models.security import SecuritySettings

        return SecuritySettings

    # Service models
    elif name == "EmailConfig":
        from django_cfg.models.services import EmailConfig

        return EmailConfig
    elif name == "TelegramConfig":
        from django_cfg.models.services import TelegramConfig

        return TelegramConfig
    elif name == "TwilioConfig":
        from django_cfg.modules.django_twilio.models import TwilioConfig

        return TwilioConfig
    elif name == "JWTConfig":
        from django_cfg.models.jwt import JWTConfig

        return JWTConfig

    # Limits models
    elif name == "LimitsConfig":
        from django_cfg.models.limits import LimitsConfig

        return LimitsConfig

    # Ngrok models
    elif name == "NgrokConfig":
        from django_cfg.models.ngrok import NgrokConfig

        return NgrokConfig
    elif name == "NgrokAuthConfig":
        from django_cfg.models.ngrok import NgrokAuthConfig

        return NgrokAuthConfig
    elif name == "NgrokTunnelConfig":
        from django_cfg.models.ngrok import NgrokTunnelConfig

        return NgrokTunnelConfig

    # Logging models
    elif name == "LoggingConfig":
        from django_cfg.models.logging import LoggingConfig

        return LoggingConfig

    # Third-party models - Django Revolution (always available)
    elif name == "RevolutionConfig":
        from django_cfg.models.revolution import RevolutionConfig

        return RevolutionConfig
    elif name == "APIZone":
        from django_revolution.config import ZoneModel as APIZone

        return APIZone
    elif name == "ZoneModel":
        from django_revolution.config import ZoneModel

        return ZoneModel
    elif name == "ZoneConfig":
        from django_revolution.app_config import ZoneConfig

        return ZoneConfig
    elif name == "DjangoRevolutionSettings":
        from django_revolution.config import DjangoRevolutionSettings

        return DjangoRevolutionSettings

    elif name == "UnfoldConfig":
        from django_cfg.models.unfold import UnfoldConfig

        return UnfoldConfig
    elif name == "UnfoldColors":
        from django_cfg.models.unfold import UnfoldColors

        return UnfoldColors
    elif name == "UnfoldSidebar":
        from django_cfg.models.unfold import UnfoldSidebar

        return UnfoldSidebar

    # Dashboard models
    elif name == "DashboardConfig":
        from django_cfg.models.unfold import DashboardWidget as DashboardConfig

        return DashboardConfig
    elif name == "QuickAction":
        from django_cfg.models.unfold import QuickAction

        return QuickAction
    elif name == "NavigationItem":
        from django_cfg.models.unfold import NavigationItem

        return NavigationItem
    elif name == "NavigationGroup":
        from django_cfg.models.unfold import NavigationGroup

        return NavigationGroup

    # Environment models
    elif name == "EnvironmentConfig":
        from django_cfg.models.environment import EnvironmentConfig

        return EnvironmentConfig

    # Exceptions
    elif name == "DjangoCfgException":
        from django_cfg.exceptions import DjangoCfgException

        return DjangoCfgException
    elif name == "ConfigurationError":
        from django_cfg.exceptions import ConfigurationError

        return ConfigurationError
    elif name == "ValidationError":
        from django_cfg.exceptions import ValidationError

        return ValidationError

    # Auto-configuring modules
    elif name == "DjangoLogger":
        from django_cfg.modules.django_logger import DjangoLogger

        return DjangoLogger
    elif name == "get_logger":
        from django_cfg.modules.django_logger import get_logger

        return get_logger
    elif name == "DjangoEmailService":
        from django_cfg.modules.django_email import DjangoEmailService

        return DjangoEmailService
    elif name == "send_email":
        from django_cfg.modules.django_email import send_email

        return send_email
    elif name == "DjangoTelegram":
        from django_cfg.modules.django_telegram import DjangoTelegram

        return DjangoTelegram
    elif name == "send_telegram_message":
        from django_cfg.modules.django_telegram import send_telegram_message

        return send_telegram_message
    elif name == "send_telegram_photo":
        from django_cfg.modules.django_telegram import send_telegram_photo

        return send_telegram_photo
    elif name == "DjangoTwilioService":
        from django_cfg.modules.django_twilio.service import DjangoTwilioService

        return DjangoTwilioService
    elif name == "send_whatsapp_otp":
        from django_cfg.modules.django_twilio.service import send_whatsapp_otp

        return send_whatsapp_otp
    elif name == "send_email_otp":
        from django_cfg.modules.django_twilio.service import send_email_otp

        return send_email_otp
    elif name == "send_sms_otp":
        from django_cfg.modules.django_twilio.service import send_sms_otp

        return send_sms_otp
    elif name == "verify_otp":
        from django_cfg.modules.django_twilio.service import verify_otp

        return verify_otp
    elif name == "DjangoLLM":
        from django_cfg.modules.django_llm import DjangoLLM

        return DjangoLLM
    elif name == "DjangoTranslator":
        from django_cfg.modules.django_llm import DjangoTranslator

        return DjangoTranslator
    elif name == "chat_completion":
        from django_cfg.modules.django_llm import chat_completion

        return chat_completion
    elif name == "translate_text":
        from django_cfg.modules.django_llm import translate_text

        return translate_text
    elif name == "translate_json":
        from django_cfg.modules.django_llm import translate_json

        return translate_json

    # Ngrok service
    elif name == "DjangoNgrok":
        from django_cfg.modules.django_ngrok import DjangoNgrok

        return DjangoNgrok
    elif name == "get_ngrok_service":
        from django_cfg.modules.django_ngrok import get_ngrok_service

        return get_ngrok_service
    elif name == "start_tunnel":
        from django_cfg.modules.django_ngrok import start_tunnel

        return start_tunnel
    elif name == "stop_tunnel":
        from django_cfg.modules.django_ngrok import stop_tunnel

        return stop_tunnel
    elif name == "get_tunnel_url":
        from django_cfg.modules.django_ngrok import get_tunnel_url

        return get_tunnel_url
    elif name == "get_webhook_url":
        from django_cfg.modules.django_ngrok import get_webhook_url

        return get_webhook_url
    elif name == "get_api_url":
        from django_cfg.modules.django_ngrok import get_api_url

        return get_api_url

    # Unfold models
    elif name == "UnfoldConfig":
        from django_cfg.models.unfold import UnfoldConfig

        return UnfoldConfig
    elif name == "UnfoldTheme":
        from django_cfg.models.unfold import UnfoldTheme

        return UnfoldTheme
    elif name == "UnfoldColors":
        from django_cfg.models.unfold import UnfoldColors

        return UnfoldColors
    elif name == "UnfoldSidebar":
        from django_cfg.models.unfold import UnfoldSidebar

        return UnfoldSidebar
    elif name == "NavigationItem":
        from django_cfg.models.unfold import NavigationItem

        return NavigationItem
    elif name == "NavigationGroup":
        from django_cfg.models.unfold import NavigationGroup

        return NavigationGroup
    elif name == "QuickAction":
        from django_cfg.models.unfold import QuickAction

        return QuickAction
    elif name == "DashboardWidget":
        from django_cfg.models.unfold import DashboardWidget

        return DashboardWidget
    elif name == "DropdownItem":
        from django_cfg.models.unfold import DropdownItem

        return DropdownItem

    # DRF models
    elif name == "DRFConfig":
        from django_cfg.models.drf import DRFConfig

        return DRFConfig
    elif name == "SpectacularConfig":
        from django_cfg.models.drf import SpectacularConfig

        return SpectacularConfig
    elif name == "SwaggerUISettings":
        from django_cfg.models.drf import SwaggerUISettings

        return SwaggerUISettings
    elif name == "RedocUISettings":
        from django_cfg.models.drf import RedocUISettings

        return RedocUISettings

    # Constance models
    elif name == "ConstanceConfig":
        from django_cfg.models.constance import ConstanceConfig

        return ConstanceConfig
    elif name == "ConstanceField":
        from django_cfg.models.constance import ConstanceField

        return ConstanceField

    # URL integration
    elif name == "add_django_cfg_urls":
        from django_cfg.integration import add_django_cfg_urls

        return add_django_cfg_urls
    elif name == "get_django_cfg_urls_info":
        from django_cfg.integration import get_django_cfg_urls_info

        return get_django_cfg_urls_info

    # Unknown attribute
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Public API - what users can import
__all__ = [
    # Core
    "DjangoConfig",
    # Database
    "DatabaseConnection",
    # Cache
    "CacheBackend",
    # Security
    "SecuritySettings",
    # Services
    "EmailConfig",
    "TelegramConfig",
    "TwilioConfig",
    "JWTConfig",
    # Limits
    "LimitsConfig",
    # Logging
    "LoggingConfig",
    # Ngrok
    "NgrokConfig",
    "NgrokAuthConfig", 
    "NgrokTunnelConfig",
    # Third-party integrations
    "RevolutionConfig",
    "APIZone",
    "UnfoldConfig",
    "UnfoldColors",
    "UnfoldSidebar",
    # Dashboard
    "DashboardConfig",
    "QuickAction",
    "NavigationItem",
    "NavigationGroup",
    # Environment
    "EnvironmentConfig",
    # LLM Configuration
    # LLM configs deprecated
    # Exceptions
    "DjangoCfgException",
    "ConfigurationError",
    "ValidationError",
    # Auto-configuring modules
    "DjangoLogger",
    "get_logger",
    "DjangoEmailService",
    "send_email",
    "DjangoTelegram",
    "send_telegram_message",
    "send_telegram_photo",
    # Twilio services
    "DjangoTwilioService",
    "send_whatsapp_otp",
    "send_email_otp",
    "send_sms_otp", 
    "verify_otp",
    "DjangoLLM",
    "DjangoTranslator",
    "chat_completion",
    "translate_text",
    "translate_json",
    # Ngrok service
    "DjangoNgrok",
    "get_ngrok_service",
    "start_tunnel",
    "stop_tunnel",
    "get_tunnel_url", 
    "get_webhook_url",
    "get_api_url",
    # Unfold admin interface
    "UnfoldConfig",
    "UnfoldTheme",
    "UnfoldColors",
    "UnfoldSidebar",
    "NavigationItem",
    "NavigationGroup",
    "DropdownItem",
    "QuickAction",
    "DashboardWidget",
    # DRF
    "DRFConfig",
    "SpectacularConfig",
    "SwaggerUISettings",
    "RedocUISettings",
    # Constance
    "ConstanceConfig",
    "ConstanceField",
    # LLM
    # LLM configs deprecated
    # URL integration
    "add_django_cfg_urls",
    "get_django_cfg_urls_info",
]
