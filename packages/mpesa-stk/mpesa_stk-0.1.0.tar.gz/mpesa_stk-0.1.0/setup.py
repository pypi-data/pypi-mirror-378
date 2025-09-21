from setuptools import setup, find_packages

setup(
    name="mpesa-stk",  
    version="0.1.0",   
    description="A simple Python library for Safaricom M-Pesa STK Push integration",
    author="Brian Ziro",
    author_email="brianziro44@gmail.com",
    url="https://github.com/BrianZiro/mpesa_stk_library.git",  
    packages=find_packages(),
    install_requires=[
        "requests>=2.20.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
