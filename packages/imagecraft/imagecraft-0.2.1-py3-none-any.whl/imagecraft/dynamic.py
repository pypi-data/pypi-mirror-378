from .utils import ImageUtils


class ImageDynamic:
    def __init__(self, verbose: bool = False):
        self.utils = ImageUtils(verbose=verbose)
        self.verbose = verbose

    @staticmethod
    def process(self, path, *args, **kwargs):
        """
        Dynamic image processor.  
        - If one size given: square resize with crop.  
        - If two sizes: resize to width then crop to target (w, h).  
        - Supports adjustments: sharpness, brightness, quality, max_size_kb.  
        Returns final optimized image.
        """
        img = self.utils.load_image(path)
        if not img:
            return None

        if len(args) == 1:  # square
            img = self.utils.resize_to_square(img, args[0])
        elif len(args) == 2:  # rectangular
            target = (args[0], args[1])
            img = self.utils.resize_to_width(img, target[0])
            img = self.utils.crop_center(img, target)
        else:
            self.utils._log("No size specified, returning original image")
            return img

        if kwargs.get("sharpness", 1.0) != 1.0:
            img = self.utils.adjust_sharpness(img, kwargs["sharpness"])

        if kwargs.get("brightness", 1.0) != 1.0:
            img = self.utils.adjust_brightness(img, kwargs["brightness"])

        quality = kwargs.get("quality", 85)
        max_size_kb = kwargs.get("max_size_kb", None)
        img = self.utils.optimize_for_web(img, quality=quality, max_size_kb=max_size_kb)

        return img