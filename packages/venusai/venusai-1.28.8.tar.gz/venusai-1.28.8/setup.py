from setuptools import setup, find_packages

setup(
    name='venusai',
    version='1.28.8',
    packages=find_packages(),
    author='Mert Sirakaya',
    install_requires=['venai'],
    description='Alias of `venai`. Install `venai` instead of this package.',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)