# coding: utf-8
"""
Manage Stakkr Packages (extra packages)
"""

from git import Repo, exc
from requests import head, HTTPError

__github_url__ = 'https://github.com/stakkr-org'


def install(services_dir: str, package: str, name: str):
    """Install a specific service by cloning a repo"""
    from os.path import isdir
    from urllib.parse import urlparse

    url = '{}/services-{}.git'.format(__github_url__, package)
    if urlparse(package).scheme != '':
        url = package

    path = '{}/{}'.format(services_dir, name)
    try:
        _check_repo_exists(url)

        if isdir(path):
            msg = 'Package "{}" is already installed, updating'.format(package)
            update_package(path)
            return True, msg

        Repo.clone_from(url, path)

        return True, None
    except HTTPError as error:
        return False, "Can't add package: {}".format(str(error))
    except ImportError:
        return False, 'Make sure git is installed'
    except exc.GitCommandError as error:
        return False, "Couldn't clone {} ({})".format(url, error)


def update_all(services_dir: str):
    """Update all services by pulling"""
    from os import listdir

    for folder in listdir(services_dir):
        path = services_dir + '/' + folder
        update_package(path)


def update_package(path: str):
    """Update a single service withgit pull"""
    try:
        repo = Repo(path)
        if repo.remotes.origin.url.endswith('.git'):
            repo.remotes.origin.pull()
    except exc.InvalidGitRepositoryError:
        pass


def _check_repo_exists(repo: str):
    status_code = head(repo, allow_redirects=True).status_code
    if status_code != 200:
        raise HTTPError("{} is not a valid repo (status = {})".format(repo, status_code))
