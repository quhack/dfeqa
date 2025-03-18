valid_name_regex = r"^[\d\-.,\'’\"\+\*\(\)\[\]\ `_\/\\A-Za-zÀ-ÖØ-öø-ÿĀ-ſ]*[A-Za-zÀ-ÖØ-öø-ÿĀ-ſ]+[\d\-.,\'’\"\+\*\(\)\[\]\ `_\/\\A-Za-zÀ-ÖØ-öø-ÿĀ-ſ]*$"
"""string is made up of alphanum and at least one alpha"""

def valid_upn(UPNstring: str):
    let_num_map = 'ABCDEFGHJKLMNPQRTUVWXYZ'
    if not isinstance(UPNstring, str):
        return False
    elif UPNstring == "":
        return False
    elif len(UPNstring) != 13:
        return False
    elif not UPNstring[0].isalpha() or UPNstring[0].islower():
        return False
    elif not UPNstring[1:-1].isdigit():
        return False
    elif not UPNstring[-1].isalnum() and not UPNstring[-1].islower():
        return False
    elif UPNstring[-1] in 'IOS':
        return False
    upn_sum = 0
    for i, x in enumerate(UPNstring[1:], 2):
        if x.isdigit():
            upn_sum += int(x) * i
        else:
            upn_sum += let_num_map.index(x) * i
    check_letter = let_num_map[upn_sum % 23]
    if check_letter != UPNstring[0]:
        return False
    return True
