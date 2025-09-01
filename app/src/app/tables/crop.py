from PIL import Image
from pdf2image import convert_from_bytes
from img2table.document import Image as I2T_Image

from util import pillow_image_to_bytes

def pdf_convert_to_images(pdf_file: bytes) -> list[Image.Image]:
    return convert_from_bytes(pdf_file, dpi=300, grayscale=True, fmt="jpeg")

def image_detect_table(img: Image.Image) -> tuple[int, int, int, int]:
    i2t_img = I2T_Image(src=pillow_image_to_bytes(img))
    bbox = i2t_img.extract_tables()[0].bbox
    return bbox.x1, bbox.y1, bbox.x2, bbox.y2

def image_crop_to_table(images: list[Image.Image]) -> list[Image.Image]:
    cropped_images = []
    for img in images:
        # first, get the outer border (which img2table thinks is a table)
        x1, y1, x2, y2 = image_detect_table(img)

        # crop so that outer border isn't visible anymore
        # TODO: this is a very sketchy solution
        img_inner = img.crop((x1 + 50, y1, x2 - 1500, y2 - 50))

        # now, get the actual table
        table_bbox = image_detect_table(img_inner)
        table = img_inner.crop(table_bbox)
        
        cropped_images.append(table)
    return cropped_images

def pdf_get_table_images(pdf_file: bytes) -> list[Image.Image]:
    return image_crop_to_table(pdf_convert_to_images(pdf_file))