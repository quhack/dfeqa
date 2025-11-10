# helpers to support sql summary object functions

import string
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from sqlalchemy import func, literal, select


class Constants(Enum):
    SERIES_LABEL = "series"
    SOURCE_LABEL = "source"
    TABLE_LABEL = "table"
    COLUMN_LABEL = "column"
    VALUE_LABEL = "value"
    FREQUENCY_LABEL = "f"


@dataclass
class SqlInstance:
    """to keep track of table name and columns of a summary"""
    tablename: str
    columns: str | tuple
    sql: Optional[select] = None
    alias: str | list = None
    output_columns: str | list = None
    # pandas_query: str = None
    def __str__(self):
        return (self.tablename + ":" + self.columns) \
            if isinstance(self.columns, str) else \
            (self.tablename + ":(" + ",".join(self.columns) + ")")
    def list_column_names(self):
        if isinstance(self.columns, str):
            return [{'t':self.tablename, 'c':self.columns}]
        else:
            return [{'t':self.tablename, 'c':c} for c in self.columns]


def _tablecolumn_from_sqlspec(sqlspec, t=None):
    """return the table and column names within a sql spec list"""
    rv=[]
    def add_to_rv(v):
            if isinstance(v,list):
                rv.extend(v)
            else:
                rv.append(v)
    if isinstance(sqlspec, dict):
        for t,c in sqlspec.items():
            add_to_rv(_tablecolumn_from_sqlspec(c, t=t))
    elif isinstance(sqlspec, list) and t is None:
        for x in sqlspec:
            add_to_rv(_tablecolumn_from_sqlspec(x))
    elif isinstance(sqlspec, (list, tuple)):
        for x in sqlspec:
            add_to_rv(_tablecolumn_from_sqlspec(x, t = t))
    return rv if rv else {'t':t, 'c':sqlspec}


def make_columns_unique(cols: list):
    """take list of dicts with table and column names - return a list of unique column names"""
    uniq_tables = list(set([x['t'] for x in cols])) # list so order is persistent
    uniq_tc = set([(x['t'],x['c']) for x in cols])
    utables, ucolumns = zip(*uniq_tc, strict=True)
    n_col_instances = Counter(ucolumns) # number of tables each column is defined in
    outlist = []
    for x in cols:
        c = x['c']
        t = x['t']
        if n_col_instances[c] == 1:
            outlist.append(c)
        else:
            outlist.append(c + '_' + _number_to_lettercombo(uniq_tables.index(t)+1))
    return outlist


def _number_to_lettercombo(num: int):
    """return a letter combination for a given integer"""
    if num == 0:
        return ''
    assert num >= 0, "negative numbers cannot be converted to letter combinations"
    outval = ""
    residual = ((num - 1) // 26)
    if residual > 0:
        outval = outval + _number_to_lettercombo(residual)
    return outval + string.ascii_uppercase[(num % 26)-1]



# TODO
# we've got a table of aliases, but rather than handling that separately
# we want to integrate that into the creation of the spec objects if possible
# then amend sql_build to build a query for those instances including the alias as one step
#######







def _sql_create_instance(table, column, sql_tables, column_aliases):
    """generator to return dict(s) containing the select element(s) with table and group_by"""
    print(column_aliases)
    print(table)
    print(column)
    # add additional columns to the query if add_column_ids is true
    if isinstance(column, list):
        for _c in column:
            yield from _sql_create_instance(table, _c, sql_tables, column_aliases)
    elif isinstance(column, tuple): # this is the case where combo columns specd
        s_instance = SqlInstance(tablename = table, columns=column)
        # sql_select = [sql_tables[table].c[_c] for _c in column]
        sql_select = [sql_tables[table].c[_c].label(Constants.COLUMN_LABEL.value + '_' + str(_i))\
            for _i, _c in enumerate(column)]
        # sql_select = [literal(_c).label(Constants.COLUMN_LABEL.value + '_' + str(_i))
        #                 for _i, _c in enumerate(column)] + sql_select
        s_instance.sql = _build_select(s_instance, sql_select).group_by(*column)
        # s_instance.alias = list(column_aliases.values())#{x:column_aliases[x] for x in column if x in column_aliases}
        s_instance.alias = [column_aliases[(table, x)] for x in column]
        s_instance.output_columns = [Constants.COLUMN_LABEL.value + '_' + str(_i)
                        for _i in range(len(column))]
        yield s_instance
    else:
        s_instance = SqlInstance(tablename = table, columns=column)
        sql_select = [#literal(column).label(Constants.COLUMN_LABEL.value + '_0'),
            # sql_tables[table].c[column].label(Constants.VALUE_LABEL.value)
            sql_tables[table].c[column].label(Constants.COLUMN_LABEL.value + '_0')
            ]
        s_instance.sql = _build_select(s_instance, sql_select).group_by(column)
        # s_instance.alias = list(column_aliases.values())[0] #column_aliases.get((table, column),None)
        s_instance.alias = column_aliases[(table, column)]
        s_instance.output_columns = Constants.COLUMN_LABEL.value + '_0'

        yield s_instance


def _sql_selects(sql_spec, tables_dict):
    """return sql select statements using the user sql spec"""
    assert isinstance(sql_spec, dict)
    assert all([x.count('.') <= 1 for x in sql_spec]), \
        'tablenames should have max 2 levels (schema and tablename)'
    oldcols = _tablecolumn_from_sqlspec(sql_spec)
    newnames = make_columns_unique(oldcols)
    column_aliases = {(o['t'],o['c']): newname for o,newname in zip(oldcols, newnames, strict=True)}
    return [sql for t,c in sql_spec.items()
                for sql in _sql_create_instance(t,c, tables_dict, column_aliases)]


def _validate_sql_spec(spec):  # noqa: C901 -- this prevents complexity check - TODO simplify
    if not isinstance(spec,dict):
        return False
    def __validate_cols(x):
        # cols can be a string (columnname), a list (of columns), or a tuple
        # lists can contain strings or tuples
        # tuples can contain strings (TODO feels like this one could be checked in a single step?)
        # TODO and does this have to be a closure? - that could be what's triggering the simplification
        if not all([isinstance(_,(str, list, tuple)) for _ in x]):
            return False
        elif not all([isinstance(__,(str, tuple)) for _ in x for __ in _ if isinstance(_, list)]):
            return False
        elif not all([isinstance(__, str) for _ in x for __ in _ if isinstance(_, tuple)]):
            return False
        elif not all([isinstance(_,str)
                    for _ in x if isinstance(x, list)
                    for __ in _ if isinstance(_, tuple)]):
            return False
        else:
            return True

    if not __validate_cols(spec.values()):
        return False

    # columns should be specified consistently
    def __profile(x):
        """return the number of columns of each frequency distributions"""
        if isinstance(x,str):
            yield 1
        elif isinstance(x,tuple):
            yield sum([__ for _ in x for __ in __profile(_)])
        elif isinstance(x,list):
            for _ in x:
                yield from __profile(_)
        else:
            yield False

    sql_col_numbers = [_ for _ in __profile(list(spec.values()))]
    # check that all frequencies will be based off the same number of columns
    if not all([x==max(sql_col_numbers) for x in sql_col_numbers]):
        return False
    else:
        return True

def _build_select(spec_instance, sql_select):
    return select(
        literal(str(spec_instance)).label(Constants.SOURCE_LABEL.value),
        literal(spec_instance.tablename).label(Constants.TABLE_LABEL.value),
        *sql_select,
        func.count().label(Constants.FREQUENCY_LABEL.value)
        )
