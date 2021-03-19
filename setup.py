#!/usr/bin/env python

from distutils.core import setup

setup(
    name='FiwareObjectConverter',
    version='0.0.1',
    maintainer='IML Fraunhofer OE130',
    packages=['fiwareobjectconverter', 'fiwareobjectconverter.json_to_object', 'fiwareobjectconverter.object_to_json', 'fiwareobjectconverter.normalizer'],
    license='LICENSE',
    description='This package serializes Python2- and -3-Objects into a Fiware-Entity and back. The generated JSON-Strings can be POSTed to their API.',
    long_description=open('README.md').read(),
    url='https://github.com/iml130/FiwareObjectConverter.git'
)