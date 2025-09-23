import numpy as np
from cython import boundscheck, wraparound
cimport numpy as np
import cv2
import time


cdef class ImageTools:
    cdef public object gamma
    cdef public object contrast
    cdef public object brightness
    cdef public object bitdepth
    cdef public object gamma_lut
    cdef public object dmap

    def __init__(self):
        self.gamma = None
        self.contrast = None
        self.brightness = None
        self.bitdepth = None
        self.gamma_lut = []
        self.dmap = []

    @boundscheck(False)
    @wraparound(False)
    cpdef np.ndarray apply_brightness(self, np.ndarray img, double brightness_value):
        """Apply brightness correction to an image.

        Args:
            image (numpy.ndarray): The image to be corrected.
            brightness_value (float): The brightness value.

        Returns:
            numpy.ndarray: The brightness-corrected image.
        """
        self.brightness = brightness_value
        return np.add(img, brightness_value)

    @boundscheck(False)
    @wraparound(False)
    cpdef np.ndarray apply_contrast(self, np.ndarray img, double contrast_value):
        """Apply contrast correction to an image.

        Args:
            image (numpy.ndarray): The image to be corrected.
            contrast_value (float): The contrast value.

        Returns:
            numpy.ndarray: The contrast-corrected image.
        """
        self.contrast = contrast_value
        return np.multiply(img, contrast_value)

    @boundscheck(False)
    @wraparound(False)
    cpdef np.ndarray apply_gamma(self, np.ndarray img, double gamma, int bpp=12):
        """
        Apply gamma correction to an image.

        Args:
            image (numpy.ndarray): The image to be corrected.
            gamma (float or [float]): The gamma value(s).
            bit_depth (int): The bit depth of the image. Defaults to 12.

        Returns:
            numpy.ndarray: The gamma-corrected image.
        """
        if bpp not in [8, 10, 12, 16]:
            raise IndexError
        max_val = 2**bpp - 1
        img = np.clip(img, 0, max_val).astype(np.uint16)
        if gamma != self.gamma or bpp != self.bitdepth:
            self.gamma = gamma
            self.bitdepth = bpp
            self.gamma_lut = np.uint16(np.clip(np.power(np.linspace(0, 1, int(2**bpp), dtype=np.float64), 1.0 / gamma) * max_val, 0, max_val))
        return self.gamma_lut[img.astype(np.uint16)].astype(np.uint8 if bpp == 8 else np.uint16)
    
    """@boundscheck(False)
    @wraparound(False)
    def apply_lut(self, np.ndarray img, np.ndarray lut):
        t = time.perf_counter()
        result = np.empty_like(img, dtype=np.uint16)
        if img.ndim == 3:    
            for i in range(img.shape[0]):
                for j in range(img.shape[1]):
                    for k in range(img.shape[2]):
                        result[i, j, k] = lut[int(img[i, j, k])]
        else:
            for i in range(img.shape[0]):
                for j in range(img.shape[1]):
                    result[i, j] = lut[int(img[i, j])]
        print(f'\n GAMMA third apply_lut took {time.perf_counter() - t:.2f} ms')
        return result"""
    
    @boundscheck(False)
    @wraparound(False)
    cpdef np.ndarray debayer(self, np.ndarray img, str cfa_pattern, int real_bit_depth, int force_mono=0):
        """Debayer an image using the given CFA pattern and bit depth."""
        conversion_codes = {
            "gb/rg": cv2.COLOR_BayerGR2RGB,  # 3
            "rg/gb": cv2.COLOR_BayerBG2RGB,  # 4
            "gr/gb": cv2.COLOR_BayerGB2RGB,  # 5
            "bg/gr": cv2.COLOR_BayerRG2RGB,  # 6
            "Mono": None                     # 0
        }
        if force_mono != 0:
            conversion_codes = {
                "gb/rg": cv2.COLOR_BayerGR2GRAY,  # 3
                "rg/gb": cv2.COLOR_BayerBG2GRAY,  # 4
                "gr/gb": cv2.COLOR_BayerGB2GRAY,  # 5
                "bg/gr": cv2.COLOR_BayerRG2GRAY,  # 6
                "Mono": None                     # 0
            }
        
        conversion_code = conversion_codes.get(cfa_pattern)
        if conversion_code is None:
            if cfa_pattern == "Mono":
                return img
            else:
                raise ValueError(f"Unknown CFA pattern: {cfa_pattern}")

        img = np.right_shift(img.astype(np.uint16), real_bit_depth - 8).astype(np.uint8)
        debayered_image = cv2.cvtColor(img, conversion_code)

        return debayered_image

    @boundscheck(False)
    @wraparound(False)
    cpdef np.ndarray apply_dmap_correction(self, np.ndarray img, str cfa, int bpp):
        """
        Do a nearest neighbor pixel replacement for marked bad pixels.
        """
        self.dmap = self.get_dmap(img, bpp)
        h, w = img.shape[:2]
        
        step_sz = 1
        if cfa != 'Mono':
            step_sz = 2

        # pixel replacement
        for d in self.dmap:
            x = d[1]
            y = d[0]
            new_x = x + step_sz
            if new_x >= w:
                new_x = x - step_sz
            if 0 <= y < h and 0 <= new_x < w:
                img[y][x] = img[y][new_x]
            
        return img

    @boundscheck(False)
    @wraparound(False)  
    def get_dmap(self, img, bpp):
        """
        get the frame indicies of all the marked bad pixels.
        """
        mark_val = 255 << (bpp - 8)
        dmap_raw = np.where(img == mark_val)
        return np.column_stack((dmap_raw[0].astype(np.uint16), dmap_raw[1].astype(np.uint16)))
    
    @boundscheck(False)
    @wraparound(False)
    def apply_wb(self, np.ndarray img, double rgain, double bgain, str cfa, int bpp):
        """
        Apply white balance gains to raw image, pre-debayer
        """
        if cfa == "gb/rg":
            #GB
            img[0::2,1::2] = img[0::2,1::2] * bgain
            img[1::2,0::2] = img[1::2,0::2] * rgain
        elif cfa == "rg/gb":
            #RG
            img[0::2,0::2] = img[0::2,0::2] * rgain
            img[1::2,1::2] = img[1::2,1::2] * bgain 
        elif cfa == "gr/gb":
            #GR
            img[0::2,1::2] = img[0::2,1::2] * rgain
            img[1::2,0::2] = img[1::2,0::2] * bgain
        elif cfa == "bg/gr":    
            #BG
            img[0::2,0::2] = img[0::2,0::2] * bgain
            img[1::2,1::2] = img[1::2,1::2] * rgain
        
        img = np.clip(img, 0, 2**bpp-1)
        img = img.astype(np.uint16)
        return img
    
    @boundscheck(False)
    @wraparound(False)
    def apply_color_corr(self, np.ndarray img, np.ndarray cmCalib):
        """
        Apply color matrix to image for post WB adjustment
        """
        cmCalib = np.asarray(cmCalib).reshape(3, 3)
        m = cmCalib / cmCalib.sum(axis=1)[:, np.newaxis]
        img = np.dot(img, m.T)
        return img
    
    @boundscheck(False)
    @wraparound(False)
    def stretch_image_rng(self, np.ndarray img, int display_bpp, double black_lvl, double white_lvl):
        """
        Interpolate the frame pixel range into the entire range of the display bit depth
        """
        img = np.interp(img, [black_lvl, white_lvl], [0, 2 ** display_bpp - 1])
        np.clip(img, 0, 2**display_bpp-1, out=img)
        return img
    
    @boundscheck(False)
    @wraparound(False)
    def decompose_cmatrix(self, np.ndarray cmatrix):
        """
        convert the color matrix into a 3x3 matrix for use by other functions
        """
        cm_3x3 = np.reshape(cmatrix, (3, 3))
        cm_out = np.linalg.inv(cm_3x3)
        # cm_out = cm_out / np.linalg.det(cm_3x3)
        cm_out = cm_out / cm_out.sum(axis=1)[:, np.newaxis]
        return cm_out

    @boundscheck(False)
    @wraparound(False)  
    def cast_to_8bpp(self, img: np.ndarray):
        return img.astype(np.uint8)

    @boundscheck(False)
    @wraparound(False)  
    def cast_to_16bpp(self, img: np.ndarray):
        return img.astype(np.uint16)







