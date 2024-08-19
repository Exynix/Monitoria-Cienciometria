#  ---------------------- Importación de librerias ---------------------- 
from enum import Enum
from typing import Optional
import sys

import knime.scripting.io as knio

from bs4 import BeautifulSoup
import pandas as pd
import re
#  ---------------------- Definición de enumeracion de mensajes de verificacion ---------------------- 
class MensajeVerficacion(Enum):
    TABLA_VALIDA = 1
    TABLA_SIN_CONTENIDOS = 0
    TABLA_INVALIDA = -1

    ISSN_INVALIDO = -5

#  ---------------------- Definition of Functions ---------------------- 


# -------------------------------- Functions from the parsing utils library -------------------------------- 

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
 
# ------------ Functions specific to parsing of art_production. -----------------

def parse_obras_productos_table(art_products_html_table_rows, built_products, group_code: int):

    processed_rows = 0

    for row in art_products_html_table_rows:

        # Check if the actual row is a header row. 
        if row.find_all("td")[0].text == "Industrias creativas y culturales":
            processed_rows += 1        
            break
        
        # If the row is a product, we parse it.
        row_cells = row.find_all("td")
        second_cell = row_cells[1]
        br_tags = second_cell.find_all("br")
        strong_tags = second_cell.find_all("strong")

        # If not a header row, then it's an Obra | Producto.
        is_validated = revisar_producto_avalado(row)
        product_name = second_cell.contents[0].strip()

        creation_date_line = br_tags[0].next_sibling
        creation_date_line = creation_date_line.rstrip()
        creation_date = match_and_verify_regex_expression(creation_date_line, "(?<=Fecha de creación:).*(?=Disciplina o ámbito de origen:)")

        if strong_tags:
            evaluation_instance_line = strong_tags[0].next_sibling
            evaluation_instance_line = evaluation_instance_line.rstrip()
            event_name = match_and_verify_regex_expression(evaluation_instance_line, "(?<=Nombre del espacio o evento:).*(?=, Fecha de presentación:)")
            presentation_date = match_and_verify_regex_expression(evaluation_instance_line, "(?<=Fecha de presentación:).*(?=, Entidad convocante 1:)")
            organizing_entity = match_and_verify_regex_expression(evaluation_instance_line, "(?<=Entidad convocante 1:).*(?=(.*|Entidad convocante 1:))")
        else:
            event_name = None
            presentation_date = None
            organizing_entity = None

        # After parsing, we create and append the product to the built products list.
        new_product = {
            "Codigo Grupo": group_code,
            "Nombre Producto": product_name,
            "Fecha Creacion": creation_date,
            "Fecha Presentacion": presentation_date,
            "Nombre Espacio o Evento": event_name,
            "Entidad Convocante": organizing_entity,
            "Subcategoria": "Obra o Producto",
            "Avalado?": is_validated
        }

        built_products.append(new_product)

        processed_rows += 1        

    # Delete all the rows processed, such that the list can be used to parse the next subcategory.
    # The additional + 1 is to avoid the "Eventos Artísticos" header row.
    del art_products_html_table_rows[:processed_rows + 1]
    
# Left intentionally blank to represent that the table has to be parsed, but empty because no group with this type of
# product has been found yet.
def parse_industrias_creativas_table(art_product_html_table_rows, built_products, group_code: int): 
    pass


def parse_eventos_artisticos_table(art_products_html_table_rows, built_products, group_code: int):

    processed_rows = 0

    for row in art_products_html_table_rows:

        # Check if the actual row is a header row. 
        if row.find_all("td")[0].text == "Talleres de Creación":
            processed_rows += 1        
            break
        
        # If the row is a product, we parse it.
        row_cells = row.find_all("td")
        second_cell = row_cells[1]
        br_tags = second_cell.find_all("br")

        # If not a header row, then it's an Obra | Producto.
        is_validated = revisar_producto_avalado(row)
        product_name = match_and_verify_regex_expression(second_cell.contents[0].strip(), "(?<=Nombre del evento:).*").strip()

        dates_line =  br_tags[0].next_sibling 
        start_date = start_date.rstrip()
        start_date = match_and_verify_regex_expression(dates_line[1:], "(?<=Fecha de inicio:).*?(?=(\d\d:\d\d:\d\d\.\d|,))")
        end_date = match_and_verify_regex_expression(dates_line, "(?<=Fecha de finalización:).*?(?=(\d\d:\d\d:\d\d\.\d)|)")

        # After parsing, we create and append the product to the built products list.
        new_product = {
            "Codigo Grupo": group_code,
            "Nombre Producto": product_name,
            "Fecha Inicio": start_date,
            "Fecha Finalizacion": end_date,
            "Subcategoria": "Evento Artistico",
            "Avalado?": is_validated
        }

        built_products.append(new_product)

        processed_rows += 1        

    # Delete all the rows processed, such that the list can be used to parse the next subcategory.
    del art_products_html_table_rows[:processed_rows]
    


def parse_talleres_creacion_table(art_products_html_table_rows, built_products, group_code: int):
    
    processed_rows = 0

    for row in art_products_html_table_rows:

        # There's no more need to check for header rows, as this is the last sub-category. It goes to the end of the table.
        
        row_cells = row.find_all("td")
        second_cell = row_cells[1]
        br_tags = second_cell.find_all("br")

        # If not a header row, then it's an Obra | Producto.
        is_validated = revisar_producto_avalado(row)
        product_name = match_and_verify_regex_expression(second_cell.contents[0].rstrip(), "(?<=Nombre del taller:).*?(?=,Tipo de taller:)").strip()

        type_of_workshop = match_and_verify_regex_expression(second_cell.contents[0].rstrip(), "(?<=Tipo de taller:).*?(?=,Participación:)").strip()

        dates_line =  br_tags[0].next_sibling 
        dates_line = dates_line.rstrip()
        start_date = match_and_verify_regex_expression(dates_line[1:], "(?<=Fecha de inicio:).*?(?=(\d\d:\d\d:\d\d\.\d|,))")
        end_date = match_and_verify_regex_expression(dates_line, "(?<=Fecha de finalización:).*?(?=(\d\d:\d\d:\d\d\.\d)|)")

        # After parsing, we create and append the product to the built products list.
        new_product = {
            "Codigo Grupo": group_code,
            "Nombre Producto": product_name,
            "Fecha Inicio": start_date,
            "Fecha Finalizacion": end_date,
            "Tipo Taller": type_of_workshop,
            "Subcategoria": "Talleres de Creación",
            "Avalado?": is_validated
        }

        built_products.append(new_product)

        processed_rows += 1        

    # Delete all the rows processed, such that the list can be used to parse the next subcategory.
    del art_products_html_table_rows[:processed_rows]
    



#  ---------------------- Interpretacion de input como DF ---------------------- 
art_products_df = knio.input_tables[0].to_pandas()
    

#  ---------------------- Creación de variables relevantes ---------------------- 
tablas_html = art_products_df["HTML_Tabla_ProductosArte"]
codigos_grupos = art_products_df["Codigo_Grupo"]

built_products = []

#  ---------------------- Parsing y procesamiento ---------------------- 

# Ciclo exterior para recorrer cada grupo
for index, table in enumerate(tablas_html):
    print("Codigo del grupo: ", codigos_grupos[index])
    # We have to check the 4 tables for each group. If the table only has 5 rows, the group doesn't have any art product
    # and can be skipped.
    verification_message = check_if_table_has_content(table, 5)
    
    # Ommision of group if no products are found.
    if (verification_message == MensajeVerficacion.TABLA_INVALIDA.value 
        or 
        verification_message == MensajeVerficacion.TABLA_SIN_CONTENIDOS.value):
        continue

    soup = BeautifulSoup(table, "html.parser")

    # Exclude "Produccion en arte..."  and "Obras o productos". The first row of the list is either:
    # - A product corresponding to the "Obras and productos" subtable
    # - Header row. "Industrias creativas y culturales"
    table_rows = soup.find_all("tr")[2:]
    
    parse_obras_productos_table(table_rows, built_products, codigos_grupos[index])

    parse_industrias_creativas_table(table_rows, built_products, codigos_grupos[index])

    parse_eventos_artisticos_table(table_rows, built_products, codigos_grupos[index])

    parse_talleres_creacion_table(table_rows, built_products, codigos_grupos[index])


output_df = pd.DataFrame(built_products)

#  ---------------------- Output del dataframe ---------------------- 
knio.output_tables[0] = knio.Table.from_pandas(output_df)
