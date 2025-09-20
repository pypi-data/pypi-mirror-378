from setuptools import setup, find_packages

setup(
    name="PosNegLib",
    version="0.1.0",
    description="Check if a number is positive, negative, or zero",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Ali Alsheikh",
    author_email="a77561289@gmail.com",
    packages=find_packages(),
    python_requires=">=3.13",
    license="MIT",
    entry_points={"console_scripts": ["PosNegLib=posneg.__main__:main"]}
)
