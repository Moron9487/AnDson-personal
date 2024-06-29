import re


def _is_month_string(month_string: str) -> bool:
    # This function will not check whether the argument is string or not
    pattern = r'^\d{4}-\d{2}$'
    if re.match(pattern, month_string):
        month = int(month_string.split("-")[1])
        if month >= 1 and month <= 12:
            return True
        else:
            return False
    else:
        return False
    
def _is_date_string(date_string: str) -> bool:
    # This function will not check whether the argument is string or not
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if re.match(pattern, date_string):
        string_section = date_string.split("-")
        month = int(string_section[1])
        day = int(string_section[2])
        if month >= 1 and month <= 12:
            if day >= 1 and day <= 31:
                return True
            else:
                return False
        else:
            return False
    else:
        return False
    
def _is_available_ranking(ranking: int) -> bool:
    return ranking >= 0 and ranking <= 10