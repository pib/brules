import os
from setuptools import setup

def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except:
        return ''

setup(
    name = "brules",
    version = "0.0.1",
    author = "Paul Bonser",
    author_email = "misterpib@gmail.com",
    description = "A tool to help you parse and process text-based business rules.",
    license = "BSD",
    keywords = "business rules parsing",
    url = "http://packages.python.org/an_example_pypi_project",
    packages=['brules', 'tests'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
