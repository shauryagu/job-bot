"""
Core Configuration Module

Imports and re-exports settings for easy access across the application.
"""

from config.settings import settings
from typing import List, Dict, Any, Optional
import yaml
from pathlib import Path

__all__ = ["settings", "load_companies_config", "get_companies_by_ats_type", "get_company_config", "validate_companies_config"]


def load_companies_config(config_path: str = "config/companies.yaml") -> Dict[str, Any]:
    """
    Load and parse companies configuration from YAML file.

    Args:
        config_path: Path to companies configuration file

    Returns:
        Dictionary containing companies configuration

    Raises:
        ConfigurationException: If file cannot be loaded or parsed
    """
    from app.core.exceptions import ConfigurationException
    from app.core.logging import get_logger

    logger = get_logger(__name__)

    try:
        config_file = Path(config_path)
        if not config_file.exists():
            raise ConfigurationException(f"Companies config file not found: {config_path}")

        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        if not config or "companies" not in config:
            raise ConfigurationException("Invalid companies config: missing 'companies' key")

        logger.info(f"Loaded companies configuration from {config_path}")
        return config

    except yaml.YAMLError as e:
        raise ConfigurationException(f"Failed to parse companies config: {str(e)}")
    except Exception as e:
        raise ConfigurationException(f"Failed to load companies config: {str(e)}")


def get_companies_by_ats_type(ats_type: str, config_path: str = "config/companies.yaml") -> List[Dict[str, Any]]:
    """
    Get companies filtered by ATS type.

    Args:
        ats_type: ATS type to filter by (e.g., "greenhouse", "lever")
        config_path: Path to companies configuration file

    Returns:
        List of company configurations matching the ATS type
    """
    from app.core.logging import get_logger

    logger = get_logger(__name__)

    try:
        config = load_companies_config(config_path)
        companies = config.get("companies", [])

        filtered = [c for c in companies if c.get("ats_type") == ats_type.lower()]
        logger.info(f"Found {len(filtered)} companies with ATS type '{ats_type}'")

        return filtered

    except Exception as e:
        logger.error(f"Failed to get companies by ATS type: {e}")
        return []


def get_company_config(company_name: str, config_path: str = "config/companies.yaml") -> Optional[Dict[str, Any]]:
    """
    Get specific company configuration by name.

    Args:
        company_name: Company name to look up
        config_path: Path to companies configuration file

    Returns:
        Company configuration dictionary or None if not found
    """
    from app.core.logging import get_logger

    logger = get_logger(__name__)

    try:
        config = load_companies_config(config_path)
        companies = config.get("companies", [])

        for company in companies:
            if company.get("name") == company_name:
                return company

        logger.warning(f"Company '{company_name}' not found in configuration")
        return None

    except Exception as e:
        logger.error(f"Failed to get company config: {e}")
        return None


def validate_companies_config(config_path: str = "config/companies.yaml") -> bool:
    """
    Validate companies configuration structure.

    Args:
        config_path: Path to companies configuration file

    Returns:
        True if configuration is valid, False otherwise
    """
    from app.core.logging import get_logger

    logger = get_logger(__name__)

    try:
        config = load_companies_config(config_path)
        companies = config.get("companies", [])

        if not isinstance(companies, list):
            logger.error("Companies config: 'companies' must be a list")
            return False

        required_fields = ["name", "priority", "ats_type", "careers_url"]
        valid_ats_types = ["greenhouse", "lever", "ashby", "workday", "manual", "other"]

        for i, company in enumerate(companies):
            if not isinstance(company, dict):
                logger.error(f"Company {i}: must be a dictionary")
                return False

            missing_fields = [field for field in required_fields if field not in company]
            if missing_fields:
                logger.error(f"Company {i}: missing required fields: {missing_fields}")
                return False

            ats_type = company.get("ats_type")
            if ats_type not in valid_ats_types:
                logger.error(f"Company {i}: invalid ATS type '{ats_type}'")
                return False

            priority = company.get("priority")
            if not isinstance(priority, int) or priority < 1 or priority > 5:
                logger.error(f"Company {i}: priority must be an integer between 1 and 5")
                return False

        logger.info(f"Companies configuration validation passed for {len(companies)} companies")
        return True

    except Exception as e:
        logger.error(f"Failed to validate companies config: {e}")
        return False