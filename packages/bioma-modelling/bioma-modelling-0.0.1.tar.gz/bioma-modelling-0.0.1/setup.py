from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
   name='bioma-modelling',
   version='0.0.1',
   description='Python library to streamline interaction with the BioMA APIs, providing a pythonic facade to data and service access.',
   license="MIT",
   long_description=long_description,
   long_description_content_type="text/markdown",
   author='CREA',
   author_email='dario.denart@crea.gov.it',
   url="https://dev.azure.com/dariodenart/_git/BioMA%20Python%20Toolkit",
   packages=['biomatools', 'biomatools.utils'],
   install_requires=['pandas','requests', 'retry'], #external packages as dependencies
)