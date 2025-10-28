import itertools
from io import BytesIO

from pdf2image import convert_from_bytes
from PIL import Image


def convert_pdf_to_images(pdf_file: bytes) -> list[Image.Image]:
    return convert_from_bytes(pdf_file, dpi=400, grayscale=True, fmt="png", use_cropbox=True)


def pillow_image_to_bytes(img: Image.Image) -> bytes:
    img_bytes = BytesIO()
    img.save(img_bytes, format="jpeg")
    return img_bytes.getvalue()


def flatten_iterable(it):
    return list(itertools.chain.from_iterable(it))
