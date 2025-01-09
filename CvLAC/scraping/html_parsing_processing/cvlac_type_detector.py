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
    print("Error in parsing private page.")
    print(traceback.format_exc())
    return CvlacType.ERROR.value


# Identification of empty and normal pages. The detection for both goes hand in hand.
def detect_private_and_normal_pages(bs4Soup) -> str:
    # Firstly, the image element in the green message is searched. It serves as the initial reference point.
    green_msg_tick_img = bs4Soup.find("img", {"height": "15px", "width": "15px"})
    # Now, we go back to it's parent <td>. We have to go 3 levels up. img < blockquote < td <td
    green_msg_parent_td = green_msg_tick_img.parent.parent.parent
    green_msg_parent_td_siblings = [element for element in green_msg_parent_td.next_siblings if element.name is not None]

    # Now that we are on the same level as all other <tr>s (which then contain the products themselves). We iterate over all next_siblings.
    is_table_empty: bool = True
    for sibling_tr in green_msg_parent_td_siblings:
        # Inside each sibling tr, we look if the child <td> has more than 1 child. If it DOES, then it's not empty.
        # If it has 1 or 0 childs, the page so far is empty.
        sibling_tr_children_list = [element for element in sibling_tr.td.children if element.name is not None]
        if len(sibling_tr_children_list) > 1:
            is_table_empty = False
            return CvlacType.NORMAL.value
    return CvlacType.EMPTY.value



# Definition of main detection function
def parse_and_identify_page_type(df_row) -> str:

    html_string = df_row["Document"]
    cvlac_url = df_row["url_cvlac"]

    soup = BeautifulSoup(html_string, "html.parser")
    try:
        return detect_private_and_normal_pages(soup)

        # 4. If none of the if statements were entered, this is an unknown page.
        return CvlacType.UNKNOWN.value
    except:
        return detect_private_pages(soup)


# ----------------------------------------------------------

# ------------------ "Main" -------------------------------------------
all_cvlacs_df = knio.input_tables[0].to_pandas()
all_cvlacs_df["Type"] = all_cvlacs_df.apply(parse_and_identify_page_type, axis=1)

knio.output_tables[0] = knio.Table.from_pandas(all_cvlacs_df)
