import base64
from pathlib import Path

from PIL import Image
import io


def encode_image_to_b64(image: bytes | str | Path) -> str:
    if isinstance(image, Path):
        with open(image, "rb") as file:
            content = file.read()
        base64_image = base64.b64encode(content).decode('utf-8')
    elif isinstance(image, bytes):
        base64_image = base64.b64encode(image).decode('utf-8')
    elif isinstance(image, str):
        base64_image = image
    else:
        raise TypeError('image is not of type bytes, str, Path')

    return f"data:image/jpeg;base64,{base64_image}"


def compress_b64_image(b64_image: str, aspect_ratio: float = None, max_dimension: float = None) -> str:
    image_data = base64.b64decode(b64_image)
    image = Image.open(io.BytesIO(image_data))
    # file_path = 'image.png'
    # image.save(file_path)
    if aspect_ratio:
        new_size = (int(image.width * aspect_ratio), int(image.height * aspect_ratio))
    elif max_dimension:
        if image.width > image.height:
            new_size = (max_dimension, int(image.height * max_dimension / image.width))
        else:
            new_size = (int(image.width * max_dimension / image.height), max_dimension)
    else:
        raise TypeError('Either aspect_ratio or max_dimension should be specified')

    resized_image = image.resize(new_size, Image.LANCZOS)
    # file_path = 'image2.png'
    # resized_image.save(file_path)
    buffered = io.BytesIO()
    resized_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()
