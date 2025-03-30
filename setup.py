from setuptools import setup, find_packages

setup(
    name="flowdev-flask",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Flask==3.0.2",
        "python-dotenv==1.0.1",
        "aioflask==0.4.0",
        "openai>=1.12.0",
        "boto3==1.34.69",
        "botocore==1.34.69"
    ],
    python_requires=">=3.9",
) 