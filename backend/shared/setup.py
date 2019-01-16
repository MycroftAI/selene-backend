"""
This is used to support pipenv installing the shared code to the virtual
environments used in developement of Selene APIs and services.
"""
from setuptools import setup, find_packages

setup(
    name='selene_util',
    version='0.0.0',
    packages=find_packages(),
    include_package_date=True,
    package_data={
        '': ['*.sql']
    },
    install_requires=['flask', 'flask-restful', 'pygithub', 'pyjwt']
)
