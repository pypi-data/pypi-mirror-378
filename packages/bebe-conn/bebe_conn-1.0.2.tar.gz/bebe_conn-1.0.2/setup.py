"""
Setup pentru BebeConn - Monitorizare Laptop de la Distanță
"""

from setuptools import setup, find_packages
import os

# Citește README-ul
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Citește requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="bebe-conn",
    version="1.0.2",
    author="Ioan Fantanaru",
    author_email="ioan.fantanaru@gmail.com",
    description="Monitorizare laptop de la distanță cu interfață web și actualizări în timp real",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/me-suzy/bebe-conn",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "bebe-conn=bebe_conn.cli:main",
        ],
    },
    keywords="monitoring, remote, laptop, web, dashboard, screenshots, system",
    project_urls={
        "Bug Reports": "https://github.com/me-suzy/bebe-conn/issues",
        "Source": "https://github.com/me-suzy/bebe-conn",
        "Documentation": "https://github.com/me-suzy/bebe-conn#readme",
    },
)
