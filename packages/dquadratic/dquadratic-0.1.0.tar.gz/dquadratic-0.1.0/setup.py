from setuptools import setup, find_packages

setup(
    name='dquadratic',
    version='0.1.0',
    packages=find_packages(),
    author='Shahabaj Tamjid',
    author_email='shahbajtamjid97@gmail.com',
    description='The package is used to find the roots and the nature of a quadratic equation.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.0',
)