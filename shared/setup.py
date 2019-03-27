"""
This is used to support pipenv installing the shared code to the virtual
environments used in developement of Selene APIs and services.
"""
from setuptools import setup, find_packages

setup(
    name='selene',
    version='0.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'passlib',
        'pygithub',
        'pyhamcrest',
        'pyjwt',
        'psycopg2-binary',
        'redis',
        'schematics',
        'stripe'
    ]
)
