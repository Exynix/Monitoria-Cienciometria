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
def parse_and_identify_page_type(df_row) -> str:

    html_string = df_row["Document"]
    cvlac_url = df_row["url_cvlac"]

    soup = BeautifulSoup(html_string, "html.parser")

    try:
        # 1. Identification of private pages. They are the simplest ones.
        only_body_html_tags = [element for element in soup.body.contents if element.name is not None]
        if len(only_body_html_tags) == 3:
            return CvlacType.PRIVATE.value

        # 2. Identification of empty pages. Second simplest.
        content_div = soup.select_one("div.container") # First level. body > div
        main_content_tbody = content_div.find("tbody") #  Third level. div > table > tbody
        social_media_tr = main_content_tbody.find_all("tr")[2] # Fourth level. div > table > tbody > tr
        social_media_td = social_media_tr.find("td") # Fifth level. div > table > tbody > tr > td
        social_media_html_tags = [element for element in social_media_td.contents if element.name is not None]

        # If there's only 1 element inside the social media <td>, the profile is counted as empty, as there's always
        # as a minimum, an <a> tag inside.
        if len(social_media_html_tags) == 1:
            return CvlacType.EMPTY.value

        # 3. If inside the social media <td>, there's 2 tags (<a> and <table>) the profile is likely filled, or full.
        # The profile is counted as a normal profile.
        if len(social_media_html_tags) == 2:
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