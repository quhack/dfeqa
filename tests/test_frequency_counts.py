import pytest
import pandas as pd
from dfeqa import fd#summarise_str_lengths


# def test_summarise_str_lengths(List_Of_Series):
#     assert summarise_str_lengths(List_Of_Series[0]).eq(pd.Series([0,0,0,0,1,2,2,4,0,1])).all()

def test_freq_dist_from_series(List_Of_Series):
    pd.testing.assert_frame_equal(
        fd(List_Of_Series[0].str.len()),
        List_Of_Series[0].str.len().value_counts().sort_index().reset_index(drop=False).rename(columns={List_Of_Series[0].name: 'value'})
    )


def test_freq_dist_from_dataframe_with_columns(List_Of_Series, Wide_Frame_Length_Summary):
    dummy_col = List_Of_Series[0].apply(lambda x: 'dummy value').rename('dummy')
    pd.testing.assert_frame_equal(
        fd(pd.concat([x.str.len() for x in List_Of_Series + [dummy_col]] , axis=1), cols = ['forename', 'surname']),
        Wide_Frame_Length_Summary
    )


def test_freq_dist_from_series_without_ids():
    s = pd.Series(['x' for a in range(10)], name="testdata")
    pd.testing.assert_frame_equal(fd(s), pd.DataFrame([{'value':'x','count':10}]))


def test_freq_dist_from_dataframe_without_columns(List_Of_Series):
    test_fd = pd.concat([
        s.value_counts(dropna=False).rename(s.name) for s in List_Of_Series
        ], axis = 1).fillna(0).astype(int)\
            .sort_index().reset_index(drop=False).rename(columns={'index':'value'})
    pd.testing.assert_frame_equal(fd(pd.concat(List_Of_Series, axis=1)), test_fd)


def test_freq_dist_from_list_of_series(List_Of_Series, Wide_Frame_Name_Freqs):
    pd.testing.assert_frame_equal(fd(List_Of_Series), Wide_Frame_Name_Freqs)


def test_freq_dist_from_list_of_series_same_name(List_Of_Series):
    d = fd([List_Of_Series[0],List_Of_Series[0]], ids=['a','b'])
    assert d.columns.tolist() == ['value','a','b']


def test_wide_freq_dist_from_dataframe_with_custom_id(List_Of_Series, Wide_Frame_Name_Freqs):
    benchmark = Wide_Frame_Name_Freqs.rename(columns={'forename':'f','surname':'s'})
    pd.testing.assert_frame_equal(fd(pd.concat(List_Of_Series , axis=1), ids=['f','s']), benchmark)


def test_wide_freq_dist_from_list_with_custom_id(List_Of_Series, Wide_Frame_Name_Freqs):
    benchmark = Wide_Frame_Name_Freqs.rename(columns={'forename':'f','surname':'s'})
    pd.testing.assert_frame_equal(fd(List_Of_Series, ids=['f','s']), benchmark)


def test_long_freq_dist_from_list_with_custom_id(List_Of_Series):
    df = fd(List_Of_Series, ids=['f','s'], long=True)
    g = df['group'].unique()
    print(df)
    assert g[0] == 'f' and g[1] == 's'
