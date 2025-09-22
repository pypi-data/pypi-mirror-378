"""Unified profile management for d365fo-client."""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from .models import FOClientConfig
    from .credential_sources import CredentialSource

logger = logging.getLogger(__name__)


@dataclass
class Profile:
    """Unified profile for CLI and MCP operations."""

    # Core identification
    name: str
    description: Optional[str] = None

    # Connection settings
    base_url: str = ""
    auth_mode: str = "default"
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    tenant_id: Optional[str] = None
    use_default_credentials: Optional[bool] = None  # None means derive from auth_mode
    verify_ssl: bool = True
    timeout: int = 60
    credential_source: Optional["CredentialSource"] = None

    # Cache settings
    use_label_cache: bool = True
    label_cache_expiry_minutes: int = 60
    use_cache_first: bool = True
    cache_dir: Optional[str] = None

    # Localization
    language: str = "en-US"

    # CLI-specific settings (with defaults for MCP)
    output_format: str = "table"

    def to_client_config(self) -> "FOClientConfig":
        """Convert profile to FOClientConfig."""
        from .models import FOClientConfig

        # Determine use_default_credentials: explicit setting takes precedence over auth_mode
        if self.use_default_credentials is not None:
            use_default_creds = self.use_default_credentials
        else:
            use_default_creds = self.auth_mode == "default"

        return FOClientConfig(
            base_url=self.base_url,
            auth_mode=self.auth_mode,
            client_id=self.client_id,
            client_secret=self.client_secret,
            tenant_id=self.tenant_id,
            use_default_credentials=use_default_creds,
            timeout=self.timeout,
            verify_ssl=self.verify_ssl,
            use_label_cache=self.use_label_cache,
            label_cache_expiry_minutes=self.label_cache_expiry_minutes,
            use_cache_first=self.use_cache_first,
            metadata_cache_dir=self.cache_dir,
            credential_source=self.credential_source,
        )

    def validate(self) -> List[str]:
        """Validate profile configuration."""
        errors = []

        if not self.base_url:
            errors.append("Base URL is required")

        if self.auth_mode == "client_credentials":
            if not self.client_id:
                errors.append("Client ID is required for client_credentials auth mode")
            if not self.client_secret:
                errors.append(
                    "Client secret is required for client_credentials auth mode"
                )
            if not self.tenant_id:
                errors.append("Tenant ID is required for client_credentials auth mode")

        if self.timeout <= 0:
            errors.append("Timeout must be greater than 0")

        if self.label_cache_expiry_minutes <= 0:
            errors.append("Label cache expiry must be greater than 0")

        return errors

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "Profile":
        """Create Profile from dictionary data with migration support."""

        # Handle parameter migration from legacy formats
        migrated_data = cls._migrate_legacy_parameters(data.copy())

        # Ensure name is set
        migrated_data["name"] = name

        # Add defaults for missing parameters
        defaults = {
            "description": None,
            "base_url": "",
            "auth_mode": "default",
            "client_id": None,
            "client_secret": None,
            "tenant_id": None,
            "use_default_credentials": None,
            "verify_ssl": True,
            "timeout": 60,
            "use_label_cache": True,
            "label_cache_expiry_minutes": 60,
            "use_cache_first": True,
            "cache_dir": None,
            "language": "en-US",
            "output_format": "table",
            "credential_source": None,
        }

        for key, default_value in defaults.items():
            if key not in migrated_data:
                migrated_data[key] = default_value

        # Filter out any unknown parameters
        valid_params = {
            k: v for k, v in migrated_data.items() if k in cls.__dataclass_fields__
        }

        # Handle credential_source deserialization
        if "credential_source" in valid_params and valid_params["credential_source"] is not None:
            from .credential_sources import CredentialSource
            credential_source_data = valid_params["credential_source"]
            try:
                valid_params["credential_source"] = CredentialSource.from_dict(credential_source_data)
            except Exception as e:
                logger.error(f"Error deserializing credential_source: {e}")
                valid_params["credential_source"] = None

        try:
            return cls(**valid_params)
        except Exception as e:
            logger.error(f"Error creating profile {name}: {e}")
            logger.error(f"Data: {valid_params}")
            raise

    @classmethod
    def _migrate_legacy_parameters(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate legacy parameter names to current format."""

        # Map old parameter names to new ones
        parameter_migrations = {
            "label_cache": "use_label_cache",
            "label_expiry": "label_cache_expiry_minutes",
        }

        for old_name, new_name in parameter_migrations.items():
            if old_name in data and new_name not in data:
                data[new_name] = data.pop(old_name)
                logger.debug(f"Migrated parameter {old_name} -> {new_name}")

        return data

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for storage."""
        from dataclasses import asdict

        # Convert to dict and remove name (stored as key)
        data = asdict(self)
        data.pop("name", None)

        # Handle credential_source serialization
        if self.credential_source is not None:
            data["credential_source"] = self.credential_source.to_dict()

        return data

    def clone(self, name: str, **overrides) -> "Profile":
        """Create a copy of this profile with a new name and optional overrides."""
        from dataclasses import replace

        # Create a copy with new name
        new_profile = replace(self, name=name)

        # Apply any overrides
        if overrides:
            new_profile = replace(new_profile, **overrides)

        return new_profile

    def __str__(self) -> str:
        """String representation of the profile."""
        return f"Profile(name='{self.name}', base_url='{self.base_url}', auth_mode='{self.auth_mode}')"

    def __repr__(self) -> str:
        """Detailed string representation of the profile."""
        return (
            f"Profile(name='{self.name}', base_url='{self.base_url}', "
            f"auth_mode='{self.auth_mode}', description='{self.description}')"
        )
