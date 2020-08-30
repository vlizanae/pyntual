#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as requirements_file:
    requirements = [
        line.strip() for line in requirements_file.readlines() if line.strip()
    ]

with open('requirements_dev.txt') as requirements_file:
    setup_requirements = [
        line.strip() for line in requirements_file.readlines() if line.strip()
    ]

test_requirements = [ ]

setup(
    author="Vicente Lizana Estivill",
    author_email='v.lizana.e@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Fintual API Python client.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='pyntual',
    name='pyntual',
    packages=find_packages(include=['pyntual', 'pyntual.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/vlizanae/pyntual',
    version='0.1.3',
    zip_safe=False,
)
