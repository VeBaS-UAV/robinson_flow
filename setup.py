import setuptools
from distutils.extension import Extension

setuptools.setup(
    name="robinson-ryven",
    version="0.0.1",
    author="matthias fueller",
    author_email="matthias.fueller@fhdw.de",
    description="robinson task planner",
    long_description="TBD",
    long_description_content_type="text/markdown",
    url="https://github.com/TBD",
    project_urls={
        "Bug Tracker": "https://github.com/TBD",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.9"
)
