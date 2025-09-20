from setuptools import setup, find_packages

setup(
    name="decunicoder",  
    version="1.0.0",  
    description="A Unicode encoding and decoding utility library",  
    long_description="A simple yet powerful library for Unicode code point encoding and decoding operations",
    author="SuperAssi2025",  
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License", 
        "Programming Language :: Python :: 3",
        "Topic :: Text Processing :: General", 
    ],
    keywords="unicode encoding decoding text-processing",  
)