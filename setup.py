from setuptools import setup
from pathlib import Path

here = Path(__file__).absolute().parent

with (here / "requirements.txt").open("r") as rf:
    r = rf.readlines()

setup(
    name='bicidata',
    version='0.1.0',
    packages=['bicidata', 'bicidata.services'],
    url='',
    license='',
    author='ibenito',
    author_email='',
    description='',
    install_requires=r,
)
