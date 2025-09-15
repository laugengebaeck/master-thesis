import os

import pandas as pd


def plan_export(tables: list[pd.DataFrame], plan_type: str, original_path: str):
    plan_name = original_path.split("/")[-1].split("_")[0]
    for idx, table in enumerate(tables):
        export_name = f"export/{plan_name}_{plan_type}_page{idx + 1}.csv"
        table.to_csv(export_name)


def plan_import(plan_type: str, plan_export_name: str) -> list[pd.DataFrame]:
    csv_files = os.listdir("export")
    # sort by page number
    csv_files.sort(key=lambda x: int(x.removesuffix(".csv").split("_")[-1]))
    plans = []
    for file in csv_files:
        plan_name, file_type, _ = file.split("_")
        if file_type == plan_type and plan_name == plan_export_name:
            plans.append(pd.read_csv(f"export/{file}"))
    return plans
