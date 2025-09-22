"""
Configuration management for mesonet alerts.

Handles environment variables and provides future hooks for database-backed configuration.
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Union, Any
from dotenv import load_dotenv
load_dotenv()


@dataclass
class EmailConfig:
    """Email configuration with SMTP settings and recipients."""
    
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    from_address: str
    to_addresses: list[str]
    alerts_table_name: Optional[str]
    expected_records_per_provider_per_hour: int

def load_email_config(config: Optional[Union[Dict[str, Any], object]] = None) -> EmailConfig:
    """
    Load email configuration from a config dict, class/object, or environment variables.
    
    Precedence:
        1. Config dict or object attributes (if provided)
        2. Environment variables
        3. Hardcoded defaults
    """
    def get_value(key: str, env_var: str, default: str) -> str:
        # Dict case
        if isinstance(config, dict) and key in config:
            return config.get(key, default)
        # Object/class case
        if config and hasattr(config, key):
            return getattr(config, key, default)
        # Env fallback
        return os.getenv(env_var, default)

    # Parse comma-separated recipients
    to_addresses_str = get_value(
        "ALERTS_TO", "ALERTS_TO", "admin@local.test,kevin@local.test"
    )
    to_addresses = [addr.strip() for addr in to_addresses_str.split(",") if addr.strip()]

    return EmailConfig(
        smtp_host=get_value("ALERTS_SMTP_HOST", "ALERTS_SMTP_HOST", "localhost"),
        smtp_port=int(get_value("ALERTS_SMTP_PORT", "ALERTS_SMTP_PORT", "1025")),
        smtp_user=get_value("ALERTS_SMTP_USER", "ALERTS_SMTP_USER", ""),
        smtp_password=get_value("ALERTS_SMTP_PASS", "ALERTS_SMTP_PASS", ""),
        from_address=get_value("ALERTS_FROM", "ALERTS_FROM", "alerts@local.test"),
        to_addresses=to_addresses,
        alerts_table_name=get_value("ALERTS_TABLE_NAME", "ALERTS_TABLE_NAME", None),
        expected_records_per_provider_per_hour=int(
            get_value(
                "EXPECTED_RECORDS_PER_PROVIDER_PER_HOUR",
                "EXPECTED_RECORDS_PER_PROVIDER_PER_HOUR",
                "100",
            )
        ),
    )


# TODO: Future database-backed configuration
# class EmailConfigRepo:
#     """Repository for fetching email configuration from database."""
#     
#     @staticmethod
#     def get_active_config() -> EmailConfig:
#         """
#         Fetch active email configuration from database.
#         
#         This would retrieve SMTP credentials, template overrides,
#         and recipient lists from a centralized configuration table.
#         
#         Returns:
#             EmailConfig: Active configuration from database
#         """
#         pass
#
#
# class RecipientRoutingRepo:
#     """Repository for provider/severity-based recipient routing."""
#     
#     @staticmethod
#     def get_recipients(provider: str, severity: str) -> list[str]:
#         """
#         Get recipients based on provider and severity level.
#         
#         This would implement sophisticated routing rules like:
#         - Critical errors go to on-call team
#         - Provider-specific alerts go to data team + provider contacts
#         - Volume drops go to operations team
#         
#         Args:
#             provider: Provider name (e.g., "colorado", "iowa")
#             severity: Alert severity (e.g., "ERROR", "WARN", "INFO")
#             
#         Returns:
#             list[str]: Email addresses for this provider/severity combination
#         """
#         pass 