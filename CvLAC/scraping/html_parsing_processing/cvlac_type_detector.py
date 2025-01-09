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


def detect_private_pages(bs4Soup) -> str:
    private_msg_baseline = "La información de este currículo no está disponible por solicitud del investigador"
    private_msg_scraped = bs4Soup.find_all("blockquote")[1].text.strip()
    if private_msg_scraped == private_msg_baseline:
        return CvlacType.PRIVATE.value
    else:
        return CvlacType.NORMAL.value


def detect_empty_and_normal_pages(bs4Soup) -> str:
    try:
        green_msg_tick_img = bs4Soup.find("img", {"height": "15px", "width": "15px"})
        green_msg_parent_td = green_msg_tick_img.parent.parent.parent
        green_msg_parent_td_siblings = [element for element in green_msg_parent_td.next_siblings if element.name is not None]

        is_table_empty: bool = True
        for sibling_tr in green_msg_parent_td_siblings:
            sibling_tr_children_list = [
                element for element in sibling_tr.td.children if element.name is not None
            ]
            if len(sibling_tr_children_list) > 1:
                is_table_empty = False
                return CvlacType.NORMAL.value

        return CvlacType.EMPTY.value

    except Exception as e:
        print(f"Error in detect_private_and_normal_pages: {e}")
        print(traceback.format_exc())
        return CvlacType.ERROR.value


def parse_and_identify_page_type(df_row) -> str:
    html_string = df_row["Document"]
    cvlac_url = df_row["url_cvlac"]

    soup = BeautifulSoup(html_string, "html.parser")
    try:
        return detect_private_pages(soup)
    except:
        return detect_empty_and_normal_pages(soup)


# ----------------------------------------------------------

# ------------------ "Main" -------------------------------------------
all_cvlacs_df = knio.input_tables[0].to_pandas()
all_cvlacs_df["Type"] = all_cvlacs_df.apply(parse_and_identify_page_type, axis=1)

knio.output_tables[0] = knio.Table.from_pandas(all_cvlacs_df)
