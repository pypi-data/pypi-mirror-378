from setuptools import setup, find_packages
import os

def read_file(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, encoding='utf-8') as f:
        return f.read()

setup(
    name='pypiget',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'requests>=2.28.0',
        'aiohttp>=3.8.0'
    ],
    include_package_data=True,
    description='A Python library to fetch PyPI package information (sync & async)',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://api-free.ir',
    author='Mahdi Ahmadi',
    author_email='mahdiahmadi.1208@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
    ],
    python_requires='>=3.6',
    keywords='pypi package async sync fetch library',
)
