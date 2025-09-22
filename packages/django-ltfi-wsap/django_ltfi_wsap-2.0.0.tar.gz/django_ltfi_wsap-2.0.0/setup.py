"""
Django Integration for LTFI-WSAP
Setup configuration for PyPI distribution
"""

from setuptools import setup, find_packages

# PyPI-friendly description without external images
pypi_description = """# Django LTFI-WSAP Integration

[![PyPI version](https://badge.fury.io/py/django-ltfi-wsap.svg)](https://pypi.org/project/django-ltfi-wsap/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/KiefStudioMA/ltfi-wsap-django/blob/main/LICENSE)
[![LTFI-WSAP](https://img.shields.io/badge/LTFI--WSAP-v2.0.0-blue.svg)](https://wsap.ltfi.ai)
[![Kief Studio](https://img.shields.io/badge/By-Kief%20Studio-green.svg)](https://kief.studio)

Official Django Integration for **LTFI-WSAP** (Layered Transformer Framework Intelligence - Web System Alignment Protocol) by **Kief Studio**.

Part of the [LTFI Ecosystem](https://ltfi.ai) • [WSAP Protocol](https://wsap.ltfi.ai)

## 📦 Installation

```bash
pip install django-ltfi-wsap
```

## 🚀 Quick Start

### 1. Add to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    # ... your other apps
    'django_ltfi_wsap',
]
```

### 2. Add Middleware

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    'django_ltfi_wsap.middleware.WSAPMiddleware',
]
```

### 3. Configure Settings

```python
# settings.py

# Required: Your LTFI-WSAP API key
LTFI_WSAP_API_KEY = 'your-api-key-here'

# Optional: Custom API endpoint (defaults to https://api.ltfi.ai)
LTFI_WSAP_BASE_URL = 'https://api.ltfi.ai'

# Optional: Add WSAP headers to responses
LTFI_WSAP_ADD_HEADERS = True
```

### 4. Include URLs

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    # ... your other URLs
    path('wsap/', include('django_ltfi_wsap.urls')),
]
```

### 5. Run Migrations

```bash
python manage.py migrate django_ltfi_wsap
```

## 🎯 Features

- **Models**: WSAPEntity and DomainVerification models
- **Admin Interface**: Full Django admin integration
- **Management Commands**: Verify domains via CLI
- **Middleware**: Automatic WSAP endpoint handling
- **Views**: Entity dashboard and verification workflow
- **Domain Verification**: DNS TXT, file upload, and meta tag methods
- **Progressive Disclosure**: Support for BASIC, STANDARD, DETAILED, and COMPLETE levels
- **Field Encryption**: Built-in support for sensitive data encryption

## 📚 Documentation

- **Main Documentation**: [docs.ltfi.ai](https://docs.ltfi.ai)
- **API Reference**: [api.ltfi.ai/docs](https://api.ltfi.ai/docs)
- **Django Guide**: [docs.ltfi.ai/django](https://docs.ltfi.ai/django)
- **Examples**: [github.com/KiefStudioMA/LTFI-WSAP-Examples](https://github.com/KiefStudioMA/LTFI-WSAP-Examples)

## 📄 License

**MIT License** - This SDK is open source and free to use.

### LTFI-WSAP Service Usage

While this SDK is open source, the LTFI-WSAP service has the following usage terms:

- ✅ **FREE** for personal use, open source projects, and small businesses
- ✅ **FREE** for most users and use cases
- 💳 **Paid plans** required for:
  - Enterprises with annual revenue exceeding $1M USD
  - Organizations managing more than 100 domains
  - High-volume API usage

For pricing details: [wsap.ltfi.ai/pricing](https://wsap.ltfi.ai/pricing)

## 🆘 Support

- **Technical Support**: developers@kief.studio
- **Business Inquiries**: business@kief.studio
- **Discord**: [discord.gg/JfjyUdjJgP](https://discord.gg/JfjyUdjJgP)

---

**Built with ❤️ by [Kief Studio](https://kief.studio)**

Part of the [LTFI Ecosystem](https://ltfi.ai) • [WSAP Protocol](https://wsap.ltfi.ai)

© 2025 Kief Studio, MA. All rights reserved.
"""

setup(
    name="django-ltfi-wsap",
    version="2.0.0",
    author="Kief Studio",
    author_email="developers@kief.studio",
    description="Django integration for LTFI-WSAP (Layered Transformer Framework Intelligence - Web System Alignment Protocol) by Kief Studio",
    long_description=pypi_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KiefStudioMA/ltfi-wsap-django",
    packages=find_packages(exclude=["tests", "example_project"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2",
        "ltfi-wsap-sdk>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-django>=4.5.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "django-stubs>=4.2.0",
        ],
    },
    project_urls={
        "Documentation": "https://wsap-django.readthedocs.io",
        "Bug Reports": "https://github.com/KiefStudioMA/wsap-django/issues",
        "Source": "https://github.com/KiefStudioMA/wsap-django",
        "Company": "https://kief.studio",
        "LTFI Ecosystem": "https://ltfi.ai",
        "WSAP Protocol": "https://wsap.ltfi.ai",
    },
    keywords="django wsap ltfi verification domain security api integration kief-studio",
    license="MIT",
    include_package_data=True,
    zip_safe=False,
)