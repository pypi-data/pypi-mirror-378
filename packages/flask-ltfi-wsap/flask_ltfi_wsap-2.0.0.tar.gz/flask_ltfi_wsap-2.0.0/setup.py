"""
Flask Integration for LTFI-WSAP
Setup configuration for PyPI distribution
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# PyPI-friendly description without external images
pypi_description = """
# Flask LTFI-WSAP Integration

**Version:** 2.0.0  
**License:** MIT with Additional Terms

## Overview

Flask extension for integrating LTFI-WSAP (Layered Transformer Framework Intelligence - Web System Alignment Protocol) into Flask applications. This package provides a complete Flask integration with models, views, middleware, and utilities for implementing WSAP in your Flask projects.

## What is LTFI-WSAP?

LTFI-WSAP is a revolutionary protocol that enables organizations to provide structured, verified information about their business to AI systems through standardized JSON files. It supports progressive disclosure levels and cryptographic verification, ensuring that AI assistants can access accurate, real-time business information while respecting privacy preferences.

## Key Features

- **Flask Extension**: Easy integration with Flask applications via `WSAP()` extension
- **Blueprint Support**: Pre-configured Blueprint with WSAP endpoints and dashboard
- **Domain Verification**: DNS TXT record verification for proving domain ownership  
- **Progressive Disclosure**: Control information visibility with multiple disclosure levels
- **Entity Management**: Support for companies, non-profits, government agencies, personal brands, and more
- **Data Models**: Complete data models and schemas for WSAP entities
- **Middleware**: Automatic WSAP endpoint serving at `/.well-known/wsap.json`
- **Security**: Built-in rate limiting, API key validation, and field encryption
- **Caching**: Response caching for improved performance
- **API Integration**: Full integration with LTFI-WSAP API service

## Installation

```bash
pip install flask-ltfi-wsap
```

## Quick Start

```python
from flask import Flask
from flask_ltfi_wsap import WSAP, wsap_blueprint

app = Flask(__name__)

# Configure WSAP
app.config['WSAP_API_KEY'] = 'your-api-key'
app.config['WSAP_ENTITY_ID'] = 'your-entity-id'

# Initialize extension
wsap = WSAP(app)

# Register blueprint (optional)
app.register_blueprint(wsap_blueprint)

if __name__ == '__main__':
    app.run()
```

## Requirements

- Python 3.8+
- Flask 2.0+
- dnspython
- cryptography
- ltfi-wsap-sdk (optional, for API integration)

## Support

For support, documentation, and updates:

- **Documentation**: https://docs.ltfi.ai/flask
- **GitHub**: https://github.com/Kief-Studio/flask-ltfi-wsap
- **Support Email**: support@ltfi.ai
- **Website**: https://ltfi.ai

## License

This package is distributed under the MIT License with additional terms for certain use cases. For commercial use by organizations with annual revenue exceeding $1 million USD or requiring support for more than 100 domains, a commercial license is required. Contact sales@ltfi.ai for pricing.

---

**Made with ❤️ by Kief Studio** | Cambridge, MA
"""

setup(
    name="flask-ltfi-wsap",
    version="2.0.0",
    author="Kief Studio",
    author_email="hello@ltfi.ai",
    description="Flask extension for LTFI-WSAP (Web System Alignment Protocol) integration",
    long_description=pypi_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KiefStudioMA/LTFI-WSAP-Flask",
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Framework :: Flask",
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
        "Flask>=2.0.0",
        "Werkzeug>=2.0.0",
        "dnspython>=2.0.0",
        "cryptography>=3.4.0",
    ],
    extras_require={
        "api": ["ltfi-wsap-sdk>=2.0.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-flask>=1.2.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    project_urls={
        "Documentation": "https://flask-ltfi-wsap.readthedocs.io",
        "Bug Reports": "https://github.com/KiefStudioMA/LTFI-WSAP-Flask/issues",
        "Source": "https://github.com/KiefStudioMA/LTFI-WSAP-Flask",
        "Company": "https://kief.studio",
        "LTFI Ecosystem": "https://ltfi.ai",
        "WSAP Protocol": "https://wsap.ltfi.ai",
    },
    keywords="flask wsap ltfi verification domain security api integration kief-studio",
    license="MIT",
    include_package_data=True,
    zip_safe=False,
)