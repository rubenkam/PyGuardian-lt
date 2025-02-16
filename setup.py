from setuptools import setup, find_packages

setup(
    name="pyguardian_lite",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "pyyaml",
        "flake8",
        "pep8-naming",
        "flake8-bandit"
    ],
    entry_points={
        "console_scripts": [
            "pyguardian-lt=pyguardian_lite.cli:main",
        ],
    },
)