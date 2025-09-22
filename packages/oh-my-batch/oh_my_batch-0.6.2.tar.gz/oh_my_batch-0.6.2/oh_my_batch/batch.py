import shlex
import glob
import os

from .util import split_list, ensure_dir, expand_globs, mode_translate


class BatchMaker:

    def __init__(self):
        self._work_dirs = []
        self._script_header = []
        self._script_bottom = []
        self._command = []

    def add_work_dirs(self, *dir: str, abs=False):
        """
        Add working directories

        :param dir: Directories to work on, can be glob patterns
        :param abs: Whether to convert to absolute path
        """
        paths = expand_globs(dir)
        if abs:
            paths = [os.path.abspath(p) for p in paths]
        self._work_dirs.extend(paths)
        return self

    def filter(self, expr: str):
        """
        Filter working directories with a Python expression

        :param expr: Python expression, the variable `{workdir}, {work_dir} or {w}` is the directory path,
                     `{index} or {i}` is the index of the directory

        Example: if expr is 'os.path.exits("{workdir}/input.json")',
        then only the directories containing 'input.json' will be kept.
        """
        filtered = []
        for i, workdir in enumerate(self._work_dirs):
            expr_eval = expr.format(workdir=workdir, work_dir=workdir, w=workdir, index=i, i=i)
            if eval(expr_eval):
                filtered.append(workdir)
        self._work_dirs = filtered
        return self

    def add_header_files(self, *file: str, encoding='utf-8'):
        """
        Add script header from files

        :param file: File path
        :param encoding: File encoding
        """
        self._script_header.extend(load_files(*file, encoding=encoding))
        return self

    def add_headers(self, *header: str):
        """
        Add script header

        :param header: Header lines
        """
        self._script_header.extend(header)
        return self

    def add_bottom_files(self, *file: str, encoding='utf-8'):
        """
        Add script bottom from files

        :param file: File path
        :param encoding: File encoding
        """
        self._script_bottom.extend(load_files(*file, encoding=encoding))
        return self

    def add_bottoms(self, *bottom: str):
        """
        Add script bottom

        :param bottom: Bottom lines
        """
        self._script_bottom.extend(bottom)
        return self

    def add_cmd_files(self, *file: str, encoding='utf-8'):
        """
        Add commands from files to run under every working directory

        :param file: File path
        :param encoding: File encoding
        """
        self._command.extend(load_files(*file, encoding=encoding))
        return self

    def add_cmds(self, *cmd: str):
        """
        add commands to run under every working directory

        :param cmd: Commands to run, can be multiple
        """
        self._command.extend(cmd)
        return self

    def make(self, path: str, concurrency=0, encoding='utf-8', mode='755', purge=False):
        """
        Make batch script files from the previous setup

        :param path: Path to save batch script files, use {i} to represent index
        :param concurrency: Number of scripts to to make, default is 0, which means make one script for each working directory
        :param purge: Whether to purge existing files of the same pattern before making new ones
        :param encoding: File encoding
        :param mode: File mode, default is 755
        """
        header = '\n'.join(self._script_header)
        bottom = '\n'.join(self._script_bottom)

        if concurrency < 1:
            concurrency = len(self._work_dirs)

        if purge:
            legacy_files = glob.glob(path.format(i='*'))
            for f in legacy_files:
                print(f'Removing existing file {f}')
                os.remove(f)

        for i, work_dirs in enumerate(split_list(self._work_dirs, concurrency)):
            body = []
            work_dirs_arr = "\n".join(shlex.quote(w) for w in work_dirs)
            body.extend([
                '[ -n "$PBS_O_WORKDIR" ] && cd $PBS_O_WORKDIR  # fix PBS',
                f'WORK_DIRS=({work_dirs_arr})',
                '',
                'for WORK_DIR in "${WORK_DIRS[@]}"; do',
                'pushd $WORK_DIR',
                *self._command,
                'popd',
                'done'
            ])
            script = '\n'.join([header, *body, bottom])
            out_path = path.format(i=i)
            ensure_dir(out_path)
            with open(out_path, 'w', encoding=encoding) as f:
                f.write(script)
            os.chmod(out_path, mode_translate(str(mode)))


def load_files(*file, encoding='utf-8', raise_invalid=False):
    """
    Load files from paths

    :param files: List of file paths
    :return: List of file contents
    """
    result = []
    for file in expand_globs(file, raise_invalid=raise_invalid):
        with open(file, 'r', encoding=encoding) as f:
            result.append(f.read())
    return result
