from PIL import Image, ImageFilter, ImageOps
from io import BytesIO
from logging import getLogger

logger = getLogger(__name__)


def filter_photo(current_photo: bytes, current_filter: str) -> bytes:
    image = Image.open(BytesIO(current_photo))

    match current_filter:
        case "Negative":
            result = ImageOps.invert(image.convert("RGB"))
        case "Black & White":
            result = image.convert("L")
        case "Soft Blur":
            result = image.filter(ImageFilter.GaussianBlur(radius=2))
        case "Sharpen Details":
            result = image.filter(ImageFilter.SHARPEN)
        case "Sketch Outline":
            result = image.filter(ImageFilter.FIND_EDGES)
        case "Contour Drawing":
            result = image.filter(ImageFilter.CONTOUR)
        case "Emboss Effect":
            result = image.filter(ImageFilter.EMBOSS)
        case "Poster Style":
            result = ImageOps.posterize(image.convert("RGB"), bits=3)
        case "Photo Negative":
            result = ImageOps.solarize(image.convert("RGB"), threshold=128)
        case _:
            result = image
    byte_io = BytesIO()
    result.save(byte_io, format='jpeg')
    byte_io.seek(0)
    rvalue = byte_io.getvalue()
    logger.info("The photo was successfully modified")

    return rvalue

