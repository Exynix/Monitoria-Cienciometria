# Import Python libraries
from typing import List, NamedTuple
from enum import Enum
import traceback

import pandas as pd
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

# ---------

def check_is_table_empty(html_tr_table: str) -> bool:
    html_table_children_list = [
        element for element in html_tr_table.td.children if element.name is not None
    ]
    if len(html_table_children_list) == 1 and html_table_children_list[0].name == "a":
        return  True

    if len(html_table_children_list) == 1 and html_table_children_list[0].name != "a":
        return False

    if len(html_table_children_list) > 1:
        return False

    return True


# ---------
def identify_table_type (html_tr_table: str):
    inner_product_table_rows = html_tr_table.find_all("tr")
    second_row = inner_product_table_rows[1]
    second_row_td = second_row.td
    second_row_first_element_child = [element for element in second_row_td.children if element.name is not None][0]

    # Identification of scattered products. Looking for <li> tag.
    if second_row_first_element_child.name == "li":
        # Then, check if the li is empty or not.
        # If empty
        if not second_row_first_element_child.text.strip():
            return TableType.SUBTYPE_AS_EMPTY_LIST_ITEM
        # Has text, and necessarily will be a normal list item.
        else:
            return  TableType.SUBTYPE_AS_LIST_ITEM

    # Identification of scattered product with <b> tag
    if second_row_first_element_child.name == "b":
        return TableType.SUBTYPE_AS_BOLD_TAG

    # Identification of blockquote products
    if second_row_first_element_child.name == "blockquote":
        return TableType.BLOCKQUOTE_PRODUCTS

    if second_row_first_element_child.name == "table":
        return TableType.NESTED_TABLES

    return  TableType.UNIDENTIFIED


# ---------
def create_product_row(id_number: int, raw_product_html: str, product_type: str, product_subtype: str):
    return {
        "id_number": id_number,
        "raw_product_html": raw_product_html,
        "product_type": product_type,
        "raw_product_subtype": product_subtype
    }

# ---------
"""
def parse_table(html_tr_table: str, table_type: TableType, professor_id_num: int):

    id_number: int = professor_id_num
    raw_product: str
    product_type: str
    product_subtype: str
    html_tr_table_products = []

    inner_product_table_rows = html_tr_table.find_all("tr")
    product_type = inner_product_table_rows[0].h3.text.strip().capitalize()
    inner_product_table_rows = inner_product_table_rows[1:] # Remove title row

    # Same logic for self-contained products.
    if type == TableType.NESTED_TABLES or TableType.BLOCKQUOTE_PRODUCTS:
        for inner_row in inner_product_table_rows:
            new_row = create_product_row(id_number, inner_row.decode_contents(), product_type, None)
            html_tr_table_products.append(new_row)

    # Same logic for scattered products with a <li> tag.
    if type == TableType.SUBTYPE_AS_LIST_ITEM or TableType.SUBTYPE_AS_EMPTY_LIST_ITEM or TableType.SUBTYPE_AS_BOLD_TAG:
        # Filas impares ahora son los <li>, pares son productos.
        even_inner_rows = inner_product_table_rows[1::2]
        for inner_row in even_inner_rows:
            new_row = create_product_row(id_number, inner_row.decode_contents(), product_type, None)
            html_tr_table_products.append(new_row)

    if type == TableType.SUBTYPE_AS_BOLD_TAG:
        pass

    if type == TableType.UNIDENTIFIED:
        pass

    return html_tr_table_products
"""
def parse_table(html_tr_table: str, table_type: TableType, professor_id_num: int):
    id_number: int = professor_id_num
    html_tr_table_products = []

    inner_product_table_rows = html_tr_table.find_all("tr")
    product_type = inner_product_table_rows[0].h3.text.strip().capitalize()
    inner_product_table_rows = inner_product_table_rows[1:]  # Remove title row

    # Handle self-contained products
    if table_type in [TableType.NESTED_TABLES, TableType.BLOCKQUOTE_PRODUCTS]:
        for inner_row in inner_product_table_rows:
            new_row = create_product_row(
                id_number=id_number,
                raw_product_html=inner_row.decode_contents(),
                product_type=product_type,
                product_subtype=None
            )
            html_tr_table_products.append(new_row)

    # Handle scattered products with tags (<li> or <b>)
    elif table_type in [TableType.SUBTYPE_AS_LIST_ITEM,
                        TableType.SUBTYPE_AS_EMPTY_LIST_ITEM,
                        TableType.SUBTYPE_AS_BOLD_TAG]:
        # Get only even-indexed rows (0-based indexing)
        product_rows = inner_product_table_rows[1::2]
        subtype_rows = inner_product_table_rows[::2]

        for i, inner_row in enumerate(product_rows):
            # Get corresponding subtype if available
            subtype = None
            if i < len(subtype_rows):
                if table_type == TableType.SUBTYPE_AS_BOLD_TAG:
                    bold_tag = subtype_rows[i].find('b')
                    subtype = bold_tag.text.strip() if bold_tag else None
                else:
                    li_tag = subtype_rows[i].find('li')
                    subtype = li_tag.text.strip() if li_tag else None

            new_row = create_product_row(
                id_number=id_number,
                raw_product_html=inner_row.decode_contents(),
                product_type=product_type,
                product_subtype=subtype
            )
            html_tr_table_products.append(new_row)

    elif table_type == TableType.UNIDENTIFIED:
        # Log or handle unidentified table types as needed
        pass

    return html_tr_table_products

# ------------------ "Main" -------------------------------------------
normal_cvlacs_df = knio.input_tables[0].to_pandas()
product_table = [] # All products will be appended to this list

for cvlac_row in normal_cvlacs_df.itertuples(index=True):

    soup = BeautifulSoup(cvlac_row.Document, "html.parser")
# 1. Go to first product table
    product_tables = get_product_tables(soup)

    # 2. Iterate over all product tables, where in each table:
    for tr_table in product_tables:
        # 0. First check if table is empty. Skipped if empty.
        if check_is_table_empty(tr_table):
            continue

        # a. table type is identified.
        table_type = identify_table_type(tr_table)

        # b. table is parsed based on table type. A list of dictionaries is returned as the rows of the table parsed.
        product_table.extend(parse_table(tr_table, table_type, cvlac_row.id_documento))


products_df = pd.DataFrame(product_table)
knio.output_tables[0] = knio.Table.from_pandas(products_df)
