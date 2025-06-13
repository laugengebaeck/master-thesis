import os
from zipfile import ZipFile

import plans_handlers

plan_file_map = {
    "Az": plans_handlers.handle_az_plan,
    "D-Weg": plans_handlers.handle_dweg_plan,
    "Flank": plans_handlers.handle_flank_plan,
    "GM": plans_handlers.handle_gm_plan,
    "Gp": plans_handlers.handle_gp_plan,
    "Rang": plans_handlers.handle_rang_plan,
    "Sb": plans_handlers.handle_sb_plan,
    "Sig1": plans_handlers.handle_sig1_plan,
    "Sig2": plans_handlers.handle_sig2_plan,
    "Wei": plans_handlers.handle_wei_plan,
    "Zug": plans_handlers.handle_zug_plan,
    "Zwie": plans_handlers.handle_zwie_plan,

}

def detect_plans(zip_file: str):
    with ZipFile(zip_file, "r") as zip:
        files_in_zip = list(filter(lambda f: f.endswith('.pdf'), zip.namelist()))
        print([os.path.basename(file) for file in files_in_zip if file.endswith('.pdf')]) 

detect_plans('../../Planungen_PT1/2019-10-30_PT1_ÄM02.zip')