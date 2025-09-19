#!/usr/bin/env python3
"""
Setup configuration for DTP SDK package.
"""

from setuptools import setup, find_packages
import os

# Read the README file safely
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "DTP SDK - Advanced cryptographic security with steganography and decoy protection"

setup(
    name='dtp-security',
    version='1.0.0',
    author='Jeyashree Narayanan', 
    author_email='jeyashree.narayanan@example.com',
    description='Advanced cryptographic SDK with steganography and active defense capabilities',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/vinothvbt/DTP-password-manager',
    project_urls={
        'Bug Reports': 'https://github.com/vinothvbt/DTP-password-manager/issues',
        'Source': 'https://github.com/vinothvbt/DTP-password-manager',
        'Documentation': 'https://github.com/vinothvbt/DTP-password-manager#readme',
    },
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'dtp': ['*.json', 'templates/*.json'],
    },
    install_requires=[
        'pycryptodome>=3.15.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0', 
            'black>=22.0',
            'flake8>=4.0',
        ],
        'demo': [
            'flask>=2.0.0',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Security :: Cryptography',
        'Topic :: Security',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    keywords='security cryptography steganography decoy active-defense cybersecurity encryption',
    license='Apache 2.0',
)
