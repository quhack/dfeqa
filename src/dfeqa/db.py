import os
import re
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.sql import quoted_name

engines = {}
inspectors = {}

def get_default_conn():
    load_dotenv()
    return os.environ.get('DEFAULT_CONN')

def load_census(year, term=None, NCYear=None, columns=None, conn='DEFAULT_CONN'):
    """to load a census dataset from PDR
    pass the year to load data from
    optionally pass the term in that year (or don't to get all terms)
    and also optionally, pass the year group NCYear,
    or a list of year groups, or don't specify to get all year groups
    and an optional list of columns to reduce the size of the query
    and resulting dataframe"""

    load_dotenv()
    db_conn = os.environ[conn] if conn in os.environ else conn

    # check what is in ncyear - list or string?
    ncyear_list = list()
    if isinstance(NCYear, str):
        ncyear_list.append(NCYear)
    elif isinstance(NCYear, list):
        ncyear_list = NCYear
    # build sql query
    query = "select "
    if columns:
        assert isinstance(columns, (str, list))
        if isinstance(columns, str):
            query += columns
        elif isinstance(columns, list):
            query += ", ".join(columns)
    else:
        query += "*"
    query += """ from {tablename}
    where AcademicYear = {acadyr}""".format(tablename = 'tier0.CensusSeasonSSA_MasterView',
        acadyr = year)
    if term:
        query += " and CensusTerm = '{term}'".format(term = term)
    if NCYear:
        query += " and NCYearActual IN ({ncyear})""".format(ncyear = "'" + "','".join(ncyear_list) + "'")
    # query the db
    return pd.read_sql(query, db_conn)

def get_table_metadata(tablename, conn):
    """
    function to get the metadata for a given SQL table
    """
    tablename_list = re.sub("\[|\]","",tablename).split(".")
    if len(tablename_list) == 1:
        tn = quoted_name(tablename_list[0], None)
        sc = quoted_name('dbo', None)
    elif len(tablename_list) == 2:
        tn = quoted_name(tablename_list[1], None)
        sc = quoted_name(tablename_list[0], None)
    else:
        raise RuntimeError("tablename not in a valid format")

    if not engines.get(conn):
        engines[conn] = create_engine(conn, echo=False, future=True)
    if not inspectors.get(conn):
        inspectors[conn] = inspect(engines[conn])

    insp = inspectors[conn]
    meta_dict = {}
    if insp.has_table(table_name = tn, schema = sc):
        meta_dict['tablename'] = tn
        try:
            cols = insp.get_columns(table_name = tn, schema = sc)
        except NotImplementedError:
            cols = None
        else:
            for index, col in enumerate(cols):
                col['order'] = index
            meta_dict['columns'] = cols
        try:
            constr = insp.get_check_constraints(table_name = tn, schema = sc)
        except NotImplementedError:
            constr = None
        else:
            meta_dict['constraints'] = constr
        try:
            fks = insp.get_foreign_keys(table_name = tn, schema = sc)
        except NotImplementedError:
            fks = None
        else:
            meta_dict['foreign_keys'] = fks
        try:
            indx = insp.get_indexes(table_name = tn, schema = sc)
            indxs=[]
            for _x in indx:
                indxs.extend([_x['name'], _x])
        except NotImplementedError:
            indxs = None
        else:
            meta_dict['indexes'] = indxs
        try:
            pk_constr = insp.get_pk_constraint(table_name = tn, schema = sc)
        except NotImplementedError:
            pk_constr = None
        else:
            meta_dict['pk_constraints'] = pk_constr
        try:
            uniq_constr = insp.get_unique_constraints(table_name = tn, schema = sc)
        except NotImplementedError:
            uniq_constr = None
        else:
            meta_dict['unique_constraints'] = uniq_constr
        try:
            tab_comment = insp.get_table_comment(table_name = tn, schema = sc)['text']
        except NotImplementedError:
            tab_comment = None
        else:
            meta_dict['table_comment'] = tab_comment
    else:
        raise KeyError ("Table doesn't exist")
    return meta_dict
