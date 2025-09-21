from setuptools import setup, find_packages

setup(
    name="TikTor",
    version="0.1.0",
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
)