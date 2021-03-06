import re
import os
from setuptools import setup


package_name = 'noqlite'


def find_version():
    root = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(root, package_name, '__init__.py')
    with open(path) as f:
        content = f.read()
    ver = re.findall('__version__ = (.+)', content)
    if not ver:
        raise RuntimeError('unable to find version string')
    ver = ver[0][1:-1]
    return ver


setup(
    name=package_name,
    version=find_version(),
    description='simple nosql over sqlite',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    url='https://github.com/gowhari/noqlite',
    author='Iman Gowhari',
    author_email='gowhari@gmail.com',
    license='MIT',
    packages=['noqlite'],
    zip_safe=False,
)
