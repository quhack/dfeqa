from datetime import datetime

def year_group(dob: str, year: int, format: str = '%d%m%Y', upper_year: int = 8):
    assert year > 2000 and year <= datetime.now().year
    dob_asdate = datetime.strptime(dob,format)
    dob_month = dob_asdate.month
    dob_year = dob_asdate.year
    ncyear = year - (dob_year + 5)
    ncyear += -1 if dob_month >= 9 else 0
    outstring = 'y' + str(ncyear)
    if ncyear + 0 == 0: outstring = 'r'
    if ncyear + 0 < 0: outstring = 'under_r'
    if ncyear + 0 > upper_year: outstring = 'abovey' + str(upper_year)
    return outstring
