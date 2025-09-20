
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simple-calculator-muharram-nizar",
    version="0.1.0",
    author="Muharram Nizar",
    author_email="muharram.nizar@example.com",
    description="A simple calculator package for basic math operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/muharram-nizar/simple-calculator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)


