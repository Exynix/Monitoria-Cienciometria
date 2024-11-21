#  ---------------------- Importacion de librerias ---------------------- 
from enum import Enum

import knime.scripting.io as knio

from bs4 import BeautifulSoup
import pandas as pd

#  ---------------------- Definición de enumeracion de mensajes de verificacion ---------------------- 
class MensajeVerficacion(Enum):
    TABLA_VALIDA = 1
    TABLA_SIN_CONTENIDOS = 0
    TABLA_INVALIDA = -1


#  ---------------------- Definición de funciones ---------------------- 

# Revisa si la tabla dada tiene registros, más alla del titulo de la tabla.
# Se analiza la tabla HTML para saber si la tabla en efecto tiene informacion de integrantes.
# Input: Tabla HTML completa de integrantes.
def revisar_contenidos_de_tabla (html_table: str) -> int:
    soup = BeautifulSoup(html_table, "html.parser")

    numero_filas = len(soup.find_all("tr"))
    

    # Si la tabla tiene menos de 3 filas, no hay integrantes.
    if (numero_filas < 3 ):

        # Si la tabla solo tiene 2 filas, solo tiene filas de headers y titulos.
        if (numero_filas == 2 ):
            return MensajeVerficacion.TABLA_SIN_CONTENIDOS.value
        # En cualquier otro caso, la tabla no es valida. 
        else:
            return MensajeVerficacion.TABLA_INVALIDA.value

    # 3 filas significa que hay minimo un integrante, y la tabla es valida.
    if (numero_filas >= 3):
        return MensajeVerficacion.TABLA_VALIDA.value

# ------
def extraer_nombre_y_cvlac(html_nombre_integrante: str) -> str:
    
    nombre: str
    url_cvlac: str
    
    nombre = html_nombre_integrante.a.text.strip()
    url_cvlac = html_nombre_integrante.a.get('href')

    return nombre, url_cvlac 

# ------
def separar_fecha_vinculacion(fecha_vinculacion_completa: str):

    fecha_inicio_vinculacion: str
    fecha_final_vinculacion: str

    lista_fechas = fecha_vinculacion_completa.split('-')

    # La fecha inicial siempre viene como fecha, por lo que se puede asignar directamente.
    fecha_inicio_vinculacion = lista_fechas[0].strip()

    fecha_final_vinculacion = lista_fechas[1].strip()

    return fecha_inicio_vinculacion, fecha_final_vinculacion
# ------
def definir_estado_vinculacion(input_fecha_final:str) -> str:

    estado: str
    output_fecha_final_vinculacion: str

    if (input_fecha_final == "Actual"):
            estado = "Activo"
            output_fecha_final_vinculacion = None
    else:
        estado = "Inactivo"
        output_fecha_final_vinculacion = input_fecha_final

    return estado, output_fecha_final_vinculacion

#  ---------------------- Interpretacion de input como DF ---------------------- 
integrantes_df = knio.input_tables[0].to_pandas()


#  ---------------------- Creación de Output dataframe ---------------------- 
columnas_output_df = [
    "Codigo_grupo",
    "Nombre Grupo",
    "URL GroupLAC",
    "Nombre_completo",
    "Estado",
    "Horas_dedicacion",
    "Fecha_inicio_vinculacion",
    "Fecha_terminacion_vinculacion",
    "Url_CvLac"
]
output_df = pd.DataFrame(columns=columnas_output_df)


#  ---------------------- Creación de variables relevantes ---------------------- 
html_tables = integrantes_df["HTML_Integrantes"]
group_names = integrantes_df["NombreGrupo"]


#  ---------------------- Parsing y procesamiento ---------------------- 
# Ciclo exterior para recorrer cada grupo
for index, table in enumerate(html_tables):

    mensaje_verificacion = revisar_contenidos_de_tabla(table)
    
    # Omision de procesado de datos si la tabla no es valida.
    if (mensaje_verificacion == -1 or mensaje_verificacion == 0):
        continue

    # Creacion de soup y variables relevantes
    soup = BeautifulSoup(table, 'html.parser')

    nombre_integrante: str
    url_cvlac_integrante: str
    horas_dedicadas: int
    fecha_vinculacion_completa: str
    inicio_vinculacion: str
    final_vinculacion: str
    estado_vinculacion: str

    # Se obtiene una lista con todos los <tr> de la tabla. Se omiten las primeras dos porque, dado que son las 
    # columnas que tienen el titulo de la tabla y los nombres de la columna, respectivamente. 
    filas_tabla = soup.find_all("tr")[2:]
    
    # Ciclo interior para recorrer cada fila de la tabla de integrantes.
    for fila in filas_tabla:
        celdas_fila = fila.find_all("td")

        nombre_integrante, url_cvlac_integrante = extraer_nombre_y_cvlac(celdas_fila[0])

        horas_dedicadas = celdas_fila[2].text.strip()

        fecha_vinculacion_completa =  celdas_fila[3].text.strip()

        inicio_vinculacion, final_vinculacion = separar_fecha_vinculacion(fecha_vinculacion_completa)

        estado, final_vinculacion = definir_estado_vinculacion(final_vinculacion)

        # print(integrantes_df.iloc[index, 1])

        # Creacion de fila. Concatenacion a dataframe de output.
        nueva_fila = pd.Series(
            {"Codigo_grupo": integrantes_df.iloc[index, 0],
            "Nombre Grupo": integrantes_df.iloc[index, 1],
            "URL GroupLAC": integrantes_df.iloc[index, 2],
            "Nombre_completo": nombre_integrante,
            "Horas_dedicacion": horas_dedicadas,
            "Estado": estado,
            "Fecha_inicio_vinculacion": inicio_vinculacion,
            "Fecha_terminacion_vinculacion": final_vinculacion,
            "Url_CvLac": url_cvlac_integrante
            }
            )

        output_df = pd.concat([output_df, nueva_fila.to_frame().T], ignore_index=True)



#  ---------------------- Output del dataframe. ----------------------     
knio.output_tables[0] = knio.Table.from_pandas(output_df)




"""
Cada fila contiene el código de grupo, y la tabla con información de sus integrantes.

Cada tabla tiene:
- Lista de nombres de integrantes.
- Lista de URLs de CvLAC.
- Lista de horas de dedicación.
- Lista de Inicios de vinculación.
- Lista de Fin vinculación.
- Lista de estados.

Output deseado: Una fila representa la información de UN solo integrante. Cada fila tiene las columnas:
- Codigo grupo
- Nombres
- CvLAC
- Horas dedicación
- Estado vinculacion
- Fecha de Vinculacion Inicial
- Fecha de finalizacion vinculacion
""" 
