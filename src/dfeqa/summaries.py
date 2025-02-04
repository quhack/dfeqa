from typing import Union, Tuple
import pandas as pd
import seaborn as sns
import regex
_pat1 = regex.compile(r'\{\{([^\{\}\|]*)\}\}')
_pat3 = regex.compile(r'{{((?:[^<>={}!]|{{(?1)}})+)'
                        r'(\<\=|\>\=|\!\=|\<|\=|\>)'
                        r'((?:[^|{}]|{{(?3)}})+)\|'
                        r'((?:[^{}|]++|{(?!{)|}(?!})|(?<=\\)\||{{(?4)}}|(?0))*)\|'
                        r'((?:[^{}]++|{(?!{)|}(?=})|{{(?5)}}|(?0))*)}}')


def summarise_str_lengths(data_column: pd.Series):
    """ takes a Pandas Series and returns a Series of length frequencies"""

    s = data_column.str.len().fillna(0).astype(int).value_counts()
    # returned series will have missing data points filled with 0
    return s.reindex(range(max(s.index) + 1)).fillna(0).astype(int)


def fd(data: pd.DataFrame|pd.Series|list, cols: list = list(), ids: list = None):
    """frequency distributions - provide a dataframe with cols to create frequencies from or
    a list of Pandas Series
    return long-form summary of freqency distribution of specified columns
    optional ids provides labels for groups in returned data"""

    if isinstance(data, pd.Series):
        # single series
        return summarise_str_lengths(data)
    elif isinstance(data, (list, tuple)):
        if not(ids): ids = [x.name for x in data]
        # collection of series
        return pd.concat([
            summarise_str_lengths(x).reset_index().rename(columns={x.name: 'length'}).assign(group = ids[i])
            for i, x in enumerate(data)
        ], axis=0)
    elif isinstance(data, pd.DataFrame):
        # pandas dataframe
        # process all if no columns specified
        if not(cols):
            cols = data.columns
        if not(ids): ids = [x for x in cols]
        return pd.concat([
            summarise_str_lengths(data[x]).reset_index().rename(columns={x: 'length'}).assign(group = ids[i])
            for i,x in enumerate(cols)
        ], axis=0)


def freqchart(chartdata:pd.DataFrame, value_col: str, freq_col: str, groups:str = None,
        min_range: int|tuple|list = None, max_range: int|tuple|list = None,
        x_rescale: int|list=None):
    """return barchart comparing frequency dists of a number of defined columns
    optionally pass min_range and max_range (integer, list or tuple) for vlines indicating range"""
    
    p = sns.barplot(x=value_col, y=freq_col, hue = groups,
        data = chartdata
        )
    if x_rescale:
        assert isinstance(x_rescale, (int, list))
        ticks = p.get_xticks()
        if isinstance(x_rescale, int):
            p.set_xticks([x for i,x in enumerate(ticks) if i%2 == 0])
        elif isinstance(x_rescale, list):
            p.set_xticks([ticks[x] for x in x_rescale])
 
    # vertical lines showing range
    if isinstance(min_range,(list,tuple)):
        for i,x in enumerate(min_range):
            p.axvline(x=x, color=sns.color_palette()[i])
    elif isinstance(min_range,int):
        p.axvline(x=min_range, color=sns.color_palette()[0])

    if isinstance(max_range,(list,tuple)):
        for i,x in enumerate(max_range):
            p.axvline(x=x, color=sns.color_palette()[i])
    elif isinstance(max_range,int):
        p.axvline(x=max_range, color=sns.color_palette()[0])

    return p


def parse_text (in_text, data: Union[tuple, dict]) -> str:
    """pattern 1 returns the value stored in data store.
    pattern 3 is split into 3 parts. Part 2 (a string) is returned if
    part 1 is true, else part 3.
    Part 1 in pattern 3 can be made up of a string, data store key and
    one of </<=/=/>=/>."""

    def _extract_from(key, data: Union[tuple, dict]) -> str:
        """returns first find of key from dictionary or tuple of dictionaries"""
        if not isinstance(data, tuple):
            data = (data,)
        found=None
        for dataset in data:
            assert isinstance(dataset, dict)
            if key in dataset:
                found = str(dataset[key])
                break
        else:
            found = str(key)
        return found

    def _f1(match_obj):
        _s = match_obj.group(1)
        return _extract_from(_s, data)

    def _f3(match_obj):
        """return a string from a 'f3' format string"""
        _s = match_obj.group(0)
        _op1 = match_obj.group(1).strip()
        _operator = match_obj.group(2).strip()
        assert _operator in ["<","<=","=",">=",">", "!="], \
            "operator in text template not supported"
        _op2 = match_obj.group(3).strip()
        operand1 = _extract_from(_op1,data)
        operand2 = _extract_from(_op2,data)
        operations = {
            "=" : lambda _x, _y: _x == _y,
            "<=" : lambda _x, _y: _x <= _y,
            ">=" : lambda _x, _y: _x >= _y,
            "<" : lambda _x, _y: _x < _y,
            ">" : lambda _x, _y: _x > _y,
            "!=" : lambda _x, _y: _x != _y
        }
        return regex.sub(_pat3, _f3, str(match_obj.group(4))) \
            if operations[_operator](operand1, operand2) \
            else regex.sub(_pat3, _f3, match_obj.group(5))

    returntext = regex.sub(_pat3, _f3, in_text)
    return regex.sub(_pat1, _f1, returntext)
