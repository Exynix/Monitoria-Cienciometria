#  ---------------------- Importación de librerias ---------------------- 
from enum import Enum
import re
import pandas as pd
import knime.scripting.io as knio

#  ---------------------- Definición de enumeracion de mensajes de verificacion ---------------------- 
class MensajeVerficacion(Enum):
    TABLA_VALIDA = 1
    TABLA_SIN_CONTENIDOS = 0
    TABLA_INVALIDA = -1
    ISSN_INVALIDO = -5

#  ---------------------- Definición de funciones ----------------------
def find_year(full_book):

    pattern = r'En:.*?(\d{4})\.\s'
    match = re.search(pattern, full_book)
    if match:
        return match.group(1)
    return None
    


# ------
def split_by_indices(string, indices, substring_length):
    parts = []
    last_index = 0
    for index in indices:
        parts.append(string[last_index:index])
        last_index = index + substring_length
    parts.append(string[last_index:])
    return parts

# ------
def check_if_cell_is_empty(cell):
    if cell is None or cell is pd.NA:
        return True
    elif isinstance(cell, str) and cell.strip() == "":
        return True
    return False

# ------
def find_all_occurrences(string, substring):
    if not isinstance(string, str):
        return []
    return [m.start() for m in re.finditer(re.escape(substring), string)]

# ------
def revisar_string_vacio(input_string: str) -> str:
    if len(input_string) == 0:
        return None
    return input_string

#  ---------------------- Interpretacion de input como DF ---------------------- 
input_table = knio.input_tables[0].to_pandas()

#  ---------------------- Creación de variables relevantes ---------------------- 
ids_column = input_table["ID documento"]
chapters_column = input_table["Capitulos de Libro"]

chapters_indexes = []
built_chapters = []

#  ---------------------- Parsing y procesamiento ---------------------- 
for index, chapters_list in enumerate(chapters_column):
    if check_if_cell_is_empty(chapters_list):
        continue

    teacher_id = ids_column[index]
    chapters_list = str(chapters_list)  # Ensure the article list is a string

    chapters_indexes_unverified = find_all_occurrences(chapters_list, "Tipo: Otro capítulo de libro publicado")
    chapters_indexes_verified = find_all_occurrences(chapters_list, "Tipo: Capítulo de libro")

    full_indexes = chapters_indexes_unverified + chapters_indexes_verified
    full_indexes.sort()

    chapters = split_by_indices(chapters_list, chapters_indexes, 5)

    for chapter in chapters:
        year = find_year(chapter)
        # Creacion de fila. 
        new_chapter = {
            "ID Documento": teacher_id,
            "Año": year,
        }
        built_chapters.append(new_chapter)

#  ---------------------- Output del dataframe ---------------------- 
knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame(built_chapters))

