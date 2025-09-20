from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

__version__ = "0.1.1" 

setup(
    name="actora",
    version=__version__,
    author="Amr Tweg",
    author_email="amrtweg@rdivxe.com", 
    description="Transformers model for Arabic social media post interaction prediction.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RdivxeAI/Actora",
    packages=find_packages(), 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License", 
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.10.0",
        "transformers>=4.20.0",
    ],
    extras_require={
        "dev": [
            "pytest",
            "twine",
            "wheel",
        ],
    },
)