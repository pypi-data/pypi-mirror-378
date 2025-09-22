from setuptools import setup, find_packages

# Read README file safely
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A Simple Calculator Package."

setup(
    name="veercal",
    version="0.1.0",
    author="Veerendra Shukla",
    author_email="veshukla@gmail.com",
    description="A Simple Calculator Package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires='>=3.6',
    entry_points={
        "console-scripts": [
            "veercal=veercal.calculator:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
