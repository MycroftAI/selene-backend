"""
Logic that uses the Github REST API to extract repository-related metadata
"""
from collections import defaultdict
from urllib.request import urlopen

from github import Github


def get_user_repositories(user_name: str, user_password: str) -> list:
    """
    Request a list of repositories that can be accessed by the supplied user.

    :param user_name: the Github login user name
    :param user_password: the Github user's password
    :return: list of repositories the user has access to
    """
    github = Github(user_name, user_password)
    github_user = github.get_user()

    return github_user.get_repos()


def is_skill_repository(repository) -> bool:
    """
    Use repository metadata to determine if it is a Mycroft skill repository

    :param repository: object representing a Github repository
    :return: boolean indicating if the repository is a Mycroft skill
    """
    return (
        repository.organization is not None and
        repository.organization.name == 'Mycroft' and
        repository.name.startswith('skill-')
    )


def download_readme(repository):
    """Download the README.md file for the specified repository

    :param repository: object representing a Github repository
    :return: a file-like object containing the README.md markdown.
    """
    return urlopen(repository.get_readme().download_url)


def download_repository_file(user_name, user_password, repository_name, file_path):
    github = Github(user_name, user_password)
    organization = github.get_organization('MycroftAI')
    repository = organization.get_repo(repository_name)
    repository_contents = repository.get_contents(file_path)

    with urlopen(repository_contents.download_url) as repository_file:
        return repository_file.read()


class SkillREADMEParser(object):
    """
    The README.md file for a Mycroft skill repository must be formatted according to template
    defined in the mycroft-markektplace repository.
    """
    def __init__(self, repository):
        self.repository = repository
        self.readme_sections = defaultdict(list)
        self.skill_name = None
        self.author = None
        self.summary = None
        self.description = None
        self.triggers = None

    def parse(self):
        """
        Download the README.md file and parse its contents
        """
        with download_readme(self.repository) as readme_file:
            self._get_sections(readme_file)
            self._parse_sections()

    def _get_sections(self, readme_file):
        """
        Split the contents of a README.md file into sections based on markdown for section header

        :param readme_file: a file-like object containing the README.md markdown.
        """
        section_name = None
        readme_lines = readme_file.read().decode().split('\n')
        for line in readme_lines:
            if line.startswith('##'):
                section_name = line.strip('##').strip()
            elif section_name is not None:
                self.readme_sections[section_name].append(line)

    def _parse_sections(self):
        """
        Derive skill metadata from the contents of the README.md sections.
        """
        for section_name, section_details in self.readme_sections.items():
            # Remove blank line at end of section, if there is one.
            if not section_details[-1]:
                section_details.pop(-1)
            if section_name == 'Description':
                self.description = '\n'.join(section_details)
            elif section_name == 'Examples':
                self.triggers = [example.strip('*').strip() for example in section_details]
            elif section_name == 'Credits':
                self.author = '\n'.join(section_details)
            else:
                self.skill_name = section_name
                self.summary = '\n'.join(section_details)
