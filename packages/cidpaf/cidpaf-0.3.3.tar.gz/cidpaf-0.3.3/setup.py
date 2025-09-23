from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cidpaf",
    version="0.2.0",
    author="CIDP Team",
    author_email="kijung.park@sk.com",
    description="CIDP Airflow utilities for Kubernetes and Spark integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.cidp.io/common/pypi/cidpaf",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    keywords="airflow kubernetes spark cidp cidpaf",
    project_urls={
        "Bug Reports": "https://gitlab.cidp.io/common/pypi/cidpaf/-/issues",
        "Source": "https://gitlab.cidp.io/common/pypi/cidpaf",
    },
)


