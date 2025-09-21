from setuptools import find_packages, setup

with open("app/README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pyprik",
    version="0.2.1",
    description="Intelligent data matching library with LLM-powered natural language responses",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Pruthvik",
    author_email="pruthvikmachhi7@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    install_requires=[
        "pandas >= 2.1.4",
        "fastapi >= 0.104.0",
        "uvicorn >= 0.24.0",
        "pydantic >= 2.0.0",
        "openai >= 1.0.0",
        "google-generativeai >= 0.3.0",
    ],
    extras_require={
        "dev": ["pytest>=8.2.2", "twine>=5.1.1"],
    },
    python_requires=">=3.8",
    keywords="data matching, search, llm, ai, natural language, fastapi",
    url="https://github.com/pruthvikmachhi/pyprik",
    project_urls={
        "Bug Reports": "https://github.com/pruthvikmachhi/pyprik/issues",
        "Source": "https://github.com/pruthvikmachhi/pyprik",
        "Documentation": "https://github.com/pruthvikmachhi/pyprik#readme",
    },
)