from io import BytesIO

import cv2
import numpy as np
from pdf2image import convert_from_bytes
from PIL import Image


def convert_pdf_to_images(pdf_file: bytes) -> list[Image.Image]:
    return convert_from_bytes(pdf_file, dpi=400, grayscale=True, fmt="png", use_cropbox=True)


def pillow_image_to_bytes(img: Image.Image) -> bytes:
    img_bytes = BytesIO()
    img.save(img_bytes, format="jpeg")
    return img_bytes.getvalue()


def load_img_from_path(path: str) -> cv2.typing.MatLike | None:
    if path.endswith(".pdf"):
        with open(path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
            page_image = pillow_image_to_bytes(convert_pdf_to_images(pdf_bytes)[0])
            page_np = np.frombuffer(page_image, dtype=np.uint8)
            return cv2.imdecode(page_np, cv2.IMREAD_GRAYSCALE)
    else:
        return cv2.imread(path, cv2.IMREAD_GRAYSCALE)
