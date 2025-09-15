from plans.detect import detect_plans, plan_file_map
from plans.import_export import plan_import
from plans.read import (
    ImageOptimizedPlanReader,
    ImageUnoptimizedPlanReader,
    PdfTextPlanReader,
    PlanReaderType,
)


def load_plans(
    zip_file: str, plan_reader_type: PlanReaderType, plan_export_name: str | None = None
):
    if plan_export_name is not None:
        for plan_type, handler in plan_file_map.items():
            tables = plan_import(plan_type, plan_export_name)
            handler(tables)
    else:
        match plan_reader_type:
            case PlanReaderType.PDF_TEXT:
                detect_plans(zip_file, PdfTextPlanReader())
            case PlanReaderType.IMAGE_OPTIMIZED:
                detect_plans(zip_file, ImageOptimizedPlanReader(min_confidence=30))
            case PlanReaderType.IMAGE_UNOPTIMIZED:
                detect_plans(zip_file, ImageUnoptimizedPlanReader())
