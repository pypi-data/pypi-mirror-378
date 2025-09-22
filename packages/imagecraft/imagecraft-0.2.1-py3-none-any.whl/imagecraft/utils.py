from PIL import Image, ImageEnhance
from io import BytesIO
import os

class ImageUtils:
    SUPPORTED_FORMATS = ("JPEG", "PNG", "WEBP", "TIFF", "BMP", "GIF", "ICO")

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def _log(self, message: str):
        if self.verbose:
            print(f"[ImageUtils] {message}")

    @staticmethod
    def validate_image(self, path: str):
        """
        Check if the given file is a valid image. 
        Opens the file with PIL and verifies integrity. 
        Returns True if valid, False otherwise.
        """
        try:
            with Image.open(path) as img:
                img.verify()
            self._log(f"Validated image: {path}")
            return True
        except Exception as e:
            self._log(f"Validation failed: {e}")
            return False

    @staticmethod
    def load_image(self, path: str):
        """
        Load an image from disk and convert it to RGBA mode. 
        Returns a PIL Image object, or None if loading fails.
        """
        try:
            img = Image.open(path).convert("RGBA")
            self._log(f"Loaded image: {path}, size={img.size}, mode={img.mode}")
            return img
        except Exception as e:
            self._log(f"Load failed: {e}")
            return None

    @staticmethod
    def save_image(self, img, path: str, format="JPEG", quality=85):
        """
        Save a PIL Image to disk with the given format and quality. 
        Automatically optimizes file size. Logs on success or failure.
        """
        try:
            img.save(path, format=format.upper(), quality=quality, optimize=True)
            self._log(f"Saved {format} at {path} (quality={quality})")
        except Exception as e:
            self._log(f"Save failed: {e}")

    @staticmethod
    def to_bytes(self, img, format="JPEG", quality=85, verbose=False):
        """
        Convert a PIL Image into an in-memory BytesIO buffer. 
        Useful for APIs, uploads, or sending without writing to disk. 
        Automatically handles RGBA → RGB conversion for JPEGs.
        """
        try:
            buffer = BytesIO()
            save_img = img
            if format.upper() == "JPEG" and img.mode == "RGBA":
                save_img = img.convert("RGB")  # JPEG can't handle alpha
            save_img.save(buffer, format=format.upper(), quality=quality, optimize=True)
            buffer.seek(0)
            if verbose:
                print(f"[to_bytes] Exported image as {format}, size={buffer.getbuffer().nbytes/1024:.1f} KB")
            return buffer
        except Exception as e:
            if verbose:
                print(f"[to_bytes] Error: {e}")
            return None

    @staticmethod
    def resize_to_square(self, img, size: int):
        """
        Resize and center-crop an image to a perfect square. 
        Maintains aspect ratio and trims edges (no borders added).
        """
        try:
            img = img.copy()
            w, h = img.size

            # Step 1: resize so the smaller side matches target
            if w > h:
                new_h = size
                new_w = int(w * (size / h))
            else:
                new_w = size
                new_h = int(h * (size / w))

            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # Step 2: center crop to square
            left = (new_w - size) // 2
            top = (new_h - size) // 2
            right = left + size
            bottom = top + size
            img = img.crop((left, top, right, bottom))

            self._log(f"Resized & center-cropped to {size}x{size}")
            return img
        except Exception as e:
            self._log(f"Resize square failed: {e}")
            return img

    @staticmethod
    def resize_to_width(self, img, width: int, keep_aspect=True):
        """
        Resize an image to a target width. 
        If keep_aspect=True, scales height proportionally. 
        If False, only width changes (may distort).
        """
        try:
            w, h = img.size
            if keep_aspect:
                ratio = width / w
                new_h = int(h * ratio)
                img = img.resize((width, new_h))
            else:
                img = img.resize((width, h))
            self._log(f"Resized width={width}, keep_aspect={keep_aspect}")
            return img
        except Exception as e:
            self._log(f"Resize width failed: {e}")
            return img

    @staticmethod
    def resize_to_height(self, img, height: int, keep_aspect=True):
        """
        Resize an image to a target height. 
        If keep_aspect=True, scales width proportionally. 
        If False, only height changes (may distort).
        """
        try:
            w, h = img.size
            if keep_aspect:
                ratio = height / h
                new_w = int(w * ratio)
                img = img.resize((new_w, height))
            else:
                img = img.resize((w, height))
            self._log(f"Resized height={height}, keep_aspect={keep_aspect}")
            return img
        except Exception as e:
            self._log(f"Resize height failed: {e}")
            return img

    @staticmethod
    def crop_center(self, img, target_size: tuple):
        """
        Crop the image to a given (width, height) from the center. 
        Useful for posters, banners, covers where exact size is required.
        """
        try:
            img = img.copy()
            w, h = img.size
            tw, th = target_size
            left = (w - tw) // 2
            top = (h - th) // 2
            img = img.crop((left, top, left + tw, top + th))
            self._log(f"Cropped center to {target_size}")
            return img
        except Exception as e:
            self._log(f"Crop center failed: {e}")
            return img

    @staticmethod
    def adjust_sharpness(self, img, factor=1.0):
        """
        Increase or decrease image sharpness. 
        factor > 1.0 makes it sharper, factor < 1.0 makes it blurrier.
        """
        try:
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(factor)
            self._log(f"Adjusted sharpness factor={factor}")
            return img
        except Exception as e:
            self._log(f"Sharpness failed: {e}")
            return img

    @staticmethod
    def adjust_brightness(self, img, factor=1.0):
        """
        Increase or decrease image brightness. 
        factor > 1.0 makes it brighter, factor < 1.0 makes it darker.
        """
        try:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(factor)
            self._log(f"Adjusted brightness factor={factor}")
            return img
        except Exception as e:
            self._log(f"Brightness failed: {e}")
            return img

    @staticmethod
    def optimize_for_web(self, img, format="JPEG", quality=95, max_size_kb=None, bg_color=(255,255,255)):
        """
        Save and compress an image optimized for web usage.
        - If format=JPEG and image has alpha, flatten with bg_color (default white)
        - Supports PNG, JPEG, WEBP
        - Reduces file size while maintaining quality
        """
        try:
            buffer = BytesIO()
            save_img = img
            if img.mode == "RGBA":
                if format.upper() == "JPEG":
                    # Flatten transparency onto white (or given bg_color)
                    background = Image.new("RGB", img.size, bg_color)
                    background.paste(img, mask=img.split()[3])  # alpha channel
                    save_img = background
                else:
                    save_img = img  # keep RGBA for PNG/WebP

            save_img.save(buffer, format=format.upper(), quality=quality, optimize=True)
            size_kb = len(buffer.getvalue()) / 1024

            if max_size_kb and size_kb > max_size_kb:
                quality = max(10, int(quality * (max_size_kb / size_kb)))
                buffer = BytesIO()
                save_img.save(buffer, format=format.upper(), quality=quality, optimize=True)

            self._log(f"Optimized web format={format}, quality={quality}, size={int(size_kb)}KB")
            buffer.seek(0)
            return Image.open(buffer)
        except Exception as e:
            self._log(f"Web optimization failed: {e}")
            return img