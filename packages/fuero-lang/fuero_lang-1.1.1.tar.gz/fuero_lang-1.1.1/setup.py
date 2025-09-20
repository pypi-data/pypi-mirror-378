from setuptools import setup, find_packages
import os

# read requirements
requirements = []
if os.path.exists('requirements.txt'):
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()

# read long description
long_description = ""
if os.path.exists('README.md'):
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name                          = "fuero-lang",
    version                       = "1.1.1",
    author                        = "ogcae",
    author_email                  = "ogcae@example.com",
    description                   = "Modern programming language with comprehensive utilities",
    long_description              = long_description,
    long_description_content_type = "text/markdown",
    url                           = "https://github.com/ogcae/fuero",
    project_urls                  = {
        "Bug Tracker": "https://github.com/ogcae/fuero/issues",
        "Documentation": "https://github.com/ogcae/fuero/tree/main/docs",
        "Source Code": "https://github.com/ogcae/fuero",
    },
    packages                      = find_packages(exclude=["tests*"]),
    include_package_data          = True,
    classifiers                   = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords                      = "programming-language interpreter fuero scripting",
    python_requires               = ">=3.8",
    install_requires              = requirements,
    extras_require                = {
        "dev": ["pytest>=6.0", "pytest-cov", "black", "flake8"],
        "docs": ["sphinx", "sphinx-rtd-theme"],
    },
    entry_points                  = {
        "console_scripts": [
            "fuero=fuero.cli:main",
        ],
    },
    zip_safe                      = False,
)
