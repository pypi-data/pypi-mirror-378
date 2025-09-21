from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="TikTor",
    version="0.9.9",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pycountry"
    ],
    entry_points={
        "console_scripts": [
            "tiktor = tiktor.main:main",
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
)