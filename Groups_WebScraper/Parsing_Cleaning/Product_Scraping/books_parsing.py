3#  ---------------------- Importación de librerias ---------------------- 
from enum import Enum

import knime.scripting.io as knio

from bs4 import BeautifulSoup
import pandas as pd

#  ---------------------- Definición de enumeracion de mensajes de verificacion ---------------------- 
class MensajeVerficacion(Enum):
    TABLA_VALIDA = 1
    TABLA_SIN_CONTENIDOS = 0
    TABLA_INVALIDA = -1

# Revisa si la tabla dada tiene registros, más alla del titulo y columnas de la tabla.
# Input: Tabla HTML completa de libros.
def revisar_contenidos_de_tabla (html_table: str) -> int:
    soup = BeautifulSoup(html_table, "html.parser")

    numero_filas = len(soup.find_all("tr"))

    # Si la tabla tiene menos de 2 filas, no hay pruductos academicos.
    if (numero_filas < 2 ):

        # Si la tabla solo tiene 1 fila, solo tiene la  fila de titulo de la tabla.
        if (numero_filas == 1 ):
            return MensajeVerficacion.TABLA_SIN_CONTENIDOS.value
        # En cualquier otro caso, la tabla no es valida. 
        else:
            return MensajeVerficacion.TABLA_INVALIDA.value

    # 2 filas significa que hay minimo un producto academico, y la tabla es valida.
    if (numero_filas >= 2):
        return MensajeVerficacion.TABLA_VALIDA.value

# ------

# Verificacion de existencia de tag <img>. Dice si el producto académico fue avalado.
def revisar_pruducto_avalado(fila_html: str) -> str:
     
        if (fila_html.td.img != None):
            return "Si"
        else:
            return "No"

# ------

def extraer_substr_isbn_editorial(isbn_anio_libro_editorial: str) -> str:

    indice_isbn = isbn_anio_libro_editorial.find("ISBN:")

    substr_isbn_editorial = isbn_anio_libro_editorial[indice_isbn:]

    return substr_isbn_editorial


# ------

def extraer_limpiar_isbn(isbn_anio_libro_editorial: str) -> str:
    
    isbn_editorial = extraer_substr_isbn_editorial(isbn_anio_libro_editorial)

    isbn_editorial = isbn_editorial.replace(" \n                ", " ")
    indice_coma = isbn_editorial.find(", Ed.")
    
    isbn_sucio = isbn_editorial[5: indice_coma]

    isbn_limpio = isbn_sucio.strip()
    
    return revisar_string_vacio(isbn_limpio)
# ------

def extraer_limpiar_editorial(isbn_anio_libro_editorial: str) -> str:
    
    """
    El editorial siempre es el ultimo token de la lista, pero hay editoriales que tienen comas en su nombre,
    por lo que no se puede usar una lista tokenizada como metodo confiable para extraer la editorial.

    Se podría buscar y usar el string que viene después de "Ed.", pero se reconoce que es posible que ese substring
    este posible en partes anteriores de la linea. Por esta razón, se busca y se limpia la cadena después del substring
    "págs:". 
    """

    isbn_editorial = extraer_substr_isbn_editorial(isbn_anio_libro_editorial) # Cadena con ISBN: ..... , Ed. ....

    isbn_editorial = isbn_editorial.replace(" \n                ", " ")
    indice_coma = isbn_editorial.find(", Ed.")
    
    editorial_sucio = isbn_editorial[indice_coma+5:]

    editorial_limpia = limpiar_nombre_editorial(editorial_sucio)    

    return editorial_limpia
# ------

def limpiar_nombre_editorial(editorial_sucio: str) -> str:
    
    editorial_limpia = editorial_sucio.strip()

    return revisar_string_vacio(editorial_limpia)

# ------

# to_search es un CARACTER. La pista de tipo es "str" ante la falta de una pista para variables tipo "char".
def find_char_indexes(to_search: str, string: str):
    
    indexes = []

    for index, character in enumerate(string):
        if (character == to_search):
            indexes.append(index)

    return indexes

# ------

def revisar_string_vacio(input_string: str) -> str:
    if(len(input_string) == 0):
        return None
    else:
        return input_string


#  ---------------------- Interpretacion de input como DF ---------------------- 
libros_df = knio.input_tables[0].to_pandas()


#  ---------------------- Creación de variables relevantes ---------------------- 
tablas_html = libros_df["HTML_Tabla_LibrosPublicados"]
codigos_grupos = libros_df["Codigo_Grupo"]

# Creacion de output dataframe.
output_df_columns = [
    "Codigo_grupo",
    "Nombre_libro",
    "Año",
    "Avalado?",
    "ISBN",
    "Editorial"
]
output_df = pd.DataFrame(columns= output_df_columns)

#  ---------------------- Parsing y procesamiento ---------------------- 

# Ciclo exterior para recorrer cada grupo
for index, tabla in enumerate(tablas_html):
    
    mensaje_verificacion = revisar_contenidos_de_tabla(tabla)
    
    # Omision de procesado de grupo si la tabla no es valida.
    if (mensaje_verificacion == -1 or mensaje_verificacion == 0):
        continue

    soup = BeautifulSoup(tabla, "html.parser")

    nombre_libro: str
    anio: str
    avalado: str
    isbn: str
    nombre_editorial: str
    

    # Se excluye la primera fila de la tabla.
    filas_tabla = soup.find_all("tr")[1:]

    # Ciclo interior para recorrer cada fila de una tabla.
    for fila in filas_tabla:

        # Extracción de nombre del libro.
        segunda_celda = fila.find_all("td")[1]

        nombre_sucio = segunda_celda.strong.next_sibling.strip()
        nombre_libro = nombre_sucio[2:]

        avalado = revisar_pruducto_avalado(fila)

        # Extraccion de ISBN, Año y Editorial
        isbn_anio_editorial = segunda_celda.find_all("br")[0].next_sibling
        isbn_anio_editorial.strip()
        lista_separada = isbn_anio_editorial.split(", ")

        anio = int(lista_separada[1].strip())

        isbn = extraer_limpiar_isbn(isbn_anio_editorial)

        nombre_editorial = extraer_limpiar_editorial(isbn_anio_editorial)

        # Creacion de fila. Concatenacion a dataframe de output.
        nueva_fila = pd.Series(
            {
                "Codigo_grupo": libros_df.iloc[index,0],
                "Nombre_libro": nombre_libro,
                "Año": anio,
                "Avalado?": avalado,
                "ISBN": isbn,
                "Editorial": nombre_editorial
            }
        )

        output_df = pd.concat([output_df, nueva_fila.to_frame().T], ignore_index=True)





#  ---------------------- Output del dataframe ---------------------- 
knio.output_tables[0] = knio.Table.from_pandas(output_df)

