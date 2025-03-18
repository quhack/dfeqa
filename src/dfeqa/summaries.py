from typing import Union, Tuple
import warnings
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns
import regex

_pat1 = regex.compile(r'\{\{([^\{\}\|]*)\}\}')
_pat3 = regex.compile(r'{{((?:[^<>={}!]|{{(?1)}})+)'
                        r'(\<\=|\>\=|\!\=|\<|\=|\>)'
                        r'((?:[^|{}]|{{(?3)}})+)\|'
                        r'((?:[^{}|]++|{(?!{)|}(?!})|(?<=\\)\||{{(?4)}}|(?0))*)\|'
                        r'((?:[^{}]++|{(?!{)|}(?=})|{{(?5)}}|(?0))*)}}')


def fd(data: pd.DataFrame|pd.Series|list, cols: list = None, ids: list = None, long=False, value_columnname=None):
    """frequency distributions - provide a dataframe with cols to create frequencies from or
    a list of Pandas Series
    return long-form summary of freqency distribution of specified columns
    optional ids provides labels for groups in returned data"""

    def _series_fd(s: pd.Series):
        return s.value_counts(dropna=False)

    class _fd:
        def __init__(self, data: (list | pd.Series | pd.DataFrame), cols=None, ids=None):
            assert isinstance(data, (list, pd.Series, pd.DataFrame))
            self._data = data
            self._cols = cols
            self._ids = ids

        @property
        def source(self):
            return self._data

        @property
        def long_data(self):
            d = pd.DataFrame()
            for colnam, col in self._data.items():
                d = pd.concat([d, col.reset_index(drop=True).assign(group=colnam)], axis=0)
            return d

        @property
        def dist(self):
            d = pd.DataFrame()
            if isinstance(self._data, pd.Series):
                d = pd.DataFrame(_series_fd(self._data).fillna(0).astype(int)\
                    .reset_index(drop=False)).rename(columns={self._data.name:'value'})
            elif isinstance(self._data, (list, tuple)):
                assert self._ids is None or len(self._data) == len(self._ids)
                # also expect ._ids elements are unique, but if not an error will be raised
                colnames = self._ids or [x.name for x in self._data]
                d = pd.concat([_series_fd(x.rename(None)).\
                    rename(colnames[i]) for i, x in enumerate(data)], axis=1).fillna(0)\
                        .astype(int).reset_index(drop=False).rename(columns={'index': 'value'})
            else:
                assert isinstance(self._data, pd.DataFrame)
                target_columns = self._cols if self._cols is not None else self._data.columns.tolist()
                d = pd.concat([_series_fd(x).\
                    rename(label) for label, x in self._data.items() if label in target_columns], axis = 1)\
                        .fillna(0).astype(int).reset_index(drop=False).rename(columns={'index': 'value'})
                if self._ids is not None:
                    assert len(target_columns) == len(self._ids)
                    d = d.rename(columns={x: self._ids[i] for i,x in enumerate(target_columns)})

            return d.sort_values('value').reset_index(drop=True)

        @property
        def dist_long(self):
            return self.dist.melt(id_vars=['value'], var_name="group", value_name="count")

    if long:
        returndata = _fd(data, cols=cols, ids=ids).dist_long
    else:
        returndata = _fd(data, cols=cols, ids=ids).dist
    if value_columnname:
        returndata = returndata.rename(columns = {'value': value_columnname})
    return returndata

def freqchart(chartdata:pd.DataFrame, value_col: str, freq_col: str = None, groups:str = None,
        min_range: int|tuple|list = None, max_range: int|tuple|list = None,
        x_rescale: int|list=None):
    """return barchart comparing frequency dists of a number of defined columns
    optionally pass min_range and max_range (integer, list or tuple) for vlines indicating range"""
    warnings.warn("freqchart() is deprecated and will be removed in a future release. Use barchart() instead.", DeprecationWarning)
    return barchart(chartdata, cats=value_col, values=freq_col, groups=groups,\
        vlines=[(x for x in min_range),(x for x in max_range)],
        x_rescale=x_rescale)

def barchart(chartdata:pd.DataFrame | pd.Series , cats: str=None, values: str = None, groups:str = None,
        xlabel: str=None, ylabel: str=None,
        vlines: int|tuple|list = None,
        x_rescale: int|list=None):
    """return barchart comparing frequency dists of a number of defined columns
    optionally pass vlines (integer, list or tuple) for vlines indicating range"""

    y_integers = None
    p = None
    plt.close("all")
# dataframe with cats and values defined
    if isinstance(chartdata, pd.DataFrame) and cats is not None and values is not None:
        p = sns.barplot(x=cats, y=values, hue = groups,
            data = chartdata
            )
        y_integers = True if chartdata[values].apply(isinstance,args = [int]).all() else False
# dataframe with only values defined
    elif isinstance(chartdata, pd.DataFrame) and values is not None and cats is None and isinstance(values,str):
        i='i' if values != 'i' else '_i'
        cols = [groups] if groups else []
        v = values if isinstance(values,list) else [values]
        cols = cols + v
        d = chartdata.copy()[cols].reset_index(drop=False, names=i)
        p = sns.barplot(data = d, x=i, y=values, hue=groups)
        y_integers = True
# dataframe with only cats defined
    elif isinstance(chartdata, pd.DataFrame) and values is None and cats is not None and isinstance(cats,str):
        p = sns.barplot(data=chartdata[cats].value_counts(dropna=False))
        y_integers = True
# pd.Series
    elif isinstance(chartdata, pd.Series):
        p = sns.barplot(chartdata)
        y_integers = True
# list of series
    elif isinstance(chartdata, list) and all(isinstance(x, pd.Series) for x in chartdata):
        names=None
        if groups is not None:
            names = groups
        elif all(x.name for x in chartdata):
            names = [x.name for x in chartdata]
        else:
            names = ["group" + str(x+1) for x in range(len(chartdata))]
        cd = []
        for i,x in enumerate(chartdata):
            y = x.copy()
            y.index = y.index.rename(None)
            y = y.reset_index(drop=False, name="value").assign(group=names[i])
            cd.append(y)
        y_integers = True if all(x['value'].apply(isinstance,args = [int]).all() for x in cd) else False
        p = sns.barplot(pd.concat(cd), x='index', y='value', hue='group')

    else:
        raise RuntimeError('unable to generate chart from given parameters')

    # vertical lines
    x_map = {a.get_text(): i for i,a in enumerate(p.get_xaxis().get_ticklabels())}
    def drawlines(lines):
        if lines is None:
            return
        elif not isinstance(lines,(list,tuple)):
            p.axvline(x=x, color=sns.color_palette()[0])
        elif isinstance(lines,(tuple,list)) and all(isinstance(x,(list,tuple)) for x in lines):
            for line in lines:
                drawlines(line)
        else:
            for i,x in enumerate(lines):
                try:
                    p.axvline(x=x_map[str(x)], color=sns.color_palette()[i])
                except KeyError:
                    print("value for vline is not on x axis")
    drawlines(vlines)

    if x_rescale:
        assert isinstance(x_rescale, (int, list))
        ticks = p.get_xticks()
        if isinstance(x_rescale, int):
            p.set_xticks([x for i,x in enumerate(ticks) if i % x_rescale == 0])
        elif isinstance(x_rescale, list):
            p.set_xticks([ticks[x] for x in x_rescale])
 
    if y_integers:
        p.yaxis.set_major_locator(MaxNLocator(integer=True))
    
    p.set_xlabel(xlabel)
    p.set_ylabel(ylabel)

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


def status_summary(objectives: list[str], rags: list[str], down=False):
    """return a formatted list of statements with RAG statuses;
    specify down=true to list verically, or leave the default to list across the page
    rags (statuses) can be None, red, amber, green or grey"""
    assert len(objectives) == len(rags)
    df = pd.DataFrame(objectives)
    if not down:
        df = df.T
    s = df.style.hide().hide(axis=1)

    s.set_table_styles([
        {'selector': 'td', 'props': 'text-align: center; border-radius: 10px; width: {}%;'.format(str(int(100 / len(objectives))))},
        {'selector': '.grey', 'props': 'background-color:rgb(205, 205, 205);'},
        {'selector': '.green', 'props': 'background-color: #e6ffe6;'},
        {'selector': '.amber', 'props': 'background-color:#ffdfb3;'},
        {'selector': '.red', 'props': 'background-color: #ffe6e6;'},
    ], overwrite=False)
    cell_colour = pd.DataFrame(rags)
    if not down:
        cell_colour = cell_colour.T
    return s.set_td_classes(cell_colour)
