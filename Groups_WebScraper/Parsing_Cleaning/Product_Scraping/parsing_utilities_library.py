import re
from typing import Optional

# ------------
def check_string_not_whitespace (input_string) -> bool:

    alphanumeric_regex = "[A-Za-z0-9]*"
    search_result = re.search(alphanumeric_regex, input_string) 
    
    if search_result == None:
        return False;
    else:
        return True;

# ------------

def revisar_string_vacio(input_string: str) -> str:
    if(len(input_string) == 0):
        return None
    else:
        return input_string

# ------------
def match_and_verify_regex_expression (string_to_check: str, regex_pattern: str) -> Optional[str]:

    # Regex mathching.
    search_result = re.search (regex_pattern, string_to_check) 

    # Verification of match existance.
    if search_result == None:
        print("No match found")
        return None
    
   # If the function returns false, then the string doesn't have any digits or numbers. That's why we return null.
    if check_string_not_whitespace(search_result.group(0)) == False:
        print("string sent is whitespace or doesn't contain alphanumeric characters.", repr(string_to_check))
        return None
    else:
        return search_result.group(0).strip()
    