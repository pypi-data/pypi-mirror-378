from setuptools import setup, find_packages

setup(
    name="PositiveNegative-Library",
    version="0.1.1",
    description="Check if a number is positive, negative, or zero",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Rahaf Salh Qadah",
    author_email="Rahafsalhqadah2@gmail.com",
    packages=find_packages(),
    python_requires=">=3.7",
    license="MIT",
    entry_points={
        "console_scripts": [
            "PositiveNegative-Library=positivenegative.__main__:main"
        ]
    }
)
