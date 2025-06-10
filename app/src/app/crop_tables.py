from typing import List
from io import BytesIO
from PIL import Image
from pdf2image import convert_from_path
from img2table.document import Image as I2T_Image

def convert_to_images(filename: str) -> List[Image.Image]:
    return convert_from_path(filename, dpi=300, grayscale=True, fmt='jpeg')

def detect_table(img: Image.Image) -> tuple[int, int, int, int]:
    img_bytes = BytesIO()
    img.save(img_bytes, format='jpeg')
    i2t_img = I2T_Image(src=img_bytes.getvalue())
    bbox = i2t_img.extract_tables()[0].bbox
    return bbox.x1, bbox.y1, bbox.x2, bbox.y2

def crop_to_table(images: List[Image.Image]) -> List[Image.Image]:
    cropped_images = []
    for img in images:
        # first, get the outer border (which img2table thinks is a table)
        x1, y1, x2, y2 = detect_table(img)

        # crop so that outer border isn't visible anymore
        # TODO: this is a very sketchy solution
        img_inner = img.crop((x1 + 50, y1, x2 - 1500, y2 - 50))

        # now, get the actual table
        table_bbox = detect_table(img_inner)
        table = img_inner.crop(table_bbox)
        
        cropped_images.append(table)
    return cropped_images

if __name__ == '__main__':
    crop_to_table(convert_to_images('../../Planungen_PT1/2019-10-30_PT1_ÄM02/P-Hausen_Sig1_ÄM02.pdf'))