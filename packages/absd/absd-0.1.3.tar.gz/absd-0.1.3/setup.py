from setuptools import setup, find_packages

setup(
    name="absd",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[],
    author="blank",
    author_email="pacyandrocash@gmail.com",
    description="testing python library",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/pacyandrocash/absd",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
    license="MIT",
    license_files=["LICENSE"],
)
