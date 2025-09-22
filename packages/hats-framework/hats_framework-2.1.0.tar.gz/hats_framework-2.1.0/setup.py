#!/usr/bin/env python3
"""
Setup script for HATS - Hacking Automation Tool Suite
Enhanced version with security features and dynamic interface
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def read_requirements():
    requirements = []
    with open("requirements.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                requirements.append(line)
    return requirements

setup(
    name="hats-framework",
    version="2.1.0",
    author="HATS Security Team",
    author_email="security@hats-framework.org",
    description="Professional cybersecurity automation framework with 36 CLI tools and enterprise security",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/hats-security/hats-framework",
    project_urls={
        "Bug Tracker": "https://github.com/hats-security/hats-framework/issues",
        "Documentation": "https://hats-framework.readthedocs.io/",
        "Source": "https://github.com/hats-security/hats-framework",
        "Security": "https://github.com/hats-security/hats-framework/security",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators", 
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: System :: Penetration Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "hats=hats.cli:main",
            "hats-config=hats.config_cli:main",
            "hats-report=hats.report_cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "hats": [
            "configs/*.yaml",
            "templates/*.html", 
            "templates/*.xml",
            "data/*.json",
        ],
    },
    keywords=[
        "cybersecurity",
        "penetration-testing", 
        "security-tools",
        "automation",
        "hacking-tools",
        "vulnerability-scanner",
        "network-security",
        "web-security", 
        "security-framework",
        "nmap",
        "gobuster",
        "sqlmap",
        "nikto",
        "john-the-ripper",
        "hydra",
        "metasploit",
        "kali-linux",
        "security-audit",
        "opsec",
        "red-team",
        "blue-team",
        "cli-tools"
    ],
    zip_safe=False,
)
