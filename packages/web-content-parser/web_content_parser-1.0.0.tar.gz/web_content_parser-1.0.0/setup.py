from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="web-content-parser",
    version="1.0.0", 
    author="Dev Team",
    author_email="dev@example.com",
    description="A Python utility for web content processing and data extraction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devteam/web-content-parser",
    py_modules=["reddit_searcher"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
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
    keywords="web, parser, content, extraction, html",
    project_urls={
        "Bug Reports": "https://github.com/devteam/web-content-parser/issues",
        "Source": "https://github.com/devteam/web-content-parser",
    },
)