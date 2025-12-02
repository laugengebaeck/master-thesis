import Levenshtein
import pandas as pd

row_mapping: dict[str, int] = {}


def get_row_number_for_attribute(df: pd.DataFrame, attribute_name: str, table_id: int):
    attribute_key = f"{table_id}=== {attribute_name}"
    if attribute_key in row_mapping:
        return row_mapping[attribute_key]

    min_edit_dist = 100000  # represents infinity, as no row name will ever be that long
    min_row = 0
    for row in range(0, df.shape[0]):
        title_cell = df.iat[row, 2]
        if not pd.isna(title_cell):
            edit_dist = Levenshtein.distance(attribute_name, str(title_cell))
            if edit_dist < min_edit_dist:
                min_edit_dist = edit_dist
                min_row = row

    print(f"Using line {df.iat[min_row, 2]} for original attribute {attribute_name}")
    row_mapping[attribute_key] = min_row
    return min_row
