from setuptools import setup, find_packages

setup(
    name="financial-data-parser",
    version="1.0.0",
    description="A robust financial data parsing system for Excel files",
    author="Financial Data Parser Team",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.0",
        "openpyxl>=3.0.0",
        "numpy>=1.21.0",
        "python-dateutil>=2.8.0",
        "pytz>=2022.1",
    ],
    python_requires=">=3.8",
) 