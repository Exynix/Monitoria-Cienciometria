import re

# ------------
def check_string_not_whitespace (input_string):

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