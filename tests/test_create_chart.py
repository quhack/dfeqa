import pytest
from matplotlib import axes
from dfeqa import fd, barchart


def test_freq_dist_chart_generates(People_As_Frame):
    assert isinstance(barchart(fd(People_As_Frame, long=True), 
        value_col = 'value', 
        freq_col = 'count', 
        groups = 'group', 
        min_range = (0,5), 
        max_range = (35,30)), axes._axes.Axes)


def test_freq_dist_chart_generates_with_ints(People_As_Frame):
    assert isinstance(barchart(fd(People_As_Frame, long=True), 
        value_col = 'value', 
        freq_col = 'count', 
        groups = 'group', 
        min_range = 0, 
        max_range = 35), axes._axes.Axes)


def test_freq_chart_reformats_string_xaxis(People_As_Frame):
    assert isinstance(barchart(fd(People_As_Frame, long=True), 
        value_col = 'value', 
        freq_col = 'count', 
        groups = 'group', 
        min_range = 0, 
        max_range = 35,
        x_rescale = 2), axes._axes.Axes)


def test_freq_chart_reformats_list_xaxis(People_As_Frame):
    assert isinstance(barchart(fd(People_As_Frame, long=True), 
        value_col = 'value', 
        freq_col = 'count', 
        groups = 'group', 
        min_range = 0, 
        max_range = 35,
        x_rescale = [0, 2, 4]), axes._axes.Axes)
