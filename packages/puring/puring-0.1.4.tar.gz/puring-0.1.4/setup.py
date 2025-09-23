from setuptools import setup, find_packages

setup(
    name="puring",
    version="0.1.4",
    author="rogatka",
    author_email="petfert405@gmail.com",
    description="Object-oriented Turing machine emulator",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mctood/puring",
    packages=find_packages(),
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)