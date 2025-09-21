from PIL import Image

def crop(path, size=(1200, 900), position="center"):
    """
    Crop an image to given size.
    position: "left", "center", "right" (landscape)
              "top", "middle", "bottom" (portrait)
    """
    img = Image.open(path)
    target_w, target_h = size

    # Scale to fit height first
    ratio = target_h / img.height
    new_w = int(img.width * ratio)
    img = img.resize((new_w, target_h), Image.LANCZOS)

    # Decide crop x offset
    if position == "left" or position == "top":
        x0 = 0
    elif position == "right" or position == "bottom":
        x0 = new_w - target_w
    else:  # center / middle
        x0 = (new_w - target_w) // 2

    img = img.crop((x0, 0, x0 + target_w, target_h))
    return img