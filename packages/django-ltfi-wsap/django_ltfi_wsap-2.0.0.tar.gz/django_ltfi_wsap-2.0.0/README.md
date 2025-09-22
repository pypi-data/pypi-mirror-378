<div align="center">
  <img src="https://github.com/KiefStudioMA/LTFI-WSAP/raw/main/assets/KS-FullLogo-DarkGrey-300dpi.png#gh-light-mode-only" alt="Kief Studio" height="80">
  <img src="https://github.com/KiefStudioMA/LTFI-WSAP/raw/main/assets/KS-FullLogo-LightSilver-300dpi.png#gh-dark-mode-only" alt="Kief Studio" height="80">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://github.com/KiefStudioMA/LTFI-WSAP/raw/main/assets/LTFI-Logo.png#gh-light-mode-only" alt="LTFI" height="80">
  <img src="https://github.com/KiefStudioMA/LTFI-WSAP/raw/main/assets/LTFI-Logo-White.png#gh-dark-mode-only" alt="LTFI" height="80">
</div>

# Django LTFI-WSAP Integration

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

## 📚 Documentation

- **Main Documentation**: [docs.ltfi.ai](https://docs.ltfi.ai)
- **API Reference**: [api.ltfi.ai/docs](https://api.ltfi.ai/docs)
- **Django Guide**: [docs.ltfi.ai/django](https://docs.ltfi.ai/django)
- **Examples**: [github.com/KiefStudioMA/LTFI-WSAP-Examples](https://github.com/KiefStudioMA/LTFI-WSAP-Examples)

## 📄 License

**MIT License** - This SDK is open source and free to use.

See [LICENSE](LICENSE) for full terms.

### LTFI-WSAP Service Usage

While this SDK is open source, the LTFI-WSAP service has the following usage terms:

- ✅ **FREE** for personal use, open source projects, and small businesses
- ✅ **FREE** for most users and use cases
- 💳 **Paid plans** required for:
  - Enterprises with annual revenue exceeding $1M USD
  - Organizations managing more than 100 domains
  - High-volume API usage

For pricing details: [wsap.ltfi.ai/pricing](https://wsap.ltfi.ai/pricing)

- **Technical Support**: developers@kief.studio
- **Business Inquiries**: business@kief.studio
- **Discord**: [discord.gg/JfjyUdjJgP](https://discord.gg/JfjyUdjJgP)
- **X (Twitter)**: [x.com/kief_ma](https://x.com/kief_ma)
- **LinkedIn**: [linkedin.com/company/kief-studio](https://www.linkedin.com/company/kief-studio/)

---

<div align="center">
  <br>
  <img src="https://raw.githubusercontent.com/KiefStudioMA/LTFI-WSAP/main/assets/KS-icon-black-1024.png#gh-light-mode-only" alt="Kief Studio" width="64">
  <img src="https://raw.githubusercontent.com/KiefStudioMA/LTFI-WSAP/main/assets/KS-icon-white-1024.png#gh-dark-mode-only" alt="Kief Studio" width="64">
  <br><br>
  
  **Built with ❤️ by [Kief Studio](https://kief.studio)**
  
  Part of the [LTFI Ecosystem](https://ltfi.ai) • [WSAP Protocol](https://wsap.ltfi.ai)
  
  © 2025 Kief Studio, MA. All rights reserved.
  
  **Open Source SDK - Service usage subject to terms**
</div>
