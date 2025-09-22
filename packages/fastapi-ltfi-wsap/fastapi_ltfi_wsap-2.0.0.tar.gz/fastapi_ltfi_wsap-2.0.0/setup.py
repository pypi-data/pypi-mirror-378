"""
Setup configuration for fastapi-ltfi-wsap package.
"""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# PyPI-friendly description without external images
pypi_description = """
# FastAPI LTFI-WSAP Integration

**Version:** 2.0.0  
**License:** MIT with Additional Terms

## Overview

FastAPI application and middleware for integrating LTFI-WSAP (Layered Transformer Framework Intelligence - Web System Alignment Protocol). This package provides a complete FastAPI integration with models, routers, middleware, and dependencies for implementing WSAP in your FastAPI projects.

## What is LTFI-WSAP?

LTFI-WSAP is a revolutionary protocol that enables organizations to provide structured, verified information about their business to AI systems through standardized JSON files. It supports progressive disclosure levels and cryptographic verification, ensuring that AI assistants can access accurate, real-time business information while respecting privacy preferences.

## Key Features

- **FastAPI Application**: Pre-configured FastAPI app with `WSAPApp` class
- **Middleware**: WSAP middleware for automatic endpoint handling and header injection
- **Router**: Ready-to-use router with dashboard and API endpoints
- **Dependencies**: Reusable dependencies for authentication and client access
- **Domain Verification**: DNS TXT record verification for domain ownership
- **Progressive Disclosure**: Control information visibility with multiple disclosure levels
- **Entity Management**: Support for companies, non-profits, government agencies, and more
- **Pydantic Models**: Complete type-safe models for all WSAP data structures
- **Async Support**: Full async/await support throughout the package
- **Rate Limiting**: Built-in rate limiting middleware and dependencies
- **Security**: API key validation, CORS configuration, and field encryption

## Installation

```bash
pip install fastapi-ltfi-wsap
```

## Quick Start

### Basic Setup

```python
from fastapi_ltfi_wsap import WSAPApp

# Create WSAP-enabled FastAPI app
app = WSAPApp(
    api_key="your-api-key",
    entity_id="your-entity-id",
    title="My API"
)

# Access the FastAPI instance
fastapi_app = app.app
```

### With Existing FastAPI App

```python
from fastapi import FastAPI
from fastapi_ltfi_wsap import WSAPMiddleware, wsap_router

app = FastAPI()

# Add middleware
app.add_middleware(WSAPMiddleware, api_key="your-api-key")

# Include router
app.include_router(wsap_router, prefix="/wsap")
```

## Requirements

- Python 3.8+
- FastAPI 0.68+
- Pydantic 1.8+
- dnspython
- cryptography
- ltfi-wsap-sdk (optional, for API integration)

## Support

For support, documentation, and updates:

- **Documentation**: https://docs.ltfi.ai/fastapi
- **GitHub**: https://github.com/Kief-Studio/fastapi-ltfi-wsap
- **Support Email**: support@ltfi.ai
- **Website**: https://ltfi.ai

## License

This package is distributed under the MIT License with additional terms for certain use cases. For commercial use by organizations with annual revenue exceeding $1 million USD or requiring support for more than 100 domains, a commercial license is required. Contact sales@ltfi.ai for pricing.

---

**Made with ❤️ by Kief Studio** | Cambridge, MA
"""

setup(
    name="fastapi-ltfi-wsap",
    version="2.0.0",
    author="Kief Studio",
    author_email="hello@ltfi.ai",
    description="FastAPI integration for LTFI-WSAP (Web System Alignment Protocol)",
    long_description=pypi_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Kief-Studio/fastapi-ltfi-wsap",
    project_urls={
        "Bug Tracker": "https://github.com/Kief-Studio/fastapi-ltfi-wsap/issues",
        "Documentation": "https://docs.ltfi.ai/fastapi",
        "Source Code": "https://github.com/Kief-Studio/fastapi-ltfi-wsap",
        "Homepage": "https://ltfi.ai",
        "Company": "https://kief.studio",
        "LTFI Ecosystem": "https://ltfi.ai",
        "WSAP Protocol": "https://wsap.ltfi.ai",
    },
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.68.0",
        "pydantic>=1.8.0",
        "uvicorn>=0.15.0",
        "dnspython>=2.0.0",
        "cryptography>=3.4.0",
        "python-multipart>=0.0.5",
    ],
    extras_require={
        "api": ["ltfi-wsap-sdk>=2.0.0"],
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.24.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
    },
    keywords="fastapi wsap ltfi api protocol verification ai integration async",
    license="MIT",
    include_package_data=True,
    zip_safe=False,
)