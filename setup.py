from setuptools import setup
import os
import sys

if sys.version_info < (3, 6):
    raise RuntimeError("This package requires Python 3.6+")

#Cribbed from simonw
def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()

setup(
    name="ouseful_fsa_datasupply",
    packages=['ouseful_fsa_datasupply'],
    version='0.2.0',
    author="Tony Hirst",
    url="https://github.com/ouseful-datasupply/food_gov_uk",
    description="A simple tool for bulk downloading of etsablishment details and ratings data from food.gov.uk",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    install_requires=[
        'Click',
        'requests',
        'beautifulsoup4',
        'pandas',
        'xmltodict',
        'tqdm',
        'lxml',
        'html5lib'
    ],
    entry_points='''
        [console_scripts]
        fsa_data = ouseful_fsa_datasupply.cli:cli
    ''',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
      ],
)
