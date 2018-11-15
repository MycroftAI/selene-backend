"""
This is used to support pipenv installing the shared code to the virtual
environments used in developement of Selene APIs and services.
"""
from setuptools import setup

setup(
    name='selene_util',
    version='0.0.0',
    packages=['selene_util'],
    install_requires=['flask', 'flask-restful', 'pygithub', 'pyjwt']
)