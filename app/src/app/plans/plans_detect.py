from zipfile import ZipFile

import plans.plans_handlers as plans_handlers
from plans.plans_import_export import plan_export
from tables.table_crop import pdf_get_table_images
from tables.table_ocr import tables_perform_ocr

plan_file_map = {
    #"Az": plans_handlers.handle_az_plan,
    #"D-Weg": plans_handlers.handle_dweg_plan,
    #"Flank": plans_handlers.handle_flank_plan,
    #"GM": plans_handlers.handle_gm_plan,
    #"Gp": plans_handlers.handle_gp_plan,
    #"Rang": plans_handlers.handle_rang_plan,
    #"Sb": plans_handlers.handle_sb_plan,
    "Sig1": plans_handlers.handle_sig1_plan,
    #"Sig2": plans_handlers.handle_sig2_plan,
    #"Wei": plans_handlers.handle_wei_plan,
    #"Zug": plans_handlers.handle_zug_plan,
    #"Zwie": plans_handlers.handle_zwie_plan,

}

def plan_read_to_dataframes(pdf_file: bytes):
    table_images = pdf_get_table_images(pdf_file)
    table_dfs = tables_perform_ocr(table_images, min_confidence=30)
    return table_dfs

def detect_plans(zip_file: str):
    with ZipFile(zip_file, "r") as zip:
        files_in_zip = list(filter(lambda f: f.endswith(".pdf"), zip.namelist()))
        for plan_type, handler in plan_file_map.items():
            plan_files = list(filter(lambda f: plan_type in f, files_in_zip))
            if len(plan_files) > 1:
                raise ValueError(f"ZIP file contains more than one plan of type {plan_type}.")
            if len(plan_files) != 0:
                pdf_file = zip.read(plan_files[0])
                tables = plan_read_to_dataframes(pdf_file)
                plan_export(tables, plan_type, plan_files[0])
                handler(tables)