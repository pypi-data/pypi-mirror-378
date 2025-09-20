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

import sys
import os
import stat
import getopt
import traceback

from PyUtilities import Utility, Git

from pathlib import Path
from typing import List, Dict, Callable

__appname__ = 'DidierCI'
__version__ = '0.91'
_head_run = False
_verbose_on = False


def print_version(_commands: List[str]) -> None:
    print(f'🌡️ {__appname__} v{__version__} 🌡️')


def print_usage(commands: List[str]) -> None:
    if len(commands) > 1:
        switch: Dict[str, Callable[[List[str]], None]] = {
            'topics': print_topics,
            'license': print_license,
            'run': print_help_run,
            'install': print_help_install
        }

        method = switch.get(commands[1])
        if method is None:
            raise RuntimeError(f'Unknown topic "{commands[1]}".')

        method(commands)
        return

    print_version(commands)
    print('')
    print('usage: DidierCI <options> commands')
    print('')
    print('The following commands are supported:')
    print('')
    print('   help <topic>    - Show a help message. topic is optional (use "help topics" for a list).')
    print('   version         - Print the current version.')
    print('   run tasks       - Run the given tasks on the local repo.')
    print('   install tasks   - Install tasks to be run pre and post commit on the local repo.')
    print('')
    print('The following options are supported:')
    print('')
    print('   --debug/-d     - Enable extra debugging information.')
    print('   --verbose/-v   - Print tasks output if any.')
    print('')
    print('DidierCI is free software, run "DidierCI help license" for license information.')


def print_topics(commands: List[str]) -> None:
    print_version(commands)
    print('')
    print('Usage:')
    print('   DidierCI help license - Show the license for the app.')
    print('   DidierCI help run     - Show help about the run command.')
    print('   DidierCI help install - Show help about the install command.')
    print('')


def print_license(commands: List[str]) -> None:
    print_version(commands)
    print('')
    print('GPL License Version 3')
    print('')
    print('Copyright (c) 2024-present Didier Malenfant <didier@malenfant.net>')
    print('')
    print('DidierCI is free software: you can redistribute it and/or modify it under the terms of the GNU General')
    print('Public License as published by the Free Software Foundation, either version 3 of the License, or')
    print('(at your option) any later version.')
    print('')
    print('DidierCI is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the')
    print('implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public')
    print('License for more details.')
    print('')
    print('You should have received a copy of the GNU General Public License along with DidierCI. If not,')
    print('see <https://www.gnu.org/licenses/>.')
    print('')


def print_help_run(commands: List[str]) -> None:
    print_version(commands)
    print('')
    print('Usage:')
    print('   DidierCI <options> run tasks  - Run the given tasks on the local repo.')
    print('')
    print('Run tasks on the local repository. The following tasks are supported:')
    print('')
    print('   flake8            - Run flake 8 linting on any folder which contains python files.')
    print('   mypy              - Run mypy to ensure correct typing information on any folder which contains '
          'python files.')
    print('   pytest            - Run pytest is the root folder contains a folder named Tests.')
    print('')
    print('The following options are supported:')
    print('')
    print('   --head         - Run the commands on the current repo\'s head commit.')
    print('')
    print('You can also list more than one task on the command line.')


def print_help_install(commands: List[str]) -> None:
    print_version(commands)
    print('')
    print('Usage:')
    print('   DidierCI install tasks - Install tasks to be run pre and post commit on the local repo.')
    print('')
    print('Install tasks to run on the local repository during pre and post git commits. The following tasks are '
          'supported:')
    print('')
    print('   flake8            - Run flake 8 linting on any folder which contains python files.')
    print('   mypy              - Run mypy to ensure correct typing information on any folder which contains '
          'python files.')
    print('   pytest            - Run pytest is the root folder contains a folder named Tests.')
    print('')
    print('You can also list more than one task on the command line.')


def find_folders_with_python_files(in_folder: Path) -> List[Path]:
    found_folders: List[Path] = []

    if len(Utility.look_in_folder_for(in_folder, '*.py')) != 0:
        found_folders.append(in_folder)

    for item in Utility.look_in_folder_for(in_folder, '*'):
        item_found = in_folder / item

        if not item_found.is_dir():
            continue

        found_folders += find_folders_with_python_files(item_found)

    return found_folders


def find_sub_modules_folders(in_folder: Path) -> List[Path]:
    found_folders: List[Path] = []

    maybe_hooks_folder = in_folder / 'hooks'

    if maybe_hooks_folder.exists() and maybe_hooks_folder.is_dir():
        found_folders.append(in_folder)
    else:
        for item in Utility.look_in_folder_for(in_folder, '*'):
            item_found = in_folder / item

            if not item_found.is_dir():
                continue

            found_folders += find_sub_modules_folders(item_found)

    return found_folders


def run_my_py(in_folder: Path) -> None:
    if not Utility.command_exists('mypy'):
        print('WARNING: Unable to find mypy for CI testing.')
        return

    for folder in find_folders_with_python_files(in_folder):
        return_code, captured_output = Utility.shell_command(['mypy',
                                                              '--disallow-any-generics',
                                                              '--ignore-missing-imports',
                                                              '--follow-imports=silent',
                                                              '--follow-untyped-imports',
                                                              '--no-incremental',
                                                              '--strict-equality',
                                                              '--disallow-incomplete-defs',
                                                              '--disallow-redefinition',
                                                              '--disallow-untyped-globals',
                                                              '--no-implicit-optional',
                                                              '--no-implicit-reexport',
                                                              '--warn-redundant-casts',
                                                              '--warn-unused-ignores',
                                                              '--warn-unreachable',
                                                              '--warn-no-return',
                                                              '--disallow-untyped-calls',
                                                              '--disallow-untyped-defs',
                                                              '--check-untyped-defs',
                                                              '--disallow-any-generics',
                                                              '--warn-return-any',
                                                              '--explicit-package-bases',
                                                              str(folder)],
                                                             capture_output=not _verbose_on,
                                                             filter_ansi=not _verbose_on)

        if return_code != 0:
            if not _verbose_on:
                for line in captured_output:
                    if len(line) > 0:
                        print(line)

            raise RuntimeError()


def run_flake8(in_folder: Path) -> None:
    if not Utility.command_exists('flake8'):
        print('WARNING: Unable to find flake8 for CI testing.')
        return

    for folder in find_folders_with_python_files(in_folder):
        return_code, captured_output = Utility.shell_command(['flake8', str(folder)],
                                                             capture_output=not _verbose_on,
                                                             filter_ansi=not _verbose_on)

        if return_code != 0:
            if not _verbose_on:
                for line in captured_output:
                    if len(line) > 0:
                        print(line)

            raise RuntimeError()


def run_py_test(in_folder: Path) -> None:
    if not Utility.command_exists('pytest'):
        print('WARNING: Unable to find pytest for CI testing.')
        return

    tests_folder = in_folder / 'Tests'
    if tests_folder.exists():
        return_code, captured_output = Utility.shell_command(['pytest', str(tests_folder)],
                                                             capture_output=not _verbose_on,
                                                             filter_ansi=not _verbose_on)

        if return_code != 0:
            if not _verbose_on:
                for line in captured_output:
                    if len(line) > 0:
                        print(line)

            raise RuntimeError()


def run_ci(commands: List[str]) -> None:
    switch: Dict[str, Callable[[Path], None]] = {
        'flake8': run_flake8,
        'mypy': run_my_py,
        'pytest': run_py_test
    }

    try:
        in_folder = Path('.')
        if _head_run:
            in_folder = Utility.temp_folder(create_if_needed=True) / 'CiRepo'

            git_repo = Git.Repo('.', url_is_local_folder=True)
            git_repo.clone_in(in_folder)

        for task in commands[1:]:
            method = switch.get(task)
            if method is None:
                raise RuntimeError(f'Unknown task "{task}".')

            method(in_folder)
    finally:
        Utility.delete_temp_folder()


def install_ci(commands: List[str]) -> None:
    local_folder = Path('.git')
    repo_folders = [local_folder]
    repo_folders += find_sub_modules_folders(local_folder / 'modules')

    for folder in repo_folders:
        if not folder.exists() or not folder.is_dir():
            raise RuntimeError(f'Folder "{folder}" has no git repo to install hooks.')

        valid_tasks: List[str] = ['flake8', 'mypy', 'pytest']
        tasks_string = ''
        for task in commands[1:]:
            if task not in valid_tasks:
                raise RuntimeError(f'Unknown task "{task}".')

            if len(tasks_string) != 0:
                tasks_string += ' '

            tasks_string += task

        post_commit_file = folder / 'hooks' / 'post-commit'
        with open(post_commit_file, 'w') as out_file:
            out_file.write('#!/bin/bash\n')
            out_file.write('#\n')
            out_file.write('# post-commit git-hook for DidierCI.\n')
            out_file.write('#\n')
            out_file.write('# This file is auto-generated. DO NOT EDIT.\n')
            out_file.write('#\n')
            out_file.write('\n')
            out_file.write('unset GIT_DIR\n')
            out_file.write('unset GIT_WORK_TREE\n')
            out_file.write('\n')
            out_file.write('OPERATION_FAILED=0\n')
            out_file.write(f'DidierCI --head run {tasks_string} || OPERATION_FAILED=1\n')
            out_file.write('\n')
            out_file.write('if [[ $OPERATION_FAILED -eq 0 ]]\n')
            out_file.write('then\n')
            out_file.write('   exit\n')
            out_file.write('fi\n')
            out_file.write('\n')
            out_file.write('exec 5>&1\n')
            out_file.write('\n')
            out_file.write('if [[ "$OSTYPE" != "darwin"* ]]; then\n')
            out_file.write('   exit 1\n')
            out_file.write('fi\n')
            out_file.write('\n')
            out_file.write(f'TEST=$(python DidierCI --head run {tasks_string})\n')
            out_file.write('\n')
            out_file.write('/usr/bin/osascript <<-EOF\n')
            out_file.write('\n')
            out_file.write(' tell application "System Events"\n')
            out_file.write('      activate\n')
            out_file.write('      display alert "Last commit failed CI tests." message "$TEST" as critical\n')
            out_file.write(' end tell\n')
            out_file.write('\n')
            out_file.write('EOF\n')

            out_file.close()

        os.chmod(post_commit_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                 stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

        pre_commit_file = folder / 'hooks' / 'pre-commit'
        with open(pre_commit_file, 'w') as out_file:
            out_file.write('#!/bin/bash\n')
            out_file.write('#\n')
            out_file.write('# pre-commit git-hook for DidierCI.\n')
            out_file.write('#\n')
            out_file.write('# This file is auto-generated. DO NOT EDIT.\n')
            out_file.write('#\n')
            out_file.write('\n')
            out_file.write('# -- Stash any unstaged changes\n')
            out_file.write('git stash -q --keep-index\n')
            out_file.write('\n')
            out_file.write('# -- Run the pre-commit tests\n')
            out_file.write(f'DidierCI run {tasks_string}\n')
            out_file.write('\n')
            out_file.write('# -- Store the last exit code in a variable\n')
            out_file.write('RESULT=$?\n')
            out_file.write('\n')
            out_file.write('# -- Un-stash the stashed changes\n')
            out_file.write('git stash pop -q\n')
            out_file.write('\n')
            out_file.write('# -- Return the exit code\n')
            out_file.write('exit $RESULT\n')
            out_file.write('\n')
            out_file.write('# << must have a newline after the above command >>\n')
            out_file.write('\n')

            out_file.close()

        os.chmod(pre_commit_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                 stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)


def main() -> None:
    global _head_run
    global _verbose_on

    _debug_on = False

    Utility.set_app_info(__appname__, __version__)

    try:
        # -- Gather the arguments, remove the first argument (which is the script filename)
        opts, commands = getopt.getopt(sys.argv[1:], 'dhv', ['help', 'debug', 'head', 'verbose'])

        for o, a in opts:
            if o in ('-d', '--debug'):
                print('Enabling debugging information.')
                _debug_on = True
            elif o in '--help':
                commands = ['help']
            elif o in ('-h', '--head'):
                _head_run = True
            elif o in ('-v', '--verbose'):
                _verbose_on = True

        if commands is None or len(commands) == 0:
            raise RuntimeError('Expected a command! Maybe start with `DidierCI help`?')

        switch: Dict[str, Callable[[List[str]], None]] = {
            'help': print_usage,
            'version': print_version,
            'run': run_ci,
            'install': install_ci
        }

        command: str = commands[0]
        method = switch.get(command)
        if method is None:
            raise RuntimeError(f'Unknown command "{command}".')

        method(commands)

    except getopt.GetoptError:
        print_usage([])
    except Exception as e:
        if _debug_on:
            print(traceback.format_exc())
        else:
            exception_string = str(e)
            if len(exception_string) != 0:
                print(f'Error: {e}')

        sys.exit(1)
    except KeyboardInterrupt:
        print('Execution interrupted by user.')
        pass


if __name__ == '__main__':
    main()
