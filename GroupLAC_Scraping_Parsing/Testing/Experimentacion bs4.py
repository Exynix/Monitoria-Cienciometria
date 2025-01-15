#  ---------------------- Importación de librerias ---------------------- 
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
# Input: Tabla HTML completa de capitulos de libros.
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
def revisar_producto_avalado(fila_html: str) -> str:
     
    if (fila_html.td.img != None):
        return "Si"
    else:
        return "No"

# ------

def extraer_limpiar_editorial(isbn_anio_libro_editorial: str) -> str:
    
    """
    El editorial siempre es el ultimo token de la lista, pero hay editoriales que tienen comas en su nombre,
    por lo que no se puede usar una lista tokenizada como metodo confiable para extraer la editorial.

    Se podría buscar y usar el string que viene después de "Ed.", pero se reconoce que es posible que ese substring
    este posible en partes anteriores de la linea. Por esta razón, se busca y se limpia la cadena después del substring
    "págs:". 
    """

    indice_pags = isbn_anio_libro_editorial.find("págs:") # Cadena con "págs: ...... , Ed. ......"

    pags_editorial_substr = isbn_anio_libro_editorial[indice_pags+5:]

    # Se busca la primera coma en el substring. Dado que el número de páginas no puede tener comas,
    # la primera coma siempre será el separador entre las páginas y la editorial.
    indice_coma = pags_editorial_substr.find(", Ed.")
    editorial_sucio = pags_editorial_substr[indice_coma+5:]

    editorial_limpia = limpiar_nombre_editorial(editorial_sucio)    

    return editorial_limpia
# ------

def limpiar_nombre_editorial(editorial_sucio: str) -> str:
    
    editorial_limpia = editorial_sucio.strip()

    return revisar_string_vacio(editorial_limpia)

# ------

def extraer_limpiar_año(lista_tokenizada: [str]) -> int:

    # El año siempre será el segundo token, dado que la mayoría (o ningún) pais tiene comas en su nombre.
    anio_sucio = lista_tokenizada[1]

    anio_limpio = anio_sucio.strip()

    return revisar_string_vacio(anio_limpio)

# ------

def extraer_limpiar_isbn(isbn_anio_libro_editorial: str) -> str:
    
    """
    El ISBN no puede ser encontrado de forma confiable a través de la lista tokenizada, dado que hay libros
    que tienen comas en su nombre*. Por esta limitación, se busca el ISBN a través de la busqueda de un substring.

    El isbn siempre ira después del string "ISBN:" e irá hasta la siguiente coma. 
    
    
    * La mejor aproximación a la tokenización de la linea es por comas.No hay ningún otro caracter que separe la 
    información de manera confiable.
    """
    
    indice_isbn = isbn_anio_libro_editorial.find("ISBN:")
    parte_isbn = isbn_anio_libro_editorial[indice_isbn:] # Cadena con contenido: "ISBN: xxxxxx..." hasta el final de la linea.

    isbn_limpio = limpiar_isbn_substring(parte_isbn)
         
    return isbn_limpio
# ------

def limpiar_isbn_substring(parte_isbn: str) -> str:

    # Elimacion de la subcadena "ISBN:"
    isbn_substr = parte_isbn[5:] # Cadena con contenido: " xxxx ..." hasta el final de la linea.    
    
    indice_primera_coma = isbn_substr.find(",")

    isbn_sucio = isbn_substr[:indice_primera_coma]

    isbn_limpio = isbn_sucio.strip()

    return revisar_string_vacio(isbn_limpio)
    
# ------

def extraer_limpiar_nombre_libro(isbn_anio_libro_editorial: str) -> str:
    
    """
    Por la misma razón que en el caso del ISBN, hay libros cuyo nombre tiene ",". Esto causa que su nombre sea tokenizado
    o separado si el nombre del libro es extraido a través de una lista tokenizada.

    Dado lo anterior, la forma en la que se puede extraer de forma confiable el nombre del libro es a través del 
    substring que esta entre el año y el ISBN.
    """
    
    indice_isbn = isbn_anio_libro_editorial.find("ISBN:")
    indice_segunda_coma = find_char_indexes(',', isbn_anio_libro_editorial )[1]

    # Cadena que contiene desde: la coma despues del año, hasta el espacio ANTES de la substr "ISBN: ..."
    nombre_libro_sucio = isbn_anio_libro_editorial[indice_segunda_coma:indice_isbn]

    nombre_libro_limpio = limpiar_nombre_libro(nombre_libro_sucio)
    
    return nombre_libro_limpio
# ------

def limpiar_nombre_libro(nombre_libro_sucio: str) -> str:
    
    libro_limpio = nombre_libro_sucio[1:-2].strip()

    return revisar_string_vacio(libro_limpio)
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
capitulos_df = knio.input_tables[0].to_pandas()


#  ---------------------- Creación de variables relevantes ---------------------- 
tablas_html = capitulos_df["HTML_CapitulosLibro"]
codigos_serie = capitulos_df["Codigo_Grupo"]

# Creacion de output dataframe.
output_df_columns = [
    "Codigo_Grupo",
    "Nombre_Capitulo",
    "Año",
    "Avalado?",
    "ISBN",
    "Nombre_Libro",
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

    nombre_capitulo: str
    anio: str
    avalado: str
    isbn: str
    nombre_libro: str
    editorial: str
    

    # Se excluye la primera fila de la tabla.
    filas_tabla = soup.find_all("tr")[1:]

    # Ciclo interior para recorrer cada fila de una tabla.
    for fila in filas_tabla:

        # Extracción de nombre del libro.
        segunda_celda = fila.find_all("td")[1]

        nombre_sucio = segunda_celda.strong.next_sibling.strip()
        nombre_capitulo = nombre_sucio[2:]

        avalado = revisar_producto_avalado(fila)

        # Extraccion de ISBN, Año y Nombre de libro
        isbn_anio_libro_editorial = segunda_celda.find_all("br")[0].next_sibling
        isbn_anio_libro_editorial.strip()
        lista_tokenizada = isbn_anio_libro_editorial.split(",")

        anio = extraer_limpiar_año(lista_tokenizada)

        isbn = extraer_limpiar_isbn(isbn_anio_libro_editorial)

        nombre_libro = extraer_limpiar_nombre_libro(isbn_anio_libro_editorial)

        editorial = extraer_limpiar_editorial(isbn_anio_libro_editorial)
        
        
        # Creacion de fila. Concatenacion a dataframe de output.
        nueva_fila = pd.Series(
            {
                "Codigo_Grupo": codigos_serie[index],
                "Nombre_Capitulo": nombre_capitulo,
                "Año": anio,
                "Avalado?": avalado,
                "ISBN": isbn,
                "Nombre_Libro": nombre_libro,
                "Editorial": editorial
            }
        )

        output_df = pd.concat([output_df, nueva_fila.to_frame().T], ignore_index=True)





#  ---------------------- Output del dataframe ---------------------- 
knio.output_tables[0] = knio.Table.from_pandas(output_df)

"""
Ed. Springer Publishing Company, Inc.


 958-683-890-0, 
                Ed. Editorial Pontificia Universidad Javeriana

                : 958-683-890-0,  Ed. Editorial Pontificia Universidad Javeriana

                ISBN: 978-9978-10-792-8, \n                Ed. Editorial Universitaria Abya-Yala \n
"""