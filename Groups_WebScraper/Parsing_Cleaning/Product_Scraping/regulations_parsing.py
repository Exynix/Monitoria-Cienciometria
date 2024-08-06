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

#  ---------------------- Definición de funciones ---------------------- 

# Revisa si la tabla dada tiene registros, más alla del titulo y columnas de la tabla.
# Input: Tabla HTML completa de articulos.
def revisar_contenidos_de_tabla (html_table: str) -> int:
    soup = BeautifulSoup(html_table, "html.parser")

    numero_filas = len(soup.find_all("tr"))


    # Si la tabla tiene menos de 2 filas, no hay articulos.
    if (numero_filas < 2 ):

        # Si la tabla solo tiene 1 filas, solo tiene filas de headers y titulos.
        if (numero_filas == 1 ):
            return MensajeVerficacion.TABLA_SIN_CONTENIDOS.value
        # En cualquier otro caso, la tabla no es valida. 
        else:
            return MensajeVerficacion.TABLA_INVALIDA.value

    # 2 filas significa que hay minimo un articulo, y la tabla es valida.
    if (numero_filas >= 2):
        return MensajeVerficacion.TABLA_VALIDA.value

# ------

# Verificacion de existencia de tag <img>. Dice si el producto académico fue avalado.
def revisar_producto_avalado(fila_html: str) -> str:
     
    if (fila_html.td.img != None):
        return "Si"
    else:
        return "No"

# ---------





# ------

def revisar_fecha(fecha: str) -> str:
    if (fecha == None):
        return None
    else:
        return fecha

# ------

def limpiar_extraer_institucion_financiadora(linea_completa_institucion: str) -> str:

    indice_institucion = linea_completa_institucion.find("Institución financiadora:")

    offset_institucion = len("Institución financiadora:")
    
    substr_institucion = linea_completa_institucion[indice_institucion:]

    nombre_sucio = substr_institucion[offset_institucion:]

    nombre_limpio = nombre_sucio.strip()

    return revisar_string_vacio(nombre_limpio)


# -------------------------------- Functions from the parsing utils library -------------------------------- 

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
    
# ------
def revisar_string_vacio(input_string: str) -> str:
    if(len(input_string) == 0):
        return None
    else:
        return input_string


# ------
def check_string_not_whitespace (input_string):

    alphanumeric_regex = "[A-Za-z0-9]+"
    search_result = re.search(alphanumeric_regex, input_string) 
    
    if search_result == None:
        return False;
    else:
        return True;

#  ---------------------- Interpretacion de input como DF ---------------------- 
tutorias_df = knio.input_tables[0].to_pandas()
    

#  ---------------------- Creación de variables relevantes ---------------------- 
tablas_html = tutorias_df["HTML_Tabla_RegulacionesNormas"]
codigos_grupos = tutorias_df["Codigo_Grupo"]

productos_construidos = []

#  ---------------------- Parsing y procesamiento ---------------------- 

# Ciclo exterior para recorrer cada grupo
for index, tabla in enumerate(tablas_html):
    
    mensaje_verificacion = revisar_contenidos_de_tabla(tabla)
    
    # Omision de procesado de datos si la tabla no es valida.
    if (mensaje_verificacion == -1 or mensaje_verificacion == 0):
        continue

    soup = BeautifulSoup(tabla, "html.parser")

    tipo_norma: str
    nombre_norma: str
    ambito: str
    fecha_publicacion: str
    institucion_financiadora: str

    # Se excluye la primera fila de la tabla.
    filas_tabla = soup.find_all("tr")[1:]
    
    #print("CodGrupo:", codigos_grupos[index])
    #print(len(filas_tabla))
    
    # Ciclo interior para recorrer cada fila de una tabla.
    for inner_index, fila in enumerate(filas_tabla):
        
        segunda_celda = fila.find_all("td")[1]
        tags_strong = segunda_celda.find_all("strong");
        tags_br = segunda_celda.find_all("br");

        tipo_norma = tags_strong[0].text

        nombre_norma = tags_strong[0].next_sibling[3:].strip()

        linea_completa_ambito_publicacion = tags_br[0].next_sibling
        ambito = match_and_verify_regex_expression(linea_completa_ambito_publicacion, "(?<=Ambito:).*?(?=,)")

        fecha_publicacion = match_and_verify_regex_expression(linea_completa_ambito_publicacion, "(?<=Fecha de publicación:).*?(?=,)")

        avalado = revisar_producto_avalado(fila)

        linea_completa_institucion = tags_br[1].next_sibling
        institucion_financiadora = limpiar_extraer_institucion_financiadora(linea_completa_institucion)

        codigo_grupo = codigos_grupos[index]

        # Creacion de fila. 
        nuevo_producto = {
                "Codigo Grupo": codigo_grupo,
                "Tipo Norma": tipo_norma,
                "Nombre Regulacion": nombre_norma,
                "Ambito": ambito,
                "Fecha Publicacion": fecha_publicacion,
                "Institucion Financiadora": institucion_financiadora,
                "Avalado?": avalado
                
        }
        
        productos_construidos.append(nuevo_producto)
        


output_df = pd.DataFrame(productos_construidos)

#  ---------------------- Output del dataframe ---------------------- 
knio.output_tables[0] = knio.Table.from_pandas(output_df)