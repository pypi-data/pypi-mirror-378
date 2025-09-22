from setuptools import setup, find_packages

setup(
    name="fastapi-testrunner",
    version="0.1.1",
    description="Automated testing utility for FastAPI applications",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Siva Rajan R",
    author_email="debuggers437@gmail.com",
    url="https://github.com/Siva-Rajan-R/fastapi_testrunner.git",
    packages=find_packages(),
    install_requires=[
        "requests>=2.32.5",
        "rich>=14.1.0"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: FastAPI",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="fastapi testing automation openapi starlette test testrunner quciktest fastapi-testrunner test-paths",
    license='MIT',
    include_package_data=True
)
