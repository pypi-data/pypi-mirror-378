"""
DynamoDB-based configuration repository for email settings and templates.

This module provides centralized configuration management using DynamoDB tables
with the following schema:
- Configuration table: id (PK), timestamp (SK)
- Alerts table: id (PK), type (SK)
"""

import boto3
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class SMTPConfig:
    """SMTP configuration settings."""
    host: str
    port: int
    user: str
    password: str
    from_address: str
    use_ssl: bool = True

@dataclass
class EmailConfig:
    """Complete email configuration including SMTP, recipients, and templates."""
    smtp: SMTPConfig
    recipients: List[str]
    templates: Dict[str, Dict[str, str]]

class ConfigRepository:
    """Repository for loading email configuration from DynamoDB."""
    
    def __init__(self, dynamodb_client, config_table_name: str):
        """
        Initialize the configuration repository.
        
        Args:
            dynamodb_client: DynamoDB client instance
            config_table_name: Name of the configuration table
        """
        self.dynamodb = dynamodb_client
        self.config_table_name = config_table_name

    def get_smtp_config(self) -> Optional[SMTPConfig]:
        """Load SMTP configuration from DynamoDB."""
        try:
            response = self.dynamodb.get_item(
                TableName=self.config_table_name,
                Key={
                    'id': {'S': 'smtp_config'},
                    'timestamp': {'S': '2025-09-10T19:30:00Z'}
                }
            )
            
            if 'Item' not in response:
                logger.warning("No SMTP config found in DynamoDB")
                return None
                
            item = response['Item']
            return SMTPConfig(
                host=item.get('host', {}).get('S', 'localhost'),
                port=int(item.get('port', {}).get('N', '1025')),
                user=item.get('user', {}).get('S', ''),
                password=item.get('password', {}).get('S', ''),
                from_address=item.get('from_address', {}).get('S', 'alerts@local.test'),
                use_ssl=item.get('use_ssl', {}).get('BOOL', True)
            )
            
        except Exception as e:
            logger.error(f"Failed to load SMTP config from DynamoDB: {e}")
            return None

    def get_recipients(self) -> List[str]:
        """Load email recipients from DynamoDB."""
        try:
            response = self.dynamodb.get_item(
                TableName=self.config_table_name,
                Key={
                    'id': {'S': 'recipients'},
                    'timestamp': {'S': '2025-09-10T19:30:00Z'}
                }
            )
            
            if 'Item' not in response:
                logger.warning("No recipients config found in DynamoDB")
                return ['admin@local.test']
                
            item = response['Item']
            email_list = item.get('email_list', {}).get('L', [])
            recipients = [email.get('S', '') for email in email_list if email.get('S')]
            
            logger.info(f"Loaded {len(recipients)} recipients from DynamoDB")
            return recipients
            
        except Exception as e:
            logger.error(f"Failed to load recipients from DynamoDB: {e}")
            return ['admin@local.test']

    def get_template(self, template_type: str) -> Optional[Dict[str, str]]:
        """
        Load a specific email template from DynamoDB.
        
        Args:
            template_type: Type of template (e.g., 'ingest_failure', 'volume_drop_warning')
            
        Returns:
            Dictionary with 'html_template', 'text_template', and 'subject' keys
        """
        try:
            response = self.dynamodb.get_item(
                TableName=self.config_table_name,
                Key={
                    'id': {'S': 'template'},
                    'timestamp': {'S': template_type}
                }
            )
            
            if 'Item' not in response:
                logger.warning(f"No template found for type: {template_type}")
                return None
                
            item = response['Item']
            return {
                'html': item.get('html_template', {}).get('S', ''),
                'text': item.get('text_template', {}).get('S', ''),
                'subject': item.get('subject', {}).get('S', f'Alert: {template_type}')
            }
            
        except Exception as e:
            logger.error(f"Failed to load template {template_type} from DynamoDB: {e}")
            return None

    def get_all_templates(self) -> Dict[str, Dict[str, str]]:
        """Load all email templates from DynamoDB."""
        try:
            # Query all template items
            response = self.dynamodb.query(
                TableName=self.config_table_name,
                KeyConditionExpression='id = :id',
                ExpressionAttributeValues={
                    ':id': {'S': 'template'}
                }
            )
            
            templates = {}
            for item in response.get('Items', []):
                template_type = item.get('timestamp', {}).get('S', '')
                if template_type:
                    templates[template_type] = {
                        'html': item.get('html_template', {}).get('S', ''),
                        'text': item.get('text_template', {}).get('S', ''),
                        'subject': item.get('subject', {}).get('S', f'Alert: {template_type}')
                    }
            
            logger.info(f"Loaded {len(templates)} templates from DynamoDB")
            return templates
            
        except Exception as e:
            logger.error(f"Failed to load templates from DynamoDB: {e}")
            return {}

    def get_email_config(self) -> Optional[EmailConfig]:
        """
        Load complete email configuration from DynamoDB.
        
        Returns:
            EmailConfig object with SMTP settings, recipients, and templates
        """
        try:
            # Load SMTP config
            smtp_config = self.get_smtp_config()
            if not smtp_config:
                logger.error("Failed to load SMTP config")
                return None
            
            # Load recipients
            recipients = self.get_recipients()
            
            # Load all templates
            templates = self.get_all_templates()
            
            config = EmailConfig(
                smtp=smtp_config,
                recipients=recipients,
                templates=templates
            )
            
            logger.info(f"Loaded complete email config with {len(recipients)} recipients and {len(templates)} templates")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load complete email config from DynamoDB: {e}")
            return None 