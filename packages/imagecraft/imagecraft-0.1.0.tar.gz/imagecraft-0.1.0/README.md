# image-magic

📸 A simple, developer-friendly Python package for resizing, cropping, and converting images.  
Built on top of Pillow, but easier.

## Features
- Resize by width, height, or both (auto aspect ratio)
- Crop images (left, center, right, top, bottom)
- Convert formats (PNG, JPG, etc.)
- Set resolution and sharpness
- Safe checks for valid image files

## Installation
```bash
pip install imagecraft
```

## Usage

```bash
from image_magic import resize, crop

# Resize width=800px, auto height
img = resize("upload.png", width=800)

# Crop to mobile size 1200x900, center
img = crop("landscape.jpg", size=(1200, 900), position="center")

# Save to JPG
img.save("output.jpg", format="JPEG")
```



- **Good function signatures** → make it easy to understand:  

```bash
resize(path, width=None, height=None, keep_aspect=True, sharpness=1.0)
crop(path, size=(1200, 900), position="center")
convert(path, format="JPEG")
```

