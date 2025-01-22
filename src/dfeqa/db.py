import os
import pandas as pd


def load_census(year, term=None, NCYear=None, columns=None, conn=None):
    """to load a census dataset from PDR
    pass the year to load data from
    optionally pass the term in that year (or don't to get all terms)
    and also optionally, pass the year group NCYear,
    or a list of year groups, or don't specify to get all year groups
    and an optional list of columns to reduce the size of the query
    and resulting dataframe"""

    default_conn = os.environ['default_conn']

    db_conn = conn or default_conn
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
