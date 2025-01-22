# Introduction 
DfE-QA helper functions - covering a variety of checks primarily to report on the quality of data.

# Getting Started
python -m pip install dfeqa

# Using

import the items as follows

`from dfeqa import x [,y...]`

- `load_census` Loads census data from the PDR database.
  - `year`* (the only mandatory argument) this is the year of the census, and if no other arguments are given, all records will be extracted.
  - `term` one of 'Spring', 'Summer', 'Autumn'
  - `NCYear` The National Curriculum year group. Can be a single year group, or a list of year groups.
  - `columns` If not provided, all columns will be extracted. A single column name or a list of column names can be provided.
  -`conn` Connection string defining how database connection should be made. If not provided will try to use an environment variable `default_conn`.

- `valid_name_regex` A regex string to identify valid name strings. They should contain letters, including unicode letters with accents. Other characters such as apostrophes, hyphens and numbers are also allowed, but cannot be the only contents of the string. Ideal for use in calculating 'valid' flags.

- `valid_upn` Function to check the format of a Unique Pupil Number and the correct check digit is applied. Also ideal for calculating 'valid' flags.

- `year_group` Function to calculate the expected National Curriculum year group given a date of birth.
  - `dob`* String containing the date of birth
  - `year`* String containing the test-year for which the group is required (i.e. the calendar year in which May falls).
  - `format` Format of the date of birth. If not supplied, defaults to YYYYMMDD.

- `summarise_str_lengths` Function which takes a Pandas Series and returns a frequency distribution.
  - `data_column` Pandas Series containing strings to be analysed.

- `fd` Function to create multiple frequency distributions in long format from a Series, a Data Frame or a list of Series.
  - `data`* A Series (for a single frequency distribution) a DataFrame (can be one or more distributions) a list of Series (for multiple distributions)
  - `cols` If `data` is a DataFrame then this argument specifies which columns should be summarised.
  - `ids` Labels to identify the distributions in the output. If not provided, the original column names will be used. This is useful if analysing datasets in the same format from different year groups (provided as a list of Series).

- `freqchart` Function to create a barchart comparing frequency distributions of a number of defined columns; optionally pass min_range and max_range (integer, list or tuple) for vlines indicating range
  - `chartdata`* Pandas dataframe in long-format containing the data to be visualised.
  - `value_col` The column defining the values that were counted - these will be set along the x-axis.
  - `freq_col` The column containing the frequency counts.
  - `groups` The column containing identifiers where multiple groups have been summarised.
  - `min_range` Optional vertical line indicating the lower end of the range. Multiple lines can be drawn if a list is passed.
  - `max_range` As `min_range` above - intended to indicate upper end of range.

- `parse_text` Templating system for generating dynamic text. 
  - `in_text` Text with variables surrounded by double curly-braces `{{` `}}` to indicate where text should be dynamically generated. If the braces only contain a variable name within the braces then the value of the variable is inserted in the text. If there are three segments separated by a vertical bar, then the first segment is a boolean condition; if true the second segment is returned, otherwise the last segment is returned. 
  - `data` A dictionary or a tuple of dictionaries containing data which can be referenced in the dynamic text.

For example:

`parse_text("{{1=1|{{a}}|B}}", {'a':'(-)'})`

will generate:

`(-)`

# Build and Test
python -m pip install dfeqa[dev]
You will need to be operating within the DfE estate to run all the tests as some of them call the dfe database. Set an environment variable `default_conn` with the connection string to the PDR database. Then run `pytest` in a shell.

# Contribute
Get in touch and I'll talk you through it.
