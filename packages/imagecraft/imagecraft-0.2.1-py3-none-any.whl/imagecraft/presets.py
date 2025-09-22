from PIL import Image, ImageEnhance
from .utils import ImageUtils

class ImagePresets:
    def __init__(self, verbose: bool = False):
        self.utils = ImageUtils(verbose=verbose)
        self.verbose = verbose

    @staticmethod
    def make_profile_image(self, path, size=256):
        """
        Preset: Generate a square, sharp profile image for avatars. 
        Resizes, sharpens slightly, and optimizes for web.
        """
        img = self.utils.load_image(path)
        if not img:
            return None
        img = self.utils.resize_to_square(img, size)
        img = self.utils.adjust_sharpness(img, 1.2)
        return self.utils.optimize_for_web(img)
    
    # --- SQUARE LOGO ---
    @staticmethod
    def logo_square(self, path, size=256, sharpness=2.0, format="JPEG"):
        """
        Square logo: logo-only or logo below text.
        Crops from center instead of padding, keeps aspect ratio.
        """
        img = self.utils.load_image(path)
        if not img:
            return None

        # Resize and crop center to square
        img = self.utils.resize_to_square(img, size)
        img = self.utils.adjust_sharpness(img, sharpness)

        return self.utils.optimize_for_web(img, format=format, quality=95, bg_color=(255,255,255))


    # --- HORIZONTAL LOGO ---
    @staticmethod
    def logo_horizontal(self, path, width=512, sharpness=2.0, format="JPEG", height_ratio=0.5):
        """
        Horizontal logo: logo + text (text below optional).
        Height auto-scaled by height_ratio, cropped if necessary.
        """
        img = self.utils.load_image(path)
        if not img:
            return None

        # Compute target height
        target_height = int(width * height_ratio)

        # Resize by width keeping aspect ratio
        img = self.utils.resize_to_width(img, width)
        img = self.utils.adjust_sharpness(img, sharpness)

        # Crop center to target_height if taller
        w, h = img.size
        if h > target_height:
            img = self.utils.crop_center(img, (w, target_height))

        return self.utils.optimize_for_web(img, format=format, quality=95, bg_color=(255,255,255))


    # --- VERTICAL LOGO ---
    @staticmethod
    def logo_vertical(self, path, height=512, sharpness=2.0, format="JPEG", width_ratio=0.6):
        """
        Vertical logo: logo + text below.
        Width auto-scaled by width_ratio, cropped from center if needed.
        """
        img = self.utils.load_image(path)
        if not img:
            return None

        # Compute target width
        target_width = int(height * width_ratio)

        # Resize by height keeping aspect ratio
        img = self.utils.resize_to_height(img, height)
        img = self.utils.adjust_sharpness(img, sharpness)

        # Crop center if wider
        w, h = img.size
        if w > target_width:
            img = self.utils.crop_center(img, (target_width, h))

        return self.utils.optimize_for_web(img, format=format, quality=95, bg_color=(255,255,255))
    
    @staticmethod
    def make_icon(self, path, size=64, sharpness=5.0):
        """
        Preset: Generate a small square icon (e.g., favicon). 
        Resizes and optimizes for web.
        """
        img = self.utils.load_image(path)
        if not img:
            return None
        img = self.utils.resize_to_square(img, size)
        img = self.utils.adjust_sharpness(img, sharpness)
        return self.utils.optimize_for_web(img)

    @staticmethod
    def make_thumbnail(self, path, width=400):
        """
        Preset: Generate a small thumbnail for previews. 
        Resizes to given width, keeps aspect ratio, optimizes for web.
        """
        img = self.utils.load_image(path)
        if not img:
            return None
        img = self.utils.resize_to_width(img, width)
        return self.utils.optimize_for_web(img)

    @staticmethod
    def make_poster(self, path, size=(1080, 1920)):
        """
        Preset: Generate a vertical poster (e.g., story format). 
        Resizes by height, then center-crops to target aspect ratio.
        """
        img = self.utils.load_image(path)
        if not img:
            return None
        img = self.utils.resize_to_height(img, size[1])
        img = self.utils.crop_center(img, size)
        return self.utils.optimize_for_web(img)

    @staticmethod
    def make_banner(self, path, size=(1920, 600)):
        """
        Preset: Generate a wide banner (landscape style). 
        Resizes by width, then crops center to final size.
        """
        img = self.utils.load_image(path)
        if not img:
            return None
        img = self.utils.resize_to_width(img, size[0])
        img = self.utils.crop_center(img, size)
        return self.utils.optimize_for_web(img)

    @staticmethod
    def make_cover(self, path, size=(1200, 628)):
        """
        Preset: Generate a social media cover (Facebook, Twitter, etc.). 
        Resizes by width, then crops center to exact size.
        """
        img = self.utils.load_image(path)
        if not img:
            return None
        img = self.utils.resize_to_width(img, size[0])
        img = self.utils.crop_center(img, size)
        return self.utils.optimize_for_web(img)

    @staticmethod
    def make_gallery_image(self, path, size=800):
        """
        Preset: Generate a square gallery image. 
        Resizes, crops square, and optimizes for web.
        """
        img = self.utils.load_image(path)
        if not img:
            return None
        img = self.utils.resize_to_square(img, size)
        return self.utils.optimize_for_web(img)