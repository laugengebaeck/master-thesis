from table_plans.csv import plan_import_csv
from table_plans.detect_files import detect_plans, plan_file_map
from table_plans.pdf_read import (
    ImageOptimizedPlanReader,
    ImageUnoptimizedPlanReader,
    PdfTextPlanReader,
    PlanReaderType,
)


def table_main(
    zip_path: str,
    plan_reader_type: PlanReaderType = PlanReaderType.IMAGE_OPTIMIZED,
    import_from: str | None = None,
):
    if import_from is not None:
        for plan_type, handler in plan_file_map.items():
            tables = plan_import_csv(plan_type, import_from)
            handler(tables)
    else:
        match plan_reader_type:
            case PlanReaderType.PDF_TEXT:
                detect_plans(zip_path, PdfTextPlanReader())
            case PlanReaderType.IMAGE_OPTIMIZED:
                detect_plans(zip_path, ImageOptimizedPlanReader(min_confidence=30))
            case PlanReaderType.IMAGE_UNOPTIMIZED:
                detect_plans(zip_path, ImageUnoptimizedPlanReader())
