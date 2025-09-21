from setuptools import setup, find_packages
from pathlib import Path

README = Path(__file__).with_name("README.md").read_text(encoding="utf-8")

setup(
    name="pratyush",
    version="0.1.4",                # bump since 0.1.3 is already published
    py_modules=["pratyush"],       # you have pratyush.py in project root
    install_requires=[
        "rich>=14.0.0",
        "typer>=0.9.0",
        "pyperclip>=1.8.2",
        "InquirerPy>=0.3.4",       # <- fixed to an existing PyPI version
        # remove the InquirerPy line if not actually used
    ],
    entry_points={
        "console_scripts": [
            "pratyush=pratyush:main",  # ensure pratyush.py defines `def main():`
        ],
    },
    author="Pratyush Ranjan",
    description="A CLI to showcase Pratyush's portfolio and projects 🚀",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://its-pratyush.web.app/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.10",
)
