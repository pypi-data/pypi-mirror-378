from setuptools import setup, find_packages

setup(
    name="readosso",
    version="0.1.3",
    author="M5TL",
    author_email="3asdad@gmail.com",
    description="URL",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests", "docs"]),
    install_requires=["requests"],
    python_requires=">=3.6",
)
