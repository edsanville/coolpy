import os
import traceback
import types
import coolpy.json as json
from typing import Callable, TypeVar
import sqlite3
import logging


# TODO:
# Use correct types for the value column in side tables
# Automatically detect existing indices on load

# Less important:
# Support deleting items


logging.basicConfig(level=logging.INFO)
l = logging.getLogger(__name__)


T = TypeVar('T')


def getattr_path(obj: any, key_path: str) -> any:
    keys = key_path.split('.')
    current = obj
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            current = getattr(current, key, None)

        if current is None:
            return None
    return current


def get_type_at_path(Class: Callable[[], T], key_path: str) -> any:
    from typing import get_type_hints, get_origin, get_args

    keys = key_path.split('.')
    current_type = Class

    for key in keys:
        hints = get_type_hints(current_type)
        if key not in hints:
            return None

        current_type = hints[key]

        origin = get_origin(current_type)
        args = get_args(current_type)

        if origin == list or origin == set:
            current_type = args[0]
        elif origin == dict:
            current_type = args[1]

    return current_type


reserved_word_map = {
    'index': 'idx',
    'table': 'tbl',
    'select': 'sel',
    'from': 'frm',
    'where': 'whr',
}


def table_name(key_path: str) -> str:
    key_path = reserved_word_map.get(key_path, key_path)
    return f'{"__".join(key_path.split("."))}'


def index_name(key_path: str) -> str:
    return f'index_{table_name(key_path)}'


class Transaction:
    db: sqlite3.Connection

    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb: types.TracebackType):
        if exc_type is None:
            self.db.commit()
        else:
            self.db.rollback()
            traceback.print_exception(exc_type, exc_value, tb)
            exit(1)


class JsonDB:
    path: str
    Class: Callable[[], T]
    conn: sqlite3.Connection
    indices: set[str] = set()

    def __init__(self, path: str, Class: Callable[[], T], overwrite: bool = False):
        self.path = path
        self.Class = Class

        if overwrite:
            try:
                os.remove(path)
            except FileNotFoundError:
                pass

        self.conn = sqlite3.connect(path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS data (
                data_id INTEGER PRIMARY KEY,
                json TEXT NOT NULL
            )
        ''')
        self.conn.commit()


    def transaction(self) -> Transaction:
        return Transaction(self.conn)


    def insert(self, obj: T):
        s = json.dumps(obj)
        self.conn.execute('INSERT INTO data (json) VALUES (?)', (s,))

        # Update indices
        cursor = self.conn.execute('SELECT last_insert_rowid()')
        data_id = cursor.fetchone()[0]

        for key_path in self.indices:
            self._update_index(key_path, obj, data_id)

    
    def _replace(self, obj: T, data_id: int):
        s = json.dumps(obj)
        self.conn.execute('UPDATE data SET json = ? WHERE data_id = ?', (s, data_id))

        # Update indices
        for key_path in self.indices:
            self._update_index(key_path, obj, data_id)


    def replace(self, obj: T, key_path: str, value: any):
        self.add_index(key_path)

        tbl_name = table_name(key_path)
        cursor = self.conn.execute(f'''
            SELECT data_id FROM data NATURAL JOIN {tbl_name} 
            WHERE {tbl_name} is ?
        ''', (value,))

        for row in cursor.fetchall():
            data_id = row[0]
            self._replace(obj, data_id)

    
    def upsert(self, obj: T, key_path: str, update_func: Callable[[T, T], T] = None):
        if update_func is None:
            import coolpy.merge
            update_func = coolpy.merge.merge

        self.add_index(key_path)

        value = getattr_path(obj, key_path)

        if value is None:
            self.insert(obj)
            return

        tbl_name = table_name(key_path)
        cursor = self.conn.execute(f'''
            SELECT data_id, json FROM data NATURAL JOIN {tbl_name} 
            WHERE {tbl_name} is ?
        ''', (value,))

        rows = cursor.fetchall()
        if len(rows) == 0:
            # Insert new
            self.insert(obj)
            return
        
        for row in rows:
            data_id = row[0]
            existing_obj = json.loads(row[1], self.Class)

            if update_func is not None:
                obj = update_func(existing_obj, obj)

            self._replace(obj, data_id)


    def _update_index(self, key_path: str, obj: T, data_id: int):
        tbl_name = table_name(key_path)

        # Remove existing entries
        self.conn.execute(f'DELETE FROM {tbl_name} WHERE data_id = ?', (data_id,))

        value = getattr_path(obj, key_path)
        if value is None:
            return

        if isinstance(value, (list, set)):
            for v in value:
                self.conn.execute(f'INSERT OR REPLACE INTO {tbl_name} (data_id, {tbl_name}) VALUES (?, ?)', (data_id, v))
        else:
            self.conn.execute(f'INSERT OR REPLACE INTO {tbl_name} (data_id, {tbl_name}) VALUES (?, ?)', (data_id, value))


    def add_index(self, key_path: str):
        if key_path in self.indices:
            return
        
        tbl_name = table_name(key_path)
        idx_name = index_name(key_path)

        # See if the index table already exists
        cursor = self.conn.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        ''', (tbl_name,))
        row = cursor.fetchone()
        if row is not None:
            self.indices.add(key_path)
            return

        l.debug(f"Adding index on key path '{key_path}'")
        with self.transaction():
            cmd = f'''
                CREATE TABLE {tbl_name} (
                    data_id INTEGER,
                    {tbl_name} TEXT,
                    FOREIGN KEY(data_id) REFERENCES data(data_id)
                    UNIQUE(data_id, {tbl_name})
                )
            '''
            l.debug(f"Creating index table with command: {cmd}")
            self.conn.execute(cmd)

            self.conn.execute(f'CREATE INDEX IF NOT EXISTS {idx_name} ON {tbl_name} ({tbl_name})')
            self.conn.execute(f'CREATE INDEX IF NOT EXISTS {tbl_name}_data_id ON {tbl_name} (data_id)')

            cursor = self.conn.execute('SELECT data_id, json FROM data')
            index = 0
            for row in cursor.fetchall():
                data_id = row[0]
                obj = json.loads(row[1], self.Class)

                self._update_index(key_path, obj, data_id)

                index += 1

                if index % 100000 == 0:
                    l.info(f"Indexed {index} rows for key path '{key_path}'")

        self.indices.add(key_path)


    def query(self, key_path: str, value: any) -> list[T]:
        if key_path not in self.indices:
            # Create an index on this key path
            self.add_index(key_path)

        tbl_name = table_name(key_path)
        cursor = self.conn.execute(f'SELECT json FROM data NATURAL JOIN {tbl_name} WHERE {tbl_name} is ?', (value,))
        return [json.loads(row[0], self.Class) for row in cursor.fetchall()]


    def load_all(self, sql: str='') -> list[T]:
        cursor = self.conn.execute(f'SELECT json FROM data {sql}')
        return [json.loads(row[0], self.Class) for row in cursor.fetchall()]

    def close(self):
        self.conn.commit()
        self.conn.close()

    def __del__(self):
        self.close()
