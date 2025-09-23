from setuptools import setup, find_packages

setup(
    name="keyauth-renee",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests"],
    author="Renee",
    description="Remote API key validator for FastAPI systems",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/keyauth",  # optional
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)