from typing import List, NamedTuple
from enum import Enum

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


# Data structure for each row of all dataframes.
class ParsedCvlac(NamedTuple):
    url_cvlac: str
    html_document: str
    cvlac_type: CvlacType

# ----------------------------------------------------------
def parse_and_identify_page_type(html_string: str) -> str:
    soup = BeautifulSoup(html_string, "html.parser")

    # 1. Identification of private pages. They are the simplest ones.
    only_body_html_tags = [element for element in soup.body.contents if element.name is not None]
    if len(only_body_html_tags) == 3:
        return CvlacType.PRIVATE.value

    # 2. Identification of empty pages. Second simplest.
    content_div = soup.select("div.container") # First level. body > div
    main_content_tbody = content_div.find("tbody")
# ----------------------------------------------------------

# ------------------ "Main" -------------------------------------------
all_cvlacs_df = knio.input_tables[0].to_pandas()
all_cvlacs_df["Type"] = all_cvlacs_df["Document"].apply(parse_and_identify_page_type)





normal_cvlacs_list: list[ParsedCvlac]
private_cvlacs_df: list[ParsedCvlac]
empty_cvlacs_df: list[ParsedCvlac]
unknown_type_cvlacs: list[ParsedCvlac]

knio.output_tables[0] = knio.input_tables[0]
