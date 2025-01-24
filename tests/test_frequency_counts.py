import pandas as pd
from dfeqa import summarise_str_lengths, fd


def test_summarise_str_lengths(Data_For_FD):
    assert summarise_str_lengths(Data_For_FD['forename']).eq(pd.Series([0,0,0,0,1,2,2,4,0,1])).all()

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
