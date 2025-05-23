#  ---------------------- Importación de librerias ---------------------- 
from enum import Enum
import sys
import re 
from typing import Optional

import knime.scripting.io as knio

from bs4 import BeautifulSoup
import pandas as pd

#  ---------------------- Definición de enumeracion de mensajes de verificacion ---------------------- 
class MensajeVerficacion(Enum):
    TABLA_VALIDA = 1
    TABLA_SIN_CONTENIDOS = 0
    TABLA_INVALIDA = -1

    ISSN_INVALIDO = -5

#  ---------------------- Definición de funciones ---------------------- 

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
        # print("No match found.")
        # print(" - Pattern: ", regex_pattern)
        # print(" - String being searched: ", repr(string_to_check))
        return None
    
   # If the function returns false, then the string doesn't have any digits or numbers. That's why we return null.
    if check_if_string_is_alphanumeric (search_result.group(0)) == False:
        print("string sent is whitespace or doesn't contain alphanumeric characters.", repr(string_to_check))
        return None
    else:
        return search_result.group(0).strip()
 
# ------------ Functions specific to parsing of tutorings. -----------------

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


def extrer_fechas_trabajo(linea_completa_fechas: str) -> str:

    fecha_inicio: str
    fecha_finalizacion: str

    indice_desde = linea_completa_fechas.find("Desde")
    indice_hasta = linea_completa_fechas.find("hasta")
    indice_orientacion = linea_completa_fechas.find("Tipo de orientación:")
    indice_primera_coma = indice_orientacion-2

    offset_desde = len("Desde")
    offset_hasta = len("hasta")
    
    fechas_substr = linea_completa_fechas[:indice_primera_coma]

    fecha_inicio = fechas_substr[(indice_desde + offset_desde) : (indice_hasta)]
    fecha_inicio = fecha_inicio.strip()
    fecha_inicio = revisar_string_vacio(fecha_inicio)

    fecha_finalizacion = fechas_substr[(indice_hasta + offset_hasta) :]
    fecha_finalizacion = fecha_finalizacion.strip()
    fecha_finalizacion = revisar_string_vacio(fecha_finalizacion)

    return revisar_fecha(fecha_inicio),  revisar_fecha(fecha_finalizacion)

# ------

def revisar_fecha(fecha: str) -> str:
    if (fecha == None):
        return None
    else:
        return fecha

# ------


def definir_estado(fecha_finalizacion: str) -> int:
    if (fecha_finalizacion == None):
        return "En Curso"
    else:
        return "Finalizado"

# ------

def extraer_limpiar_programa_academico(linea_completa_estudiantes_programa):
    
    programa_academico: str

    indice_separador_programa = linea_completa_estudiantes_programa.find("Programa académico:")

    offset_programa = len("Programa académico:")

    substr_programa = linea_completa_estudiantes_programa[indice_separador_programa : ]

    programa_sucio = substr_programa[offset_programa : ]

    programa_limpio = programa_sucio.strip()

    return revisar_string_vacio(programa_limpio)
    

# ------

def limpiar_extraer_institucion(linea_completa_institucion: str) -> str:

    indice_institucion = linea_completa_institucion.find("Institución:")

    offset_institucion = len("Institución:")
    
    substr_institucion = linea_completa_institucion[indice_institucion:]

    nombre_sucio = substr_institucion[offset_institucion:]

    nombre_limpio = nombre_sucio.strip()

    return revisar_string_vacio(nombre_limpio)


# ------

# ------
def revisar_string_vacio(input_string: str) -> str:
    if(len(input_string) == 0):
        return None
    else:
        return input_string


#  ---------------------- Interpretacion de input como DF ---------------------- 
tutorias_df = knio.input_tables[0].to_pandas()
    

#  ---------------------- Creación de variables relevantes ---------------------- 
tablas_html = tutorias_df["HTML_Tabla_Tutorias"]
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

    tipo_formacion: str
    nombre_trabajo: str
    avalado: str
    nombres_estudiantes: str
    estado: str
    programa_academico: str
    institucion: str
    fecha_inicio: str
    fecha_finalizacion: str

    # Se excluye la primera fila de la tabla.
    filas_tabla = soup.find_all("tr")[1:]
    
    #print("CodGrupo:", codigos_grupos[index])
    #print(len(filas_tabla))
    
    # Ciclo interior para recorrer cada fila de una tabla.
    for inner_index, fila in enumerate(filas_tabla):
        
        segunda_celda = fila.find_all("td")[1]
        tags_strong = segunda_celda.find_all("strong");
        tags_br = segunda_celda.find_all("br");

        tipo_formacion = tags_strong[0].text

        nombre_trabajo = tags_strong[0].next_sibling[3:].strip()

        linea_completa_fechas = tags_br[0].next_sibling
        fecha_inicio, fecha_finalizacion = extrer_fechas_trabajo(linea_completa_fechas)

        avalado = revisar_producto_avalado(fila)

        estado = definir_estado(fecha_finalizacion)

        linea_completa_estudiantes_programa = tags_br[1].next_sibling
        linea_completa_estudiantes_programa = linea_completa_estudiantes_programa.replace("\n", '')
        linea_completa_estudiantes_programa = linea_completa_estudiantes_programa.rstrip()
        nombres_estudiantes = match_and_verify_regex_expression(linea_completa_estudiantes_programa, "(?<=Nombre del estudiante:).*?(?=(,|Programa académico))")

        programa_academico = extraer_limpiar_programa_academico(linea_completa_estudiantes_programa)

        linea_completa_institucion = tags_br[2].next_sibling
        institucion = limpiar_extraer_institucion(linea_completa_institucion)

        codigo_grupo = codigos_grupos[index]

        # Creacion de fila. 
        nuevo_producto = {
                "Codigo Grupo": codigo_grupo,
                "Tipo Formacion": tipo_formacion,
                "Nombre Trabajo": nombre_trabajo,
                "Estado": estado,
                "Fecha Inicio": fecha_inicio,
                "Fecha Finalizacion": fecha_finalizacion,
                "Nombres Estudiantes": nombres_estudiantes,
                "Programa Academico": programa_academico,
                "Institucion": institucion,
                "Avalado?": avalado
                
        }
        
        productos_construidos.append(nuevo_producto)
        


output_df = pd.DataFrame(productos_construidos)

#  ---------------------- Output del dataframe ---------------------- 
knio.output_tables[0] = knio.Table.from_pandas(output_df)


