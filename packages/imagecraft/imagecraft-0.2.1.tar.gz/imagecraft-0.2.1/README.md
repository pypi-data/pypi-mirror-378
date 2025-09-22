# ImageCraft 🖼️

[![PyPI version](https://img.shields.io/pypi/v/imagecraft)](https://pypi.org/project/imagecraft/)  
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

`ImageCraft` is a Python package for professional image processing and optimization.  
It provides **dynamic resizing, cropping, sharpening, and preset image templates** for logos, thumbnails, banners, posters, and more.  
Optimized for **web usage** with support for PNG, JPEG, and WEBP formats.

---

## Features

- **Dynamic image resizing** (width, height, square) with aspect ratio preservation
- **Center cropping** instead of padding for logos and banners
- **Sharpness and brightness adjustments**
- **Web optimization** with automatic alpha flattening for JPEG
- **Preset templates**: profile images, logos (square, horizontal, vertical), icons, banners, posters, thumbnails, gallery images, social covers
- Works with PNG (transparency preserved), JPEG, WEBP
- Easy integration for web projects, APIs, and automated workflows

---

## Installation

```bash
pip install imagecraft
```

## Quick Start

```python
from imagecraft.preset import ImagePresets
from PIL import Image

presets = ImagePresets(verbose=True)

logo_jpg = "example_logo.jpg"
logo_png = "example_logo.png"

# Square logo (center-cropped)
logo_square = presets.logo_square(logo_jpg, size=256)
logo_square.show()

# Horizontal logo
logo_horizontal = presets.logo_horizontal(logo_jpg, width=512, height_ratio=0.5)
logo_horizontal.show()

# Vertical logo
logo_vertical = presets.logo_vertical(logo_jpg, height=512, width_ratio=0.6)
logo_vertical.show()
```


## Core Classes & Functions

### ImageUtils
Low-level image utilities for resizing, cropping, adjusting sharpness/brightness, and web optimization.


| Function                                              | Description                              | Key Params                                     |
| ----------------------------------------------------- | ---------------------------------------- | ---------------------------------------------- |
| `load_image(path)`                                    | Load image from disk and convert to RGBA | `path:str`                                     |
| `resize_to_square(img, size)`                         | Resize & center-crop to square           | `img:Image`, `size:int`                        |
| `resize_to_width(img, width, keep_aspect=True)`       | Resize width, optional aspect ratio      | `img:Image`, `width:int`                       |
| `resize_to_height(img, height, keep_aspect=True)`     | Resize height, optional aspect ratio     | `img:Image`, `height:int`                      |
| `crop_center(img, target_size)`                       | Crop from center to target size          | `target_size:(w,h)`                            |
| `adjust_sharpness(img, factor)`                       | Sharpen/blur image                       | `factor:float`                                 |
| `adjust_brightness(img, factor)`                      | Brighten/darken image                    | `factor:float`                                 |
| `optimize_for_web(img, format, quality, max_size_kb)` | Compress & optimize for web              | `format:str`, `quality:int`, `max_size_kb:int` |


-----------

### ImagePresets
High-level presets for commonly used image types.

| Function                                             | Description                  | Default Size / Ratio  | Example Usage                            |
| ---------------------------------------------------- | ---------------------------- | --------------------- | ---------------------------------------- |
| `make_profile_image(path, size=256)`                 | Square profile/avatars       | 256x256               | `make_profile_image("avatar.png")`       |
| `logo_square(path, size=256, sharpness=2.0)`         | Square logo, center-cropped  | 256x256               | `logo_square("logo.jpg", 512)`           |
| `logo_horizontal(path, width=512, height_ratio=0.5)` | Horizontal logo, height auto | Width=512, height=50% | `logo_horizontal("logo.jpg", width=256)` |
| `logo_vertical(path, height=512, width_ratio=0.6)`   | Vertical logo, width auto    | Height=512, width=60% | `logo_vertical("logo.jpg", height=256)`  |
| `make_icon(path, size=64)`                           | Small square icon/favicons   | 64x64                 | `make_icon("icon.png")`                  |
| `make_thumbnail(path, width=400)`                    | Small preview image          | width=400             | `make_thumbnail("image.jpg")`            |
| `make_poster(path, size=(1080,1920))`                | Vertical poster/story format | 1080x1920             | `make_poster("poster.jpg")`              |
| `make_banner(path, size=(1920,600))`                 | Wide banner                  | 1920x600              | `make_banner("banner.jpg")`              |
| `make_cover(path, size=(1200,628))`                  | Social media cover           | 1200x628              | `make_cover("cover.jpg")`                |
| `make_gallery_image(path, size=800)`                 | Square gallery images        | 800x800               | `make_gallery_image("photo.png")`        |



### ImageDynamic

Dynamic resizing for custom sizes with optional adjustments.

```python 
from imagecraft.dynamic import ImageDynamic

dynamic = ImageDynamic(verbose=True)

# Square crop
img1 = dynamic.process("logo.jpg", 256)

# Custom rectangle crop
img2 = dynamic.process("poster.jpg", 800, 1200, sharpness=2.0, brightness=1.2, quality=90)

img1.show()
img2.show()
```


### Notes:

- `*args` in `process`: 1 value → square, 2 values → width & height
- `kwargs`: `sharpness`, `brightness`, `quality`, `max_size_kb`
- Returns optimized web-ready image


---------

## Support & Donations ☕️

This package was born out of necessity while building a **multi-project SaaS platform**. I couldn’t find a ready-to-use, well-maintained package for managing multiple projects, so I created this as a clean, reusable boilerplate. Cloning other solutions proved hard, often outdated or not flexible enough, which is why `ImageCraft` exists.  

The license is **MIT**, so it’s fully usable and editable. If you find any bugs or have suggestions, please feel free to **open an issue** or **contribute on [GitHub](https://github.com/xgino/imagecraft)**. Your feedback is highly appreciated!  

If you find `ImageCraft` useful, consider supporting me with a coffee:  
[![Ko-fi](https://img.shields.io/badge/Ko--fi-FF5E5B?logo=ko-fi&logoColor=white)](https://ko-fi.com/xgino)  
Every sip helps fuel a new line of code and keeps this project alive. Thank you for your support!  

---

## 📦 ImageCraft — Examples & Use Cases  

This section gives you a **clear overview** of how to use `imagecraft` with practical examples and images.  
Each example shows **code on the left** and the **resulting image on the right**, so you can quickly understand what each function does.  

---

## 🔧 Utilities  

### 🖼️ `utils.resize_to_square`  
Resize any image into a perfect square.  

```python
from imagecraft.utils import ImageUtils

sq_img = ImageUtils.resize_to_square(img, 256)

```
![resize_to_square](readme_images/resize_to_square.png)
---

## ⚡ Dynamic Processing

### ⚙️ `Dynamic.resize_to_square`
Resize with on-the-fly adjustments for sharpness, brightness, quality, and file size.

```python
from imagecraft.dynamic import ImageDynamic

dyn_img = ImageDynamic.process(
    jpg_path,
    256,
    sharpness=1.2,
    brightness=1.1,
    quality=70,
    max_size_kb=100
)
```
![dynamic_to_square](readme_images/dynamic_processed.png)
---

### ⚙️ `Dynamic.resize_to_rectangle`
```python
from imagecraft.dynamic import ImageDynamic

dyn_img = ImageDynamic.process(
    jpg_path, 
    256, 
    sharpness=1.2, 
    brightness=1.1, 
    quality=70, 
    max_size_kb=100
)
```
![dynamic_to_rectangle](readme_images/dynamic_processed_rectangle.png)
---

### 🎨 Presets
ImageCraft includes ready-made presets for common use cases:

#### 👤 `Profile Image`
```python
from imagecraft.presets import ImagePresets

profile = ImageDynamic.make_profile_image(
    jpg_path, 
    size=128
)
```

![resize_to_square](readme_images/make_profile_image.png)
---




### 🟦 `Logo Variants`

#### Square Logo
```python
from imagecraft.presets import ImagePresets

logo_square = ImageDynamic.logo_square(
    logo_jpg, 
    size=256, 
    sharpness=2.0
)
```

![logo_square](readme_images/logo_square.png)
---


#### Square Rectangle
```python
from imagecraft.presets import ImagePresets

logo_horizontal = ImageDynamic.logo_horizontal(
    logo_jpg, 
    width=256, 
    sharpness=2.0
)
```

![logo_horizontal](readme_images/logo_horizontal.png)
---


#### Square Vertical
```python
from imagecraft.presets import ImagePresets

logo_vertical = ImagePresets.logo_vertical(
    logo_jpg, 
    height=256, 
    sharpness=2.0
)
```

![logo_horizontal](readme_images/logo_vertical.png)
---



### 🔲 `Icon`
```python
from imagecraft.presets import ImagePresets

icon = ImagePresets.make_icon(
    jpg_path, 
    size=64
    )
```

![logo_horizontal](readme_images/icon.png)
---


### 🖼️ `Thumbnail`
```python
from imagecraft.presets import ImagePresets

thumb = ImageDynamic.make_thumbnail(
    jpg_path, 
    width=300
)
```

![logo_horizontal](readme_images/thumbnail.png)
---




### 🎬 `Poster`
```python
from imagecraft.presets import ImagePresets

poster = ImagePresets.make_poster(
    jpg_path
)
```

![logo_horizontal](readme_images/poster.png)
---



### 📢 `Banner`
```python
from imagecraft.presets import ImagePresets

banner = ImagePresets.make_banner(
    jpg_path
)
```

![logo_horizontal](readme_images/banner.png)
---



### 📕 `Cover`
```python
from imagecraft.presets import ImagePresets

banner = ImagePresets.make_cover(
    jpg_path
)
```

![logo_horizontal](readme_images/cover.png)
---



### 🖼️ `Gallery Image`
```python
from imagecraft.presets import ImagePresets

gallery = ImagePresets.make_gallery_image(
    jpg_path, 
    size=800
)
```

![logo_horizontal](readme_images/gallery.png)
---



## Recommended Usage / Tips

- For **logos**, always keep original aspect ratio and crop from center.  
- Use **PNG** for transparency, JPEG/WebP for web-optimized images.  
- Default **sharpness**: 2.0 for logos, 1.2 for profile images.  
- Height/width ratios for horizontal/vertical logos: **0.5** (horizontal), **0.6** (vertical).  
- Small icons: **64x64** standard.  

---------

### License

**MIT License** – free to use, modify, and integrate into your projects.

---------

**Author:** [Your Name](https://github.com/xgino)  
**GitHub:** [https://github.com/xgino/imagecraft](https://github.com/xgino/imagecraft)  
**PyPI:** [https://pypi.org/project/imagecraft](https://pypi.org/project/imagecraft)

