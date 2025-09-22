from setuptools import setup, find_packages

setup(
    name="sculblog",
    version="0.1.27",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4",
        "pypandoc",
    ],
    entry_points={
        "console_scripts": [
            "sculblog=sculblog.main:main",
        ],
    },
    author="Diego Cabello",
    description="Super Cool Utility Lightweight Blog - A minimalist blogging framework",
    python_requires=">=3.6",
)

