from setuptools import setup
from pathlib import Path

here = Path(__file__).absolute().parent

with (here / "requirements.txt").open("r") as rf:
    reqs = rf.readlines()

with (here / "README.md").open("r") as rf:
    readme = rf.read()

setup(
    name='bicidata',
    version='0.0.2',
    packages=['bicidata', 'bicidata.services'],
    url='https://github.com/bicidata/bicidata',
    license='',
    author='Ismael Benito Altamirano',
    author_email='',
    description='bicidate is a framework to work with the General Bikeshare Feed Specification (GBFS)',
    long_description=readme,
    long_description_content_type='text/markdown',
    install_requires=reqs,
)
