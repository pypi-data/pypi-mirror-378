"""
PyShield Setup Configuration
============================

Setup script for PyShield - Advanced Python Code Encryptor
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "PyShield - Advanced Python Code Encryptor"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ['cryptography>=3.4.8', 'click>=8.0.0']

setup(
    name='pyshield-encryptor',
    version='1.0.0',
    author='PyShield Team',
    author_email='contact@pyshield.dev',
    description='Advanced Python Code Encryptor with seamless execution',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/pyshield/pyshield',
    project_urls={
        'Bug Reports': 'https://github.com/pyshield/pyshield/issues',
        'Source': 'https://github.com/pyshield/pyshield',
        'Documentation': 'https://pyshield.readthedocs.io',
    },
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development :: Code Generators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Operating System :: Android',
        'Environment :: Console',
        'Environment :: Other Environment',
    ],
    keywords='encryption, python, code-protection, obfuscation, security, cross-platform, android, termux',
    python_requires='>=3.7',
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.800',
        ],
        'docs': [
            'sphinx>=4.0',
            'sphinx-rtd-theme>=1.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'pyshield=pyshield.cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    platforms=['any'],
    license='MIT',
    test_suite='tests',
)
