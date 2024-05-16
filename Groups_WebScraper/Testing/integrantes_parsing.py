import knime.scripting.io as knio
from bs4 import BeautifulSoup



integrantes_df = knio.input_tables[0].to_pandas()
integrantes_df.loc


# This example script simply outputs the node's input table.
knio.output_tables[0] = knio.input_tables[0]



