# =============================================================================
# setup.py
# =============================================================================
"""Setup script for secure-env package."""

from setuptools import setup, find_packages
import os

# Read long description from README
def read_long_description():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        return f.read()

setup(
    name="secure-env",
    version="1.0.1",
    author="Mohamed Ndiaye",
    author_email="mintok2000@gmail.com",
    description="A simple and secure way to manage environment variables with AES encryption",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Moesthetics-code/secure-env",
    project_urls={
        "Bug Reports": "https://github.com/Moesthetics-code/secure-env/issues",
        "Source": "https://github.com/Moesthetics-code/secure-env",
        "Documentation": "https://github.com/Moesthetics-code/secure-env#readme",
    },
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security :: Cryptography",
        "Topic :: System :: Systems Administration",
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
        "cryptography>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
            "twine>=3.0",
            "wheel>=0.36",
            "build>=0.7",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
    },
    keywords="environment variables, encryption, security, configuration, secrets",
    entry_points={
        "console_scripts": [
            "secure-env=secure_env.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
