"""
Yomito - High-accuracy OCR library with intelligent auto-optimization.
"""

from .core import YomitoOCR, recognize_text, get_ocr_instance
from .ocr import OEM, PSM

__version__ = "1.3.0"
__author__ = "Yomito OCR"
__description__ = "High-accuracy OCR library with intelligent optimization"

__all__ = [
    "YomitoOCR",
    "recognize_text", 
    "get_ocr_instance",
    "OEM",
    "PSM"
]

OCR = YomitoOCR
recognize = recognize_text