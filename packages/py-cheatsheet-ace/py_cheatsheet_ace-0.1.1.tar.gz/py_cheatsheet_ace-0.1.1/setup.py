from setuptools import setup, find_packages

setup(
    # Change this to your new, unique name
    name="py-cheatsheet-ace", 
    
    # Reset the version for the new package
    version="0.1.1", 
    
    author="prashant shirke",
    description="A personal cheatsheet library for my DS practicals.",
    packages=find_packages(),
    python_requires='>=3.6',
    package_data={
        "mycheats.practicals": ["*.py"],
    },
    install_requires=[],
)