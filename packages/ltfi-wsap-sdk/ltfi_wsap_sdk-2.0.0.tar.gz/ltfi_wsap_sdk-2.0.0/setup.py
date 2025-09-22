"""
WSAP Python SDK
Setup configuration for PyPI distribution
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ltfi-wsap-sdk",
    version="2.0.0",
    author="Kief Studio",
    author_email="developers@kief.studio",
    maintainer="LTFI Team",
    maintainer_email="support@wsap.ltfi.ai",
    description="Official Python SDK for LTFI-WSAP (Web System Alignment Protocol) by Kief Studio - Part of the LTFI ecosystem",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KiefStudioMA/LTFI-WSAP-Python",
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0",
        "pydantic>=2.0.0",
        "cryptography>=41.0.0",
        "dnspython>=2.3.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "async": ["aiohttp>=3.8.0", "asyncio>=3.4.3"],
        "cli": ["click>=8.0.0", "rich>=13.0.0", "tabulate>=0.9.0"],
        "django": ["django>=3.2"],
        "flask": ["flask>=2.0.0"],
        "cache": ["redis>=4.5.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ltfi-wsap=ltfi_wsap.cli:main",
        ],
    },
    project_urls={
        "Documentation": "https://wsap-python.readthedocs.io",
        "Bug Reports": "https://github.com/KiefStudioMA/LTFI-WSAP/wsap-python/issues",
        "Source": "https://github.com/KiefStudioMA/LTFI-WSAP/wsap-python",
        "Discord": "https://discord.gg/wsap",
        "Company": "https://kief.studio",
        "LTFI Ecosystem": "https://ltfi.ai",
        "WSAP Protocol": "https://wsap.ltfi.ai",
    },
    keywords="wsap verification domain security api sdk kief-studio ltfi ai-verification organizational-data",
    license="MIT",
    include_package_data=True,
    zip_safe=False,
)