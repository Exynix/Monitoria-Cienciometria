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

#  ---------------------- Definition of Functions ---------------------- 


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
        print("No match found")
        return None
    
   # If the function returns false, then the string doesn't have any digits or numbers. That's why we return null.
    if check_if_string_is_alphanumeric (search_result.group(0)) == False:
        print("string sent is whitespace or doesn't contain alphanumeric characters.", repr(string_to_check))
        return None
    else:
        return search_result.group(0).strip()
 
# ------------ Functions specific to parsing of art_production. -----------------

def parse_obras_productos_table(html_table_rows, built_products):

    end_of_table = False

    soup = BeautifulSoup(tabla, "html.parser")

    for row in html_table_rows:

        # Check if the actual row is a header row. 

        if row
    
# Left intentionally blank to represent that the table has to be parsed, but empty because no group with this type of
# product has been found yet.
def parse_industrias_creativas_table():
    pass


def parse_eventos_artisticos_table():
    pass


def parse_talleres_creacion_table():
    pass



#  ---------------------- Interpretacion de input como DF ---------------------- 
art_products_df = knio.input_tables[0].to_pandas()
    

#  ---------------------- Creación de variables relevantes ---------------------- 
tablas_html = art_products_df["HTML_Tabla_ProductosArte"]
codigos_grupos = art_products_df["Codigo_Grupo"]

built_products = []

#  ---------------------- Parsing y procesamiento ---------------------- 

# Ciclo exterior para recorrer cada grupo
for index, tabla in enumerate(tablas_html):

    # We have to check the 4 tables for each group. If the table only has 5 rows, the group doesn't have any art product
    # and can be skipped.
    verification_message = check_if_table_has_content(tabla, 5)
    
    # Ommision of group if no products are found.
    if (verification_message == MensajeVerficacion.TABLA_INVALIDA.value 
        or 
        verification_message == MensajeVerficacion.TABLA_SIN_CONTENIDOS.value):
        continue

    soup = BeautifulSoup(tabla, "html.parser")

    tipo_norma: str
    nombre_norma: str
    ambito: str
    fecha_publicacion: str
    institucion_financiadora: str

    # Exclude "Produccion en arte..."  and "Obras o productos"
    table_rows = soup.find_all("tr")[2:]
    
    parse_obras_productos_table()

    parse_industrias_creativas_table()

    parse_eventos_artisticos_table()

    parse_talleres_creacion_table()

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
        
        built_products.append(nuevo_producto)
        


output_df = pd.DataFrame(built_products)

#  ---------------------- Output del dataframe ---------------------- 
knio.output_tables[0] = knio.Table.from_pandas(output_df)

















"""
"<tbody><tr>
            <td class=""celdaEncabezado"" colspan=""2"">Producción en arte, arquitectura y diseño</td>
        </tr>
        <tr>
            <td class=""celdaEncabezado"" colspan=""2"">Obras o productos</td>
        </tr>
        
        <tr>
            <td class=""celdaEncabezado"" colspan=""2"">Industrias creativas y culturales</td>
        </tr>
        
        <tr>
            <td class=""celdaEncabezado"" colspan=""2"">Eventos Artísticos</td>
        </tr>
        
        <tr>
            <td class=""celdaEncabezado"" colspan=""2"">Talleres de Creación</td>
        </tr>
        
    </tbody>"

------------------------------------------------------------------

"<tbody><tr>
            <td class=""celdaEncabezado"" colspan=""2"">Producción en arte, arquitectura y diseño</td>
        </tr>
        <tr>
            <td class=""celdaEncabezado"" colspan=""2"">Obras o productos</td>
        </tr>
        

        <tr>
            <td class=""celdas_1"" align=""right""> 

                
            </td>
            <td class=""celdas1"">
                Nombre del Producto: TRASTOS,<br>                
                Fecha de creación: Junio de 2020                   
                Disciplina o ámbito de origen: Humanidades -- Arte -- Danza o Artes danzarías
                <br>
                                
                <strong><br>Instancias de valoración<br></strong>
                    
                Nombre del espacio o evento: TEATRO EL PARQUE, Fecha de presentación: 2021-11-30, Entidad convocante 1: Instituto Distrital de las Artes - Idartes
                
                <br>
                
            </td>


            
        </tr> 

        

        <tr>
            <td class=""celdas_0"" align=""right""> 

                
            </td>
            <td class=""celdas0"">
                Nombre del Producto: LELIO O EL RETORNO A LA VIDA,<br>                
                Fecha de creación: Marzo de 2020                   
                Disciplina o ámbito de origen: Humanidades -- Arte -- Otras artes
                <br>
                                
                <strong><br>Instancias de valoración<br></strong>
                    
                Nombre del espacio o evento: Festival Internacional de las Artes, Fecha de presentación: 2018-04-07, Entidad convocante 1: Ministerio De Cultura De Colombia
                
                Nombre del espacio o evento: Temporada La Mirada del Avestruz, Fecha de presentación: 2017-06-08, Entidad convocante 1: PONTIFICIA UNIVERSIDAD JAVERIANA
                
                Nombre del espacio o evento: Celebraci¿n cumplea¿os 90 Universidad Javeriana , Fecha de presentación: 2020-02-28, Entidad convocante 1: PONTIFICIA UNIVERSIDAD JAVERIANA
                
                <br>
                
            </td>


            
        </tr> 

        

        <tr>
            <td class=""celdas_1"" align=""right""> 

                
                <img src=""/gruplac/images/chulo_1.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas1"">
                Nombre del Producto: La Razon de las Ofelias,<br>                
                Fecha de creación: Febrero de 2019                   
                Disciplina o ámbito de origen: Humanidades -- Arte -- Danza o Artes danzarías
                <br>
                                
                <strong><br>Instancias de valoración<br></strong>
                    
                Nombre del espacio o evento: III Festibienal de de Teatro de  Bogota, Fecha de presentación: 2019-04-19, Entidad convocante 1: Fundacion Factoria L' explose
                
                Nombre del espacio o evento: Factoria L'explose, Fecha de presentación: 2019-02-08, Entidad convocante 1: Fundacion Factoria L' explose
                
                <br>
                
            </td>


            
        </tr> 

        

        <tr>
            <td class=""celdas_0"" align=""right""> 

                
                <img src=""/gruplac/images/chulo_0.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas0"">
                Nombre del Producto: La Razon de las Ofelias,<br>                
                Fecha de creación: Febrero de 2019                   
                Disciplina o ámbito de origen: Humanidades -- Arte -- Danza o Artes danzarías
                <br>
                                
                <strong><br>Instancias de valoración<br></strong>
                    
                Nombre del espacio o evento: III Festibienal de de Teatro de  Bogota, Fecha de presentación: 2019-04-19, Entidad convocante 1: Fundacion Factoria L' explose
                
                Nombre del espacio o evento: Factoria L'explose, Fecha de presentación: 2019-02-08, Entidad convocante 1: Fundacion Factoria L' explose
                
                <br>
                
            </td>


            
        </tr> 

        

        <tr>
            <td class=""celdas_1"" align=""right""> 

                
                <img src=""/gruplac/images/chulo_1.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas1"">
                Nombre del Producto: Iris,<br>                
                Fecha de creación: Septiembre de 2018                   
                Disciplina o ámbito de origen: Humanidades -- Arte -- Danza o Artes danzarías
                <br>
                                
                <strong><br>Instancias de valoración<br></strong>
                    
                Nombre del espacio o evento: Temporada de la obra Iris, Fecha de presentación: 2018-04-26, Entidad convocante 1: PONTIFICIA UNIVERSIDAD JAVERIANA
                
                Nombre del espacio o evento: Temporada de Carmina Burana, Fecha de presentación: 2018-06-21, Entidad convocante 1: PONTIFICIA UNIVERSIDAD JAVERIANA
                
                Nombre del espacio o evento: Festival Detonos, Fecha de presentación: 2019-10-13, Entidad convocante 1: Corporación cortocinesis
                
                <br>
                
            </td>


            
        </tr> 

        

        <tr>
            <td class=""celdas_0"" align=""right""> 

                
                <img src=""/gruplac/images/chulo_0.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas0"">
                Nombre del Producto: Iris,<br>                
                Fecha de creación: Septiembre de 2018                   
                Disciplina o ámbito de origen: Humanidades -- Arte -- Danza o Artes danzarías
                <br>
                                
                <strong><br>Instancias de valoración<br></strong>
                    
                Nombre del espacio o evento: Temporada de la obra Iris, Fecha de presentación: 2018-04-26, Entidad convocante 1: PONTIFICIA UNIVERSIDAD JAVERIANA
                
                Nombre del espacio o evento: Temporada de Carmina Burana, Fecha de presentación: 2018-06-21, Entidad convocante 1: PONTIFICIA UNIVERSIDAD JAVERIANA
                
                Nombre del espacio o evento: Festival Detonos, Fecha de presentación: 2019-10-13, Entidad convocante 1: Corporación cortocinesis
                
                <br>
                
            </td>


            
        </tr> 

        

        <tr>
            <td class=""celdas_1"" align=""right""> 

                
            </td>
            <td class=""celdas1"">
                Nombre del Producto: Iris,<br>                
                Fecha de creación: Septiembre de 2018                   
                Disciplina o ámbito de origen: Humanidades -- Arte -- Danza o Artes danzarías
                <br>
                                
                <strong><br>Instancias de valoración<br></strong>
                    
                Nombre del espacio o evento: Temporada de la obra Iris, Fecha de presentación: 2018-04-26, Entidad convocante 1: PONTIFICIA UNIVERSIDAD JAVERIANA
                
                Nombre del espacio o evento: Temporada de Carmina Burana, Fecha de presentación: 2018-06-21, Entidad convocante 1: PONTIFICIA UNIVERSIDAD JAVERIANA
                
                Nombre del espacio o evento: Festival Detonos, Fecha de presentación: 2019-10-13, Entidad convocante 1: Corporación cortocinesis
                
                <br>
                
            </td>


            
        </tr> 

        

        <tr>
            <td class=""celdas_0"" align=""right""> 

                
                <img src=""/gruplac/images/chulo_0.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas0"">
                Nombre del Producto: Cancionero para Señoritas,<br>                
                Fecha de creación: Julio de 2018                   
                Disciplina o ámbito de origen: Humanidades -- Arte -- Danza o Artes danzarías
                <br>
                                
                <strong><br>Instancias de valoración<br></strong>
                    
                Nombre del espacio o evento: Cancionero para Señoritas, Fecha de presentación: 2018-08-27, Entidad convocante 1: Corporación Colombiana de Teatro
                
                Nombre del espacio o evento: Temporada de Cancionero para Señoritas, Fecha de presentación: 2018-08-27, Entidad convocante 1: Ministerio De Cultura De Colombia
                
                <br>
                
            </td>


            
        </tr> 

        

        <tr>
            <td class=""celdas_1"" align=""right""> 

                
                <img src=""/gruplac/images/chulo_1.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas1"">
                Nombre del Producto: Cancionero para Señoritas,<br>                
                Fecha de creación: Julio de 2018                   
                Disciplina o ámbito de origen: Humanidades -- Arte -- Danza o Artes danzarías
                <br>
                                
                <strong><br>Instancias de valoración<br></strong>
                    
                Nombre del espacio o evento: Cancionero para Señoritas, Fecha de presentación: 2018-08-27, Entidad convocante 1: Corporación Colombiana de Teatro
                
                Nombre del espacio o evento: Temporada de Cancionero para Señoritas, Fecha de presentación: 2018-08-27, Entidad convocante 1: Ministerio De Cultura De Colombia
                
                <br>
                
            </td>


            
        </tr> 

        

        <tr>
            <td class=""celdas_0"" align=""right""> 

                
                <img src=""/gruplac/images/chulo_0.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas0"">
                Nombre del Producto: Hermana Republica,<br>                
                Fecha de creación: Junio de 2018                   
                Disciplina o ámbito de origen: Humanidades -- Arte -- Danza o Artes danzarías
                <br>
                                
                <strong><br>Instancias de valoración<br></strong>
                    
                Nombre del espacio o evento: Teatro La Factoria L'Explose, Fecha de presentación: 2018-06-21, Entidad convocante 1: PONTIFICIA UNIVERSIDAD JAVERIANA
                
                <br>
                
            </td>


            
        </tr> 

        

        <tr>
            <td class=""celdas_1"" align=""right""> 

                
                <img src=""/gruplac/images/chulo_1.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas1"">
                Nombre del Producto: La Mirada del Avestruz,<br>                
                Fecha de creación: Junio de 2017                   
                Disciplina o ámbito de origen: Humanidades -- Arte -- Danza o Artes danzarías
                <br>
                                
                <strong><br>Instancias de valoración<br></strong>
                    
                Nombre del espacio o evento: Festival Internacional de las Artes, Fecha de presentación: 2018-04-07, Entidad convocante 1: Ministerio De Cultura De Colombia
                
                Nombre del espacio o evento: Temporada La Mirada del Avestruz, Fecha de presentación: 2017-06-08, Entidad convocante 1: PONTIFICIA UNIVERSIDAD JAVERIANA
                
                Nombre del espacio o evento: Celebraci¿n cumplea¿os 90 Universidad Javeriana , Fecha de presentación: 2020-02-28, Entidad convocante 1: PONTIFICIA UNIVERSIDAD JAVERIANA
                
                <br>
                
            </td>


            
        </tr> 

        

        <tr>
            <td class=""celdas_0"" align=""right""> 

                
            </td>
            <td class=""celdas0"">
                Nombre del Producto: La Mirada del Avestruz,<br>                
                Fecha de creación: Junio de 2017                   
                Disciplina o ámbito de origen: Humanidades -- Arte -- Danza o Artes danzarías
                <br>
                                
                <strong><br>Instancias de valoración<br></strong>
                    
                Nombre del espacio o evento: Festival Internacional de las Artes, Fecha de presentación: 2018-04-07, Entidad convocante 1: Ministerio De Cultura De Colombia
                
                Nombre del espacio o evento: Temporada La Mirada del Avestruz, Fecha de presentación: 2017-06-08, Entidad convocante 1: PONTIFICIA UNIVERSIDAD JAVERIANA
                
                Nombre del espacio o evento: Celebraci¿n cumplea¿os 90 Universidad Javeriana , Fecha de presentación: 2020-02-28, Entidad convocante 1: PONTIFICIA UNIVERSIDAD JAVERIANA
                
                <br>
                
            </td>


            
        </tr> 

        
        <tr>
            <td class=""celdaEncabezado"" colspan=""2"">Industrias creativas y culturales</td>
        </tr>
        
        <tr>
            <td class=""celdaEncabezado"" colspan=""2"">Eventos Artísticos</td>
        </tr>
        

        <tr>
            <td class=""celdas_1"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_1.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas1"">
                Nombre del evento: TEATRO EL PARQUE<br>
                Fecha de inicio: 2020-01-06,Fecha de finalización: 2020-12-25<br>
                Descripción del evento:      
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_0"" align=""right"">                    
                
            </td>
            <td class=""celdas0"">
                Nombre del evento: Archivo Vivo<br>
                Fecha de inicio: 2019-04-26,Fecha de finalización: <br>
                Descripción del evento: Mis labores consisten en:

-Representar al Departamento de Artes Escénicas de la Pontificia Universidad Javeriana. 
- Dinamizar encuentros y organizar actividades del proyecto     
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_1"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_1.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas1"">
                Nombre del evento: III Festibienal de Teatro de  Bogota<br>
                Fecha de inicio: 2019-04-13,Fecha de finalización: 2019-04-21<br>
                Descripción del evento: Bailarina en la obra ""La Razón de las Ofelias"" con la compañía L'Explose.      
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_0"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_0.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas0"">
                Nombre del evento: III Festibienal de Teatro de Bogota<br>
                Fecha de inicio: 2019-04-13,Fecha de finalización: 2019-04-21<br>
                Descripción del evento: Participación cimo bailarina en la obra ""La Razín de las Ofelias"" los días 19 y 20 se Abril de 2019 en el marco del III Festibienal de Teatro de Bogotá.     
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_1"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_1.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas1"">
                Nombre del evento: Temporada de La Razon de las Ofelias<br>
                Fecha de inicio: 2019-02-08,Fecha de finalización: 2019-02-24<br>
                Descripción del evento: Temporada de la obra ""La Razón de las Ofelias"" de la Compañía L'Explose.      
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_0"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_0.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas0"">
                Nombre del evento: Temporada de la obra Iris<br>
                Fecha de inicio: 2018-10-26,Fecha de finalización: 2018-10-27<br>
                Descripción del evento: Organizadora y bailarina en la Temporada de la obra Iris en la Programación del Teatro Factoría L'Explose     
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_1"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_1.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas1"">
                Nombre del evento:  Festival Detonos<br>
                Fecha de inicio: 2018-09-29,Fecha de finalización: 2018-10-27<br>
                Descripción del evento: Artista invitada a crear y presentar una obra dentro del marco de la Residencia Artística del Festival Detonos.     
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_0"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_0.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas0"">
                Nombre del evento: Temporada de Cancionero para Señoritas<br>
                Fecha de inicio: 2018-08-27,Fecha de finalización: 2018-09-01<br>
                Descripción del evento: Temporada de la obra Cancionero para Señoritas en la Sala Seki Sano. Fui organizadora, co-directora de la obra y bailarina. Cancionero para Señoritas pertenece al proyecto ""Apropiación de la tradición desde la corporalidad contemporánea"", de la cual sky investigadora principal.     
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_1"" align=""right"">                    
                
            </td>
            <td class=""celdas1"">
                Nombre del evento: Hermana Republica<br>
                Fecha de inicio: 2018-06-21,Fecha de finalización: 2018-06-30<br>
                Descripción del evento: Asistente de la dirección en la obra, Hermana Republica; una obra escénica que surge a partir de una investigación colaborativa entre artistas de diferentes nacionalidades para abordar, desde el cuerpo, las huellas de la migración. El instinto del hogar, la poética del viaje, las dinámicas de encuentro y desencuentro, los choques culturales... son temas que dan vida a una creación coreográfica que surge de la experiencia intima de sus creadores.     
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_0"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_0.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas0"">
                Nombre del evento: Hermana Republica Temporada de Estreno<br>
                Fecha de inicio: 2018-06-21,Fecha de finalización: 2018-06-30<br>
                Descripción del evento: Funciones de la obra escenica Hermana Reepublica en la Factoria L'explose.     
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_1"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_1.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas1"">
                Nombre del evento: Temporada Hermana República<br>
                Fecha de inicio: 2018-06-21,Fecha de finalización: 2018-06-30<br>
                Descripción del evento: Temporada de la obra Hermana República en el Teatro La Factoría. 6 Funciones     
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_0"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_0.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas0"">
                Nombre del evento: Temporada de Carmina Burana Teatro Mayor Julio Mario Santo Domingo 2018<br>
                Fecha de inicio: 2018-06-21,Fecha de finalización: 2018-06-23<br>
                Descripción del evento: Bailarina en el montaje de Carmina Burana con la compañía L'explose, la Orquesta Sinfónica Nacional y el Coro de la Ópera de Colombia. Producción del Teatro Mayor Julio Mario Santo Domingo. Temporada de funciones del 21 al 23 de Junio de 2018.     
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_1"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_1.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas1"">
                Nombre del evento: Temporada de Carmina Burana Gran Teatro Nacional de Lima<br>
                Fecha de inicio: 2018-04-18,Fecha de finalización: 2018-07-20<br>
                Descripción del evento: Bailarina en el montaje de Carmina Burana con la compañía L'explose, la Orquesta Sinfónica Nacional y el Coro Nacional de Perú. Producción del Teatro Mayor Julio Mario Santo Domingo de Bogotá y el Gran Teatro Nacional de Lima. Temporada de funciones del 18 al 20 de junio de 2018.     
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_0"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_0.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas0"">
                Nombre del evento: X Festival Danza en la Ciudad<br>
                Fecha de inicio: 2017-11-12,Fecha de finalización: 2017-11-12<br>
                Descripción del evento: Bailarina en la obra ""Del Otro Lado"" con la compañía La Bestia, dentro del marco del X Festival Danza en la Ciudad que se realizó del 1 al 13 de Noviembre de 2017. Lugar, parqueadero de La Candelaria, Bogotá.     
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_1"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_1.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas1"">
                Nombre del evento: IV Encuentro Endanzante<br>
                Fecha de inicio: 2017-09-28,Fecha de finalización: 2017-09-28<br>
                Descripción del evento: Presentación de la obra ""Del otro Lado"" con la Compañía La Bestia dirigida por Eduardo Oramas. Teatro Popular de Medellin.      
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_0"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_0.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas0"">
                Nombre del evento: Temporada de La Mirada del Avestruz<br>
                Fecha de inicio: 2017-06-08,Fecha de finalización: 2017-06-25<br>
                Descripción del evento: Temporada de la obra La Mirada del Avestruz de la Compañía L'Explose en el Teatro Factoría L'Explose. Participé como bailarina.     
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_1"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_1.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas1"">
                Nombre del evento: Función Del Otro Lado Aula Múltiple PUJ<br>
                Fecha de inicio: 2016-11-19,Fecha de finalización: 2016-11-19<br>
                Descripción del evento: Presentación de la Obra Del Otro Lado cin el colectivo La Bestia, como parte de la programación cultural del Aula Múltiple de la Facultad de Artes de la Pontificia Universidad Javeriana de Bogotá. Yo fui organizadora del evento.      
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_0"" align=""right"">                    
                
            </td>
            <td class=""celdas0"">
                Nombre del evento: IX Festival Danza en la Ciudad<br>
                Fecha de inicio: 2016-11-10,Fecha de finalización: 2016-11-11<br>
                Descripción del evento: Co-creadora junto con Santiago Parada de la obra ""Niebla"", producto de proyecto seleccionado por convocatoria para ser mostrado en el IX Festival Danza en la Ciudad, 2016     
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_1"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_1.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas1"">
                Nombre del evento: IX Festival Danza en la Ciudad<br>
                Fecha de inicio: 2016-11-10,Fecha de finalización: 2016-11-11<br>
                Descripción del evento: Creación y muestra de ""Niebla"" junto con el artista Santiago Parada. Proyecto selecionado por convocatoria en el IX Festival de Danza en la Ciudad.      
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_0"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_0.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas0"">
                Nombre del evento: Encuentro Javeriano de Arte y Creatividad<br>
                Fecha de inicio: 2016-09-11,Fecha de finalización: 2016-09-16<br>
                Descripción del evento: Ponencia sobre el proceso de creación de la obra ""Feroz, una tragedia clown""     
            </td>        
        </tr> 

        

        <tr>
            <td class=""celdas_1"" align=""right"">                    
                
                <img src=""/gruplac/images/chulo_1.jpg"" height=""15px"" width=""15px"">
                
            </td>
            <td class=""celdas1"">
                Nombre del evento: El marrano no se vende<br>
                Fecha de inicio: 2016-08-26,Fecha de finalización: 2016-08-26<br>
                Descripción del evento: Participación como bailarina invitada al Festival de Improvisación El marrano no se vende.      
            </td>        
        </tr> 

        
        <tr>
            <td class=""celdaEncabezado"" colspan=""2"">Talleres de Creación</td>
        </tr>
        
    </tbody>"

"""