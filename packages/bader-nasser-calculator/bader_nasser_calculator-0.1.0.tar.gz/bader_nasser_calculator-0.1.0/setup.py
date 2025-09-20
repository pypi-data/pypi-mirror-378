
from setuptools import setup, find_packages

setup(
    name='bader-nasser-calculator',
    version='0.1.0',
    author='بدر ناصر',
    author_email='bader.nasser@example.com', # Placeholder email
    description='A simple calculator package for basic math operations by Bader Nasser',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/bader-nasser/simple-calculator', # Placeholder URL
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)


