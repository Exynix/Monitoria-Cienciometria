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
def find_year(full_event):

    substring = " Realizado el:"
    index = full_event.find(substring)

    if index != -1:

        year_start_index = index + len (" Realizado el:")
        year_end_index = year_start_index + 4

        return full_event [year_start_index : year_end_index]

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
events_column = input_table["Evento Cientifico"]

events_indexes = []
built_events = []

#  ---------------------- Parsing y procesamiento ---------------------- 
for index, events_list in enumerate(events_column):
    if check_if_cell_is_empty(events_list):
        continue

    teacher_id = ids_column[index]
    events_list = str(events_list)  # Ensure the article list is a string

    events_indexes = find_all_occurrences(events_list, "Nombre del evento:")
    events = split_by_indices(events_list, events_indexes, len("Nombre del evento:"))

    for event in events:
        year = find_year(event)
        # Creacion de fila. 
        new_article = {
            "ID Documento": teacher_id,
            "Año": year,
        }
        built_events.append(new_article)

#  ---------------------- Output del dataframe ---------------------- 
knio.output_tables[0] = knio.Table.from_pandas(pd.DataFrame(built_events))

