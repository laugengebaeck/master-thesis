from zipfile import ZipFile

from table_plans.csv_import_export import plan_import_csv
from table_plans.detect_plans import detect_and_handle_plans
from table_plans.pdf_read import PlanReaderType, plan_reader_for_type, read_tables_from_document


def table_main(
    zip_path: str,
    plan_reader_type: PlanReaderType,
    import_from: str | None = None,
):
    if import_from is not None:
        detect_and_handle_plans(lambda plan_type: plan_import_csv(plan_type, import_from))
    else:
        with ZipFile(zip_path, "r") as zip:
            detect_and_handle_plans(
                lambda plan_type: read_tables_from_document(
                    plan_type, zip, plan_reader_for_type(plan_reader_type)
                )
            )
