#  ---------------------- Importación de librerias ---------------------- 
from enum import Enum
import sys

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


# ------

def limpiar_extraer_numero_registro(linea_completa_anio: str) -> str:

    indice_numero_registro = linea_completa_anio.find("Número del registro:")

    offset_numero_registro = len("Número del registro:")

    substr_numero_registro = linea_completa_anio[(indice_numero_registro+offset_numero_registro):]

    indice_coma = substr_numero_registro.find("Nombre del titular:") - 2

    nombre_sucio = substr_numero_registro[:indice_coma]

    nombre_limpio = nombre_sucio.strip()

    return revisar_string_vacio(nombre_limpio)


# ------

def limpiar_extraer_nombre_titular(linea_completa_anio: str) -> str:

    indice_numero_registro = linea_completa_anio.find("Número del registro:")

    offset_numero_registro = len("Número del registro:")

    substr_numero_registro = linea_completa_anio[(indice_numero_registro+offset_numero_registro):]

    indice_nombre_titular = substr_numero_registro.find("Nombre del titular:")

    offset_nombre_titular = len("Nombre del titular:")

    nombre_sucio = substr_numero_registro[indice_nombre_titular+offset_nombre_titular:]

    nombre_limpio = nombre_sucio.strip()
    
    return revisar_string_vacio(nombre_limpio)


# ------
def revisar_string_vacio(input_string: str) -> str:
    if(len(input_string) == 0):
        return None
    else:
        return input_string


#  ---------------------- Interpretacion de input como DF ---------------------- 
signos_df = knio.input_tables[0].to_pandas()
    

#  ---------------------- Creación de variables relevantes ---------------------- 
tablas_html = signos_df["HTML_Tabla_Signos"]
codigos_grupos = signos_df["Codigo_Grupo"]

productos_construidos = []

#  ---------------------- Parsing y procesamiento ---------------------- 

# Ciclo exterior para recorrer cada grupo
for index, tabla in enumerate(tablas_html):
    
    mensaje_verificacion = revisar_contenidos_de_tabla(tabla)
    
    # Omision de procesado de datos si la tabla no es valida.
    if (mensaje_verificacion == -1 or mensaje_verificacion == 0):
        continue

    soup = BeautifulSoup(tabla, "html.parser")

    nombre_signo: str
    anio: int
    avalado: str
    pais: str
    numero_registro: str
    nombre_titular: str

    # Se excluye la primera fila de la tabla.
    filas_tabla = soup.find_all("tr")[1:]
    
    #print("CodGrupo:", codigos_grupos[index])
    #print(len(filas_tabla))
    
    # Ciclo interior para recorrer cada fila de una tabla.
    for inner_index, fila in enumerate(filas_tabla):
        
        segunda_celda = fila.find_all("td")[1]
        tags_strong = segunda_celda.find_all("strong");
        tags_br = segunda_celda.find_all("br");

        nombre_signo = tags_strong[0].next_sibling[3:].strip()

        linea_completa_anio = tags_br[0].next_sibling
        linea_tokenizada_anio = linea_completa_anio.strip().split(',')
        anio = int(linea_tokenizada_anio[1].strip())

        avalado = revisar_producto_avalado(fila)

        pais = linea_tokenizada_anio[0].strip()

        numero_registro = limpiar_extraer_numero_registro(linea_completa_anio)

        nombre_titular = limpiar_extraer_nombre_titular(linea_completa_anio)

        codigo_grupo = codigos_grupos[index]

        # Creacion de fila. 
        nuevo_producto = {
                "Codigo Grupo": codigo_grupo,
                "Nombre Signo": nombre_signo,
                "Año": anio,
                "Avalado?": avalado,
                "Pais": pais,
                "Numero de Registro": numero_registro,
                "Nombre de Titular": nombre_titular
        }
        
        productos_construidos.append(nuevo_producto)
        


output_df = pd.DataFrame(productos_construidos)

#  ---------------------- Output del dataframe ---------------------- 
knio.output_tables[0] = knio.Table.from_pandas(output_df)