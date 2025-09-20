import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dict-of-lists",
    version="1.0.0",
    author="Ehsan Karbasian",
    author_email="ehsan.karbasian@gmail.com",
    description="A dictionary with empty list/sets pre-setted values",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ehsankarbasian/dict_of_lists",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
