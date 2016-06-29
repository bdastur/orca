from setuptools import setup, find_packages


setup(
    name='orca',
    version='0.1',

    description='AWS Tools and Utilities for Operational Simplification',
    long_description=__doc__,
    url='https://github.com/bdastur/orca.git',

    author='Behzad Dastur',

    packages=find_packages(exclude=('tests*','scripts','server','cliclient')),

    # Available classifiers: https://goo.gl/G1iJ2B
    classifiers=[
        'Environment :: Console',

        'Intended Audience :: Developers',
        'Topic :: Software Development',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
