"""
Setup configuration for the ragger.ai Python SDK package.
"""

from setuptools import setup, find_packages

# Read the README file for the long description
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Python SDK for ragger.ai RAG (Retrieval Augmented Generation) API"

# Read requirements from requirements.txt
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = ["requests>=2.25.0"]

setup(
    name="ragger-python-sdk",
    version="0.1.0",
    author="Ragger Team",
    author_email="support@ragger.ai",
    description="Python SDK for ragger.ai RAG API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RaggerAI/python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Indexing",
    ],
    license="MIT",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
        ],
    },
    keywords="rag retrieval augmented generation ai llm nlp vector search",
    project_urls={
        "Bug Reports": "https://github.com/RaggerAI/python-sdk/issues",
        "Source": "https://github.com/RaggerAI/python-sdk",
        "Documentation": "https://github.com/RaggerAI/python-sdk#readme",
    },
)
