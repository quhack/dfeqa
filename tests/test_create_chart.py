import pytest
from matplotlib import axes
from dfeqa import fd, freqchart


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


def test_freq_chart_reformats_string_xaxis(Data_For_FD):
    assert isinstance(freqchart(fd(Data_For_FD), 
        value_col = 'length', 
        freq_col = 'count', 
        groups = 'group', 
        min_range = 0, 
        max_range = 35,
        x_rescale = 2), axes._axes.Axes)


def test_freq_chart_reformats_list_xaxis(Data_For_FD):
    assert isinstance(freqchart(fd(Data_For_FD), 
        value_col = 'length', 
        freq_col = 'count', 
        groups = 'group', 
        min_range = 0, 
        max_range = 35,
        x_rescale = [0, 2, 4]), axes._axes.Axes)
