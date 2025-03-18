import os
import pytest
import pandas as pd


def pytest_addoption(parser):
    parser.addoption('--slow', action='store_true', default=False,
                      help='Also run slow tests')

def pytest_collection_modifyitems(config, items):
    if not config.getoption("--slow"):
        skipper = pytest.mark.skip(reason="Only run when --slow is given")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skipper)

@pytest.fixture
def List_Of_Series():
    return [
        pd.Series(['John', 'Simon', 'Lenina', 'Raymond', 'Alfredo', 'George', 'Associate', 'Edgar', 'Zachary', 'William'], name='forename'),
        pd.Series(['Spartan', 'Phoenix', 'Huxley', 'Cocteau', 'Garcia', 'Earle', 'Bob', 'Friendly', 'Lamb', 'Smithers'], name='surname')
    ]

@pytest.fixture
def People_As_Frame(List_Of_Series):
    d = pd.concat(List_Of_Series, axis=1)
    d['fname_len']=d['forename'].str.len()
    return d

@pytest.fixture
def Wide_Frame_Length_Summary(List_Of_Series):
    return pd.concat(
        [x.str.len().value_counts(dropna=False).rename(x.name)\
            for x in List_Of_Series], axis=1
            ).fillna(0).astype(int).sort_index().reset_index(drop=False).rename(columns={'index':'value'})

@pytest.fixture
def Long_Frame_Length_Summary(Wide_Frame_Length_Summary):
    return Wide_Frame_Length_Summary.melt(id_vars=['value'], value_name='count', var_name='group')

@pytest.fixture
def Long_Frame_Name_Freqs(List_Of_Series):
    return pd.concat(
        [x.value_counts(dropna=False).reset_index(drop=False)\
            .rename(columns={x.name:'value'}).assign(group=x.name)
            for x in List_Of_Series]
    )

@pytest.fixture
def Wide_Frame_Name_Freqs(List_Of_Series):
    return pd.concat(
        [x.value_counts(dropna=False).rename(x.name)\
            for x in List_Of_Series], axis=1
    ).fillna(0).astype(int).sort_index().reset_index(drop=False).rename(columns={'index':'value'})

@pytest.fixture
def PDR_Conn():
    return os.environ['default_conn']
