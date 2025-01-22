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
def Data_For_FD():
    return pd.DataFrame([
        {'forename': 'John', 'surname': 'Spartan'},
        {'forename': 'Simon', 'surname': 'Phoenix'},
        {'forename': 'Lenina', 'surname': 'Huxley'},
        {'forename': 'Raymond', 'surname': 'Cocteau'},
        {'forename': 'Alfredo', 'surname': 'Garcia'},
        {'forename': 'George', 'surname': 'Earle'},
        {'forename': 'Associate', 'surname': 'Bob'},
        {'forename': 'Edgar', 'surname': 'Friendly'},
        {'forename': 'Zachary', 'surname': 'Lamb'},
        {'forename': 'William', 'surname': 'Smithers'}
    ]
    )

@pytest.fixture
def FD_Frame_Summary():
    return pd.DataFrame([
        {'length': 0, 'count': 0, 'group': 'forename'},
        {'length': 1, 'count': 0, 'group': 'forename'},
        {'length': 2, 'count': 0, 'group': 'forename'},
        {'length': 3, 'count': 0, 'group': 'forename'},
        {'length': 4, 'count': 1, 'group': 'forename'},
        {'length': 5, 'count': 2, 'group': 'forename'},
        {'length': 6, 'count': 2, 'group': 'forename'},
        {'length': 7, 'count': 4, 'group': 'forename'},
        {'length': 8, 'count': 0, 'group': 'forename'},
        {'length': 9, 'count': 1, 'group': 'forename'},
        {'length': 0, 'count': 0, 'group': 'surname'},
        {'length': 1, 'count': 0, 'group': 'surname'},
        {'length': 2, 'count': 0, 'group': 'surname'},
        {'length': 3, 'count': 1, 'group': 'surname'},
        {'length': 4, 'count': 1, 'group': 'surname'},
        {'length': 5, 'count': 1, 'group': 'surname'},
        {'length': 6, 'count': 2, 'group': 'surname'},
        {'length': 7, 'count': 3, 'group': 'surname'},
        {'length': 8, 'count': 2, 'group': 'surname'},
    ], index = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8])

@pytest.fixture
def PDR_Conn():
    return os.environ['default_conn']
