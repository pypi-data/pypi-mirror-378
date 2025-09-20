import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="agapi",
    version="2025.9.15",
    author="Kamal Choudhary",
    author_email="kchoudh2@jhu.edu",
    description="agapi",
    slakonet=[
        "numpy>=1.22.0",
        "scipy>=1.6.3",
        "jarvis-tools>=2021.07.19",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/atomgptlab/agapi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
