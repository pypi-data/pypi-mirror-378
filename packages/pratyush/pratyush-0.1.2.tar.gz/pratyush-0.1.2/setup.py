from setuptools import setup

setup(
    name="pratyush",  
    version="0.1.1",
    py_modules=["pratyush"],
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
    python_requires=">=3.6",
)
