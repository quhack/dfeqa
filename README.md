# Introduction 
DfE-QA Python helper functions - covering a variety of checks primarily to report on the quality of data.

# Getting Started

`python -m pip install dfeqa`

or you can install with additional dependencies for analysis using Quarto with:

`python -m pip install dfeqa[user]`

# Using

Once `dfeqa` has been installed you can create new project files at the shell:

`dfeqa create data_quality my_dq_report.qmd`

Type `dfeqa create help` for a list of templates.

You don't need to use the templates at all - you can just import the functions into your own scripts as follows

`from dfeqa import x [,y...]`

for example:

`from dfeqa import load_census, barchart as bc`

- `load_census` Loads census data from the PDR database.
  - `year`* (the only mandatory argument) this is the year of the census, and if no other arguments are given, all records will be extracted.
  - `term` one of 'Spring', 'Summer', 'Autumn'
  - `NCYear` The National Curriculum year group. Can be a single year group, or a list of year groups.
  - `columns` If not provided, all columns will be extracted. A single column name or a list of column names can be provided.
  - `conn` Connection string defining how database connection should be made. If not provided will try to use an environment variable `DEFAULT_CONN`.

Rather than including connection strings in your scripts, you may want to set an environment variable which contains a connection string. If you are able, use the key `DEFAULT_CONN` and as well as `load_census()` picking this up by default, you can use `get_default_conn()` to pull the string and use it elsewhere (passing to Pandas to query a table for example). If your IT admin doesn't allow you to add environment variables, you can create a .env file instead. Create a file with the extension .env and write "DEFAULT_CONN=(connection string)" in it. The connection string will look something like: mssql+pyodbc://database_address(,port)/db_name?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server. So opening the file, it should be something like:

```
DEFAULT_CONN=mssql+pyodbc://MYSQLSERVER\SERVERNAME,25678/MY_DB?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server

```

- `get_table_metadata` Loads metadata from SQL table (including column names)
  - `tablename`* this can be a view; can include domain, but not databasename or higher. `dbo.mytable` or `mytable` is fine, but will throw an error if you try `mydatabase.dbo.mytable`.
  - `conn`* connection object or string

- `valid_name_regex` A regex string to identify valid name strings. They should contain letters, including unicode letters with accents. Other characters such as apostrophes, hyphens and numbers are also allowed, but cannot be the only contents of the string. Ideal for use in calculating 'valid' flags.

- `valid_upn` Function to check the format of a Unique Pupil Number and the correct check digit is applied. Also ideal for calculating 'valid' flags.

- `year_group` Function to calculate the expected National Curriculum year group given a date of birth.
  - `dob`* String containing the date of birth
  - `year`* String containing the test-year for which the group is required (i.e. the calendar year in which May falls).
  - `format` Format of the date of birth. If not supplied, defaults to DDMMYYYY.
  - `upper_year` defaults to reporting years R to 8, but can set upper limit to something else by passing an integer in this argument.

- `fd` Function to create multiple frequency distributions in long format from a Series, a Data Frame or a list of Series.
  - `data`* A Series (for a single frequency distribution) a DataFrame (can be one or more distributions) a list of Series (for multiple distributions)
  - `cols` If `data` is a DataFrame then this argument specifies which columns should be summarised.
  - `ids` Labels to identify the distributions in the output. If not provided, the original column names will be used. This is useful if analysing datasets in the same format from different year groups (provided as a list of Series).
  - `long` Data is provided in wide format unless this flag is set, when it is returned in long format.
  - `value_columnname` You may want to rename the column used to report the instance value if you are passing straight to `barchart()`. This was `label` in 0.0.3.

`fd` (frequency distribution) is a convenience function to create frequency distributions in a format suitable for displaying as a table (wide-format) or data to be passed to a chart-plotting function (long-format). It will also create a consistent set of values when generating counts of multiple datasets. For example if one dataset contains a value that the other doesn't, it will create a zero for that value in the resulting data for the dataset with no instances.

You can pass a dataframe, a series, or a list of series.

```{python}
s1 = seaice[seaice['Date'].dt.year == 1980]['Date'].dt.month
s2 = seaice[seaice['Date'].dt.year == 2010]['Date'].dt.month
df = pd.DataFrame({'s1':s1,'s2':s2})

fd(df, cols=['s1','s2']) # returns a table suitable for printing
fd(s1) # a simple fd using a single series
fd([s1,s2],ids=['1980','2010'], long=True, value='month') # suitable for passing to barchart()

```

- `freqchart` _deprecated_ Function to create a barchart comparing frequency distributions of a number of defined columns; optionally pass min_range and max_range (integer, list or tuple) for vlines indicating range
  - `chartdata`* Pandas dataframe in long-format containing the data to be visualised.
  - `value_col` The column defining the values that were counted - these will be set along the x-axis.
  - `freq_col` The column containing the frequency counts.
  - `groups` The column containing identifiers where multiple groups have been summarised.
  - `min_range` Optional vertical line indicating the lower end of the range. Multiple lines can be drawn if a list is passed.
  - `max_range` As `min_range` above - intended to indicate upper end of range.
  - `x_rescale` pass an integer specifying the number of values to skip between values on x-axis, or a list of the indexes of the values to keep in x-axis

- `barchart` Function to create a barchart comparing frequency distributions of a number of defined columns; optionally pass `vlines` for vertical lines indicating range
  - `chartdata`* Pandas data containing the data to be visualised - may be dataframe, series or list of series.
  - `cats` The column defining categories to be represented in the chart - these will be set along the x-axis.
  - `values` The column containing the continuous values to be plotted on the y-axis.
  - `groups` The column containing identifiers representing multiple groups.
  - `xlabel` String to label the x-axis.
  - `ylabel` String to label the y-axis.
  - `vlines` integer, list, tuple or list/ tuple  of lists/ tuples to draw vertical lines on the plot - these can be used to represent ranges in different groups. Note these are now *values* rather than *indexes* as was the case in 0.0.3.
  - `x_rescale` pass an integer specifying the number of values to skip between values on x-axis, or a list of the indexes of the values to keep in x-axis

The following examples can be run with the following setup code:

```
import seaborn as sns
from dfeqa import barchart

seaice = sns.load_dataset('seaice')
year_counts = seaice['Date'].dt.year.value_counts()
```

**Format 1**: Dataframe with `cats` and `values` arguments

`cats` and `values` contain the column names for the values that will appear on the x-axis and y-axis respectively.

`barchart(chartdata=year_counts.reset_index(drop=False), cats='Date', values='count', x_rescale=5)`

**Format 2**: Dataframe with `cats` but no `values` arguments

This is the only form of `barchart()` that analyses the data in some way before rendering a chart. It counts the instances of the values in `cats` and plots those counts on the y-axis.

```
barchart(seaice['Date'].dt.year.reset_index(drop=False), cats='Date', x_rescale=5)`
barchart(pd.DataFrame(seaice['Date'].dt.year), cats='Date', x_rescale=5)
```

**Format 3**: Dataframe with `values` but no `cats` arguments

If a dataframe is passed, but no `cats` argument, it is assumed the values for the x-axis are in the index.

```{python}
barchart(pd.DataFrame(seaice['Date'].dt.year.value_counts()), values='count',x_rescale=5)

# create dataframe with month as index and only two years in the 'year' column
si = seaice.copy().assign(year = seaice['Date'].dt.year, month = seaice['Date'].dt.month)[['year','month']].value_counts().reset_index(drop=False)
si = si[si['year'].isin([1980,2010])].set_index('month')

barchart(si, values='count', groups='year')
```

**Format 4**: Series

`barchart(seaice['Date'].dt.year.value_counts(), x_rescale=5)`

**Format 5**: List of Series

Groups can be defined in the format 1 (dataframe with `cats` and `values`) as well as this one (format 5; List of Series)

```{python}
s1 = seaice[seaice['Date'].dt.year == 1980]['Date'].dt.month.value_counts()
s2 = seaice[seaice['Date'].dt.year == 2010]['Date'].dt.month.value_counts()

barchart([s1,s2], groups=['1980','2010'])
```

- `parse_text` Templating system for generating dynamic text. 
  - `in_text` Text with variables surrounded by double curly-braces `{{` `}}` to indicate where text should be dynamically generated. If the braces only contain a variable name within the braces then the value of the variable is inserted in the text. If there are three segments separated by a vertical bar, then the first segment is a boolean condition; if true the second segment is returned, otherwise the last segment is returned. 
  - `data` A dictionary or a tuple of dictionaries containing data which can be referenced in the dynamic text.

For example:

`parse_text("{{1=1|{{a}}|B}}", {'a':'(-)'})`

will generate:

`(-)`

- `status_summary`
  - `objectives`
  - `rags`
  - `down`

`status_summary` can be used to report any list of objectives or goals, but was intended primarily to relate quality back to organisational goals. This was an idea promulgated by DQHub (ONS) at DataConnect21. The idea is to relate the importance of the findings in the report back to the organisational goals. I've put the high-level DfE objectives in the `data_quality` template, but these could easily be broken down further to illustrate lower-level objectives.

A list of strings should be passed in the `objectives` argument, and a list of strings indicating the status of each is passed in `rags`. These should be one of `None`, 'grey', 'red', 'amber' or 'green'. The idea was there may be objectives that aren't directly addressed in the report, and so are coloured grey - the rest get a RAG colour to indicate status - ideally at the top of the report to summarise what the report contains.

# Build and Test
python -m pip install dfeqa[dev]
You will need to be operating within the DfE estate to run all the tests as some of them call the dfe database. Set an environment variable `default_conn` with the connection string to the PDR database. Then run `pytest` in a shell.

# Contribute
Get in touch and I'll talk you through it.
