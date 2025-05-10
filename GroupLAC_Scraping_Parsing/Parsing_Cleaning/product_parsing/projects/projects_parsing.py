#  ---------------------- Importación de librerias ----------------------
from enum import Enum
import sys
import re

import knime.scripting.io as knio

from bs4 import BeautifulSoup
import pandas as pd

#  ---------------------- Definición de enumeracion de mensajes de verificacion ----------------------
class MensajeVerficacion(Enum):
    TABLA_VALIDA = 1
    TABLA_SIN_CONTENIDOS = 0
    TABLA_INVALIDA = -1

#  ---------------------- Definición de funciones ----------------------

# Revisa si la tabla dada tiene registros, más alla del titulo y columnas de la tabla.
# Input: Tabla HTML completa de proyectos.
def revisar_contenidos_de_tabla(html_table: str) -> int:
    soup = BeautifulSoup(html_table, "html.parser")

    numero_filas = len(soup.find_all("tr"))

    # Si la tabla tiene menos de 2 filas, no hay proyectos.
    if (numero_filas < 2):
        # Si la tabla solo tiene 1 fila, solo tiene filas de headers y titulos.
        if (numero_filas == 1):
            return MensajeVerficacion.TABLA_SIN_CONTENIDOS.value
        # En cualquier otro caso, la tabla no es valida.
        else:
            return MensajeVerficacion.TABLA_INVALIDA.value

    # 2 filas o más significa que hay minimo un proyecto, y la tabla es valida.
    if (numero_filas >= 2):
        return MensajeVerficacion.TABLA_VALIDA.value

# ------

# Verificacion de existencia de tag <img>. Dice si el producto académico fue avalado.
def revisar_producto_avalado(fila_html: str) -> str:
    primera_celda = fila_html.find_all("td")[0]
    if primera_celda.find("img") is not None:
        return "Si"
    else:
        return "No"

# ------

# Extrae las fechas de inicio y finalización del proyecto
def extraer_fechas_proyecto(texto_fechas: str) -> tuple:
    # Limpiamos el texto
    texto_fechas = texto_fechas.strip()

    # Dividimos por el guión que separa las fechas
    partes = texto_fechas.split("-")

    # Extraemos la fecha de inicio
    fecha_inicio = partes[0].strip()

    # Extraemos la fecha de finalización
    if len(partes) > 1:
        fecha_fin = partes[1].strip()
        if fecha_fin.lower() == "actual":
            fecha_fin = None
    else:
        fecha_fin = None

    return fecha_inicio, fecha_fin

# ------

# Define el estado del proyecto basado en la fecha de finalización
def definir_estado(fecha_finalizacion: str) -> str:
    if fecha_finalizacion is None or fecha_finalizacion.lower() == "actual":
        return "En Curso"
    else:
        return "Finalizado"

# ------

# Revisa si un string está vacío y retorna None en ese caso
def revisar_string_vacio(input_string: str) -> str:
    if input_string is None or len(input_string.strip()) == 0:
        return None
    else:
        return input_string.strip()

#  ---------------------- Interpretacion de input como DF ----------------------
proyectos_df = knio.input_tables[0].to_pandas()

#  ---------------------- Creación de variables relevantes ----------------------
tablas_html = proyectos_df["HTML_Tabla_Proyectos"]
codigos_grupos = proyectos_df["Codigo_Grupo"]

productos_construidos = []

#  ---------------------- Parsing y procesamiento ----------------------

# Ciclo exterior para recorrer cada grupo
for index, tabla in enumerate(tablas_html):

    mensaje_verificacion = revisar_contenidos_de_tabla(tabla)

    # Omision de procesado de datos si la tabla no es valida.
    if (mensaje_verificacion == -1 or mensaje_verificacion == 0):
        continue

    # Asegurémonos que estamos trabajando con el elemento tbody
    if "<tbody>" not in tabla:
        tabla = f"<tbody>{tabla}</tbody>"

    soup = BeautifulSoup(tabla, "html.parser")

    # Se excluye la primera fila de la tabla (encabezado)
    filas_tabla = soup.find_all("tr")[1:]

    # Ciclo interior para recorrer cada fila de una tabla.
    for inner_index, fila in enumerate(filas_tabla):
        try:
            # Verificar si el producto está avalado
            avalado = revisar_producto_avalado(fila)

            # Obtener la segunda celda que contiene la información del proyecto
            segunda_celda = fila.find_all("td")[1]

            # Obtener el contenido completo como texto
            contenido_texto = segunda_celda.get_text(strip=True)

            # Encontrar el tag <b> que contiene el tipo de proyecto
            tag_b = segunda_celda.find("b")
            tipo_proyecto = tag_b.get_text() if tag_b else ""

            # Obtener el nombre del proyecto (después del tag <b>)
            # El formato es: "numero.- <b>tipo</b>: nombre del proyecto"
            nombre_completo = segunda_celda.get_text()

            # Encontrar la posición donde termina el tipo de proyecto
            pos_fin_tipo = nombre_completo.find(tipo_proyecto) + len(tipo_proyecto)
            # Extraer el nombre del proyecto (después de ":" que sigue al tipo)
            nombre_proyecto = nombre_completo[pos_fin_tipo:].split("<br>")[0].strip()
            if nombre_proyecto.startswith(":"):
                nombre_proyecto = nombre_proyecto[1:].strip()

            # Obtener el tag <br> y extraer el contenido después para las fechas
            tag_br = segunda_celda.find("br")
            if tag_br and tag_br.next_sibling:
                texto_fechas = tag_br.next_sibling.strip()
                fecha_inicio, fecha_finalizacion = extraer_fechas_proyecto(texto_fechas)
            else:
                fecha_inicio, fecha_finalizacion = None, None

            # Definir el estado del proyecto
            estado = definir_estado(fecha_finalizacion)

            # Obtener el código del grupo
            codigo_grupo = codigos_grupos[index]

            # Creación de la fila para el proyecto
            nuevo_producto = {
                "Codigo Grupo": codigo_grupo,
                "Tipo Proyecto": tipo_proyecto,
                "Nombre Proyecto": nombre_proyecto,
                "Estado": estado,
                "Fecha Inicio": fecha_inicio,
                "Fecha Finalizacion": fecha_finalizacion,
                "Avalado?": avalado
            }

            productos_construidos.append(nuevo_producto)

        except Exception as e:
            print(f"Error al procesar la fila {inner_index} del grupo {codigo_grupo}: {str(e)}")
            continue

# Crear el DataFrame de salida
output_df = pd.DataFrame(productos_construidos)

#  ---------------------- Output del dataframe ----------------------
knio.output_tables[0] = knio.Table.from_pandas(output_df)