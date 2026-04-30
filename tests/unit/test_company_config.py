"""
Unit Tests for Company Configuration Service

Tests the company configuration loading and sync functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from app.services.config.company_config import CompanyConfigService
from app.core.exceptions import ConfigurationException


class TestCompanyConfigService:
    """Tests for CompanyConfigService."""

    def test_load_config(self):
        """Test loading company configuration."""
        config_content = """
companies:
  - name: "Test Company A"
    priority: 5
    ats_type: "greenhouse"
    careers_url: "https://test-a.com/careers"
    locations:
      - "New York"
      - "Remote"
    notes: "Test notes"

  - name: "Test Company B"
    priority: 3
    ats_type: "lever"
    careers_url: "https://test-b.com/jobs"
    locations:
      - "Remote"
    notes: "Another test"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_content)
            temp_path = f.name

        try:
            service = CompanyConfigService(temp_path)
            config = service.load_config()

            assert "companies" in config
            assert isinstance(config["companies"], list)
            assert len(config["companies"]) == 2
            assert config["companies"][0]["name"] == "Test Company A"
            assert config["companies"][1]["name"] == "Test Company B"
        finally:
            os.unlink(temp_path)

    def test_load_config_empty(self):
        """Test loading empty configuration."""
        config_content = """
companies: []
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_content)
            temp_path = f.name

        try:
            service = CompanyConfigService(temp_path)
            config = service.load_config()

            assert "companies" in config
            assert config["companies"] == []
        finally:
            os.unlink(temp_path)

    def test_load_config_invalid_path(self):
        """Test loading config with invalid path."""
        service = CompanyConfigService("config/nonexistent.yaml")

        with pytest.raises(ConfigurationException, match="not found"):
            service.load_config()

    def test_load_config_invalid_yaml(self):
        """Test loading config with invalid YAML."""
        config_content = """
companies:
  - name: "Test Company"
    priority: invalid
    ats_type: greenhouse
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_content)
            temp_path = f.name

        try:
            service = CompanyConfigService(temp_path)

            # This should load successfully (YAML is valid)
            # Validation happens when using the data
            config = service.load_config()
            assert config is not None
            assert "companies" in config
        finally:
            os.unlink(temp_path)

    def test_load_config_malformed_yaml(self):
        """Test loading config with malformed YAML."""
        config_content = """
companies:
  - name: "Test Company"
  invalid yaml syntax
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_content)
            temp_path = f.name

        try:
            service = CompanyConfigService(temp_path)

            with pytest.raises(ConfigurationException):
                service.load_config()
        finally:
            os.unlink(temp_path)

    def test_sync_with_database_create(self, db_session):
        """Test syncing config with database - create mode."""
        config_content = """
companies:
  - name: "New Company A"
    priority: 5
    ats_type: "greenhouse"
    careers_url: "https://new-a.com/careers"
    locations:
      - "New York"
    notes: "New company"

  - name: "New Company B"
    priority: 3
    ats_type: "lever"
    careers_url: "https://new-b.com/jobs"
    locations:
      - "Remote"
    notes: "Another new company"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_content)
            temp_path = f.name

        try:
            service = CompanyConfigService(temp_path)
            stats = service.sync_with_database(db_session, overwrite=False)

            assert stats["created"] == 2
            assert stats["updated"] == 0
            assert stats["skipped"] == 0
            assert len(stats["errors"]) == 0
        finally:
            os.unlink(temp_path)

    def test_sync_with_database_skip_existing(self, db_session):
        """Test syncing config with database - skip existing companies."""
        from app.services.companies import CompanyService
        from app.schemas.company import CompanyCreate

        # Create existing company
        company_service = CompanyService(db_session)
        company_service.create_company(
            CompanyCreate(name="Existing Company", priority=5, ats_type="greenhouse")
        )

        config_content = """
companies:
  - name: "Existing Company"
    priority: 3
    ats_type: "lever"
    careers_url: "https://existing.com/careers"
    locations:
      - "Remote"
    notes: "Updated config"

  - name: "New Company"
    priority: 4
    ats_type: "ashby"
    careers_url: "https://new.com/careers"
    locations:
      - "New York"
    notes: "New from config"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_content)
            temp_path = f.name

        try:
            service = CompanyConfigService(temp_path)
            stats = service.sync_with_database(db_session, overwrite=False)

            assert stats["created"] == 1
            assert stats["updated"] == 0
            assert stats["skipped"] == 1
            assert len(stats["errors"]) == 0

            # Verify existing company wasn't updated
            existing = company_service.get_company_by_name("Existing Company")
            assert existing.priority.value == 5  # Still original value
            assert existing.ats_type.value == "greenhouse"  # Still original value
        finally:
            os.unlink(temp_path)

    def test_sync_with_database_overwrite_existing(self, db_session):
        """Test syncing config with database - overwrite existing companies."""
        from app.services.companies import CompanyService
        from app.schemas.company import CompanyCreate

        # Create existing company
        company_service = CompanyService(db_session)
        company = company_service.create_company(
            CompanyCreate(name="Existing Company", priority=5, ats_type="greenhouse")
        )

        config_content = """
companies:
  - name: "Existing Company"
    priority: 3
    ats_type: "lever"
    careers_url: "https://existing.com/careers"
    locations:
      - "Remote"
    notes: "Updated config"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_content)
            temp_path = f.name

        try:
            service = CompanyConfigService(temp_path)
            stats = service.sync_with_database(db_session, overwrite=True)

            assert stats["created"] == 0
            assert stats["updated"] == 1
            assert stats["skipped"] == 0
            assert len(stats["errors"]) == 0

            # Verify existing company was updated
            db_session.refresh(company)
            assert company.priority.value == 3  # Updated value
            assert company.ats_type.value == "lever"  # Updated value
        finally:
            os.unlink(temp_path)

    def test_sync_with_database_invalid_company_data(self, db_session):
        """Test syncing config with invalid company data."""
        config_content = """
companies:
  - name: "Valid Company"
    priority: 5
    ats_type: "greenhouse"

  - name: ""
    priority: 3
    ats_type: "lever"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_content)
            temp_path = f.name

        try:
            service = CompanyConfigService(temp_path)
            stats = service.sync_with_database(db_session, overwrite=False)

            assert stats["created"] == 1
            assert stats["updated"] == 0
            assert stats["skipped"] == 0
            assert len(stats["errors"]) == 1
            assert stats["errors"][0]["company"] == ""
        finally:
            os.unlink(temp_path)

    def test_sync_with_database_mixed_results(self, db_session):
        """Test syncing config with mixed results."""
        from app.services.companies import CompanyService
        from app.schemas.company import CompanyCreate

        # Create existing company
        company_service = CompanyService(db_session)
        company_service.create_company(CompanyCreate(name="Existing Company", priority=5, ats_type="greenhouse"))

        config_content = """
companies:
  - name: "Existing Company"
    priority: 4
    ats_type: "ashby"

  - name: "New Company A"
    priority: 5
    ats_type: "greenhouse"

  - name: "New Company B"
    priority: 3
    ats_type: "lever"

  - name: ""
    priority: 2
    ats_type: "manual"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_content)
            temp_path = f.name

        try:
            service = CompanyConfigService(temp_path)
            stats = service.sync_with_database(db_session, overwrite=False)

            assert stats["created"] == 2
            assert stats["updated"] == 0
            assert stats["skipped"] == 1
            assert len(stats["errors"]) == 1
        finally:
            os.unlink(temp_path)

    def test_config_service_default_path(self):
        """Test config service with default path."""
        service = CompanyConfigService()

        assert service.config_path == "config/companies.yaml"

    def test_config_service_custom_path(self):
        """Test config service with custom path."""
        custom_path = "config/custom_companies.yaml"
        service = CompanyConfigService(custom_path)

        assert service.config_path == custom_path
