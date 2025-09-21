from PIL import Image
import os

def convert(path, output_format="PNG", save_path=None):
    """
    Convert an image to another format (PNG, JPEG, etc.)
    """
    img = Image.open(path).convert("RGB")  # force RGB
    if save_path is None:
        base, _ = os.path.splitext(path)
        save_path = f"{base}.{output_format.lower()}"
    img.save(save_path, format=output_format.upper())
    return save_path