from typing import List, NamedTuple
from enum import Enum
import traceback

from bs4 import BeautifulSoup
import knime.scripting.io as knio

# 1. Processing of each row.
# 2. Function for detecting the type of cvlac.
# 3. Appending of row to the corresponding list.
# 4. Creation and exporting of corresponding DFs


# Enum for all possible types of CvLAC
class CvlacType(Enum):
    NORMAL = "Normal"
    PRIVATE = "Privado"
    EMPTY = "Vacio"
    UNKNOWN = "Tipo desconocido"
    ERROR = "Error processando la URL"


# Data structure for each row of all dataframes.
class ParsedCvlac(NamedTuple):
    url_cvlac: str
    html_document: str
    cvlac_type: CvlacType

# ----------------------------------------------------------
# Definition of detectiion function
def parse_and_identify_page_type(df_row) -> str:

    html_string = df_row["Document"]
    cvlac_url = df_row["url_cvlac"]

    soup = BeautifulSoup(html_string, "html.parser")

    try:
        # 1. Identification of private pages. They are the simplest ones.
        private_msg_baseline = "La información de este currículo no está disponible por solicitud del investigador"
        private_msg_scraped = soup.find_all("blockquote")[1].text.strip()
        if private_msg_scraped == private_msg_baseline:
            return CvlacType.PRIVATE.value

        # 2. Identification of empty pages. Second simplest.
        academic_formation_string = "Formación Académica"
        academic_formation_element_string = soup.find(string=academic_formation_string)

        if academic_formation_element_string is None:
            return CvlacType.EMPTY.value

        if academic_formation_element_string is not None:
            return CvlacType.NORMAL.value


        # 4. If none of the if statements were entered, this is an unknown page.
        return CvlacType.UNKNOWN.value
    except:
        print(f"Error ocurred in processing of cvlac: {cvlac_url}")
        print(traceback.format_exc())
        return CvlacType.ERROR.value


# ----------------------------------------------------------

# ------------------ "Main" -------------------------------------------
all_cvlacs_df = knio.input_tables[0].to_pandas()
all_cvlacs_df["Type"] = all_cvlacs_df.apply(parse_and_identify_page_type, axis=1)

knio.output_tables[0] = knio.Table.from_pandas(all_cvlacs_df)
