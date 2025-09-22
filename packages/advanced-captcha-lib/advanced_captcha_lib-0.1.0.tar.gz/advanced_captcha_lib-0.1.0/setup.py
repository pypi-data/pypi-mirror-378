from setuptools import setup, find_packages

setup(
    name="advanced_captcha_lib",
    version="0.1.0",
    description="Advanced CAPTCHA library with language detection",
    author="TuFueguito",
    packages=find_packages(),
    install_requires=[
        "PySide6",
        "customtkinter",
        "PyQt5",
        "PyQt6",
        "PySide5",
        "wxPython"
    ],
    python_requires=">=3.9",
)
