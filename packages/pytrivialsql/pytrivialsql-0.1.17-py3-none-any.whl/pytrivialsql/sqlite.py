import re
import sqlite3

from . import sql

_COLNAME_RE = re.compile(r'^\s*(?:[`"\[])?([A-Za-z_][A-Za-z0-9_]*)')


class Sqlite3:
    def __init__(self, db_path):
        self.path = db_path
        self._conn = sqlite3.connect(
            self.path, check_same_thread=not self.is_threadsafe()
        )

    def exec(self, query, args=None):
        with self._conn as cur:
            cur.execute(query, args or ())

    def execs(self, query_args_pairs):
        with self._conn as cur:
            for q, qargs in query_args_pairs:
                cur.execute(q, qargs)

    def is_threadsafe(self):
        mem = sqlite3.connect("file::memory:?cache=shared")
        cur = mem.execute(
            "select * from pragma_compile_options where compile_options like 'THREADSAFE=%'"
        )
        res = cur.fetchall()
        cur.close()
        try:
            return res[0][0].split("=")[1] == "1"
        except Exception:
            return False

    def drop(self, *table_names):
        with self._conn as cur:
            for tbl in table_names:
                cur.execute(sql.drop_q(tbl))

    def create(self, table_name, props):
        try:
            with self._conn as cur:
                cur.execute(sql.create_q(table_name, props))
                return True
        except Exception:
            return False

    def _column_exists(self, table_name, column_name):
        cur = self._conn.execute(f"PRAGMA table_info({table_name})")
        try:
            return any(row[1] == column_name for row in cur.fetchall())  # row[1] = name
        finally:
            cur.close()

    def _extract_colname(self, col_def):
        # Handles:  foo TEXT,  "Foo Bar" TEXT,  `foo` INT,  [foo] TEXT, etc.
        m = _COLNAME_RE.match(col_def)
        return m.group(1) if m else col_def.strip().split()[0]

    def add_column(self, table_name, col_def):
        col_name = self._extract_colname(col_def)
        try:
            if self._column_exists(table_name, col_name):
                return True  # idempotent: column already present
            with self._conn as conn:
                conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_def}")
            return True
        except Exception:
            return False

    def index(self, index_name, table_name, columns, unique=False):
        """
        SQLite CREATE INDEX IF NOT EXISTS.
        """
        try:
            with self._conn as cur:
                cur.execute(sql.index_q(index_name, table_name, columns, unique=unique))
            return True
        except Exception:
            return False

    def select(
        self,
        table_name,
        columns,
        distinct=None,
        where=None,
        order_by=None,
        limit=None,
        join=None,
        offset=None,
        transform=None,
    ):
        with self._conn as cur:
            c = cur.cursor()
            if columns is None or columns == "*":
                columns = [
                    el[1]
                    for el in c.execute(f"PRAGMA table_info({table_name})").fetchall()
                ]
            if not columns:
                raise Exception(f"No such table {table_name}")
            elif isinstance(columns, str):
                columns = [columns]
            query, args = sql.select_q(
                table_name,
                columns,
                where=where,
                distinct=distinct,
                order_by=order_by,
                join=join,
                limit=limit,
                offset=offset,
            )
            c.execute(query, args)
            res = (dict(zip(columns, vals)) for vals in c.fetchall())
            if transform is not None:
                return [transform(el) for el in res]
            return list(res)

    def insert(self, table_name, **args):
        with self._conn as cur:
            c = cur.cursor()
            c.execute(*sql.insert_q(table_name, **args))
            return c.lastrowid

    def update(self, table_name, bindings, where):
        with self._conn as cur:
            c = cur.cursor()
            q, args = sql.update_q(table_name, where=where, **bindings)
            c.execute(q, args)

    def delete(self, table_name, where):
        with self._conn as cur:
            c = cur.cursor()
            c.execute(*sql.delete_q(table_name, where=where))
