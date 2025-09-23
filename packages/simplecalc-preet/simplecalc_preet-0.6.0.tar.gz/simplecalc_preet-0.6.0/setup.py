from setuptools import setup, find_packages

setup(
    name="simplecalc-preet",
    version="0.6.0",
    packages=find_packages(),
    description="A simple calculator package",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "mycalculator=mycalculator.cli:main",
        ],
    },
         
)