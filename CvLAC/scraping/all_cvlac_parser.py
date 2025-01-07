# --------------------------  Importation of libraries. --------------------------
import knime.scripting.io as knio
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict

# -------------------------- Definition of functions --------------------------

def load_html(html_content):
    """
    Parse HTML content into a BeautifulSoup object.
    """
    if pd.isnull(html_content):
        return None
    return BeautifulSoup(html_content, 'html.parser')


def detect_structure(soup):
    """
    Detect whether the page is 'empty', 'normal', or 'unknown'.
    """
    if not soup:
        return "missing"

    blockquote = soup.find('blockquote')
    if blockquote and blockquote.text.strip() == "La información de este currículo no está disponible por solicitud del investigador":
        return "empty"

    divs = soup.body.find_all('div', recursive=False)
    if len(divs) >= 3:
        return "normal"

    return "unknown"


def process_normal_page(soup):
    """
    Process a 'normal' page to extract product categories and counts.
    """
    divs = soup.body.find_all('div', recursive=False)
    target_div = divs[2]

    # Locate the main <table> within the third <div>
    table = target_div.find('table')
    if not table:
        return {}

    # Dictionary to hold tallies by product category
    product_tallies = defaultdict(int)

    # Iterate over rows starting from the 14th
    rows = table.find_all('tr')[13:]  # 0-based index, 14th row is index 13
    current_category = None

    for row in rows:
        tds = row.find_all('td')
        if not tds:
            continue

        # Check if the row starts a new category (with <h3>)
        h3 = tds[0].find('h3')
        if h3:
            current_category = h3.text.strip()
            product_tallies[current_category] = 0
            continue

        # Count products in the current category
        if current_category:
            blockquote = tds[0].find('blockquote')
            if blockquote:
                product_tallies[current_category] += 1
                continue

            # Handle intercalated redundant rows
            li = tds[0].find('li')
            if li and li.find('b'):
                img_tag = li.find_next_sibling('img')
                if img_tag:
                    product_tallies[current_category] += 1

    return product_tallies


def process_page(row):
    """
    Main processing function for each row in the input DataFrame.
    Returns product tallies or a reason for failure.
    """
    soup = load_html(row["Document"])
    structure = detect_structure(soup)

    if structure == "missing":
        return None, "Missing HTML Document"
    elif structure == "empty":
        return None, "Empty CvLAC Page"
    elif structure == "normal":
        product_tallies = process_normal_page(soup)
        return product_tallies, None
    else:
        return None, "Unknown Page Structure"

# -------------------------- "Main()" --------------------------

# 1. Interpretation of input table as DF.
scraped_cvlac_htmls = knio.input_tables[0].to_pandas()

# Output tables
tallies_data = []
error_data = []

# Process each row in the input table
for _, row in scraped_cvlac_htmls.iterrows():
    product_tallies, error_reason = process_page(row)

    if error_reason:
        # Append to error table
        error_data.append({
            "ID Documento": row["ID Documento"],
            "Nombre Completo Normalizado": row["Nombre Completo Normalizado"],
            "url_cvlac": row["url_cvlac"],
            "Razon": error_reason
        })
    else:
        # Append to tallies table
        tallies_row = {
            "ID Documento": row["ID Documento"],
            "Nombre Completo Normalizado": row["Nombre Completo Normalizado"],
            "url_cvlac": row["url_cvlac"]
        }
        tallies_row.update(product_tallies)
        tallies_data.append(tallies_row)

# Convert results to DataFrames
tallies_df = pd.DataFrame(tallies_data).fillna(0)  # Fill missing categories with 0
errors_df = pd.DataFrame(error_data)

# Output the results to KNIME
knio.output_tables[0] = knio.Table.from_pandas(tallies_df)
knio.output_tables[1] = knio.Table.from_pandas(errors_df)
