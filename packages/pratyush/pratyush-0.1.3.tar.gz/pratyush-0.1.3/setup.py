from setuptools import setup

setup(
    name="pratyush",  
    version="0.1.3",
    py_modules=["pratyush"],
    install_requires=[
        "rich>=14.0.0",
        "typer>=0.9.0",
        "pyperclip>=1.8.2",
        "InquirerPy>=1.6.3"
    ],
    entry_points={
        "console_scripts": [
            "pratyush = pratyush:main",
        ],
    },
    author="Pratyush Ranjan",
    description="A CLI to showcase Pratyush's portfolio and projects 🚀",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://its-pratyush.web.app/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.10",
)
