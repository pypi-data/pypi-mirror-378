import numpy as np

class ImageTools:
    """
    Image processing tools for Phantom camera images.
    """
    def __init__(self) -> None: ...
    
    def apply_brightness(self, img: np.ndarray, brightness_value: float) -> np.ndarray:
        """
        Adjust the brightness of an image.
        :param img: Input image (numpy array)
        :param brightness_value: Value to add to each pixel
        :return: Brightness-adjusted image
        """
        ...

    def apply_contrast(self, img: np.ndarray, contrast_value: float) -> np.ndarray:
        """
        Adjust the contrast of an image.
        :param img: Input image (numpy array)
        :param contrast_value: Contrast multiplier
        :return: Contrast-adjusted image
        """
        ...

    def apply_gamma(self, img: np.ndarray, gamma: float, bpp: int = 12) -> np.ndarray:
        ...

    def debayer(self, img: np.ndarray, cfa_pattern: str, real_bit_depth: int, force_mono: int = 0) -> np.ndarray:
        ...

    def apply_dmap_correction(self, img: np.ndarray, cfa: str, bpp: int) -> np.ndarray:
        ...

    def get_dmap(self, img: np.ndarray, bpp: int) -> np.ndarray: ...
    def apply_wb(self, img: np.ndarray, rgain: float, bgain: float, cfa: str, bpp: int) -> np.ndarray: ...
    def apply_color_corr(self, img: np.ndarray, cmCalib: np.ndarray) -> np.ndarray: ...
    def stretch_image_rng(self, img: np.ndarray, display_bpp: int, black_lvl: float, white_lvl: float) -> np.ndarray: ...
    def decompose_cmatrix(self, cmatrix: np.ndarray) -> np.ndarray: ...
    def cast_to_8bpp(self, img: np.ndarray) -> np.ndarray: ...
    def cast_to_16bpp(self, img: np.ndarray) -> np.ndarray: ...
    # Public attributes
    gamma: any
    contrast: any
    brightness: any
    bitdepth: any
    gamma_lut: any
    dmap: any


