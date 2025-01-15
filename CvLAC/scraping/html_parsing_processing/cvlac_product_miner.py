# Import Python libraries
from typing import List, NamedTuple
from enum import Enum
import traceback

# Import third party modules
from bs4 import BeautifulSoup
import knime.scripting.io as knio

# ----------------------------------------------------------
# Definition of Table type Enum
class TableType(Enum):
    NESTED_TABLES = "Self contained product. Product information is inside nested tables."
    BLOCKQUOTE_PRODUCTS = "Self contained product. All product information inside Blockquote"
    SUBTYPE_AS_LIST_ITEM = "Scattered information. Subtype is in <li> tag."
    SUBTYPE_AS_EMPTY_LIST_ITEM= "Scattered information. Subtype should be in <li> tag, but the tag is empty."
    SUBTYPE_AS_BOLD_TAG = "Scattered information. Subtype is in <b> tag."
    UNIDENTIFIED = "Table type couldn't be identified."

# ----------------------------------------------------------
def get_product_tables(bs4Soup) -> []:
    green_msg_tick_img = bs4Soup.find("img", {"height": "15px", "width": "15px"})
    green_msg_parent_tr = green_msg_tick_img.parent.parent.parent
    green_msg_parent_tr_siblings = [element for element in green_msg_parent_tr.next_siblings if element.name is not None]
    return green_msg_parent_tr_siblings

def check_is_table_empty(html_table: str) -> bool:
    html_table_children_list = [
        element for element in html_table.td.children if element.name is not None
    ]
    if len(html_table_children_list) > 1:
        return False

    return True


def identify_table_type (html_table: str):
    pass


def parse_table(html_table_element: str, type:TableType):
    if type == TableType.NESTED_TABLES:
        pass
    if type == TableType.BLOCKQUOTE_PRODUCTS:
        pass
    if type == TableType.SUBTYPE_AS_LIST_ITEM:
        pass
    if type == TableType.SUBTYPE_AS_EMPTY_LIST_ITEM:
        pass
    if type == TableType.SUBTYPE_AS_BOLD_TAG:
        pass
    if type == TableType.UNIDENTIFIED:
        pass

# ------------------ "Main" -------------------------------------------
normal_cvlacs_df = knio.input_tables[0].to_pandas()
product_table = [] # All products will be appended to this list

for cvlac_row in normal_cvlacs_df.itertuples(index=True):

    soup = BeautifulSoup(cvlac_row.Document, "html.parser")
    # 1. Go to first product table
    product_tables = get_product_tables(soup)

    # 2. Iterate over all product tables, where in each table:
    for table in product_tables:
        # 0. First check if table is empty. Skipped if empty.
        if check_is_table_empty(table):
            continue

        # a. table type is identified.
        table_type = identify_table_type(table)

        # b. table is parsed based on table type. A list of dictionaries is returned as the rows of the table parsed.
        product_table.extend(parse_table(table, table_type))



knio.output_tables[0] = knio.Table.from_pandas(all_cvlacs_df)
