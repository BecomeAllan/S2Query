from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'Semantic Scholar paper api consuming'
LONG_DESCRIPTION = 'A package that allows to consuming the API of Semantic Scholar and the web content of all papers that they make available.'

# Setting up
setup(
    name="S2search",
    version=VERSION,
    author="BecomeAllan (Allan)",
    author_email="<allan.filesia@gmail.com>",
    description=DESCRIPTION,
    # long_description_content_type="text/markdown",
    # long_description=long_description,
    packages=find_packages(),
    install_requires=['requests', 'pandas', 'pyaudio'],
    keywords=['python', 'Semantic Scholar', 'API', 'Papers', 'semantic-scholar', 'papers'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)