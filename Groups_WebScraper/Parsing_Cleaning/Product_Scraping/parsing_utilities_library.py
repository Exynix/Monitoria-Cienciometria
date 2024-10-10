import re
from typing import Optional
from enum import Enum

from bs4 import BeautifulSoup

#  ---------------------- Definición de enumeracion de mensajes de verificacion ---------------------- 
class MensajeVerficacion(Enum):
    TABLA_VALIDA = 1
    TABLA_SIN_CONTENIDOS = 0
    TABLA_INVALIDA = -1

    ISSN_INVALIDO = -5

#  ---------------------- Definition of Functions ---------------------- 

# Checks if a given HTML table has content beyond the header and columns.
# Input: Complete HTML table to check. Number of "informative" rows (informative can be headers, column names. etc).
def check_if_table_has_content(html_table: str, number_of_information_rows: int) -> int:
    soup = BeautifulSoup(html_table, "html.parser")

    total_number_of_rows = len(soup.find_all("tr"))

    if (total_number_of_rows <= number_of_information_rows):

        # If the total number of rows is equal to the informative rows, then the table is empty.
        if (total_number_of_rows == number_of_information_rows):
            return MensajeVerficacion.TABLA_SIN_CONTENIDOS.value
        # In any other case, the table is invalid.
        else:
            return MensajeVerficacion.TABLA_INVALIDA.value

    # A number of total rows bigger than the num. of informative rows means that there's at least one product. 
    if (total_number_of_rows > number_of_information_rows):
        return MensajeVerficacion.TABLA_VALIDA.value

# -------------

# Verificacion de existencia de tag <img>. Dice si el producto académico fue avalado.
def revisar_producto_avalado(fila_html: str) -> str:
     
    if (fila_html.td.img != None):
        return "Si"
    else:
        return "No"

# ------------
# ------------
def check_if_string_is_alphanumeric (input_string) -> bool:

    alphanumeric_regex = "[A-Za-z0-9]+"
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
        print("No match found.")
        print(" - Pattern: ", regex_pattern)
        print(" - String being searched: ", repr(string_to_check))
        return None
    
   # If the function returns false, then the string doesn't have any digits or numbers. That's why we return null.
    if check_if_string_is_alphanumeric (search_result.group(0)) == False:
        print("string sent is whitespace or doesn't contain alphanumeric characters.", repr(string_to_check))
        return None
    else:
        return search_result.group(0).strip()
 
# ------------



# ------------




# ------------