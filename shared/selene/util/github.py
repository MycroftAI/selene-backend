"""
Logic that uses the Github REST API to extract repository-related metadata
"""
from logging import getLogger
from urllib.request import urlopen

from github import Github

_log = getLogger(__package__)


def log_into_github(user_name: str, user_password: str) -> Github:
    _log.info('logging into GitHub as "{}"'.format(user_name))
    return Github(user_name, user_password)


def download_repository_file(github, repository_name, branch, file_path):
    organization = github.get_organization('MycroftAI')
    repository = organization.get_repo(repository_name)
    repository_contents = repository.get_contents(file_path, ref=branch)

    with urlopen(repository_contents.download_url) as repository_file:
        return repository_file.read()
