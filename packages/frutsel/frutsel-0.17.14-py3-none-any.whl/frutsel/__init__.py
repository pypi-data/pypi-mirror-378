#!/usr/bin/env python3

# This is frutsel.py, the reference implementation of the Frutsel DBMS.
# A copy-pastable, human readable, scalable database with an easy API.

# Copyright (C) 2021-2025 maveobi path-fanfare-canon@duck.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from logging import getLogger, StreamHandler, DEBUG, INFO, WARNING
from datetime import datetime, timedelta
from subprocess import run, DEVNULL
from functools import cache
from hashlib import sha256
import multiprocessing
import cProfile
import argparse
import pathlib
import os.path
import inspect
import random
import codecs
import pstats
import shutil
import base64
import glob
import stat
import lzma
import time
import sys
import os
import io

# These libraries may be useful in lambda expressions created from command line arguments.
import re  # noqa

# This is for command line output.
from pprint import pprint

# These are imported to define JSON translation rules.
import decimal  # noqa

from frutsel.vendor import jsonpickle

try:
    # Posix based file locking (Linux, MacOS, etc.)
    #   Only allows locking on writable files, might cause
    #   strange results for reading.
    import fcntl
    import os

    def lock_file(f):
        if f.writable():
            fcntl.lockf(f, fcntl.LOCK_EX)

    def unlock_file(f):
        if f.writable():
            fcntl.lockf(f, fcntl.LOCK_UN)
except ModuleNotFoundError:
    # Windows file locking
    import msvcrt
    import os

    def file_size(f):
        return os.path.getsize(os.path.realpath(f.name))

    def lock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_RLCK, file_size(f))

    def unlock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, file_size(f))


# https://semver.org/
FRUTSEL_VERSION = ''

frutsel_logger = getLogger('frutsel')
frutsel_logger.addHandler(StreamHandler())
META_EMBEDDED_DATA_SIZE_THRESHOLD = 1024 * 1024
_FILENAME_SAFE_CHARS = '1234567890-_+()@abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

# See http://be-n.com/spw/you-can-list-a-million-files-in-a-directory-but-not-with-ls.html
MAX_ITEMS_PER_FOLDER = 256

MIN_MAINTENANCE_INTERVAL = timedelta(minutes=1)

# This singleton is initialised further down. Mentioned here as well, to keep a clear view of module globals.
_json_encoder = None


# Public constants
class _FrutselConstant:
    def __init__(self, string):
        self.string = string

    def __str__(self):
        return self.string


ANY = _FrutselConstant('ANY')
MIN = _FrutselConstant('MIN')
MAX = _FrutselConstant('MAX')


class FrutselError(Exception):
    pass


class JSONEncoder:
    def encode(self, o):
        return jsonpickle.encode(o, use_base85=True, indent=2)


_json_encoder = JSONEncoder()


class Document:
    def __init__(self, db, data, tags: set = set(), document_datetime: datetime = None):
        self._db = db
        self._data = data

        self._tags = Document._validate_tags(tags)
        self._looked_in_tagfiles_for_tags = True
        self.datetime = document_datetime

    def _validate_tags(tags):
        if not tags:
            return set()
        if type(tags) not in (set, list, tuple):
            raise FrutselError(f'tags should be a set, list or tuple, not {type(tags).__name__}')
        for tag in tags:
            if not isinstance(tag, str):
                raise FrutselError(f'Tag "{tag}" should be of type str, not {type(tag).__name__}')
        return set(tags) - set(('',))

    @property
    def tags(self):
        if not self._looked_in_tagfiles_for_tags:
            frutsel_logger.debug(f'Looking in tagfiles for tags for {self.metafile_checksum}.')
            for tagfile in self._db._get_all_tagfiles():
                if self.metafile_checksum in tagfile.metafile_checksums:
                    self._tags.add(tagfile.name)
            self._looked_in_tagfiles_for_tags = True
        return self._tags

    @property
    def timestamp(self):
        if self.datetime:
            return self.datetime.timestamp()

    def _serialise(self):
        document_dict = {}
        datafile_absolute_filepath = None

        data_is_json_serialized = False
        data_is_raw_bytes = False
        try:
            data_json = _json_encoder.encode(self.data)
            data_is_json_serialized = True
        except TypeError:
            # Not JSON serializable.
            if isinstance(self.data, bytes):
                data_is_raw_bytes = True
            else:
                raise FrutselError(f'Data ({type(self.data)} length {len(self.data)}) is not raw bytes and is not JSON serializable.')
        if data_is_json_serialized:
            if len(data_json) < META_EMBEDDED_DATA_SIZE_THRESHOLD:
                # Small JSON document: embed in metadata
                document_dict['data'] = self.data
                del data_json
            else:
                # Large JSON document: write to datafile
                self._datafile_checksum, datafile_absolute_filepath = self._db._write_anonymous_file('data', data_json.encode(), compress=True, extension='json')
                document_dict['datafile'] = self._datafile_checksum
                document_dict['data_encoding'] = 'json'
                del self._data
        elif data_is_raw_bytes:
            if len(self.data) < META_EMBEDDED_DATA_SIZE_THRESHOLD:
                # Few bytes: embed in metadata, base64 encoded
                document_dict['data'] = base64.b64encode(self.data).decode()
                document_dict['data_encoding'] = 'base64'
            else:
                # Many bytes: write to datafile
                self._datafile_checksum, datafile_absolute_filepath = self._db._write_anonymous_file('data', self.data, compress=True, extension='')
                document_dict['datafile'] = self._datafile_checksum
                del self._data

        # if self.tags:
        #    document_dict['tags'] = sorted(list(self.tags))

        if self.datetime:
            document_dict['dt'] = self.timestamp

        return (_json_encoder.encode(document_dict), datafile_absolute_filepath)

    def from_metafile_checksum(db, metafile_checksum):
        return Document._from_file(db, folder=os.path.join(db.root_path, 'meta'), name=metafile_checksum)

    def from_path(db, absolute_file_path):
        return Document._from_file(db, absolute_file_path)

    def _from_file(db, *args, **kwargs):
        metafile = _FrutselFile(*args, **kwargs)
        try:
            document_dict = metafile.contents
        except FileNotFoundError:
            frutsel_logger.debug(f'{metafile.path} not found.')
            return None
        except EOFError:
            frutsel_logger.error(f'Metadata file {metafile.path} seems corrupt: unexpected end of file.')
            return None

        try:
            metafile_checksum = metafile.get_name(strip=os.path.join(db.root_path, 'meta'))
        except Exception:
            frutsel_logger.error(f'Failed to get checksum for metadata file {metafile.path}')
            return None

        def err(msg):
            if metafile.check_checksum(strip_name_prefix=os.path.join(db.root_path, 'meta')):
                frutsel_logger.error(f'Incompatible metadata file {metafile.path}: {msg}')
            else:
                frutsel_logger.error(f'Corrupt metadata file {metafile.path}: {msg}')
            return None

        if not isinstance(document_dict, dict):
            return err(f'unexpectedly has {type(document_dict).__name__} contents instead of a dict.')
        try:
            # Backward compatibility: Read tags from (old) metafile, then append tags from (new) tag files lazily.
            tags = set(document_dict.get('tags', set()))
        except Exception:
            return err('failed to get tags.')

        try:
            document_datetime_timestamp = document_dict.get('dt')
            document_datetime = None
            if document_datetime_timestamp:
                document_datetime = datetime.fromtimestamp(document_datetime_timestamp)
            doc = Document(db, document_dict.get('data'), tags=tags, document_datetime=document_datetime)
            doc._datafile_checksum = document_dict.get('datafile')
            doc._data_encoding = document_dict.get('data_encoding')
            doc._metafile = metafile
            doc.metafile_checksum = metafile_checksum
            doc._looked_in_tagfiles_for_tags = False
            return doc
        except Exception as ex:
            return err(f'{ex} while loading.')

    @property
    def data(self):
        if hasattr(self, '_datafile_checksum') and self._datafile_checksum:
            # Load data lazily
            opened_file = _FrutselFile(folder=os.path.join(self._db.root_path, 'data'), name=self._datafile_checksum)
            try:
                return opened_file.contents
            except Exception as ex:
                if isinstance(ex, EOFError):
                    frutsel_logger.error(f'Data file {opened_file.path} seems corrupt. You may want to remove it as well as metadata file {self._metafile.path}.')
                elif isinstance(ex, FileNotFoundError):
                    frutsel_logger.error(f'Data file {opened_file.path} not found. You may want to remove metadata file {self._metafile.path}.')
                else:
                    raise ex
                return None
        elif hasattr(self, '_data'):
            if hasattr(self, '_data_encoding') and self._data_encoding == 'base64':
                return base64.b64decode(self._data.encode())
            else:
                return self._data

    def add_tags(self, *tags):
        tags = Document._validate_tags(tags)
        frutsel_logger.debug(f'Adding tags {tags} to {self.metafile_checksum}')

        touched_files = []
        for tag_index_filepath in self._db._add_tags_to_document(self.metafile_checksum, tags):
            touched_files.append(tag_index_filepath)

        if self._db.git_autocommit:
            self._db._git('add', *touched_files)
            self._db._git('commit', '-m', f'Added tags to {self.metafile_checksum}', *touched_files)

    def delete(self):
        # Not removing data file; it may be referenced from another metadata file.
        # TODO: make sure that orphaned data files are removed in maintenance round.
        metafile_file_path = self._metafile.path
        frutsel_logger.debug(f'Deleting {metafile_file_path}.')
        try:
            # Doing a git rm dry run to see if the file is managed by git.
            if self._db._git('rm', '--dry-run', '-f', metafile_file_path) and self._db.git_autocommit:
                self._db._git('rm', '-f', metafile_file_path)
                self._db._git('commit', '-m', f'Removed {self.metafile_checksum}', metafile_file_path)
                return
        except FileNotFoundError as ex:
            frutsel_logger.debug(f'{ex} while trying to delete {metafile_file_path}.')
            pass
        except:  # noqa
            frutsel_logger.exception(f'Error while trying to remove metadata file {metafile_file_path}.')
        # Otherwise, do an ordinary delete.
        try:
            os.remove(metafile_file_path)
        except FileNotFoundError:
            frutsel_logger.debug(f"Trying to delete {metafile_file_path}, but it's already gone...")
            pass
        except:  # noqa
            frutsel_logger.exception(f'Error while trying to remove metadata file {metafile_file_path}.')

    def __repr__(self):
        data_representation = repr(self.data)
        if len(data_representation) > 42:
            data_representation = data_representation[: 42 - 3] + '...'
        init_args = f'data={data_representation}'
        if self.tags:
            init_args += f', tags={self.tags!r}'
        if self.datetime:
            init_args += f', document_datetime={self.datetime!r}'
        return f'frutsel.Document({init_args})'

    def __str__(self):
        result = f'Document with metadata checksum {self.metafile_checksum}'
        if self.datetime:
            result += f'\n\tdatetime: {self.datetime}'
        if hasattr(self, '_datafile_checksum') and self._datafile_checksum:
            result += f'\n\tdatafile checksum: {self._datafile_checksum}'
        else:
            result += f'\n\tdata: {self._data}'

        if self.tags:
            result += '\n\ttags: '
            result += ','.join(sorted(self.tags))
        result += '\n'
        return result


class FrutselDB:
    """FrutselDB can be used safely in these ways:

    with FrutselDB() as db:
        db.get()

    db = FrutselDB()
    db.get()
    del db

    db = FrutselDB()
    db.get()
    db.close()

    FrutselDB(async_puts=False).put('foo')
    """

    def __init__(self, root_path, do_maintenance=False, logging_level=WARNING, async_puts=True, support_complex_types=None, git_autocommit=False):
        """Instantiate a new FrutselDB

        root_path: The path to the top directory of the database.
        do_maintenance: Enable periodic maintenance (during query handling), cleaning up and repairing the database.
        logging_level: Logging level (using standard library logging module).
        async_puts: Enable writing Documents to disk in background threads, allowing to use put(data, blocking=False).
        """
        frutsel_logger.setLevel(level=logging_level)
        root_path = os.path.expanduser(root_path)
        root_path = os.path.abspath(root_path)
        root_path = os.path.normpath(root_path)
        root_path = os.path.normcase(root_path)
        self.root_path = root_path
        try:
            frutsel_sourcefile_path = inspect.getsourcefile(type(self))
            frutsel_backupfile_path = os.path.join(root_path, 'frutsel.py')
            do_sourcefile_backup = True
            if os.path.exists(frutsel_backupfile_path):
                # TODO: Only update if our version is higher than the backup version.
                with open(frutsel_sourcefile_path, 'rb') as f:
                    frutsel_sourcefile_checksum = sha256(f.read()).hexdigest()
                with open(frutsel_backupfile_path, 'rb') as f:
                    frutsel_backupfile_checksum = sha256(f.read()).hexdigest()
                if frutsel_sourcefile_checksum == frutsel_backupfile_checksum:
                    frutsel_logger.debug(f'{frutsel_backupfile_path} is up-to-date.')
                    do_sourcefile_backup = False
            if do_sourcefile_backup:
                frutsel_logger.debug(f'Copying {frutsel_sourcefile_path} to {frutsel_backupfile_path}.')
                os.makedirs(self.root_path, exist_ok=True)
                try:
                    shutil.copyfile(frutsel_sourcefile_path, frutsel_backupfile_path)
                    os.chmod(frutsel_backupfile_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                except shutil.SameFileError:
                    pass
                except Exception as ex:
                    frutsel_logger.debug(f'{ex} while trying to backup {frutsel_sourcefile_path} to {frutsel_backupfile_path}.')
        except Exception:
            pass

        # TODO: Detect if complex types were written to disk before. Warn if support is disabled afterwards.
        # TODO: Provide a conversion function for old (now incompatible) databases?
        if support_complex_types:
            raise FrutselError('support_complex_types is removed from this version of FrutselDB.')

        self.git_autocommit = False
        # We let subprocess.run() throw a FileNotFoundError when git is not installed.
        if git_autocommit:
            if self._git('rev-parse', '--git-dir', print_output=False, error_on_exit_code=False):
                self.git_autocommit = True
            else:
                # If autocommit was requested, but the DB root is not (in) a git repo: raise an exception.
                raise FrutselError(f'git autocommit was requested, but {root_path} is not in a git repository')
        if self.git_autocommit and do_sourcefile_backup:
            self._git('add', frutsel_backupfile_path)
            self._git('commit', '-m', 'Added/updated frutsel.py', frutsel_backupfile_path)

        if do_maintenance:
            self._last_maintenance_started = datetime.now()
        else:
            self._last_maintenance_started = datetime.max

        self._data_queue = multiprocessing.Queue()
        self._workers = []
        if async_puts:
            if sys.platform == 'linux':
                for _ in range(min(os.cpu_count(), 3)):
                    worker = multiprocessing.Process(target=self._process_puts, args=(self._data_queue,))
                    worker.start()
                    self._workers.append(worker)
                frutsel_logger.debug('Worker pool created. Ready to accept commands.')
            else:
                # TODO: This does seem solvable.
                frutsel_logger.warning(f'Async puts requested, but not supported on {sys.platform}. Will do put() synchronously instead.')
        else:
            frutsel_logger.debug('Using slow synchronous writes because worker processes are disabled. Ready to accept commands.')

    def _process_puts(self, data_queue):
        # frutsel_logger.debug('Worker started.')
        for data, tags, document_datetime in iter(data_queue.get, 'STOP'):
            self._create_new_document(data, tags=tags, document_datetime=document_datetime)
        # frutsel_logger.debug('Got a stop signal. Worker stopping.')

    def close(self):
        if hasattr(self, '_workers') and self._workers:
            frutsel_logger.debug('Stopping worker pool.')
            for _ in range(len(self._workers)):
                # frutsel_logger.debug('Sending a stop signal to workers.')
                try:
                    self._data_queue.put('STOP')
                except (ValueError, AssertionError):
                    # Already closed.
                    # Before Python 3.8, this is an AssertionError,
                    # after that a ValueError.
                    pass
            # for worker in self._workers:
            #    try:
            #        worker.join()
            #    except AssertionError:
            #        pass

        if hasattr(self, '_data_queue') and self._data_queue:
            frutsel_logger.debug('Closing data queue.')
            try:
                self._data_queue.close()
            except ValueError:
                # Already closed.
                pass

            self._data_queue.join_thread()

        frutsel_logger.debug('Database closed.')

    def sync(self):
        """
        Waits for the internal data queue to be reportedly empty. This should give some indication of data being written to disk.
        Because of multithreading/multiprocessing semantics, this is not reliable. (See https://docs.python.org/3.8/library/multiprocessing.html#multiprocessing.Queue.empty)
        """
        for retry in range(10):
            while not self._data_queue.empty():
                time.sleep(0.1)
            # This is arbitrary, but shows in tests to help significantly.
            # TODO: Write markers to the _data_queue until all workers report to have seen it.
            time.sleep(0.5)

    def git_sync(self, print_output=None):
        """
        Does a git pull and a git push.
        """
        self._git('pull', print_output=print_output)
        self._git('push', print_output=print_output)
        self.maintenance()

    def _git(self, *args, print_output=None, error_on_exit_code=True):
        if print_output or frutsel_logger.getEffectiveLevel() == DEBUG:
            stdout, stderr = (sys.stdout, sys.stderr)
        else:
            stdout = stderr = DEVNULL
        completed_process = run(['git', '-C', self.root_path, *args], stdout=stdout, stderr=stderr)
        if completed_process.returncode != 0 and error_on_exit_code:
            error_msg = f'git {" ".join(args)} returned exit code {completed_process.returncode}'
            if args[0] == 'commit' or '--dry-run' in args:
                # Frequently this is git commit seeing no difference between two commits.
                frutsel_logger.debug(error_msg)
            else:
                raise FrutselError(error_msg)
        return completed_process.returncode == 0

    # __enter__() and __exit__() implement a context manager.
    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()
        return False

    def __del__(self):
        self.close()

    def _create_new_document(self, data, tags, document_datetime):
        doc = Document(self, data, tags=tags, document_datetime=document_datetime)

        # WARNING: Only at this point can we know the Document's meta checksum.
        #          After deserialisation, we have to set this attribute again in from_path().
        meta_bytes, datafile_absolute_filepath = doc._serialise()
        meta_bytes = meta_bytes.encode()
        doc.metafile_checksum, metafile_absolute_filepath = self._write_anonymous_file('meta', meta_bytes, compress=False, extension='json')
        touched_files = [
            metafile_absolute_filepath,
        ]
        if datafile_absolute_filepath:
            touched_files.append(datafile_absolute_filepath)

        # Update tag files for this Document.
        for tag_index_filepath in self._add_tags_to_document(doc.metafile_checksum, doc.tags):
            touched_files.append(tag_index_filepath)

        # TODO: Index Document on datetime.

        if self.git_autocommit:
            self._git('add', *touched_files)
            self._git('commit', '-m', f'Added {doc.metafile_checksum}', *touched_files)
        return doc.metafile_checksum

    def _add_tags_to_document(self, metafile_checksum, tags):
        for tag in tags:
            try:
                checksums_of_metafiles_with_this_tag = set(self._read_named_file('tags', tag, 'txt').decode().split('\n'))
            except FileNotFoundError:
                checksums_of_metafiles_with_this_tag = set()
            checksums_of_metafiles_with_this_tag.add(metafile_checksum)
            tag_index_filepath = self._write_named_file('tags', tag, 'txt', '\n'.join(sorted(checksums_of_metafiles_with_this_tag)).encode(), compress=False)
            # print(f'Written {metafile_checksum} to {tag_index_filepath}.')
            yield tag_index_filepath

    def _get_all_tagfiles(self):
        db_subdir = 'tags'
        for dirname, dirnames, filenames in os.walk(os.path.join(self.root_path, db_subdir)):
            for filename in filenames:
                yield _TagFile(dirname, filename, db=self)

    @property
    def tags(self):
        for tag in self._get_all_tagfiles():
            yield tag.name

    @property
    def kv(self):
        return FrutselKeyValue(self)

    def _write_named_file(self, db_folder, name, extension, contents, compress):
        folder_path = os.path.join(self.root_path, db_folder)
        written_file = _NamedFrutselFile(folder_path, contents, name, extension=extension, compress=compress)
        return written_file.path

    def _write_anonymous_file(self, db_folder, contents, compress, extension):
        folder_path = os.path.join(self.root_path, db_folder)
        written_file = _AnonymousFrutselFile(folder_path, contents, extension, compress=compress)
        checksum = written_file.get_name()
        return (checksum, written_file.path)

    def _read_named_file(self, db_folder, name, extension):
        filename = '.'.join(filter(bool, (name, extension)))
        return _FrutselFile(self.root_path, db_folder, filename).contents

    def put(self, data, tags=set(), document_datetime=None, blocking=True):
        """Put data in the database.

        The database file structure has a few important advantages, but speed in querying is not one of them.
        To increase performance in queries, you should use tags and document_datetime.
        To increase performance in putting data into the database, you can make this function asynchronous using the parameter blocking=False (and using a database instance with async_puts=True).
        data can be a variety of Python objects. FrutselDB saves data in JSON format, so at least JSON supported types are supported:
        dict
        list
        tuple
        str
        int
        float
        int- & float-derived Enums
        True
        False
        None
        On top of this, FrutselDB supports bytes.
        """
        if document_datetime is not None and type(document_datetime) not in (bool, datetime, None):
            raise FrutselError(f'document_datetime should be bool or datetime.datetime, not {type(document_datetime).__name__}')
        if document_datetime is True:
            document_datetime = datetime.now()
        if blocking or not self._workers:
            return self._create_new_document(data, tags=tags, document_datetime=document_datetime)
        else:
            self._data_queue.put((data, tags, document_datetime))
            return None

    def get(self, *args, **kwargs):
        """Perform a Query and return the ResultSet.

        If one Query object is given as parameter, that query is performed.
        Otherwise, all arguments are passed to the constructor of Query.
        In other words, this function has two signatures: one with a single Query object as parameter, and one that equals the constructor of Query.
        Here are two equal examples:
        db.get(And(Query(tags=['foo'])))
        db.get(tags=['foo'])
        """
        if len(args) == 1 and isinstance(args[0], Query) and not kwargs:
            query = args[0]
        else:
            query = Query(*args, **kwargs)

        return ResultSet(query, self)

    def get_one(self, *args, **kwargs):
        """Perform a Query and return the first Document from the ResultSet, if any.

        For parameters, see get()
        """
        for doc in self.get(*args, **kwargs):
            return doc

    def delete(self, *args, **kwargs):
        """Perform a Query and delete all Documents in the ResultSet.

        If one Query object is given as parameter, that query is performed.
        Otherwise, all arguments are passed to the constructor of Query.
        In other words, this function has two signatures: one with a single Query object as parameter, and one that equals the constructor of Query.
        Here are two equal examples:
        db.delete(And(Query(tags=['foo'])))
        db.delete(tags=['foo'])
        """
        for doc in self.get(*args, **kwargs):
            doc.delete()

    def rsync(self, remote_path):
        # TODO: replace rsync, as it is fault sensitive.
        remote_path = os.path.normcase(os.path.normpath(remote_path))
        cmd = ['rsync', '-r']
        if frutsel_logger.isEnabledFor(DEBUG):
            cmd.append('-v')
        run(cmd + [os.path.join(remote_path, '*'), self.root_path])
        run(cmd + [*glob.glob(os.path.join(self.root_path, '*')), remote_path])

    def checksums(self):
        sums = []
        for db_subdir in ('meta', 'data', 'tags', 'kv'):
            for dirname, dirnames, filenames in os.walk(os.path.join(self.root_path, db_subdir)):
                for filename in filenames:
                    metafile = _FrutselFile(dirname, filename)
                    metafile_checksum = metafile.get_name(strip=os.path.join(self.root_path, db_subdir))
                    sums.append(metafile_checksum)
        return sorted(sums)

    def maintenance(self):
        frutsel_logger.debug('Starting forced maintenance round.')
        self._last_maintenance_started = datetime.min
        for _ in self.get():
            pass
        frutsel_logger.debug('Forced maintenance round done.')


class Query:
    # TODO: Serialise and save Query object (part)s. (Always? Or on getting query_object.checksum?) Make Query objects available from their checksum. (Query.from_checksum())

    def __init__(self, metafile_checksum=None, tags=ANY, exact_tags=ANY, filter_function=None, min_datetime=MIN, max_datetime=MAX):
        if metafile_checksum:
            if any(((tags not in (ANY, None, set())), (exact_tags not in (ANY, None, set())), filter_function, (min_datetime not in (MIN, None)), (max_datetime not in (MAX, None)))):
                raise FrutselError('Either a specific metadata checksum should be given, or search criteria.')
            if not isinstance(metafile_checksum, str):
                raise FrutselError(f'Expected a metafile_checksum of type str, got {type(metafile_checksum).__name__}.')
        tags_given = tags not in (ANY, None)
        if tags_given and type(tags) not in (set, list, tuple):
            raise FrutselError(f'tags should be a set, list or tuple, not {type(tags).__name__}')
        self._match_tags_exactly = exact_tags != ANY
        if self._match_tags_exactly and type(exact_tags) not in (type(None), set, list, tuple):
            raise FrutselError(f'exact_tags should be None, a set, list or tuple, not {type(exact_tags).__name__}')
        if tags_given and self._match_tags_exactly:
            raise FrutselError('Both tags and exact_tags are set.')

        self.metafile_checksum = metafile_checksum
        if self._match_tags_exactly:
            if exact_tags is None:
                self.tags = set()
            else:
                self.tags = set(exact_tags)
        else:
            self.tags = tags
            if self.tags not in (ANY, None):
                self.tags = set(self.tags)
        self.filter_function = filter_function
        self.min_datetime = min_datetime
        self.max_datetime = max_datetime

    def _test_document(self, document, check_tags):
        # frutsel_logger.debug(f'Testing document {document} against query {self}.')
        if self.metafile_checksum:
            # frutsel_logger.debug(f'Match is {self.metafile_checksum == document.metafile_checksum} based on metafile_checksum.')
            return self.metafile_checksum == document.metafile_checksum
        else:
            if check_tags and self.tags != ANY:
                if self._match_tags_exactly:
                    if self.tags != document.tags:
                        # frutsel_logger.debug(f'Checking tags is enabled, tags is not ANY and {self.tags} is not == {document.tags}.')
                        return False
                elif self.tags:
                    if not self.tags <= document.tags:
                        # frutsel_logger.debug(f'Checking tags is enabled, tags is not in (ANY, None) and {self.tags} is not <= {document.tags}.')
                        return False

            if document.datetime and ((self.min_datetime not in (None, MIN) and document.datetime < self.min_datetime) or (self.max_datetime not in (None, MAX) and document.datetime > self.max_datetime)):
                # frutsel_logger.debug(f'{document.datetime} is outside {self.min_datetime} - {self.max_datetime}.')
                return False

            if self.filter_function is not None and not bool(self.filter_function(document)):
                # frutsel_logger.debug(f'filter function returned {self.filter_function(document)}')
                return False

            # frutsel_logger.debug('Document matches!')
            return True

    def _get_tags(self):
        # Check if self.tags is not something like ANY or None
        if isinstance(self.tags, set):
            return self.tags

    def __str__(self):
        if self.metafile_checksum:
            description = f'the document with metafile checksum {self.metafile_checksum}'
        else:
            description = 'all documents'
            if self._match_tags_exactly:
                if self.tags != ANY:
                    if self.tags:
                        description += ' exactly tagged '
                        description += ','.join(sorted(self.tags))
                    else:
                        description += ' without tags '
            else:
                if self.tags not in (ANY, None):
                    description += ' tagged '
                    description += ','.join(sorted(self.tags))
            if self.min_datetime not in (None, MIN) and self.max_datetime not in (None, MAX):
                description += f' between {self.min_datetime} and {self.max_datetime}'
            elif self.min_datetime not in (None, MIN):
                description += f' since {self.min_datetime}'
            elif self.max_datetime not in (None, MAX):
                description += f' until {self.max_datetime}'
            if self.filter_function:
                try:
                    source = inspect.getsource(self.filter_function).strip()
                except OSError:
                    # could not get source code
                    source = 'filter function'
                description += f' for which {source} returns True'
        return description


class _ComplexQuery(Query):
    def __init__(self, *subqueries):
        if len(subqueries) == 1 and type(subqueries[0]) in (set, list, tuple):
            subqueries = subqueries[0]
        for subquery in subqueries:
            if not isinstance(subquery, Query):
                raise TypeError(f'{type(self).__name__} subquery is of type {type(subquery).__name__}. Expected an instance of Query.')
        self.subqueries = subqueries

    def _get_tags(self):
        all_subquery_tags = set()
        for subquery in self.subqueries:
            subquery_tags = subquery._get_tags()
            if subquery_tags and not isinstance(subquery, Not):
                all_subquery_tags |= subquery_tags
            else:
                return None
        return all_subquery_tags

    def _format_subquery(self, subquery):
        if isinstance(subquery, _ComplexQuery) and len(subquery.subqueries) > 1:
            return f'({subquery})'
        else:
            return str(subquery)


class Or(_ComplexQuery):
    def _test_document(self, document, check_tags):
        return any(map(lambda q: q._test_document(document, check_tags), self.subqueries))

    def __str__(self):
        return ' or '.join(map(self._format_subquery, self.subqueries))

    def _get_child_query_metafile_checksums(self):
        checksums = set()
        for child in self.subqueries:
            child_type = type(child)
            if child_type == Query:
                checksums.add(child.metafile_checksum)
            elif child_type == Or:
                checksums |= child._get_child_query_metafile_checksums()
            else:
                return None
        if None not in checksums:
            return checksums


class And(_ComplexQuery):
    def _test_document(self, document, check_tags):
        return all(map(lambda q: q._test_document(document, check_tags), self.subqueries))

    def __str__(self):
        return ' and '.join(map(self._format_subquery, self.subqueries))


class Xor(_ComplexQuery):
    def _test_document(self, document, check_tags):
        return sum(map(lambda q: int(q._test_document(document, check_tags)), self.subqueries)) == 1

    def __str__(self):
        return ' xor '.join(map(self._format_subquery, self.subqueries))


class Not(_ComplexQuery):
    def _test_document(self, document, check_tags):
        return not any(map(lambda q: q._test_document(document, check_tags), self.subqueries))

    def __str__(self):
        return f'none of {", ".join(map(self._format_subquery, self.subqueries))}'


class ResultSet:
    def __init__(self, query, db):
        self._query = query
        self._db = db
        query_tags = query._get_tags()
        child_checksums = isinstance(query, Or) and query._get_child_query_metafile_checksums()

        if type(query) is Query and query.metafile_checksum:
            self._stage_1_checksums = [
                query.metafile_checksum,
            ]
            frutsel_logger.debug(f'Speeding up query "{query}" with 1 metafile checksum.')
        elif child_checksums:
            self._stage_1_checksums = child_checksums
            frutsel_logger.debug(f'Speeding up query "{query}" with {len(child_checksums)} metafile checksums.')
        elif query_tags:
            self._stage_1_checksums = set()
            for tag in query_tags:
                try:
                    self._stage_1_checksums |= set(db._read_named_file('tags', tag, 'txt').decode().split('\n'))
                except FileNotFoundError:
                    # No Documents with this tag.
                    self._stage_1_checksums = None
                    break
            if self._stage_1_checksums:
                frutsel_logger.debug(f'Speeding up query "{query}" with indexed tags: {", ".join(query_tags)}.')
            else:
                frutsel_logger.debug(f'Failed to speed up query "{query}" with indexed tags: {", ".join(query_tags)}.')
        else:
            self._stage_1_checksums = None

    def __iter__(self):
        return ResultSetIterator(self._query, self._stage_1_checksums, self._db)


class ResultSetIterator:
    def __init__(self, query, stage_1_checksums, db):
        self._query = query
        self._db = db

        # These are used for maintenance.
        self._reconstructed_tag_indices = dict()
        self._changed_files = set()

        now = datetime.now()
        self._do_maintenance = db._last_maintenance_started < (now - MIN_MAINTENANCE_INTERVAL)
        if self._do_maintenance:
            db._last_maintenance_started = now
            frutsel_logger.info('Doing maintenance on database.')
        self._stage_1_checksums = stage_1_checksums
        if (not self._do_maintenance) and self._stage_1_checksums:
            self._stage_1_checksums_iterator = self._stage_1_checksums.__iter__()
        else:
            self._file_iterator = os.walk(os.path.join(self._db.root_path, 'meta'))
            self._stage_1_checksums_iterator = None

    def __iter__(self):
        return self

    def __next__(self):
        if self._stage_1_checksums_iterator:
            doc = self._next_stage_1_checksum()
        else:
            doc = self._next_file()
        return doc

    def _next_file(self):
        while True:
            try:
                filename = self._current_dir_filenames.__next__()
            except (AttributeError, StopIteration):
                try:
                    self._dirname, dirnames, filenames = self._file_iterator.__next__()
                    # By walking the file system in a random order, we may get performance and completeness improvements.
                    # - If the database is distributed over multiple physical media, we may use media in parallel when doing concurrent walks.
                    # - Maintenance will complete sooner in cases where walks end before all files are touched.
                    random.shuffle(dirnames)
                    self._current_dir_filenames = iter(filenames)
                except StopIteration:
                    if self._do_maintenance:
                        if self._db.git_autocommit:
                            self._db._git('commit', '-m', 'Done maintenance.', *self._changed_files)

                        frutsel_logger.info('Done doing maintenance on database.')
                    raise StopIteration()
                continue

            absolute_file_path = os.path.join(self._dirname, filename)
            doc = Document.from_path(self._db, absolute_file_path=absolute_file_path)
            if self._do_maintenance:
                # Maintenance! Doing this during iteration over a ResultSet has the following effects:
                # - Some queries will be slower, because of the extra operations per file and because
                #   stage 1 filtering is disabled (forcing us to iterate over all files in the database).
                # - No need for a maintenance thread. This is more in line with the intended use of FrutselDB:
                #   Focus on fast data storage. Move complexity to the query phase. Also, low traffic
                #   applications will not need to keep busy doing maintenance if they mainly store data.
                # - Overall resource usage is lower because a Document only needs to be loaded once
                if not doc:
                    raise FrutselError(f'Loading {absolute_file_path} gave {doc}.')

                # Write doc back to disk, to apply changes in file structure, if any. (For instance, separating tags from metafiles.)
                old_metafile_checksum = doc.metafile_checksum
                new_metafile_checksum = self._db._create_new_document(doc.data, tags=doc.tags, document_datetime=doc.datetime)
                if new_metafile_checksum != old_metafile_checksum:
                    doc.delete()
                    frutsel_logger.info(f'Updated document file format: {old_metafile_checksum} became {new_metafile_checksum}.')

                # TODO: Verify checksums of files. Take cipher changes (such as SHA1 -> SHA256) into account.
                # FIXME: This is unsafe! In practice, this bit of code has already caused data loss.
                #        Somehow, the original Document was removed and the new Document was not yet fully written.
                # checksum_after_reserialisation = sha256(doc._serialise().encode()).hexdigest()
                # if checksum_after_reserialisation != doc.metafile_checksum:
                #    frutsel_logger.info(f'Migrating {absolute_file_path} to more compact JSON format.')
                #    # Saving the file currently also sets doc.metafile_checksum to the new checksum, so the rest of the maintenance code will proceed correctly.
                #    doc.save()
                #    os.remove(absolute_file_path)

                # TODO: Reconstruct timeline.

                # TODO: Update saved Query results.
                # TODO: Check and fix filesystem permissions, optionally.

            if doc and self._query._test_document(doc, check_tags=True):
                return doc

    def _next_stage_1_checksum(self):
        while True:
            stage_1_checksum = self._stage_1_checksums_iterator.__next__()
            if stage_1_checksum:
                doc = Document.from_metafile_checksum(self._db, stage_1_checksum)
                if doc and self._query._test_document(doc, check_tags=False):
                    return doc
        raise StopIteration


# Class for ensuring that all file operations are atomic, treat
# initialization like a standard call to 'open' that happens to be atomic.
# This file opener *must* be used in a "with" block.
class LockFile:
    # Open the file with arguments provided by user. Then acquire
    # a lock on that file object (WARNING: Advisory locking).
    def __init__(self, path):
        # Open the file and acquire a lock on the file before operating
        self.path = path + '.lock'
        while True:
            try:
                self.file = open(self.path, 'w')
                break
            except PermissionError:
                time.sleep(0.1)
        # Lock the opened file
        lock_file(self.file)

    # Return the opened file object (knowing a lock has been obtained).
    def __enter__(self, *args, **kwargs):
        return self.file

    # Unlock the file and close the file object.
    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        # Flush to make sure all buffered contents are written to file.
        self.file.flush()
        os.fsync(self.file.fileno())
        # Release the lock on the file.
        unlock_file(self.file)
        self.file.close()

        try:
            os.remove(self.path)
        except:  # noqa
            pass

        # Handle exceptions that may have come up during execution, by
        # default any exceptions are raised to the user.
        if exc_type is not None:
            return False
        else:
            return True


class _FrutselFile:
    def __init__(self, *path_parts, folder=None, name=None):
        if not path_parts and (folder and name):
            self.path = self._find_path(folder, name, create=False)
        elif len(path_parts) == 1:
            self.path = path_parts[0]
        elif path_parts:
            self.path = os.path.join(*path_parts)
        else:
            raise ValueError(f'Unable to construct a path from {path_parts=} {folder=} {name=}')
        self._contents = None
        self._name = None

    def _find_path(self, folder, name, extension='', create=True):
        if not name:
            raise ValueError(f'Should not operate on file without name in {folder} (with extension {extension!r})')
        extension = extension or ''
        try:
            items_in_folder = os.listdir(folder)
        except FileNotFoundError:
            items_in_folder = []
            if create:
                os.makedirs(folder, exist_ok=True)

        for possible_extension in set(
            (
                extension,
                '',
                'xz',
                'txt',
                'json',
                'json.xz',
            )
        ):
            filename = '.'.join(filter(bool, (name, possible_extension)))
            if filename in items_in_folder:
                existing_file_path = os.path.join(folder, filename)
                if os.path.isfile(existing_file_path):
                    # This filename already exists in this folder.
                    # frutsel_logger.debug(f'Found existing file {os.path.join(folder, filename)} by bruteforcing extensions.')
                    return existing_file_path

        if len(name) > 2:
            new_subfolder_name = name[0:2]
            new_subfolder_path = os.path.join(folder, new_subfolder_name)
            if new_subfolder_name in items_in_folder:
                if os.path.isdir(new_subfolder_path):
                    # Subfolder already exists. Dive into subfolder.
                    return os.path.join(new_subfolder_path, self._find_path(folder=new_subfolder_path, name=name[2:], extension=extension, create=create))
            elif len(items_in_folder) >= MAX_ITEMS_PER_FOLDER:
                # Max number of items per folder reached. Dive into subfolder.
                return os.path.join(new_subfolder_path, self._find_path(folder=new_subfolder_path, name=name[2:], extension=extension, create=create))

        filename = '.'.join(filter(bool, (name, extension)))
        # frutsel_logger.debug(f'Using new path {new_path} because there was room in the folder and the filename is long enough.')
        return os.path.join(folder, filename)

    @cache
    def check_checksum(self, strip_name_prefix):
        # Trigger file reading.
        _ = self.contents
        try:
            current_contents_checksum = sha256(self._raw_contents).hexdigest()
        except Exception as ex:
            raise FrutselError(f'{ex} while hashing {self.path} {type(self._raw_contents).__name__} contents')
        checksum_from_filename = self.get_name(strip=strip_name_prefix)
        return current_contents_checksum == checksum_from_filename

    @cache
    def get_name(self, strip=None):
        if self._name:
            return self._name
        else:
            p = pathlib.Path(self.path)
            if strip:
                path_folder = p.relative_to(strip).parent
            else:
                path_folder = p.parent
            prev_path_stem_attempt = None
            while True:
                path_stem = p.stem
                if path_stem != prev_path_stem_attempt:
                    prev_path_stem_attempt = path_stem
                else:
                    break
            joined = ''.join((path_folder / path_stem).parts)
            # Decode as quoted-printable.
            decoded = codecs.decode(joined.encode(), 'quoted-printable').decode()
            return decoded

    @property
    def contents(self):
        if not self._contents:
            with LockFile(self.path):
                with open(self.path, 'rb') as f:
                    self._raw_contents = f.read()
                    self._contents = self._raw_contents
                    if self.path.endswith('.xz'):
                        self._contents = lzma.decompress(self._contents)
                    if self.path.endswith('.json') or self.path.endswith('.json.xz'):
                        self._contents = jsonpickle.loads(self._contents)
        return self._contents


class _TagFile(_FrutselFile):
    def __init__(self, *path_parts, folder=None, name=None, db=None):
        if not db:
            raise ValueError(f'{type(self).__name__} needs a db')
        self._db = db
        super().__init__(*path_parts, folder=folder, name=name)

    @property
    def name(self):
        return self.get_name(strip=os.path.join(self._db.root_path, 'tags'))

    @property
    def metafile_checksums(self):
        return self.contents.decode().split('\n')


class _NamedFrutselFile(_FrutselFile):
    def __init__(self, folder, contents, name, extension=None, compress=False, overwrite=True):
        self._folder = folder
        self._contents = contents
        self._name = name
        self._extension = extension
        # Safely encode filename as quoted-printable.
        safe_name = []
        for c in name:
            if c not in _FILENAME_SAFE_CHARS:
                c = f'={ord(c):02X}'
            safe_name.append(c)
        safe_name = ''.join(safe_name)

        self.path = self._find_path(self._folder, safe_name, self._extension)

        # Apparently, our compressed files sometimes (often?) are bigger than the original data.
        # Compress and then compare size with original; write what's smaller.
        if compress:
            compressed_contents = lzma.compress(contents)
            if len(compressed_contents) < len(contents):
                contents = compressed_contents
                if not self.path.endswith('.xz'):
                    self.path += '.xz'

        with LockFile(self.path):
            if (not overwrite) and os.path.exists(self.path):
                frutsel_logger.debug(f'{self.path} already exists; not spending time overwriting it.')
                return
            with open(self.path, 'wb') as f:
                f.write(contents)

        # FIXME: We should set permissions while we open the file. See https://stackoverflow.com/questions/5624359/write-file-with-specific-permissions-in-python
        # Make the database readable and writable by our user and our group.
        os.chmod(self.path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP)


class _AnonymousFrutselFile(_NamedFrutselFile):
    def __init__(self, folder, contents, extension, compress):
        # TODO: Write out contents to a temp file, calculate checksum, rename temp file to final path. (To potentially save time.)
        checksum = sha256(contents).hexdigest()
        super().__init__(folder, contents, name=checksum, extension=extension, compress=compress, overwrite=False)


class FrutselKeyValue:
    def __init__(self, db):
        self._db = db

    def __setattr__(self, name, value):
        if name.startswith('_'):
            self.__dict__[name] = value
            return
        data_json = _json_encoder.encode(value)
        self._db._write_named_file(db_folder='kv', name=name, extension=None, contents=data_json.encode(), compress=None)

    def __getattr__(self, name):
        if name.startswith('_'):
            return self.__dict__.get(name)
        data_json = self._db._read_named_file('kv', name, extension=None).decode()
        return jsonpickle.loads(data_json)

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __setitem__(self, name, value):
        self.__setattr__(name, value)


def command_line_interface():
    arg0_dir = os.path.dirname(sys.argv[0]) or '.'
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # usage='%(prog)s [options] database_path',
        epilog="""FILTERLAMBDA
Consider the following command line.
%(prog)s -f /tmp/foo --dangerous-filter-function "doc.data > 42"
The given string argument to --dangerous-filter-function is executed as Python code as follows.
The equivalent of this code will be run:
exec(f'filter_function = lambda doc: {FILTERLAMBDA}')
for doc in database:
    if filter_function(doc):
        yield doc
""",
    )
    parser.add_argument('-f', '--database-path', action='store', help=f"the path to the root directory of the database (will be created if it doesn't exist) default: {arg0_dir}")

    group = parser.add_argument_group()
    group.add_argument('-v', '--verbose', action='store_true', help='talk a lot')
    group.add_argument('-d', '--debug', action='store_true', help='talk dirty')

    subgroup = group.add_mutually_exclusive_group(required=True)
    # TODO: Add mode to get statistics
    subgroup.add_argument('--put', action='store', metavar='TEXT', help='put TEXT in the database')
    subgroup.add_argument('--put-file', action='store', metavar='PATH', help='put a file in the database')
    subgroup.add_argument('--get', action='store_true', help='search frutsels in the database')
    subgroup.add_argument('--delete', action='store_true', help='delete frutsels from the database')
    subgroup.add_argument('--do-maintenance-round', action='store_true', help='do one maintenance round')
    subgroup.add_argument('--rsync', action='store', metavar='REMOTE_DB', help='sync with REMOTE_DB using rsync (once)')
    subgroup.add_argument('--git-sync', action='store_true', help='do a git pull and a git push')
    subgroup.add_argument('--checksums', action='store_true', help='return the checksums of all files in the database')
    subgroup.add_argument('--list-tags', action='store_true', help='list all tags in the database')
    subgroup.add_argument('-V', '--version', action='store_true', help='return version info')
    subgroup.add_argument('--license', action='store_true', help='return license info')

    parser.add_argument('-t', '--tags', action='store', help='tags (can be multiple, like -t foo bar baz)', nargs='+')
    parser.add_argument('--dangerous-filter-function', action='store', metavar='FILTERLAMBDA', help='string to execute as Python code (see FILTERLAMBDA)')
    parser.add_argument('--git-autocommit', action='store_true', help='automatically do a git commit after each change to the database')

    parser.add_argument('metafile_checksums', action='store', nargs='*', help='get/delete these specific documents')

    args = parser.parse_args()

    if args.version:
        print(f'frutsel.py {FRUTSEL_VERSION}')
    if args.license:
        print("""frutsel.py  Copyright (C) 2021-2025 maveobi path-fanfare-canon@duck.com
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under the terms of the GNU Lesser General Public License.
See https://www.gnu.org/licenses/ for details.""")

    if args.debug:
        frutsel_logger.setLevel(DEBUG)
        # Setup performance measuring.
        pr = cProfile.Profile()
        pr.enable()
    elif args.verbose:
        frutsel_logger.setLevel(INFO)
    else:
        frutsel_logger.setLevel(WARNING)

    if args.tags:
        tags = set(args.tags)
    else:
        if args.put or args.put_file:
            tags = None
        elif args.get or args.delete:
            tags = ANY

    if not args.database_path:
        args.database_path = arg0_dir

    if args.checksums:
        with FrutselDB(args.database_path, do_maintenance=False, logging_level=frutsel_logger.level) as db:
            for checksum in db.checksums():
                print(checksum)
        exit()
    elif args.list_tags:
        with FrutselDB(args.database_path, do_maintenance=False, logging_level=frutsel_logger.level) as db:
            for tag in db.tags:
                print(tag)
        exit()

    if args.dangerous_filter_function:
        frutsel_logger.warning(f'Injecting code from the command line ({args.dangerous_filter_function}) into a lambda function.')
        filter_function = eval(f'lambda doc: {args.dangerous_filter_function}')
    else:
        filter_function = None

    if args.do_maintenance_round:
        with FrutselDB(args.database_path, do_maintenance=True, logging_level=frutsel_logger.level, git_autocommit=args.git_autocommit) as db:
            db.maintenance()
    else:
        with FrutselDB(args.database_path, do_maintenance=False, logging_level=frutsel_logger.level, git_autocommit=args.git_autocommit) as db:
            if args.put:
                db.put(args.put, tags=tags, blocking=True)
            elif args.put_file:
                with open(args.put_file, 'rb') as f:
                    db.put(f.read(), tags=tags, blocking=True)
            elif args.get:
                for checksum in args.metafile_checksums or [
                    None,
                ]:
                    query = Query(metafile_checksum=checksum, tags=tags, filter_function=filter_function, min_datetime=MIN, max_datetime=MAX)
                    for doc in db.get(query):
                        print(doc)
                        if args.verbose:
                            pprint(doc.data)
            elif args.delete:
                for checksum in args.metafile_checksums or [
                    None,
                ]:
                    query = Query(metafile_checksum=checksum, tags=tags, filter_function=filter_function, min_datetime=MIN, max_datetime=MAX)
                    db.delete(query)
            elif args.rsync:
                db.rsync(args.rsync)

    if args.debug:
        pr.disable()
        s = io.StringIO()
        sortby = pstats.SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats(sortby)
        # Print top time eaters.
        ps.print_stats(20)
        print(s.getvalue())


if __name__ == '__main__':
    command_line_interface()
