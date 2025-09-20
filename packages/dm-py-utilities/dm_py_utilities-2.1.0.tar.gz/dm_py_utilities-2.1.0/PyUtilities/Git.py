#
# Copyright (c) 2024-present Didier Malenfant <didier@malenfant.net>
#
# This file is part of PyUtilities.
#
# PyUtilities is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyUtilities is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License along with PyUtilities. If not,
# see <https://www.gnu.org/licenses/>.
#

import semver

from PyUtilities import Utility

from pathlib import Path
from typing import List, Dict, Tuple, Optional


class Repo:
    """Utility methods for git repos."""

    def __init__(self, url: str, url_is_local_folder: bool = False):
        """Setup access to the git repo at url."""

        if not Utility.command_exists('git'):
            raise RuntimeError('You must have git installed on your machine to continue.')

        self._url = url if url_is_local_folder else f'https://{url}.git'
        self._refs: Optional[Dict[str, str]] = None
        self._tags: Optional[List[str]] = None
        self._tag_versions: Optional[List[semver.Version]] = None
        self._branches: Optional[Dict[str, str]] = None
        self._head_branch: Optional[str] = None
        self._latest_version: Optional[semver.Version] = None

    def _cmd(self, arguments: List[str], folder: Optional[Path] = None) -> List[str]:
        arguments.insert(0, 'git')
        arguments.append(self._url.replace('https://', 'https://anonymous:@'))

        if folder is not None:
            arguments.append(str(folder))

        result: Tuple[int, List[str]] = Utility.shell_command(arguments, capture_output=True)
        if result[0] != 0:
            error = result[1][0]

            if error.startswith('usage: git'):
                # -- git is giving us the usage info back it seems.
                raise SyntaxError('Invalid git command line')
            elif error.startswith('fatal: not a git repository (or any of the parent directories): .git'):
                raise RuntimeError('Your project folder needs to be a git repo for certain commands to work correctly.'
                                   'Try `git init` to create one.')
            elif error == 'remote: Invalid username or password.':
                raise RuntimeError(f'Cannot access git repo at "{self._url}". Maybe it is private?')
            else:
                # -- Or maybe something else went wrong.
                raise RuntimeError(f'Error running git: {error}')

        return result[1]

    def list_refs(self) -> Dict[str, str]:
        if self._refs is None:
            self._refs = {}
            for ref in self._cmd(['ls-remote', '--refs']):
                refs_index = ref.find('refs/')
                if refs_index >= 0:
                    self._refs[ref[refs_index + 5:]] = ref[:40]

        return self._refs

    def list_branches(self) -> Dict[str, str]:
        if self._branches is None:
            self._branches = {}
            refs = self.list_refs()
            for ref in refs.keys():
                if ref.startswith('heads/'):
                    self._branches[ref[6:]] = refs[ref]

        return self._branches

    def get_head_branch(self) -> str:
        if self._head_branch is None:
            for line in self._cmd(['remote', 'show']):
                if line.startswith('  HEAD branch:'):
                    self._head_branch = line[15:]

            if self._head_branch is None:
                raise RuntimeError(f'Cannot find head branch for "{self._url}".')

        return self._head_branch

    def list_tags(self) -> List[str]:
        if self._tags is None:
            self._tags = []
            for ref in self.list_refs().keys():
                if ref.startswith('tags/'):
                    tag = ref[5:]
                    if not tag.startswith('@'):
                        self._tags.append(tag)

        return self._tags

    def list_tag_versions(self) -> List[semver.Version]:
        if self._tag_versions is None:
            self._tag_versions = []

            for tag in self.list_tags():
                try:
                    if tag.startswith('v'):
                        tag = tag[1:]

                    self._tag_versions.append(semver.Version.parse(tag))
                except ValueError:
                    pass

            self._tag_versions = sorted(self._tag_versions)

        return self._tag_versions

    def get_latest_version(self) -> Optional[semver.Version]:
        if self._latest_version is None:
            all_versions = self.list_tag_versions()

            if len(all_versions) > 0:
                self._latest_version = all_versions[-1]

        return self._latest_version

    def get_latest_commit_hash_for_branch(self, branch_name: str) -> Optional[str]:
        return self.list_branches().get(branch_name)

    def is_a_branch(self, name: str) -> bool:
        return name in self.list_branches()

    def is_a_tag(self, name: str) -> bool:
        for tag in self.list_tags():
            if tag == name:
                return True

        return False

    def clone_in(self, folder: Path, branch: Optional[str] = None, recurse_submodules: bool = True,
                 shallow: bool = False) -> None:
        folder.mkdir(parents=True, exist_ok=True)

        command_line: List[str] = ['clone', '--quiet']

        if shallow:
            command_line.append('--depth')
            command_line.append('1')

        if recurse_submodules:
            command_line.append('--recurse-submodules')

        if branch is not None:
            command_line.append('--branch')
            command_line.append(branch)

        self._cmd(command_line, folder)
