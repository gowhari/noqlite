import re
import sqlite3


class NoQLite(object):

    def __init__(self, db_name, auto_commit=True):
        self.auto_commit = auto_commit
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self._check_default_table()

    def _check_default_table(self):
        self.cur.execute('create table if not exists _default (id integer primary key autoincrement)')

    def _process_error(self, err, recall_args):
        msg = err.args[0]
        found = re.match(r'table (.+) has no column named (.+)', msg)
        if found:
            self._add_column(*found.groups())
            self._recall(*recall_args)
            return
        raise NotImplementedError('error does not handled: %s' % msg)

    def _add_column(self, table, column):
        try:
            self.cur.execute('alter table %s add column %s' % (table, column))
        except sqlite3.OperationalError as err:
            if not err.args[0].startswith('duplicate column name'):
                raise

    def _recall(self, method, args):
        method(*args)

    def _run_auto_commit(self):
        if self.auto_commit:
            self.conn.commit()

    def commit(self):
        self.conn.commit()

    def insert(self, doc):
        cols_escape = ','.join(['"%s"' % i for i in doc.keys()])
        vals = tuple(doc[k] for k in doc)
        frmt = ','.join('?' * len(doc))
        qry = 'insert into _default (%s) values (%s)' % (cols_escape, frmt)
        try:
            self.cur.execute(qry, vals)
        except sqlite3.OperationalError as err:
            self._process_error(err, (self.insert, (doc,)))
        self._run_auto_commit()

    def search(self, query):
        sql, args = query.compile()
        sql = 'select * from _default where ' + sql
        res = self.cur.execute(sql, args).fetchall()
        return list(map(dict, res))

    def update(self, query, vals):
        pass


class Query(object):

    def __init__(self, op=None, left=None, right=None):
        self.op = op
        self.left = left
        self.right = right

    def __getattr__(self, attr):
        return Query(left=attr)

    def __repr__(self):
        return "Query%s" % ((self.op, self.left, self.right),)

    def __eq__(self, right):
        return Query('=', self.left, right)

    def __ne__(self, right):
        return Query('!=', self.left, right)

    def __lt__(self, right):
        return Query('<', self.left, right)

    def __le__(self, right):
        return Query('<=', self.left, right)

    def __ge__(self, right):
        return Query('>=', self.left, right)

    def __gt__(self, right):
        return Query('>', self.left, right)

    def __and__(self, right):
        return Query('and', self, right)

    def __or__(self, right):
        return Query('or', self, right)

    def __invert__(self):
        return Query('not', self)

    def compile(self):
        left, l_args = self.left.compile() if isinstance(self.left, Query) else ('"%s"' % self.left, ())
        right, r_args = self.right.compile() if isinstance(self.right, Query) else ('?', (self.right,))
        args = l_args + r_args
        if self.op == 'not':
            return ('not(%s)' % left), args[:-1]
        if self.op in ('and', 'or'):
            return ('(%s) %s (%s)' % (left, self.op, right)), args
        return ('%s %s %s' % (left, self.op, right)), args
