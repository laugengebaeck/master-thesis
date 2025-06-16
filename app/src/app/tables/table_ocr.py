from typing import List
from pandas import DataFrame
from PIL import Image
from img2table.document import Image as I2T_Image
from img2table.ocr import DocTR

from util import pillow_image_to_bytes

def table_perform_ocr(table_image: Image.Image, min_confidence: int) -> DataFrame:
    doc = I2T_Image(pillow_image_to_bytes(table_image))
    ocr = DocTR(detect_language=False, kw={
            "det_arch": "db_resnet50", 
            "reco_arch": "crnn_vgg16_bn", 
            "pretrained": True})
    extracted_tables = doc.extract_tables(ocr=ocr, min_confidence=min_confidence)
    if len(extracted_tables) > 1:
        raise ValueError("Image contains more than one table.")
    return extracted_tables[0].df

def tables_perform_ocr(table_images: List[Image.Image], min_confidence: int) -> List[DataFrame]:
    return [table_perform_ocr(image, min_confidence) for image in table_images]