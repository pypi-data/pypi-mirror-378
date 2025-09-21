from setuptools import setup, find_packages

setup(
    name="pyfunclink",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["PyQt5", "wxPython"],  # adjust if using PyQt6 or PySide6
    author="Your Name",
    description="Automatically detect and link URLs in GUI widgets",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
