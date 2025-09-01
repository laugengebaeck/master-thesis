from zipfile import ZipFile

import plans.handlers as handlers
from plans.import_export import plan_export
from plans.read import PlanReader

plan_file_map = {
    #"Az": handlers.handle_az_plan,
    #"D-Weg": handlers.handle_dweg_plan,
    #"Flank": handlers.handle_flank_plan,
    #"GM": handlers.handle_gm_plan,
    #"Gp": handlers.handle_gp_plan,
    #"Rang": handlers.handle_rang_plan,
    #"Sb": handlers.handle_sb_plan,
    "Sig1": handlers.handle_sig1_plan,
    #"Sig2": handlers.handle_sig2_plan,
    #"Wei": handlers.handle_wei_plan,
    #"Zug": handlers.handle_zug_plan,
    #"Zwie": handlers.handle_zwie_plan,

}

def detect_plans(zip_file: str, plan_reader: PlanReader):
    with ZipFile(zip_file, "r") as zip:
        files_in_zip = list(filter(lambda f: f.endswith(".pdf"), zip.namelist()))
        for plan_type, handler in plan_file_map.items():
            plan_files = list(filter(lambda f: plan_type in f, files_in_zip))
            if len(plan_files) > 1:
                raise ValueError(f"ZIP file contains more than one plan of type {plan_type}.")
            if len(plan_files) != 0:
                pdf_file = zip.read(plan_files[0])
                tables = plan_reader.read_tables(pdf_file)
                plan_export(tables, plan_type, plan_files[0])
                handler(tables)