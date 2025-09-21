from setuptools import setup, find_packages

setup(
    name="streamlit-ollama",
    version="0.1.1",
    author="Your Name",
    author_email="your.email@example.com",
    description="Streamlit utilities for Ollama LLM integration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/streamlit-ollama",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.0",
        "requests>=2.25"
    ],

    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],


    python_requires=">=3.7",
)
