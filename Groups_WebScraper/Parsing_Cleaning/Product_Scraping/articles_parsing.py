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

def extraer_limpiar_anio(linea_completa: str) -> str:
    
    indice_issn = buscar_indice_ISSN(linea_completa);
    
    substr_issn = linea_completa[indice_issn:]

    indice_primera_coma = substr_issn.find(",");

    substr_anio = substr_issn[indice_primera_coma:]

    indice_vol = substr_anio.find("vol:");

    anio_sucio = substr_anio[1:indice_vol];

    anio_limpio = anio_sucio.strip()

    anio_limpio = revisar_string_vacio(anio_limpio)

    if (anio_limpio == None):
        return None
    else:
        return int(anio_limpio)

# ------


def extraer_limpiar_nombre_revista(linea_completa: str) -> str:
    
    indice_primera_coma = linea_completa.find(",")
    indice_issn = buscar_indice_ISSN(linea_completa)

    nombre_sucio = linea_completa[indice_primera_coma+1:indice_issn]
    
    nombre_limpio = nombre_sucio.strip()

    return revisar_string_vacio(nombre_limpio)

# ------

def extraer_limpiar_ISSN(linea_completa: str) -> str:
    
    indice_issn = buscar_indice_ISSN(linea_completa);
    
    substr_issn = linea_completa[indice_issn:]

    indice_primera_coma = substr_issn.find(",");

    issn_sucio = substr_issn[5:indice_primera_coma]

    issn_limpio = issn_sucio.strip()

    return revisar_string_vacio(issn_limpio);

# ------
def buscar_indice_ISSN(linea_completa: str) -> str:
    
    indice_issn = linea_completa.find("ISSN:")

    return indice_issn

# ------

def revisar_string_vacio(input_string: str) -> str:
    if(len(input_string) == 0):
        return None
    else:
        return input_string


#  ---------------------- Interpretacion de input como DF ---------------------- 
articulos_df = knio.input_tables[0].to_pandas()
    

#  ---------------------- Creación de variables relevantes ---------------------- 
tablas_html = articulos_df["HTML_Tabla_Articulos_Publicados"]
codigos_grupos = articulos_df["Codigo_Grupo"]

articulos_construidos = []

#  ---------------------- Parsing y procesamiento ---------------------- 

# Ciclo exterior para recorrer cada grupo
for index, tabla in enumerate(tablas_html):
    
    mensaje_verificacion = revisar_contenidos_de_tabla(tabla)
    
    # Omision de procesado de datos si la tabla no es valida.
    if (mensaje_verificacion == -1 or mensaje_verificacion == 0):
        continue

    soup = BeautifulSoup(tabla, "html.parser")

    nombre_articulo: str
    avalado: str
    issn: str
    doi: str
    nombre_revista: str
    anio: str

    # Se excluye la primera fila de la tabla.
    filas_tabla = soup.find_all("tr")[1:]
    
    #print("CodGrupo:", codigos_grupos[index])
    #print(len(filas_tabla))
    
    # Ciclo interior para recorrer cada fila de una tabla.
    for inner_index, fila in enumerate(filas_tabla):
        
        segunda_celda = fila.find_all("td")[1]
        tags_strong = segunda_celda.find_all("strong");
        tags_br = segunda_celda.find_all("br");

        linea_completa = tags_br[0].next_sibling
        linea_tokenizada = linea_completa.strip().split(',')

        nombre_articulo = segunda_celda.strong.next_sibling.strip()

        anio = extraer_limpiar_anio (linea_completa);

        avalado = revisar_producto_avalado(fila)

        nombre_revista = extraer_limpiar_nombre_revista(linea_completa)

        doi = revisar_string_vacio(tags_strong[1].next_sibling.strip())

        issn = extraer_limpiar_ISSN(linea_completa)

        codigo_grupo = codigos_grupos[index]

        # Creacion de fila. 
        nuevo_articulo = {
                "Codigo_grupo": codigo_grupo,
                "Nombre_articulo": nombre_articulo,
                "Año": anio,
                "Avalado?": avalado,
                "Nombre_revista": nombre_revista,
                "DOI": doi,
                "ISSN": issn,
        }
        
        articulos_construidos.append(nuevo_articulo)
        


output_df = pd.DataFrame(articulos_construidos)

#  ---------------------- Output del dataframe ---------------------- 
knio.output_tables[0] = knio.Table.from_pandas(output_df)