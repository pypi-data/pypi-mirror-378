# setup.py
from setuptools import setup, find_packages
import os

def read_readme():
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    return "SQL/PLSQL Study Assistant for Oracle DBMS Lab"

setup(
    name="Orcasql",  # ⚠️ If taken, try "Orca-SQL" or "OrcaDBMS"
    version="1.0.0",
    author="Δrj★n",
    description="Prints Oracle SQL/PLSQL code from DBMS lab record for study & practice",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Education",
        "Topic :: Database",
        "Intended Audience :: Education",
    ],
    python_requires=">=3.7",
    keywords="oracle sql plsql study lab dbms education",
)