from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="PyExtender",
    version="1.0.1a1",
    description="A simple Python extension toolkit.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="cnong",
    author_email="bzjsmdl88@qq.com",
    url="https://github.com/bzjsmdl/PyExtender",
    license='MIT',
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries", 
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)