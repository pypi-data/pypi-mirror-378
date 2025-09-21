"""
Setup script for iplocator library
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="myserverip",
    version="1.0.0",
    author="younes daoudi",
    author_email="your.email@example.com",
    description="A Python library to get server's public IP address from system interfaces",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daoudiyounes/serverip",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3",
    install_requires=[
        "netifaces>=0.11.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "myserverip=serverip.myserverip:main",
        ],
    },
    keywords="server ip address network interface system local",
    project_urls={
        "Bug Reports": "https://github.com/daoudiyounes/serverip/issues",
        "Source": "https://github.com/daoudiyounes/serverip",
    },
)