from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vior-cli",
    version="1.0.2",
    author="Viorcloud Team",
    author_email="support@viorcloud.com",
    description="Vior Secrets CLI - Secure command-line interface for Vior Secrets management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/viorcloud/vior-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.25.0",
        "cryptography>=3.4.0",
    ],
    extras_require={
        "dev": ["pytest>=6.0", "black>=21.0", "flake8>=3.8", "mypy>=0.812"],
    },
    entry_points={
        "console_scripts": [
            "vior=vior_cli.cli:cli",
        ],
    },
)