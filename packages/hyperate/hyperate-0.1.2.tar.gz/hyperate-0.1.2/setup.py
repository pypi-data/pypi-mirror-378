from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="hyperate",
    version="0.1.2",
    description="Python client for the HypeRate WebSocket API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Serpensin",
    author_email="serpensin@serpensin.com",
    packages=find_packages(),
    install_requires=[
        "websockets>=10.0",
    ],
    python_requires=">=3.10",
    license="AGPL-3.0",
    license_files=("LICENSE",),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        "Topic :: Communications :: Conferencing",
        "Topic :: Utilities",
    ],
    url="https://hyperate.io/",
    project_urls={
        "Documentation": "https://github.com/Serpensin/HypeRate-Python#readme",
        "Source": "https://github.com/Serpensin/HypeRate-Python",
        "Homepage": "https://serpensin.com",
    },
)
