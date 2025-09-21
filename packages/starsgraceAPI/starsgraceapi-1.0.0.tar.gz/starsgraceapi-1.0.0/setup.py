from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="starsgraceAPI",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
    ],
    author="StarsGrace",
    author_email="bashirsandking@gmail.com",  
    description="Python client for the Fragment API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/starsgrace-api/FragmentAPI", 
    license="MIT", 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    keywords="fragment api telegram stars premium ton",
)