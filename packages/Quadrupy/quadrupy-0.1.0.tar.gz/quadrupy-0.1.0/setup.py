from setuptools import setup, find_packages
import pathlib

# Read the README for long description
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="Quadrupy",                     # pip install Quadrupy
    version="0.1.0",                     
    description="Simple library to control the STQ V1 via Bluetooth",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jaden Stout-Reason",
    author_email="jadenstoutreason@gmail.com",  
    url="https://github.com/jadenstoutreason/Quadrupy",
    packages=find_packages(),
    install_requires=[
        "bleak"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    license="Proprietary",   # tells PyPI it’s not open source
    include_package_data=True,
    package_data={
        "": ["LICENSE"],  # bundle license file in the package
    },
    project_urls={
        "Source": "https://github.com/jadenstoutreason/Quadrupy",
    },
)