from io import BytesIO
from PIL import Image

def pillow_image_to_bytes(img: Image.Image) -> bytes:
    img_bytes = BytesIO()
    img.save(img_bytes, format='jpeg')
    return img_bytes.getvalue()