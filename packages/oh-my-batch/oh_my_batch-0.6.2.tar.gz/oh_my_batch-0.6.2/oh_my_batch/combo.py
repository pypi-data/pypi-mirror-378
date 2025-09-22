from itertools import product
from string import Template
import traceback
import random
import json
import os

from .util import expand_globs, mode_translate, ensure_dir, shell_run

class ComboMaker:

    def __init__(self, seed=None):
        """
        ComboMaker constructor

        :param seed: Seed for random number generator
        """
        self._vars = {}
        self._broadcast_keys = []
        if seed is not None:
            random.seed(seed)
        self._combos = []

    def add_seq(self, key: str, start: int, stop: int, step: int=1):
        """
        Add a variable with sequence of integer values

        :param key: Variable name
        :param start: Start value
        :param stop: Stop value
        :param step: Step
        """
        args = list(range(start, stop, step))
        self.add_var(key, *args)
        return self

    def add_randint(self, key: str, n: int, a: int, b: int, uniq=False, seed=None):
        """
        Add a variable with random integer values

        :param key: Variable name
        :param n: Number of values
        :param a: Lower bound
        :param b: Upper bound
        :param uniq: If True, values are unique, default is False
        :param seed: Seed for random number generator
        """
        if seed is not None:
            random.seed(seed)
        if uniq:
            if b - a + 1 < n:
                raise ValueError("Not enough unique values")
            args = random.sample(range(a, b + 1), n)
        else:
            args = [random.randint(a, b) for _ in range(n)]
        self.add_var(key, *args)
        return self

    def add_rand(self, key: str, n: int, a: float, b: float, seed=None):
        """
        Add a variable with random float values

        :param key: Variable name
        :param n: Number of values
        :param a: Lower bound
        :param b: Upper bound
        :param seed: Seed for random number generator
        """
        if seed is not None:
            random.seed(seed)
        args = [random.uniform(a, b) for _ in range(n)]
        self.add_var(key, *args)
        return self

    def add_files(self, key: str, *path: str, abs=False, raise_invalid=False):
        """
        Add a variable with files by glob pattern
        For example, suppose there are 3 files named 1.txt, 2.txt, 3.txt in data directory,
        then calling add_files('DATA_FILE', 'data/*.txt') will add list ["data/1.txt", "data/2.txt", "data/3.txt"]
        to the variable DATA_FILE.

        :param key: Variable name
        :param path: Path to files, can include glob pattern
        :param abs: If True, path will be turned into absolute path
        :param raise_invalid: If True, will raise error if no file found for a glob pattern
        """
        args = expand_globs(path, raise_invalid=raise_invalid)
        if not args:
            raise ValueError(f"No files found for {path}")
        if abs:
            args = [os.path.abspath(p) for p in args]
        self.add_var(key, *args)
        return self

    def add_file_set(self, key: str, *path: str, format=None,
                     sep=' ', abs=False, raise_invalid=False):
        """
        Add a variable with files by glob pattern as one string
        Unlike add_files, this function joins the files with a delimiter.
        For example, suppose there are 1.txt, 2.txt, 3.txt in data directory,
        then calling add_file_set('DATA_FILE', 'data/*.txt') will add string "data/1.txt data/2.txt data/3.txt"
        to the variable DATA_FILE.

        :param key: Variable name
        :param path: Path to files, can include glob pattern
        :param format: the way to format the files, can be None, 'json-list','json-item'
        :param sep: Separator to join files
        :param abs: If True, path will be turned into absolute path
        :param raise_invalid: If True, will raise error if no file found for a glob pattern
        """
        args = expand_globs(path, raise_invalid=raise_invalid)
        if not args:
            raise ValueError(f"No files found for {path}")
        if abs:
            args = [os.path.abspath(p) for p in args]
        if format is None:
            value = sep.join(args)
        elif format == 'json-list':
            value = json.dumps(args)
        elif format == 'json-item':
            value = json.dumps(args).strip('[]')
        else:
            raise ValueError(f"Invalid format: {format}")
        self.add_var(key, value)
        return self

    def add_var(self, key: str, *args):
        """
        Add a variable with values

        :param key: Variable name
        :param args: Values
        """
        if key == 'i':
            raise ValueError("Variable name 'i' is reserved")
        self._vars.setdefault(key, []).extend(args)
        return self

    def shuffle(self, *keys: str, seed=None):
        """
        Shuffle variables
        :param keys: Variable names to shuffle
        :param seed: Seed for random number generator
        """
        if seed is not None:
            random.seed(seed)

        for key in keys:
            if key in self._vars:
                random.shuffle(self._vars[key])
            else:
                raise ValueError(f"Variable {key} not found")
        return self

    def sort(self, *keys: str, reverse=False):
        """
        Sort variables
        :param keys: Variable names to sort
        :param reverse: If True, sort in descending order, default is False
        """
        for key in keys:
            if key in self._vars:
                self._vars[key].sort(reverse=reverse)
            else:
                raise ValueError(f"Variable {key} not found")
        return self

    def set_broadcast(self, *keys: str):
        """
        Specify variables use broadcast strategy instead of cartesian product

        :param keys: Variable names to broadcast
        """
        for key in keys:
            if key not in self._vars:
                raise ValueError(f"Variable {key} not found")
            self._broadcast_keys.append(key)
        return self

    def make_files(self, file: str, template: str, delimiter='@', mode=None, encoding='utf-8',
                   extra_vars_from_file=None, ignore_error=False):
        """
        Make files from template against each combo
        The template file can include variables with delimiter.
        For example, if delimiter is '@', then the template file can include @var1, @var2, ...

        The destination can also include variables in string format style.
        For example, if dest is 'output/{i}-{TEMP}.txt',
        then files are saved as output/0-300K.txt, output/1-400K.txt, ...

        :param file: Path pattern to destination file
        :param template: Path to template file, the path can include variables in string format style
        :param delimiter: Delimiter for variables in template, default is '@', as '$' is popular in shell scripts
        can be changed to other character, e.g $, $$, ...
        :param mode: File mode, e.g. 755, 644, ...
        :param encoding: File encoding
        :param extra_vars_from_file: Load extra variables from json file, which can be used in template
        :param ignore_error: If True, ignore error when making files
        """
        _delimiter = delimiter

        class _Template(Template):
            delimiter = _delimiter

        combos = self._make_combos()
        for i, combo in enumerate(combos):
            try:
                _template = template.format(i=i, **combo)
                with open(_template, 'r') as f:
                    template_text = f.read()

                if extra_vars_from_file is not None:
                    _vars_file = extra_vars_from_file.format(i=i, **combo)
                    with open(_vars_file, 'r') as f:
                        extra_vars = json.load(f)
                else:
                    extra_vars = {}
                text = _Template(template_text).safe_substitute(combo, **extra_vars)
                _file = file.format(i=i, **combo)
                ensure_dir(_file)

                with open(_file, 'w', encoding=encoding) as f:
                    f.write(text)
                if mode is not None:
                    os.chmod(_file, mode_translate(str(mode)))
            except Exception as e:
                if ignore_error:
                    print(f"Error during making file, ignore: {e}")
                    traceback.print_exc()
                else:
                    raise e
        return self

    def dump_combos(self, file: str, encoding='utf-8', indent=2):
        """
        dump each combo to a json file

        This is useful for debugging or use with `--extra-vars-from-file` in `make_files`

        :param file: path pattern to json file, can include format style variables, e.g. {i}, {i:03d}, {TEMP}
        :param encoding: File encoding
        :param indent: Indentation for json file
        """
        combos = self._make_combos()
        for i, combo in enumerate(combos):
            out_path = file.format(i=i, **combo)
            ensure_dir(out_path)
            with open(out_path, 'w', encoding=encoding) as f:
                json.dump(combo, f, indent=indent)
        return self

    def print(self, *line: str, file: str = '', mode=None, encoding='utf-8'):
        """
        Print lines to a file against each combo

        :param line: Lines to print, can include format style variables, e.g. {i}, {i:03d}, {TEMP}
        :param file: File to save the output, if not provided, print to stdout
        """
        combos = self._make_combos()
        out_lines = []
        for i, combo in enumerate(combos):
            out_lines.extend(l.format(i=i, **combo) for l in line)
        out = '\n'.join(out_lines)
        if file:
            ensure_dir(file)
            with open(file, 'w', encoding=encoding) as f:
                f.write(out)
            if mode is not None:
                os.chmod(file, mode_translate(str(mode)))
        else:
            print(out)
        return self

    def run_cmd(self, cmd: str):
        """
        Run command against each combo

        For example,

        run_cmd "cp {DATA_FILE} ./path/to/workdir/{i}/data.txt"

        will copy each file in DATA_FILE to ./path/to/workdir/{i}/data.txt

        :param cmd: Command to run, can include format style variables, e.g. {i}, {i:03d}, {TEMP}
        """
        combos = self._make_combos()
        for i, combo in enumerate(combos):
            _cmd = cmd.format(i=i, **combo)
            cp = shell_run(_cmd)
            if cp.returncode != 0:
                print(cp.stdout.decode('utf-8'))
                print(cp.stderr.decode('utf-8'))
                raise RuntimeError(f"Failed to run command: {_cmd}")
        return self

    def show_combos(self):
        """
        Show all combos in a human-readable format for debugging
        """
        combos = self._make_combos()
        if not combos:
            print("No combos")
        keys = combos[0].keys()

        for i, combo in enumerate(combos):
            print(f"> Combo {i}:")
            for k in keys:
                v = str(combo[k])
                if '\n' in v:
                    v = f"\n{v}"
                print(f"@{k}: {v}")

    def done(self, debug=False):
        """
        End of command chain
        :param debug: If True, show all combos for debugging
        """
        if debug:
            self.show_combos()

    def _make_combos(self):
        if not self._vars:
            return self._combos

        broadcast_vars = {}

        for k in self._broadcast_keys:
            broadcast_vars[k] = self._vars[k]
            del self._vars[k]

        keys = self._vars.keys()
        values_list = product(*self._vars.values())

        combos = [ dict(zip(keys, values)) for values in values_list ]
        for i, combo in enumerate(combos):
            for k, v in broadcast_vars.items():
                combo[k] = v[i % len(v)]
        self._combos.extend(combos)
        self._vars = {}
        self._broadcast_keys = []
        return self._combos
