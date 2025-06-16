from plans.plans_detect import detect_plans, plan_file_map
from plans.plans_import_export import plan_import

def load_plans(zip_file: str, plan_export_name: str | None = None):
    if plan_export_name is not None:
        for plan_type, handler in plan_file_map.items():
            tables = plan_import(plan_type, plan_export_name)
            handler(tables)
    else:
        detect_plans(zip_file)