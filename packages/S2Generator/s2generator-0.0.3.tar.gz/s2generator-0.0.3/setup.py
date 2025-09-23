import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="S2Generator",
    packages=setuptools.find_packages(),
    version="0.0.3",
    description="A series-symbol (S2) dual-modality data generation mechanism, enabling the unrestricted creation of high-quality time series data paired with corresponding symbolic representations.",  # 包的简短描述
    url="https://github.com/wwhenxuan/S2Generator",
    author="whenxuan, johnfan12, changewam",
    author_email="wwhenxuan@gmail.com",
    keywords=["Time Series", "Data Generation"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.24.4",
        "scipy>=1.14.1",
        "matplotlib>=3.9.2",
        "scikit-learn>=1.2.2",
        "colorama>=0.4.6",
        "pysdkit>=0.4.21",
    ],
)
