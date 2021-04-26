import setuptools
 
with open("README.md", "r") as file:
    program_description = file.read()
 
setuptools.setup(
    name="green_environment",
    version="0.0.0",
    author="Lars Hahn",
    author_email="lhahn@data-learning.de",
    description="Package to setup an application and libraries concerning environmental sensors and plant irrigation",
    long_description=program_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)