# pyass🍑/setup.py

from setuptools import setup, find_packages

try:
    # Read README
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "The definitive Gen-Z & internet slang library for Python. Vibes > verbs."

setup(
    name="pyass-genz",
    version="2025.1.0",
    author="Zer0C0d3r",
    author_email="odin.coder77@proton.me",
    description="The definitive Gen-Z & internet slang library for Python. Vibes > verbs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zer0C0d3r/pyass-genz",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={
        "pyass": ["data/*.json", "data/packs/*.json", "assets/*.json", "assets/*.csv"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Sociology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "aiohttp>=3.8.0",
        "fuzzywuzzy>=0.18.0",
        "python-levenshtein>=0.21.0; platform_system != 'Windows'",
    ],
    extras_require={
        "ml": ["sentence-transformers>=2.2.0", "scikit-learn>=1.2.0"],
        "dev": ["pytest>=7.0", "pytest-asyncio>=0.21.0", "black>=23.0", "mypy>=1.4", "httpx>=0.24.0"],
    },
    entry_points={
        "console_scripts": [
            "pyass=pyass.cli.commands:app",
        ],
    },
)
