# coding: utf-8
"""
Manage Stakkr Packages (extra packages)
"""

__github_url__ = 'https://github.com/stakkr-org'


def install(services_dir: str, package: str):
    from os.path import isdir
    from urllib.parse import urlparse

    url = '{}/services-{}.git'.format(__github_url__, package)
    if urlparse(package).scheme != '':
        url = package

    dest = '{}/{}'.format(services_dir, package)
    if isdir(dest):
        msg = 'Package "{}" is already installed'.format(package)
        return False, msg

    try:
        from git import Repo, exc
        Repo.clone_from(url, dest)

        return True, None
    except ImportError as error:
        return False, 'Make sure git is installed'
    except exc.GitCommandError as error:
        return False, "Couldn't clone {} ({})".format(url, error)


def update_all(services_dir: str):
    from os import listdir

    for folder in listdir(services_dir):
        path = services_dir + '/' + folder
        update_package(path)


def update_package(path: str):
    from git import Repo, exc

    try:
        repo = Repo(path)
        if repo.remotes.origin.url.startswith(__github_url__):
            repo.remotes.origin.pull()
    except exc.InvalidGitRepositoryError:
        pass
