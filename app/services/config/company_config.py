"""
Company Configuration Service Module

Handles loading and syncing company configuration from YAML files.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
import yaml
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.services.companies import CompanyService
from app.core.logging import get_logger
from app.core.exceptions import ConfigurationException


class CompanyConfigService:
    """Service for loading and syncing company configuration from YAML."""

    def __init__(self, config_path: str = "config/companies.yaml"):
        self.config_path = config_path
        self.logger = get_logger(__name__)

    def load_config(self) -> Dict[str, Any]:
        """Load company configuration from YAML file."""
        try:
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)

            self.logger.info(f"Loaded company config from {self.config_path}")
            return config
        except FileNotFoundError:
            raise ConfigurationException(f"Company config file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ConfigurationException(f"Invalid YAML in company config: {str(e)}")
        except Exception as e:
            raise ConfigurationException(f"Error loading company config: {str(e)}")

    def sync_with_database(self, db: Session, overwrite: bool = False) -> Dict[str, Any]:
        """
        Sync YAML configuration with database.

        Args:
            db: Database session
            overwrite: If True, overwrite existing companies; if False, skip existing

        Returns:
            Sync statistics
        """
        config = self.load_config()
        companies_data = config.get("companies", [])

        service = CompanyService(db)
        stats = {"created": 0, "updated": 0, "skipped": 0, "errors": []}

        for company_data in companies_data:
            try:
                name = company_data["name"]
                existing = service.get_company_by_name(name)

                if existing:
                    if overwrite:
                        update_data = CompanyUpdate(**company_data)
                        service.update_company(existing.id, update_data)
                        stats["updated"] += 1
                    else:
                        stats["skipped"] += 1
                else:
                    create_data = CompanyCreate(**company_data)
                    service.create_company(create_data)
                    stats["created"] += 1

            except Exception as e:
                self.logger.error(f"Failed to sync company {company_data.get('name', 'unknown')}: {e}")
                stats["errors"].append({"company": company_data.get("name", "unknown"), "error": str(e)})

        self.logger.info(f"Sync complete: {stats}")
        return stats
