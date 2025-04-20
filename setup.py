# setup.py
from setuptools import setup, find_packages

# read deps from requirements.txt
with open("requirements.txt") as f:
    install_requires = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="xtend",
    version="0.1.0",
    author="Venkata Ramana",
    author_email="pvrreddy155@gmail.com",
    description="Extend monitor via local web server",
    url="https://github.com/itsmepvr/Xtend",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=install_requires,
    python_requires=">=3.11,<3.14",
    entry_points={
        "console_scripts": [
            "xtend=xtend.cli:main",
        ],
    },
)
