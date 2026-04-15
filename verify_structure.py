"""
Structure Verification Script

Verifies that the production-level directory structure is properly set up.
"""

import sys
from pathlib import Path


def check_directory_structure():
    """Check if all required directories exist."""
    required_dirs = [
        "app/api",
        "app/core",
        "app/db",
        "app/models",
        "app/schemas",
        "app/services/fetchers",
        "app/services/scoring",
        "app/services/applications",
        "app/services/outreach",
        "app/services/sheets",
        "app/services/llm",
        "app/ui/static",
        "app/ui/templates",
        "app/ui/components",
        "data/database",
        "data/cache",
        "data/exports",
        "data/uploads",
        "scripts",
        "tests/unit",
        "tests/integration",
        "tests/e2e",
        "docs",
        "config",
        ".github/workflows",
    ]

    print("📁 Checking directory structure...")
    all_exist = True

    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} - MISSING")
            all_exist = False

    return all_exist


def check_configuration_files():
    """Check if all required configuration files exist."""
    required_files = [
        "main.py",
        "requirements.txt",
        "requirements-dev.txt",
        "pyproject.toml",
        ".env.example",
        ".gitignore",
        "Dockerfile",
        "docker-compose.yml",
        "README.md",
        "config/settings.py",
        "config/companies.yaml",
    ]

    print("\n📋 Checking configuration files...")
    all_exist = True

    for file_path in required_files:
        path = Path(file_path)
        if path.exists() and path.is_file():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING")
            all_exist = False

    return all_exist


def check_core_modules():
    """Check if all core modules exist."""
    required_modules = [
        "app/__init__.py",
        "app/core/__init__.py",
        "app/core/config.py",
        "app/core/logging.py",
        "app/core/security.py",
        "app/core/exceptions.py",
        "app/db/__init__.py",
        "app/db/session.py",
        "app/db/base.py",
        "app/db/init_db.py",
    ]

    print("\n🔧 Checking core modules...")
    all_exist = True

    for module_path in required_modules:
        path = Path(module_path)
        if path.exists() and path.is_file():
            print(f"  ✓ {module_path}")
        else:
            print(f"  ✗ {module_path} - MISSING")
            all_exist = False

    return all_exist


def check_api_modules():
    """Check if all API modules exist."""
    required_modules = [
        "app/api/__init__.py",
        "app/api/jobs.py",
        "app/api/applications.py",
        "app/api/outreach.py",
        "app/api/tracker.py",
        "app/api/profile.py",
    ]

    print("\n🌐 Checking API modules...")
    all_exist = True

    for module_path in required_modules:
        path = Path(module_path)
        if path.exists() and path.is_file():
            print(f"  ✓ {module_path}")
        else:
            print(f"  ✗ {module_path} - MISSING")
            all_exist = False

    return all_exist


def check_models():
    """Check if all models exist."""
    required_models = [
        "app/models/__init__.py",
        "app/models/job.py",
        "app/models/application.py",
        "app/models/contact.py",
        "app/models/outreach.py",
        "app/models/profile.py",
        "app/models/tracker.py",
    ]

    print("\n🗄️  Checking data models...")
    all_exist = True

    for model_path in required_models:
        path = Path(model_path)
        if path.exists() and path.is_file():
            print(f"  ✓ {model_path}")
        else:
            print(f"  ✗ {model_path} - MISSING")
            all_exist = False

    return all_exist


def check_schemas():
    """Check if all schemas exist."""
    required_schemas = [
        "app/schemas/__init__.py",
        "app/schemas/jobs.py",
        "app/schemas/applications.py",
        "app/schemas/outreach.py",
        "app/schemas/profile.py",
    ]

    print("\n📝 Checking Pydantic schemas...")
    all_exist = True

    for schema_path in required_schemas:
        path = Path(schema_path)
        if path.exists() and path.is_file():
            print(f"  ✓ {schema_path}")
        else:
            print(f"  ✗ {schema_path} - MISSING")
            all_exist = False

    return all_exist


def check_services():
    """Check if all service modules exist."""
    required_services = [
        "app/services/__init__.py",
        "app/services/fetchers/__init__.py",
        "app/services/fetchers/base.py",
        "app/services/fetchers/greenhouse.py",
    ]

    print("\n⚙️  Checking service modules...")
    all_exist = True

    for service_path in required_services:
        path = Path(service_path)
        if path.exists() and path.is_file():
            print(f"  ✓ {service_path}")
        else:
            print(f"  ✗ {service_path} - MISSING")
            all_exist = False

    return all_exist


def check_documentation():
    """Check if all documentation files exist."""
    required_docs = [
        "docs/api.md",
        "docs/architecture.md",
        "docs/deployment.md",
        "docs/user_guide.md",
    ]

    print("\n📚 Checking documentation...")
    all_exist = True

    for doc_path in required_docs:
        path = Path(doc_path)
        if path.exists() and path.is_file():
            print(f"  ✓ {doc_path}")
        else:
            print(f"  ✗ {doc_path} - MISSING")
            all_exist = False

    return all_exist


def check_tests():
    """Check if test files exist."""
    required_tests = [
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/unit/__init__.py",
        "tests/unit/test_fetchers.py",
        "tests/unit/test_scoring.py",
        "tests/integration/__init__.py",
        "tests/integration/test_api.py",
        "tests/e2e/__init__.py",
        "tests/e2e/test_user_flows.py",
    ]

    print("\n🧪 Checking test files...")
    all_exist = True

    for test_path in required_tests:
        path = Path(test_path)
        if path.exists() and path.is_file():
            print(f"  ✓ {test_path}")
        else:
            print(f"  ✗ {test_path} - MISSING")
            all_exist = False

    return all_exist


def check_scripts():
    """Check if utility scripts exist."""
    required_scripts = [
        "scripts/__init__.py",
        "scripts/fetch_jobs.py",
        "scripts/sync_tracker.py",
        "scripts/seed_data.py",
        "scripts/cleanup.py",
    ]

    print("\n🔨 Checking utility scripts...")
    all_exist = True

    for script_path in required_scripts:
        path = Path(script_path)
        if path.exists() and path.is_file():
            print(f"  ✓ {script_path}")
        else:
            print(f"  ✗ {script_path} - MISSING")
            all_exist = False

    return all_exist


def main():
    """Run all structure checks."""
    print("🚀 Job Bot Structure Verification")
    print("=" * 50)

    results = {
        "directories": check_directory_structure(),
        "configuration": check_configuration_files(),
        "core_modules": check_core_modules(),
        "api_modules": check_api_modules(),
        "models": check_models(),
        "schemas": check_schemas(),
        "services": check_services(),
        "documentation": check_documentation(),
        "tests": check_tests(),
        "scripts": check_scripts(),
    }

    print("\n" + "=" * 50)
    print("📊 Summary:")
    print("=" * 50)

    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)

    for check_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {check_name.replace('_', ' ').title()}: {status}")

    print("=" * 50)
    print(f"Total: {passed_checks}/{total_checks} checks passed")

    if passed_checks == total_checks:
        print("\n🎉 All structure checks passed! The production-level directory structure is complete.")
        return 0
    else:
        print(f"\n⚠️  {total_checks - passed_checks} check(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())