from typing import List

import pandas as pd

def handle_az_plan(tables: List[pd.DataFrame]):
    pass

def handle_dweg_plan(tables: List[pd.DataFrame]):
    pass

def handle_flank_plan(tables: List[pd.DataFrame]):
    pass

def handle_gm_plan(tables: List[pd.DataFrame]):
    pass

def handle_gp_plan(tables: List[pd.DataFrame]):
    pass

def handle_rang_plan(tables: List[pd.DataFrame]):
    pass

def handle_sb_plan(tables: List[pd.DataFrame]):
    pass

def handle_sig1_plan(tables: List[pd.DataFrame]):
    print("Processing Signaltabelle 1...")
    for table in tables:
        for i in range(3, table.shape[1]):
            if not pd.isna(table.iat[0, i]):
                print(f"Main or distant signal {table.iat[0, i]}") 
            elif not pd.isna(table.iat[1, i]):
                print(f"Shunting signal {table.iat[1, i]}")
            elif not pd.isna(table.iat[2, i]):
                print(f"Other signal {table.iat[2, i]}")
            # else ignore column
            if not pd.isna(table.iat[20, i]):
                print(table.iat[20, i])
                print("Has Hp0")

def handle_sig2_plan(tables: List[pd.DataFrame]):
    pass

def handle_wei_plan(tables: List[pd.DataFrame]):
    pass

def handle_zug_plan(tables: List[pd.DataFrame]):
    pass

def handle_zwie_plan(tables: List[pd.DataFrame]):
    pass