from setuptools import setup, find_packages

setup(
    name="ml_libs1234",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas"
    ],
    description="A small ML library with CE, Find-S, FOIL Gain, and dataset stats",
    author="Your Name",
    author_email="your_email@example.com",
    url="https://github.com/yourusername/ml_lib",  # optional
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
