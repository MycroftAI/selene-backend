"""
This is used to support pipenv installing the shared code to the virtual
environments used in developement of Selene APIs and services.
"""
from setuptools import setup

setup(
    name='selene',
    version='0.0.0',
    packages=['selene'],
    install_requires=['flask', 'flask-restful', 'pygithub', 'pyjwt']
)
