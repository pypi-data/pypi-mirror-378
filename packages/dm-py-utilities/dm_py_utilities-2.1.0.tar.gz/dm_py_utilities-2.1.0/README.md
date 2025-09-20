# PyUtilities

[![GPL-v3.0](https://img.shields.io/badge/license-GPL--3.0-orange)](https://spdx.org/licenses/GPL-3.0-or-later.html) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dm-py-utilities.svg)](https://python.org) [![PyPI - Version](https://img.shields.io/pypi/v/dm-py-utilities.svg)](https://pypi.org/project/dm-py-utilities)

A collections of scripts used by my Python projects.

### Installation

**PyUtilities** is a pure Python project. It requires at least [Python](https://python.org) 3.10. It is maintained on **Linux** but should probably also work on **macOS** and **Windows**.

You can install **PyUtilities** by typing the following in a terminal window:
```console
pip install dm-py-utilities
```

### DidierCI

**DidierCI** is a bare-bones local CI system that can run a few tasks before and after committing changes to your repo.

```console
DidierCI <options> commands
```

The following commands are supported:

```
   help <topic>    - Show a help message. topic is optional (use "help topics" for a list).
   version         - Print the current version.
   run tasks       - Run the given tasks on the local repo.
   install tasks   - Install tasks to be run pre and post commit on the local repo.
```

The following options are supported:

```
   --debug/-d     - Enable extra debugging information.
   --verbose/-v   - Print tasks output if any.
```

### License

**PyUtilities** is distributed under the terms of the [GPLv3.0](https://spdx.org/licenses/GPL-3.0-or-later.html) or later license.
