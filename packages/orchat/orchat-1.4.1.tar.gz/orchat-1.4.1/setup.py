from setuptools import setup
from pathlib import Path

# Read README.md for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="orchat",
    version="1.4.1",
    author="oop7",
    author_email="oop7_support@proton.me",
    description="A powerful CLI for chatting with AI models through OpenRouter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oop7/OrChat",
    py_modules=['main'],  # Single file instead of packages
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests",
        "tiktoken",
        "rich",
        "python-dotenv", 
        "colorama",
        "packaging",
        "pyfzf",
        "cryptography",
        "prompt_toolkit",
    ],
    entry_points={
        "console_scripts": [
            "orchat=main:main",  # Points to main() function in main.py
        ],
    },
    project_urls={
        'Homepage': 'https://github.com/oop7/OrChat',
        'Bug Tracker': 'https://github.com/oop7/OrChat/issues',
        'Reddit': 'https://www.reddit.com/r/NO-N_A_M_E/',
    },
)