from setuptools import setup, find_packages
# import codecs
import os

# here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

VERSION = '1.0.3'
DESCRIPTION = 'Semantic Scholar paper api consuming'
LONG_DESCRIPTION = 'A package that allows to consuming the API of Semantic Scholar and the web content of all papers that they make available.'

# Setting up
setup(
    name="S2query",
    version=VERSION,
    author="BecomeAllan (Allan)",
    author_email="<allan.filesia@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    package_data={'S2query': ['VERSION']},
    # packages=['S2search'],
    install_requires=["requests", "pandas"],
    keywords=['python', 'Semantic Scholar', 'API', 'Papers', 'semantic-scholar', 'papers'],
    classifiers=[
        # "Development Status :: 2 - Pre-Alpha",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Science/Research',
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
