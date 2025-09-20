from setuptools import setup, find_packages
from pathlib import Path

# مسار الملف README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="actora",             # اسم المكتبة على PyPI
    version="0.1.0",                  # نسخة المكتبة
    packages=find_packages(),          # يلتقط كل الباكيجات تلقائيًا
    install_requires=[                 # المتطلبات لو فيه
        "torch",
        "transformers"
    ],
    author="mecha",
    author_email="info@mechaml.com",
    description="A Python library for Actora model and prediction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RdivxeAI/actora",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
