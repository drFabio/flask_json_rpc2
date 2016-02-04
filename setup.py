"""
Flask-JSON-RPC-2
-------------

Lightweight flask extension for json rpc 2.0  method handling
It is capable of handle urls without bounding method, urls bounding methods 
and handling using a class
"""
from setuptools import setup

setup(
    name='flask_json_rpc2',
    version='0.1',
    url='https://github.com/drFabio/flask_json_rpc2',
    license='MIT',
    author='Fabio Costa',
    author_email='blackjackdevel@gmail.com',
    description='Adds json rpc 2 capabilities',
    long_description=__doc__,
    py_modules=['json_rpc'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)