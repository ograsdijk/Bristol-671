import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Bristol671",
    version="0.1",
    author="o.grasdijk",
    author_email="o.grasdijk@gmail.com",
    description="Python interface for the Bristol 671 wavelength meter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=["easy_scpi", "astropy"],
    classifiers=["Programming Language :: Python :: 3", "Operating System :: Windows"],
    python_requires=">=3.8",
)
