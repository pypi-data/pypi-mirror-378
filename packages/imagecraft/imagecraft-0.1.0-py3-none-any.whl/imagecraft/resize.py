from PIL import Image, ImageEnhance

def resize(path, width=None, height=None, keep_aspect=True, sharpness=1.0):
    """
    Resize an image by width, height, or both.
    - keep_aspect=True will auto-scale the other dimension.
    - sharpness can be >1.0 (sharper) or <1.0 (softer).
    """
    img = Image.open(path)

    if keep_aspect:
        if width and not height:
            ratio = width / img.width
            height = int(img.height * ratio)
        elif height and not width:
            ratio = height / img.height
            width = int(img.width * ratio)
    else:
        if not width or not height:
            raise ValueError("Width and height must be set if keep_aspect=False")

    img = img.resize((width, height), Image.LANCZOS)

    if sharpness != 1.0:
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(sharpness)

    return img