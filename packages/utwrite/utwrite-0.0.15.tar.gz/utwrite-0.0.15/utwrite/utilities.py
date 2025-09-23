r"""Utilities for python unittest generator."""

import os
import sys
import pathlib


def leading_whitespace(s) -> int:
    r"""Get amount of leading whitespace.

    Args:
        - s `str`: Text to get number of leading whitespace.

    Returns:
        `int`: Number of whitespaces

    Examples::

        from utwrite import utilities

        s = '    foo bar'
        utilities.leading_whitespace(s)
        # Result: 4 #
        utilities.leading_whitespace('no whitespace')
        # Result: 0 #
        utilities.leading_whitespace(' one  two   three')
        # Result: 1 #
    """
    return len(s) - len(s.lstrip(' '))


def get_files_from_dir(path, ext=[], ignore=[], sort_key=None) -> list:
    r"""Get files inside given path.

    Args:
        - path `str`: Path to get files in directory from.
        - ext `list`: Default []. Wanted extension filter (i.e. `.py`)
        - ignore `list`: Default []. Files wanted to ignore (i.e. `__init__.py`)
        - sortKey `str`: Default None. Key to use to sort in `files` list

    Returns:
        `list`: Files inside given `path` param matching criteria from params.

    Examples::

        from utwrite import utilities

        p = utilities.__file__
        files = utilities.get_files_from_dir(p)
        files = [os.path.basename(f) for f in files]
        expected_files = ['auto_generate_test.py', 'headers.py', 'unittest_cases.py', 'utilities.py']

        all (e in files for e in expected_files)
        # Result: True #

        '__init__.py' in files
        # Result: True #

        files = utilities.get_files_from_dir(p, ext=['.py'], ignore=['__init__.py'])
        files = [os.path.basename(f) for f in files]
        '__init__.py' in files
        # Result: False #

        'utilities.py' in files
        # Result: True #
    """
    if os.path.isfile(path):
        path = os.path.dirname(path)

    if not os.path.isdir(path):
        raise IOError('%s: Path does not exist' % path)

    if ext:
        ext = ['.%s' % e if e[0] != '.' else e for e in ext]

    files = [f for f in os.listdir(path) if f not in ignore]
    if ext:
        files = [f for f in files if os.path.splitext(f)[-1] in ext]

    files = [os.path.join(path, f) for f in files]
    if sort_key:
        files.sort(key=sort_key)
    return files


def write_to_file(contents, fp, verbose=True) -> bool:
    r"""Write contents to a file.

    Args:
        - contents `types`: Contents wanted to write to a file
        - fp `str`: File path to write contents on.
        - verbose `bool`: Default True, prints file writting messages.

    Returns:
        `bool`: True if file successfully written, False otherwise.

    Examples::

        from utwrite import utilities

        import os, tempfile, shutil

        temp_dir = os.path.join(tempfile.gettempdir(), 'utwrite_utilities_unittest_DELETE')
        f = os.path.join(temp_dir, 'f.txt')
        if os.path.isfile(f):
           shutil.rmtree(temp_dir)

        os.path.isfile(f)
        # Result: False #

        utilities.write_to_file('utwrite.utilities.write_to_file() unittest', f, verbose=False)

        os.path.isfile(f)
        # Result: True #

        # Delete temp dir
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
    """
    try:
        ensure_path_to_file(fp)
        populate_init_files(fp, verbose=verbose)
        with open(fp, 'w') as f:
            f.write(contents)
            if verbose:
                print('%s: File written!' % fp)
        return True
    except Exception as e:
        os.remove(fp)
        print('%s: Failed to write to file!\n%s' % (fp, e))
        return False


def populate_init_files(fp, root='', verbose=True) -> None:
    r"""Add `__init__.py` files along given filepath.

    Expects project root in PYTHONPATH.

    Args:
        - fp `str`: File to
        - root `str`: Root directory for head cut off.
        - verbose `bool`: Default True, print each __init__.py file created

    Returns:
        `None`: Creates `__init__.py` files and and print info

    Examples::

        from utwrite import utilities
        import os, tempfile, shutil

        root_dir = os.path.join(tempfile.gettempdir(), 'utwrite_utilities_unittest_DELETE')
        if os.path.isdir(root_dir):
            shutil.rmtree(root_dir)

        os.path.isdir(root_dir)
        # Result: False #

        f = os.path.join(root_dir, 'd1', 'd2', 'ut_file.py')

        # Ensure path to file is created
        utilities.ensure_path_to_file(f)

        # Populate init files along the way
        utilities.populate_init_files(f, root=root_dir, verbose=False)

        os.path.isfile(os.path.join(root_dir, '__init__.py'))
        # Result: False #
        os.path.isfile(os.path.join(root_dir, 'd1', '__init__.py'))
        # Result: True #
        os.path.isfile(os.path.join(root_dir, 'd1', 'd2', '__init__.py'))
        # Result: True #

        # Delete temp dir
        if os.path.isdir(root_dir):
            shutil.rmtree(root_dir)
    """
    fp_dir = os.path.dirname(fp)
    if not root:
        # root = get_git_dir(fp) or fp_dir
        root = get_project_root_dir(fp) or fp_dir

    rel_path = os.path.relpath(fp_dir, root)
    populate_path = root
    package_path = module_path_data(fp)['path']
    in_package = True if package_path else False
    for d in rel_path.split(os.sep):
        populate_path = os.path.join(populate_path, d)
        if in_package and is_path_children(package_path, populate_path):
            continue
        init_file = os.path.join(populate_path, '__init__.py')
        if not os.path.isfile(init_file):
            open(init_file, 'w').close()
            if verbose:
                print('%s: File created!' % init_file)


def ensure_path_to_file(fp) -> None:
    r"""Create any missing directories to `fp`.

    Args:
        - fp `str`: File path to check for existence

    Returns:
        `None`: Create file if does not exist, and necessary folders.

    :Tags:
        notest, already-tested

    Examples::

        from utwrite import utilities
        import os, tempfile, shutil

        root_dir = os.path.join(tempfile.gettempdir(), 'utwrite_utilities_unittest_DELETE')
        if os.path.isdir(root_dir):
            shutil.rmtree(root_dir)

        f = os.path.join(root_dir, 'd1', 'd2', 'ut_file.py')

        os.path.isfile(f)
        # Result: False #

        # Ensure path to file is created
        utilities.ensure_path_to_file(f)

        os.path.isfile(f)
        # Result: True #

        # Delete temp dir
        if os.path.isdir(root_dir):
            shutil.rmtree(root_dir)
    """

    dir_name = os.path.dirname(fp)
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    if not os.path.isfile(fp):
        open(fp, 'w').close()


def get_test_dir(module_path) -> str:
    r"""Get a tests directory.

    Args:
        - module_path `str`: Path to a python module file to get the `tests`
          directory from.

    Returns:
        `str`: Location path for `tests` directory

    Examples::

        from utwrite import utilities
        import os, tempfile, shutil

        root_dir = os.path.join(tempfile.gettempdir(), 'utwrite_utilities_unittest_DELETE')
        if os.path.isdir(root_dir):
            shutil.rmtree(root_dir)

        git_dir = os.path.join(root_dir, '.git')
        os.makedirs(git_dir)
        f = os.path.join(root_dir, 'd1', 'd2', 'ut_file.py')

        utilities.ensure_path_to_file(f)
        test_dir = utilities.get_test_dir(f)
        os.path.realpath(test_dir) == os.path.realpath(os.path.join(root_dir, 'tests', 'd1', 'd2'))
        # Result: True #

        # Delete temp dir
        if os.path.isdir(root_dir):
            shutil.rmtree(root_dir)

    """
    if not os.path.isfile(module_path):
        print('"%s": module path not a file' % module_path)
        return ''

    mod_dir = os.path.realpath(os.path.dirname(module_path))
    project_root = mod_dir

    # - Try to get git project root
    # git_dir = get_git_dir(module_path)
    root_dir = get_project_root_dir(module_path)
    if root_dir:
        project_root = os.path.realpath(root_dir)

    rel_path = os.path.relpath(mod_dir, project_root)
    tst_dir = os.path.join(project_root, 'tests', rel_path)
    return tst_dir


def get_project_root_dir(module_path, root_identifiers=['.git', '.projectile']) -> str:
    r"""Go up directories until find a `root_identifier`.

    Args:
        - module_path `str`: Path to a python module file to get the root git
          directory from.
        - root_indentifiers `list`: Default ['.git', '.projectile']. Files or
          folders that define the root of the project

    Returns:
        `str`: Location path for Git repo root.

    :Tags:
        notest, already-tested

    Examples::

        from utwrite import utilities
        import os, tempfile, shutil

        root_dir = os.path.join(tempfile.gettempdir(), 'utwrite_utilities_unittest_DELETE')
        if os.path.isdir(root_dir):
            shutil.rmtree(root_dir)

        git_dir = os.path.join(root_dir, '.git')
        os.makedirs(git_dir)
        f = os.path.join(root_dir, 'd1', 'd2', 'ut_file.py')

        utilities.ensure_path_to_file(f)
        r = utilities.get_project_root_dir(f)

        os.path.isdir(os.path.join(r, '.git'))
        # Result: True #

        # Delete temp dir
        if os.path.isdir(root_dir):
            shutil.rmtree(root_dir)

    """
    if not os.path.isfile(module_path):
        raise RuntimeError('"%s": file given does not exist' % module_path)
    # walk up directories and look for a .git folder
    module_dir = os.path.realpath(os.path.dirname(module_path))
    directories = module_dir.split(os.path.sep)
    max_loops = 100
    while directories:
        max_loops -= 1
        if not max_loops:
            break
        p = os.path.sep.join(directories)

        roots_id = [os.path.join(p, r) for r in root_identifiers]
        found = [os.path.isdir(r) or os.path.isfile(r) for r in roots_id]
        if any(found):
            return p
        directories.pop()

    return ''


def number_increase(st, increase_by=1) -> str:
    r"""Increase trailing number is `st` by `increase_by`.

    Args:
        - st `str`: String to increase trailing number
        - increase_by `int`: Number to increase the string by

    Returns:
        `str`: Resulting string with number increase

    Examples::

        from utwrite import utilities

        utilities.number_increase('some string')
        # Result: 'some string1' #
        utilities.number_increase('1_some_string_2')
        # Result:  '1_some_string_3'#
        utilities.number_increase('my_string_005', increase_by=10)
        # Result:  'my_string_015'#
    """
    last_char = st[-1]
    try:
        float(last_char)
        max_loops = 999
        counter = 0
        idx = 0
        charLen = len(st)
        for i in range(charLen):
            max_loops -= 1
            if max_loops < 0:
                break
            idx -= 1
            if not st[idx].isnumeric():
                break
            counter += 1

        # shift idx back to last number
        idx += 1
        # increment number
        nextNum = int(st[idx:]) + increase_by
        res = st[:idx] + str(nextNum).zfill(counter)
        return res
    except:
        # - does not end with a number, just add increase_by
        return st + str(increase_by)  #'1'


def flatten_list(lst) -> list:
    r"""Flatten list given recursivelly

    Args:
        - l `list`: List to be flattened

    Returns:
        `list`: Flattened list

    Examples::

        from utwrite import utilities

        l = [0,1,[2],3,[4,[5,6,7,[8]]]]
        utilities.flatten_list(l)
        # Result:  [0, 1, 2, 3, 4, 5, 6, 7, 8] #
    """
    return_list = []
    for i in lst:
        if isinstance(i, (list, tuple)):
            return_list.extend(flatten_list(i))
        else:
            return_list.append(i)

    return return_list


def add_to_env(env_var, *paths, **kwargs) -> list:
    r"""Add given *paths to environment variable `env_var`

    NOTE if `env_var` is "PATH" also add to the sys.path variable

    Args:
        - env_var `str`: Name of environment variable to add paths to
        - *paths `str`: Files paths to add to environment variable
        - **kwargs:
            - mode `str`: Default 'head', inserts paths at the front of
              environment variable. if wanted at the end use `tail`

    Returns:
        `list`: list of bools, where True means the path was inserted, False
            means the path was already part of `env_var`

    Examples::

        import sys,os
        from utwrite import utilities
        usr_dir = os.path.realpath(os.path.expanduser('~'))
        if usr_dir in sys.path:
             sys.path.remove(usr_dir)

        utilities.add_to_env('PATH', usr_dir)
        # Result: [True] #

        usr_dir in os.environ['PATH']
        # Result: True #

        usr_dir in sys.path
        # Result: True #

        sys.path.remove(usr_dir)
        usr_dir in sys.path
        # Result: False #

        utilities.add_to_env('PATH', usr_dir)
        # Result: [True] #
        utilities.add_to_env('PATH', usr_dir)
        # Result: [False] #

    """
    mode = kwargs.get('mode', 'head')

    # Conver to system default.
    paths = [os.path.normpath(p) for p in paths]

    # Add env_var to env
    if env_var not in os.environ:
        os.environ[env_var] = os.pathsep.join(paths)
        return [True] * len(paths)

    # Update to system default
    env_paths = [os.path.normpath(ep) for ep in os.environ[env_var].split(os.pathsep)]

    add_path_func = lambda a, b: b + os.pathsep + a
    if mode.lower() == 'tail':
        add_path_func = lambda a, b: a + os.pathsep + b
    else:
        paths = paths[::-1]

    # - Add each path as necessary
    # Start all as false, switch to true as adding
    return_list = [False] * len(paths)
    for i, path in enumerate(paths):
        if path not in env_paths:
            # add path to env
            os.environ[env_var] = add_path_func(os.environ[env_var], path)
            return_list[i] = True
        if env_var == 'PATH':
            # udate sys.path
            if path not in sys.path:
                if mode.lower() == 'tail':
                    sys.path.append(path)
                else:
                    sys.path.insert(0, path)
                return_list[i] = True

    return return_list


def clean_file_path(fp) -> str:
    r"""Format given path to full real path.

    Args:
        - fp `str`: File path to format

    Returns:
        `str`: Formatted file path. If given file does not exist, return empty
          string

    Examples::

        import os
        from utwrite import utilities
        # temporarely use utw dir as home
        cur_home = os.path.expanduser('~')
        utw_path = os.path.dirname(utilities.__file__)
        os.environ['HOME'] = utw_path
        os.environ['USERPROFILE'] = utw_path
        home_contents = os.listdir(os.path.expanduser('~'))
        if home_contents:
            v = '~/%s'%home_contents[0]
            len(v) < len(utilities.clean_file_path(v))
            # Result: True #
        os.environ['HOME'] = cur_home
        os.environ['USERPROFILE'] = cur_home
    """
    fp = os.path.realpath(os.path.expanduser(fp))
    if not (os.path.isfile(fp) or os.path.isdir(fp)):
        return ''
    return fp


def maya_installation_dir(version='latest') -> str:
    r"""Find Autodesk Maya installation directory

    NOTE: currently only works on Windows

    Args:
        - version `str`, `int`: Default 'latest', uses latest installed version
          in the machine. Version to use to find Maya installation directory

    Returns:
        `str`: Autodesk Maya installation directory

    :Tags:
        notest, software-required

    Examples::

        import os
        from utwrite import utilities

        m = utilities.maya_installation_dir(version='2022')
        os.path.isdir(m)
        # Result: True #

        m
        # Result: 'C:\\Program Files\\Autodesk\\Maya2022'#

        m = utilities.maya_installation_dir()
        m
        # Result: 'C:\\Program Files\\Autodesk\\Maya2025' #

        os.path.isdir(m)
        # Result: True #

        m = utilities.maya_installation_dir(version=2022)
        os.path.isdir(m)
        # Result: True #

    """
    maya_split = 'Maya'
    program_dir = r'C:\Program Files\Autodesk'
    if sys.platform.startswith('linux'):
        maya_split = 'maya'
        program_dir = r'/usr/autodesk'

    if not os.path.isdir(program_dir):
        raise RuntimeError(
            f'Failed to find Maya (expected: {program_dir}). Ensure it is installed'
        )

    if isinstance(version, str):
        if version.isnumeric():
            version = int(version)

    if version == 'latest':
        maya_versions = [
            m.split(maya_split)[-1]
            for m in os.listdir(program_dir)
            if m.startswith(maya_split)
        ]
        maya_versions = sorted([int(m) for m in maya_versions if m.isnumeric()])
        return os.path.join(program_dir, f'{maya_split}{maya_versions[-1]}')
    else:
        p = os.path.join(program_dir, f'{maya_split}{version}')
        if not os.path.isdir(p):
            raise RuntimeError(f'"{p}": Directory not found in the system!')
        return os.path.join(program_dir, f'{maya_split}{version}')


def mayapy(version='latest') -> str:
    r"""Find mayapy.exe for a given Maya version.

    NOTE: currently only works on Windows

    Args:
        - version `str`, `int`: Default 'latest', uses latest installed version
          in the machine. Version to use to find Maya installation directory

    Returns:
        `str`: Path of mayapy executable

    :Tags:
        notest, software-required

    Examples::

        mpy = utilities.mayapy()
        mpy
        # Result: 'C:\\Program Files\\Autodesk\\Maya2025\\bin\\mayapy.exe' #

        os.path.isfile(mpy)
        # Result: True #

        mpy = utilities.mayapy(version=2022)
        mpy
        # Result: 'C:\\Program Files\\Autodesk\\Maya2022\\bin\\mayapy.exe' #

        os.path.isfile(mpy)
        # Result: True #

    """
    maya = maya_installation_dir(version=version)
    ext = '.exe'
    if sys.platform.startswith('linux'):
        ext = ''
    return os.path.realpath(os.path.join(maya, 'bin', f'mayapy{ext}'))


def module_path_data(fp) -> dict[str, str]:
    r"""Get Python module data from file.

    Args:
        fp `str`: File path to get module data from

    Returns:
        `dict`: Module data info.

    Examples::

        import utwrite.utilities

        fp = utwrite.utilities.__file__
        res = utwrite.utilities.module_path_data(fp)

        'utwrite' in res['imp']
        # Result: True #

        res['mod']
        # Result: 'utilities' #

        not res['path']
        # Result: False #

    """
    data = dict(imp='', mod='', path='')
    f = pathlib.Path(fp).resolve()
    for i in map(pathlib.Path, sys.path):
        try:
            f.relative_to(i)
        except ValueError:
            pass
        else:
            *parts, _ = f.relative_to(i).parts
            data['imp'] = '.'.join(parts)
            data['mod'] = f.stem
            data['path'] = os.path.dirname(i)

    return data


def is_path_children(chlPath, parPath) -> bool:
    r"""Check if chlPath is under parPath.

    Args:
        chlPath: `str`. Path to check if is children
        parPath: `str`. Parent path to compare to

    Returns:
        `bool`: True if is children False otherwise

    Examples::

        from utwrite.utilities import is_path_children
        import os, tempfile, shutil
        temp_dir = os.path.join(tempfile.gettempdir(), 'utwrite_utilities_unittest_DELETE')
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        temp_chl_dir = os.path.join(temp_dir,'chldir')
        os.makedirs(temp_chl_dir)
        is_path_children(temp_dir, temp_chl_dir)
        # Result: False #
        is_path_children(temp_chl_dir, temp_dir)
        # Result: True #
        shutil.rmtree(temp_dir)
    """
    try:
        pathlib.Path(chlPath).resolve().relative_to(pathlib.Path(parPath).resolve())
        return True
    except ValueError:
        return False


class RollbackImporter:
    """Used to remove imported modules from the module list.

    This allows tests to be rerun after code updates without doing any reloads.
    Original idea from: http://pyunit.sourceforge.net/notes/reloading.html

    :Examples::

        import utwrite.utilities

        r = utwrite.utilities.RollbackImporter()
        if 'math' in r.previous_modules:
            r.previous_modules.remove('math')
        'math' in r.previous_modules
        # Result: False #
        'math' in sys.modules
        # Result: True #
        r.uninstall()

        'math' in sys.modules
        # Result: False #

    """

    def __init__(self):
        """Creates an instance and installs as the global importer."""
        self.previous_modules = set(sys.modules.keys())

    def uninstall(self):
        r"""Uninstall python system modules.

        :Tags:
            notest, already-tested

        Examples::

            import utwrite.utilities

            r = utwrite.utilities.RollbackImporter()
            if 'math' in r.previous_modules:
                r.previous_modules.remove('math')
            'math' in r.previous_modules
            # Result: False #
            'math' in sys.modules
            # Result: True #
            r.uninstall()

            'math' in sys.modules
            # Result: False #
        """
        for modname in list(sys.modules.keys()):
            if modname not in self.previous_modules:
                # Force reload when modname next imported
                del sys.modules[modname]
