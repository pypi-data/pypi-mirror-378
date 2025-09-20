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

import os
import sys
import shutil
import time
import tempfile
import errno
import stat
import glob
import platform
import subprocess
import re
import typing
import pytz
import semver

from PyUtilities import Git

if sys.platform != 'win32':
    import pty

from xml.etree import ElementTree
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import List, Tuple, Callable, Any, Optional


# -- Private
def _handle_remove_readonly(func: Callable[..., Any], path: str, exc: Tuple[type[BaseException],
                            BaseException, TracebackType]) -> None:
    exc_value = typing.cast(OSError, exc[1])
    if func in (os.rmdir, os.remove, os.unlink) and exc_value.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # -- 0777
        func(path)
    else:
        raise


_app_name = ''
_app_version = ''

# -- This is used in Unit tests to mock the time for 'now'.
_mock_now_date: Optional[datetime] = None

# -- Public

# -- This makes sure that some things work when running as an app and not from the command line.
# -- For example this fixes the error: "The process has forked, and you cannot use this CoreFoundation
# -- functionality safely. You MUST exec()." when calling shellCommand().
use_ui_application_mode = False


def set_app_info(name: str, _version: str) -> None:
    global _app_name
    global _app_version

    _app_name = name
    _app_version = name


def shell_command(command_and_args: List[str], from_dir: Optional[Path] = None, capture_output: bool = False,
                  filter_ansi: bool = False) -> Tuple[int, List[str]]:
    try:
        captured_output: List[str] = []

        if sys.platform == 'win32' or use_ui_application_mode:
            if capture_output:
                result = subprocess.run(command_and_args, cwd=from_dir, stderr=subprocess.STDOUT,
                                        stdout=subprocess.PIPE)
                captured_output = result.stdout.decode('utf-8').split('\n')
            else:
                result = subprocess.run(command_and_args, cwd=from_dir, stderr=sys.stderr, stdout=sys.stdout)

            return_code = result.returncode
        else:
            if from_dir is not None:
                raise RuntimeError('from_dir is not supported when using pty.spawn.')

            if capture_output:
                output_bytes = bytearray()

                def read_pty_output(fd: int) -> bytes:
                    data = os.read(fd, 1024)

                    if len(data) != 0:
                        output_bytes.extend(data)

                        # -- We don't need to print anything out, we're just capturing.
                        data = bytearray()
                        data.append(0)

                    return data

                return_code = pty.spawn(command_and_args, master_read=read_pty_output)
                captured_output = output_bytes.decode('utf-8').split('\n')
            else:
                return_code = pty.spawn(command_and_args)

            for i in range(len(captured_output)):
                if captured_output[i].endswith('\r'):
                    captured_output[i] = captured_output[i].strip('\r')

        if filter_ansi:
            # -- If we are in UI mode then we filter any ANSI characters
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

            new_output: List[str] = []
            for line in captured_output:
                new_output.append(ansi_escape.sub('', line))

            captured_output = new_output

        return return_code, captured_output
    except Exception as e:
        raise RuntimeError(f'Error running shell command: {e}')


def command_exists(command: str) -> bool:
    return_code, captured_output = shell_command(['where' if os.name == 'nt' else 'which', command],
                                                 capture_output=True)
    return return_code == 0


def require_command(command: str) -> None:
    if not command_exists(command):
        raise RuntimeError(f'Cannot find command "{command}".')


def string_to_int(string: Optional[str]) -> Optional[int]:
    if string is None:
        return None

    return int(string)


def string_to_float(string: Optional[str]) -> Optional[float]:
    if string is None:
        return None

    return float(string)


def date_from_string(string: Optional[str], string_format: str, utc: bool = False) -> Optional[datetime]:
    if string is None:
        return None

    try:
        date = datetime.strptime(string, string_format)
        if utc:
            date = pytz.utc.localize(date)  # type: ignore

        return date
    except ValueError:
        return None


def utc_time_now() -> datetime:
    if _mock_now_date is not None:
        return _mock_now_date

    return datetime.now().astimezone(pytz.utc)


def utc_datetime(year: int, month: int, day: int, hour: int, minutes: int, seconds: int) -> datetime:
    result: datetime = pytz.utc.localize(datetime(year, month, day, hour, minutes, seconds))  # type: ignore
    return result


def xml_element_to_string(element: ElementTree.Element, xml_declaration: bool = False) -> str:
    return ElementTree.tostring(element, encoding='unicode', short_empty_elements=False,
                                xml_declaration=xml_declaration)


def process_is_running(process_name: str) -> bool:
    return_code, captured_output = shell_command(['ps', '-axc', '-o', 'comm'])
    return process_name in captured_output


def look_in_folder_for(folder: Path, wildcard: str) -> List[str]:
    # -- We use this here instead of just simply Path.exists()
    # -- because we want the test to be case-sensitive on all platforms,
    # -- so we list what the match are and let glob give us the paths.
    paths_found = []
    looking_in = folder / wildcard
    prefix = str(folder / ' ')[:-1]

    for p in glob.glob(str(looking_in), recursive=True):
        as_string = str(p)
        if len(as_string) > 4:
            if len(prefix) != 0 and as_string.startswith(prefix):
                as_string = as_string[len(prefix):]

            paths_found.append(as_string)

    return paths_found


def delete_folder(folder: Path, force_delete: bool = False) -> None:
    if folder.exists():
        if force_delete:
            ignore_errors = False
            on_error = _handle_remove_readonly
        else:
            ignore_errors = True
            on_error = None

        shutil.rmtree(folder, ignore_errors=ignore_errors, onerror=on_error)


def file_older_than(path: Path, time_in_seconds: int) -> bool:
    if not path.exists():
        return True

    return (time.time() - path.stat().st_mtime) > time_in_seconds


def app_folder(create_if_needed: bool = False) -> Path:
    if _app_name == '':
        raise RuntimeError('Utility.set_app_info() needs to be called during app init.')

    if platform.system() != 'Darwin':
        # -- TODO: Paths need to be ported to 'Windows' and 'Linux'
        raise RuntimeError('Utility.app_folder() is macOS only at the moment.')

    folder = Path.home() / 'Library' / 'Application Support' / f'net.malenfant.{_app_name}'
    if create_if_needed:
        folder.mkdir(parents=True, exist_ok=True)

    return folder


def temp_folder(create_if_needed: bool = False) -> Path:
    if _app_name == '':
        raise RuntimeError('Utility.set_app_info() needs to be called during app init.')

    folder = Path(tempfile.gettempdir()) / f'net.malenfant.{_app_name}' / str(os.getpid())
    if create_if_needed:
        folder.mkdir(parents=True, exist_ok=True)

    return folder


def delete_temp_folder() -> None:
    folder = temp_folder()
    if folder.exists():
        delete_folder(folder, force_delete=True)


def check_for_updates(force_check: bool) -> None:
    # noinspection PyBroadException
    try:
        if _app_name == '' or _app_version == '':
            return

        out_file = app_folder(create_if_needed=True) / 'app-update-check'
        if not force_check and not file_older_than(out_file, time_in_seconds=(24 * 60 * 60)):
            return

        latest_version = Git.Repo(f'code.malenfant.net/didier/{_app_name}').get_latest_version()
        if latest_version is None:
            return

        if out_file.exists():
            out_file.unlink()

        out_file.write_text('check')

        if latest_version > semver.Version.parse(_app_version):
            warning = '‼️' if sys.platform == 'darwin' else '!!'
            print(f'{warning}  Version v{str(latest_version)} is available for Main.'
                  f'You have v{_app_version} {warning}')
            print(f'Please run "pip install {_app_name} --upgrade" to upgrade.')
    except Exception:
        pass
