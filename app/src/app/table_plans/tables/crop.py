from img2table.document import Image as I2T_Image
from PIL import Image
from util.images import convert_pdf_to_images, pillow_image_to_bytes

MARGIN_WIDTH = 50
TITLE_BLOCK_WIDTH = 1500


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
        img_inner = img.crop((x1 + MARGIN_WIDTH, y1, x2 - TITLE_BLOCK_WIDTH, y2 - MARGIN_WIDTH))

        # now, get the actual table
        table_bbox = image_detect_table(img_inner)
        table = img_inner.crop(table_bbox)

        cropped_images.append(table)
    return cropped_images


def pdf_get_table_images(pdf_file: bytes) -> list[Image.Image]:
    return image_crop_to_table(convert_pdf_to_images(pdf_file))
