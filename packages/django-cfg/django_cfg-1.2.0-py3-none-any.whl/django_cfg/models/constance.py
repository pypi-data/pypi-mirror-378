"""
Django Constance Configuration Models

Type-safe configuration for django-constance with automatic
Unfold admin integration and smart field grouping.
"""

from typing import Dict, List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field, field_validator
from pathlib import Path


class ConstanceField(BaseModel):
    """
    Configuration for a single Constance field.

    Provides type-safe field definition with automatic
    Django settings generation and Unfold integration.
    """

    name: str = Field(
        ...,
        description="Field name (will be used as setting key)",
        min_length=1,
        max_length=100,
        pattern=r"^[A-Z][A-Z0-9_]*$",  # Enforce uppercase setting names
    )

    default: Union[str, int, float, bool] = Field(
        ...,
        description="Default value for the field",
    )

    help_text: str = Field(
        default="",
        description="Help text displayed in admin interface",
        max_length=500,
    )

    field_type: Literal["str", "int", "float", "bool", "choice"] = Field(
        default="str",
        description="Field type for form rendering and validation",
    )

    group: str = Field(
        default="General",
        description="Group name for organizing fields in admin",
        max_length=50,
    )

    choices: Optional[List[tuple[str, str]]] = Field(
        default=None,
        description="Choices for choice field type",
    )

    required: bool = Field(
        default=True,
        description="Whether field is required",
    )

    @field_validator("choices")
    @classmethod
    def validate_choices(cls, v, info):
        """Validate choices are provided for choice field type."""
        if info.data.get("field_type") == "choice" and not v:
            raise ValueError("Choices must be provided for choice field type")
        return v

    def to_constance_config(self) -> tuple[Any, str]:
        """Convert to Constance configuration format."""
        return (self.default, self.help_text)

    def to_constance_field_config(self) -> Dict[str, Any]:
        """Convert to Constance additional fields configuration."""
        if self.field_type == "choice" and self.choices:
            return [
                "django.forms.fields.ChoiceField",
                {
                    "widget": "unfold.widgets.UnfoldAdminSelectWidget",
                    "choices": self.choices,
                },
            ]

        # Map field types to Django form fields with Unfold widgets
        field_mapping = {
            "str": [
                "django.forms.CharField",
                {"widget": "unfold.widgets.UnfoldAdminTextInputWidget"},
            ],
            "int": [
                "django.forms.IntegerField",
                {"widget": "unfold.widgets.UnfoldAdminIntegerFieldWidget"},
            ],
            "float": [
                "django.forms.FloatField",
                {"widget": "unfold.widgets.UnfoldAdminTextInputWidget"},
            ],
            "bool": [
                "django.forms.BooleanField",
                {"widget": "unfold.widgets.UnfoldBooleanSwitchWidget"},
            ],
        }

        return field_mapping.get(self.field_type, field_mapping["str"])


class ConstanceConfig(BaseModel):
    """
    Django Constance configuration with automatic Unfold integration.

    Provides type-safe configuration for django-constance with:
    - Automatic field grouping in admin interface
    - Unfold widget integration
    - Smart Django settings generation
    - Field validation and type safety
    """

    database_cache_backend: Optional[str] = Field(
        default=None,
        description="Cache backend for database storage (None to disable)",
    )

    redis_connection_class: Optional[str] = Field(
        default=None,
        description="Redis connection class for Redis backend",
    )

    redis_prefix: str = Field(
        default="constance:",
        description="Redis key prefix",
    )

    cache_prefix: str = Field(
        default="constance:cache:",
        description="Cache key prefix",
    )

    cache_autofill_timeout: int = Field(
        default=300,
        description="Cache autofill timeout in seconds",
        ge=0,
    )

    fields: List[ConstanceField] = Field(
        default_factory=list,
        description="List of Constance fields",
    )

    def get_config_dict(self) -> Dict[str, tuple[Any, str]]:
        """Generate CONSTANCE_CONFIG dictionary."""
        return {field.name: field.to_constance_config() for field in self.fields}

    def get_fieldsets_dict(self) -> Dict[str, List[str]]:
        """Generate CONSTANCE_FIELDSETS dictionary grouped by field groups."""
        fieldsets = {}

        for field in self.fields:
            group = field.group
            if group not in fieldsets:
                fieldsets[group] = []
            fieldsets[group].append(field.name)

        return fieldsets

    def get_additional_fields_dict(self) -> Dict[str, List[Any]]:
        """Generate CONSTANCE_ADDITIONAL_FIELDS dictionary."""
        # Start with Unfold base fields
        from unfold.contrib.constance.settings import UNFOLD_CONSTANCE_ADDITIONAL_FIELDS

        additional_fields = dict(UNFOLD_CONSTANCE_ADDITIONAL_FIELDS)

        # Add custom field configurations
        for field in self.fields:
            if field.field_type == "choice" or field.choices:
                additional_fields[f"{field.name.lower()}_field"] = field.to_constance_field_config()

        return additional_fields

    def to_django_settings(self) -> Dict[str, Any]:
        """Generate Django settings for Constance."""
        if not self.fields:
            return {}

        settings = {
            # Main configuration
            "CONSTANCE_CONFIG": self.get_config_dict(),
            "CONSTANCE_FIELDSETS": self.get_fieldsets_dict(),
            # Backend settings (using default database backend)
            "CONSTANCE_BACKEND": "constance.backends.database.DatabaseBackend",
            # Cache settings
            "CONSTANCE_DATABASE_CACHE_BACKEND": self.database_cache_backend,
            "CONSTANCE_DATABASE_PREFIX": self.cache_prefix,
            "CONSTANCE_DATABASE_CACHE_AUTOFILL_TIMEOUT": self.cache_autofill_timeout,
            # Redis settings (if using Redis backend)
            "CONSTANCE_REDIS_CONNECTION_CLASS": self.redis_connection_class,
            "CONSTANCE_REDIS_PREFIX": self.redis_prefix,
            # Additional fields with Unfold widgets
            "CONSTANCE_ADDITIONAL_FIELDS": self.get_additional_fields_dict(),
            # Ignore admin version check
            "CONSTANCE_IGNORE_ADMIN_VERSION_CHECK": True,
        }

        # Remove None values
        return {k: v for k, v in settings.items() if v is not None}


