from setuptools import setup, find_packages


def read_readme() -> str:
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()


setup(
    name="MaMAI",
    version="3.5.0",
    packages=find_packages(exclude=("tests", "tests.*", "test", "test.*")),
    python_requires=">=3.10",
    install_requires=[
        "langchain>=0.3.27",
        "langchain-core>=0.3.76",
        "langchain-community>=0.3.29",
        "langchain-openai>=0.3.33",
        "langchain-text-splitters>=0.3.11",
        "faiss-cpu>=1.12.0",
        "pypdf>=6.0.0",
        "flask>=3.0.0",
        "beautifulsoup4>=4.13.0",
        "urllib3>=2.0.0",
        "requests>=2.31.0",
    ],
    author="Francesco Bellifemine",
    author_email="effebi.co@gmail.com",
    description="MaMa è un toolkit RAG modulare basato su LangChain per knowledge base locali e interfacce conversazionali.",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/cyberbionik/MaMa",
    project_urls={
        "Source": "https://github.com/cyberbionik/MaMa",
        "Tracker": "https://github.com/cyberbionik/MaMa/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
