# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='is_there_a_giants_game_tomorrow',
    version='1.0.0',
    description="Tool to check if there's a Giants game tomorrow and send an email alert",
    long_description=long_description,
    url='https://github.com/gene1wood/is-there-a-giants-game-tomorrow',
    author='Gene Wood',
    author_email='gene_wood@cementhorizon.com',
    license='GPL-3.0',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='sf san francisco giants schedule',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    entry_points={
        "console_scripts": [
            "is-there-a-giants-game-tomorrow = is_there_a_giants_game_tomorrow:main"
        ]
    }
)
