from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="awscostexport",
    version="1.0.0",
    author="David Schwartz",
    author_email="david.schwartz@devfactory.com",
    description="Export comprehensive AWS cost data for analysis and optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trilogy-group/aws-cost-extractor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Office/Business :: Financial",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "boto3>=1.26.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "awscostexport=awscostexport.cli:cli",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/trilogy-group/aws-cost-extractor/issues",
        "Source": "https://github.com/trilogy-group/aws-cost-extractor",
    },
)
