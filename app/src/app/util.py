import itertools
from enum import Enum
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


class ValidationRuleResult:
    def __init__(self, success: bool, error_message: str = "") -> None:
        self.success = success
        self.error_message = error_message


class ValidationRuleSeverity(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3

    def get_message(self) -> str:
        if self == ValidationRuleSeverity.INFO:
            return "ℹ️ Information:"
        elif self == ValidationRuleSeverity.WARNING:
            return "⚠️  Warning:"
        elif self == ValidationRuleSeverity.ERROR:
            return "❌ Error:"
        else:
            return ""
