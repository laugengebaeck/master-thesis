from abc import ABC, abstractmethod
from enum import Enum
from zipfile import ZipFile

import pandas as pd
from img2table.document import PDF
from table_plans.csv_import_export import plan_export_csv
from table_plans.tables.crop import pdf_get_table_images
from table_plans.tables.ocr import tables_perform_ocr
from util.images import convert_pdf_to_images


class PlanReaderType(Enum):
    PDF_TEXT = 1
    IMAGE_UNOPTIMIZED = 2
    IMAGE_OPTIMIZED = 3


class PlanReader(ABC):
    @abstractmethod
    def read_tables(self, pdf_file: bytes) -> list[pd.DataFrame]:
        pass


class PdfTextPlanReader(PlanReader):
    def read_tables(self, pdf_file: bytes) -> list[pd.DataFrame]:
        doc = PDF(pdf_file, pdf_text_extraction=True)
        extracted_tables = doc.extract_tables()
        # TODO use second table instead to not get the outer border "table"?
        return [page_tables[0].df for page_tables in extracted_tables.values()]


class ImageUnoptimizedPlanReader(PlanReader):
    def read_tables(self, pdf_file: bytes) -> list[pd.DataFrame]:
        table_images = convert_pdf_to_images(pdf_file)
        # ignore min_confidence to get all text the OCR can detect
        return tables_perform_ocr(table_images, min_confidence=0)


class ImageOptimizedPlanReader(PlanReader):
    def __init__(self, min_confidence: int) -> None:
        self.min_confidence = min_confidence

    def read_tables(self, pdf_file: bytes) -> list[pd.DataFrame]:
        table_images = pdf_get_table_images(pdf_file)
        return tables_perform_ocr(table_images, min_confidence=self.min_confidence)


def plan_reader_for_type(type: PlanReaderType) -> PlanReader:
    match type:
        case PlanReaderType.PDF_TEXT:
            return PdfTextPlanReader()
        case PlanReaderType.IMAGE_OPTIMIZED:
            return ImageOptimizedPlanReader(min_confidence=30)
        case PlanReaderType.IMAGE_UNOPTIMIZED:
            return ImageUnoptimizedPlanReader()


def read_tables_from_document(
    plan_type: str, zip: ZipFile, plan_reader: PlanReader
) -> list[pd.DataFrame]:
    plan_files = list(filter(lambda f: f.endswith(".pdf") and plan_type in f, zip.namelist()))
    if len(plan_files) > 1:
        raise ValueError(f"ZIP file contains more than one plan of type {plan_type}.")
    elif len(plan_files) == 1:
        pdf_file = zip.read(plan_files[0])
        tables = plan_reader.read_tables(pdf_file)
        plan_export_csv(tables, plan_type, plan_files[0])
        return tables
    else:
        return []
