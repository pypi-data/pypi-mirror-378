from setuptools import setup, find_packages
import os

# Read README file
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Official RoQuick API wrapper for Roblox group management with advanced features"

# Read requirements
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    # Fallback to hardcoded requirements if file doesn't exist
    requirements = [
        "requests>=2.25.0",
        "colorama>=0.4.4"
    ]

setup(
    name="roquick-api",
    version="0.0.3b0",
    author="bluezly",
    author_email="hotelc229@gmail.com",
    description="Official RoQuick API wrapper for Roblox group management with advanced features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Discord": "https://discord.gg/GwxzWg9Cbh",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Games/Entertainment",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=requirements,
    keywords=["roblox", "api", "group", "management", "roquick", "discord", "bot"],
    license="MIT",
)