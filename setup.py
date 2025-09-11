"""
Setup script for net.krak WiFi Penetration Testing Suite
"""
from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="netkrak",
    version="2.0.0",
    author="NetKrak Team",
    author_email="team@netkrak.dev",
    description="A comprehensive WiFi penetration testing suite with enhanced attack vectors and modern web dashboard",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/netkrak/netkrak",
    project_urls={
        "Bug Reports": "https://github.com/netkrak/netkrak/issues",
        "Source": "https://github.com/netkrak/netkrak",
        "Documentation": "https://github.com/netkrak/netkrak/wiki",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "netkrak=orchestrator:main",
            "netkrak-diagnostics=utils.runtime_diagnostics:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.html", "*.css", "*.js", "*.json", "*.md"],
    },
    keywords="wifi, penetration-testing, security, aircrack-ng, wireless, pentest, cybersecurity",
    zip_safe=False,
)