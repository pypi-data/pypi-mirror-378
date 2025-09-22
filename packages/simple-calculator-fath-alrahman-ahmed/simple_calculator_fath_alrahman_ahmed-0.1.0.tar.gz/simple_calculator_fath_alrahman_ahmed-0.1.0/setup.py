from setuptools import setup, find_packages

setup(
    name='simple-calculator-fath-alrahman-ahmed',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    author='Fath Alrahman Ahmed',
    author_email='fath.alrahman.ahmed@example.com',
    description='A simple calculator package for basic math operations.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/fath-alrahman-ahmed/simple-calculator-fath-alrahman-ahmed',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)


