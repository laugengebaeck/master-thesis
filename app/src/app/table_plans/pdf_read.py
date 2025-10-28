from abc import ABC, abstractmethod
from enum import Enum

import pandas as pd
from img2table.document import PDF
from table_plans.tables.crop import pdf_get_table_images
from table_plans.tables.ocr import tables_perform_ocr
from util import convert_pdf_to_images


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
