from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-model-sentinel",
    version="0.1.3",
    author="Saleh Asaad Abughabraa",
    author_email="saleh87alally@gmail.com",
    description="Comprehensive AI Model Monitoring and Drift Detection Toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SalehAsaadAbughabraa/ai-model-sentinel",
    packages=find_packages(include=['ai_model_sentinel', 'ai_model_sentinel.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ai-sentinel=ai_model_sentinel.cli:cli",
            "ai-model-sentinel=ai_model_sentinel.cli:cli",
        ]
    },
    include_package_data=True,
    package_data={
        'ai_model_sentinel': ['templates/*', 'static/*', '*.json'],
    },
)