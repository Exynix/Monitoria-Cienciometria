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

def limpiar_extraer_nombre_comercial(linea_nombre_comercial: str) -> str:

    indice_nombre_comercial = linea_nombre_comercial.find("Nombre comercial:")
    indice_nombre_proyecto = linea_nombre_comercial.find("Nombre del proyecto:")

    offset_nombre_comercial = len("Nombre comercial:")
    offset_nombre_proyecto = len("Nombre del proyecto:") - 2

    nombre_sucio = linea_nombre_comercial[indice_nombre_comercial+offset_nombre_comercial:indice_nombre_proyecto+offset_nombre_proyecto]
    nombre_limpio = nombre_sucio.strip()

    return revisar_string_vacio(nombre_limpio)

# ------

def limpiar_extraer_nombre_proyecto(linea_nombre_comercial: str) -> str:

    indice_nombre_proyecto = linea_nombre_comercial.find("Nombre del proyecto:")

    offset_nombre_proyecto = len("Nombre del proyecto:")

    nombre_sucio = linea_nombre_comercial[indice_nombre_proyecto+offset_nombre_proyecto:]
    nombre_limpio = nombre_sucio.strip()

    return revisar_string_vacio(nombre_limpio)

# ------

def limpiar_extraer_nombre_financiadora(linea_completa_financiadora: str) -> str:

    indice_nombre_financiadora = linea_completa_financiadora.find("Institución financiadora:")

    offset_nombre_financiadora = len("Institución financiadora:")

    nombre_sucio = linea_completa_financiadora[indice_nombre_financiadora:offset_nombre_financiadora]
    nombre_limpio = nombre_sucio.strip()

    return revisar_string_vacio(nombre_limpio)

# ------

def limpiar_extraer_nombre_sitioweb(linea_nombre_anio: str) -> str:

    indice_disponibilidad = linea_nombre_anio.find("Disponibilidad:")

    offset_disponibilidad = len("Disponibilidad:")

    substr_disponibilidad = linea_nombre_anio[indice_disponibilidad+offset_disponibilidad:]
    
    indice_sitioweb = substr_disponibilidad.find("Sitio web:")
    
    offset_sitioweb = len("Sitio web:")

    nombre_sucio = substr_disponibilidad[indice_sitioweb+offset_sitioweb:]
    nombre_limpio = nombre_sucio.strip()

    return revisar_string_vacio(nombre_limpio)

# ------

def limpiar_extraer_nombre_disponibilidad(linea_nombre_anio: str) -> str:

    indice_disponibilidad = linea_nombre_anio.find("Disponibilidad:")

    offset_disponibilidad = len("Disponibilidad:")

    substr_disponibilidad = linea_nombre_anio[indice_disponibilidad+offset_disponibilidad:]
    
    indice_coma = substr_disponibilidad.find("Sitio web:") - 2
    
    nombre_sucio = substr_disponibilidad[:indice_coma]
    nombre_limpio = nombre_sucio.strip()

    return revisar_string_vacio(nombre_limpio)

# ------
def revisar_string_vacio(input_string: str) -> str:
    if(len(input_string) == 0):
        return None
    else:
        return input_string


#  ---------------------- Interpretacion de input como DF ---------------------- 
softwares_df = knio.input_tables[0].to_pandas()
    

#  ---------------------- Creación de variables relevantes ---------------------- 
tablas_html = softwares_df["HTML_Tabla_Softwares"]
codigos_grupos = softwares_df["Codigo_Grupo"]

productos_construidos = []

#  ---------------------- Parsing y procesamiento ---------------------- 

# Ciclo exterior para recorrer cada grupo
for index, tabla in enumerate(tablas_html):
    
    mensaje_verificacion = revisar_contenidos_de_tabla(tabla)
    
    # Omision de procesado de datos si la tabla no es valida.
    if (mensaje_verificacion == -1 or mensaje_verificacion == 0):
        continue

    soup = BeautifulSoup(tabla, "html.parser")

    nombre_software: str
    anio: int
    avalado: str
    nombre_comercial: str
    nombre_proyecto: str
    institucion_financiadora: str
    url_sitio_web: str
    disponibilidad: str
    

    # Se excluye la primera fila de la tabla.
    filas_tabla = soup.find_all("tr")[1:]
    
    print("CodGrupo:", codigos_grupos[index])
    print(len(filas_tabla))
    
    # Ciclo interior para recorrer cada fila de una tabla.
    for inner_index, fila in enumerate(filas_tabla):
        
        segunda_celda = fila.find_all("td")[1]
        tags_strong = segunda_celda.find_all("strong");
        tags_br = segunda_celda.find_all("br");

        nombre_software = tags_strong[0].next_sibling[3:].strip()

        linea_completa_anio = tags_br[0].next_sibling
        linea_tokenizada_anio = linea_completa_anio.strip().split(',')
        anio = linea_tokenizada_anio[1].strip()

        avalado = revisar_producto_avalado(fila)

        linea_completa_nombre_comercial = tags_br[1].next_sibling
        nombre_comercial = limpiar_extraer_nombre_comercial(linea_completa_nombre_comercial)

        nombre_proyecto = limpiar_extraer_nombre_proyecto(linea_completa_nombre_comercial)

        linea_completa_financiadora = tags_br[-2].next_sibling
        institucion_financiadora = limpiar_extraer_nombre_financiadora(linea_completa_financiadora)

        url_sitio_web = limpiar_extraer_nombre_sitioweb(linea_completa_anio)

        disponibilidad = limpiar_extraer_nombre_disponibilidad(linea_completa_anio)

        codigo_grupo = codigos_grupos[index]

        # Creacion de fila. 
        nuevo_producto = {
                "Codigo Grupo": codigo_grupo,
                "Nombre Software": nombre_software,
                "Año": anio,
                "Avalado?": avalado,
                "Nombre Comercial": nombre_comercial,
                "Nombre Proyecto": nombre_proyecto,
                "Institucion Financiador": institucion_financiadora,
                "Disponibillidad": disponibilidad,
                "URL Sitio Web": url_sitio_web
        }
        
        productos_construidos.append(nuevo_producto)
        


output_df = pd.DataFrame(productos_construidos)

#  ---------------------- Output del dataframe ---------------------- 
knio.output_tables[0] = knio.Table.from_pandas(output_df)