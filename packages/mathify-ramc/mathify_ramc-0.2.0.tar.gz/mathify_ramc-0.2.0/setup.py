from setuptools import setup,find_packages

setup(
    name="mathify_ramc",
    version="0.2.0",
    author="ram",
    author_email="ramachandark436@gmail.com",
    description="A simple Arithmetic and algebric package",
    long_description=open("README.md","r",encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
    license="MIT",
    entry_points={
        "console_scripts": [
            "mathify-algebra=mathify.algebra:main",
            "mathify-arithmetic=mathify.arithmetic:main"
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)