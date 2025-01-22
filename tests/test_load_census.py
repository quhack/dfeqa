import re
import pandas as pd
from matplotlib import axes
import pytest
from dfeqa import load_census, summarise_str_lengths, fd, freqchart, valid_name_regex, parse_text, valid_upn, year_group


def test_load_census_without_conn():
    df = load_census(202324, NCYear = "R", term = "Autumn", columns = "PupilMatchingRefAnonymous")
    assert df.shape[0] > 100

@pytest.mark.slow
def test_load_census_with_conn_multiple_columns(PDR_Conn):
    df = load_census(202324, NCYear = "R", term = "Autumn",
        columns = ["forename","surname"],
        conn = PDR_Conn)
    assert df.shape[0] > 100

@pytest.mark.slow
def test_load_census_multiyeargroup(PDR_Conn):
    df = load_census(202324, NCYear = ["R","1"], term = "Autumn",
        columns = "PupilMatchingRefAnonymous",
        conn = PDR_Conn)
    assert df.shape[0] > 100

@pytest.mark.slow
def test_load_allcols():
    df = load_census(202324, NCYear = "R", term = "Autumn")
    assert df.shape[0] > 100

def test_freq_dist_from_series(Data_For_FD):
    pd.testing.assert_series_equal(
        fd(Data_For_FD['forename']),
        pd.Series(
            [0,0,0,0,1,2,2,4,0,1],
            name='count',
            index=pd.Index(name='forename', data = list(range(10)))
        )
    )

def test_freq_dist_from_dataframe_with_columns(Data_For_FD, FD_Frame_Summary):
    pd.testing.assert_frame_equal(
        fd(Data_For_FD, cols = ['forename', 'surname']),
        FD_Frame_Summary
    )

def test_freq_dist_from_dataframe_without_columns(Data_For_FD, FD_Frame_Summary):
    pd.testing.assert_frame_equal(fd(Data_For_FD), FD_Frame_Summary)

def test_freq_dist_from_list_of_series(Data_For_FD, FD_Frame_Summary):
    pd.testing.assert_frame_equal(fd([Data_For_FD['forename'],Data_For_FD['surname']]), FD_Frame_Summary)

def test_freq_dist_from_list_with_custom_id(Data_For_FD):
    df = fd([Data_For_FD['forename'],Data_For_FD['surname']], ids=['f','s'])
    g = df['group'].unique()
    assert g[0] == 'f' and g[1] == 's'

def test_freq_dist_chart_generates(Data_For_FD):
    assert isinstance(freqchart(fd(Data_For_FD), 
        value_col = 'length', 
        freq_col = 'count', 
        groups = 'group', 
        min_range = (0,5), 
        max_range = (35,30)), axes._axes.Axes)

def test_freq_dist_chart_generates_with_ints(Data_For_FD):
    assert isinstance(freqchart(fd(Data_For_FD), 
        value_col = 'length', 
        freq_col = 'count', 
        groups = 'group', 
        min_range = 0, 
        max_range = 35), axes._axes.Axes)

def test_valid_name():
    assert re.findall(valid_name_regex,'Raymond Cocteau') == ['Raymond Cocteau']

def test_valid_name_contains_number():
    assert re.findall(valid_name_regex,'Raym0nd Cocteau') == ['Raym0nd Cocteau']

def test_invalid_name_contains_phone_number():
    assert re.findall(valid_name_regex,'01898 888444') == []

def test_valid_upn():
    assert valid_upn('A123456789012') == True

def test_invalid_upn():
    assert valid_upn('B123456789012') == False

def test_parsed_text():
    my_data = {'my_val': "to catch one"}
    assert parse_text("send a maniac {{my_val}}",my_data) == "send a maniac to catch one"

def test_older_year_group():
    assert year_group("23092012",2024) == 'y6'

def test_younger_year_group():
    assert year_group("01012013",2024) == 'y6'

def test_really_old_year_group():
    assert year_group("01012010",2024) == 'abovey8'

def test_reception_year_group():
    assert year_group("01012019",2024) == 'r'

def test_really_young_year_group():
    assert year_group("01012020",2024) == 'under_r'
