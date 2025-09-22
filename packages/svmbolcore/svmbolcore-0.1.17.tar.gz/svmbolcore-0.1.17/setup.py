from setuptools import setup, find_packages
setup(
    name="svmbolcore",
    version="0.1.17",
    author="codespaceDrifter",  
    author_email="codespaceDrifter@gmail.com",  
    description="symbolic math lib that generates parallel CUDA",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/svmbolcore",  # Your GitHub URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
    ],
)



'''
how to update note to self:
-> Update version in setup.py (e.g. "0.1.0" -> "0.1.1")
commands:
(run in root folder where setup.py is)
python -m build
python -m twine upload dist/*
'''
