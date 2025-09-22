from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="adel_majli_calculator",
    version="0.1.0",
    author="عادل مجلي",
    author_email="contact@adelmajli.com", # Placeholder email
    description="آلة حاسبة بسيطة لإجراء العمليات الحسابية الأساسية.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adelmajli/simple-calculator", # Placeholder URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

