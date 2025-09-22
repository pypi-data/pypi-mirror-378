"""Yomito OCR - Main API."""

import logging
import shutil
import sys
from pathlib import Path
from typing import Union, Optional

try:
    from PIL import Image as PILImage
except ImportError:
    raise ImportError("Pillow required: pip install Pillow")

from .ocr import preprocess, perform_ocr, get_languages, TessArgs, OEM, PSM, OcrResult

logger = logging.getLogger(__name__)


class YomitoOCR:
    """High-accuracy OCR with intelligent auto-optimization."""
    
    def __init__(self, 
                 tesseract_path: Optional[Union[str, Path]] = None,
                 tessdata_path: Optional[Union[str, Path]] = None,
                 default_lang: str = "eng",
                 auto_languages: Optional[list[str]] = None):
        self.tesseract_path = self._find_tesseract(tesseract_path)
        self.tessdata_path = Path(tessdata_path) if tessdata_path else None
        self.default_lang = default_lang
        self.auto_languages = auto_languages or []
        
        logger.info(f"Yomito OCR initialized: {self.tesseract_path}")
    
    def _find_tesseract(self, tesseract_path: Optional[Union[str, Path]]) -> Path:
        if tesseract_path:
            path = Path(tesseract_path)
            if path.exists():
                return path
            raise FileNotFoundError(f"Tesseract not found: {tesseract_path}")
        
        tesseract_bin = shutil.which("tesseract")
        if tesseract_bin:
            return Path(tesseract_bin)
        
        raise RuntimeError("Tesseract not found! Install tesseract-ocr package.")
    
    def _prepare_image(self, image_input: Union[str, Path, 'PILImage.Image']) -> PILImage.Image:
        """Prepare image for OCR processing."""
        if isinstance(image_input, PILImage.Image):
            return image_input
        elif isinstance(image_input, (str, Path)):
            try:
                return PILImage.open(str(image_input))
            except Exception as e:
                raise ValueError(f"Could not load image: {image_input}") from e
        else:
            raise TypeError(f"Unsupported image type: {type(image_input)}")
    
    def _detect_language_fast(self, image: PILImage.Image) -> str:
        """Fast language detection based on character analysis."""
        available_langs = self.get_available_languages()

        if self.auto_languages:
            lang_candidates = [lang for lang in self.auto_languages if lang in available_langs]
        else:
            lang_candidates = []
            if 'eng' in available_langs:
                lang_candidates.append('eng')
            if 'rus' in available_langs:
                lang_candidates.append('rus')
        
        if not lang_candidates:
            return self.default_lang

        first_lang = lang_candidates[0] if lang_candidates else 'eng'
        result = self._recognize_with_lang(image, first_lang)
        text = result.text.strip()

        cyrillic_count = sum(1 for char in text if '\u0400' <= char <= '\u04FF')
        latin_count = sum(1 for char in text if char.isalpha() and char.isascii())
        digit_count = sum(1 for char in text if char.isdigit())
        
        total_chars = max(len(text), 1)
        cyrillic_ratio = cyrillic_count / total_chars
        latin_ratio = latin_count / total_chars

        url_indicators = ['http', 'www', '.com', '.org', '.net', '://', 'github']
        has_url_pattern = any(indicator in text.lower() for indicator in url_indicators)

        if has_url_pattern and 'eng' in lang_candidates:
            return 'eng'
        elif cyrillic_ratio > 0.3 and 'rus' in lang_candidates:
            return 'rus'
        elif latin_ratio > 0.5 and 'eng' in lang_candidates:
            return 'eng'
        
        return first_lang
    
    def _detect_language_precise(self, image: PILImage.Image) -> str:
        """Precise language detection with comprehensive analysis."""
        available_langs = self.get_available_languages()

        if self.auto_languages:
            lang_candidates = [lang for lang in self.auto_languages if lang in available_langs]
        else:
            lang_candidates = []
            if 'eng' in available_langs:
                lang_candidates.append('eng')
            if 'rus' in available_langs:
                lang_candidates.append('rus')
        
        if not lang_candidates:
            return self.default_lang
        
        results = {}
        for lang in lang_candidates:
            try:
                result = self._recognize_with_lang(image, lang)
                text = result.text.strip()

                cyrillic_count = sum(1 for char in text if '\u0400' <= char <= '\u04FF')
                latin_count = sum(1 for char in text if char.isalpha() and char.isascii())
                digit_count = sum(1 for char in text if char.isdigit())

                total_chars = max(len(text), 1)
                cyrillic_ratio = cyrillic_count / total_chars
                latin_ratio = latin_count / total_chars

                score = result.mean_conf

                url_indicators = ['http', 'www', '.com', '.org', '.net', '://', 'github', 'issues']
                has_url_pattern = any(indicator in text.lower() for indicator in url_indicators)
                
                if lang == 'eng':
                    score += latin_ratio * 20
                    score -= cyrillic_ratio * 30
                    if has_url_pattern:
                        score += 25
                    if digit_count > 0 and latin_ratio > 0.3:
                        score += 10
                elif lang == 'rus':
                    score += cyrillic_ratio * 25
                    score -= latin_ratio * 10 if cyrillic_ratio < 0.1 else 0
                    if has_url_pattern and cyrillic_ratio < 0.2:
                        score -= 20
                
                results[lang] = score
                
            except:
                continue
        
        if not results:
            return self.default_lang
        
        best_lang = max(results.keys(), key=lambda lang: results[lang])
        return best_lang
    
    def _recognize_with_lang(self, image: PILImage.Image, lang: str) -> 'OcrResult':
        processed_image_path = preprocess(image=image, padding=80)
        
        tess_args = TessArgs(
            tessdata_path=self.tessdata_path,
            lang=lang,
            oem=OEM.DEFAULT,
            psm=PSM.AUTO
        )
        
        ocr_result_data = perform_ocr(
            tesseract_bin_path=self.tesseract_path,
            image_path=processed_image_path,
            args=tess_args.as_list()
        )
        
        return OcrResult(tess_args=tess_args, words=ocr_result_data)
    
    def recognize(self,
                  image: Union[str, Path, 'PILImage.Image'],
                  lang: Optional[str] = None,
                  resize_factor: Optional[float] = None,
                  padding_size: int = 80,
                  psm: PSM = PSM.AUTO,
                  oem: OEM = OEM.DEFAULT) -> str:
        """Recognize text with auto-optimization."""
        pil_image = self._prepare_image(image)

        if lang is None:
            lang = self.default_lang
        elif lang == "auto_fast":
            lang = self._detect_language_fast(pil_image)
        elif lang == "auto" or lang == "auto_high":
            lang = self._detect_language_precise(pil_image)
        elif lang == "all":
            available_langs = self.get_available_languages()
            lang = '+'.join(available_langs) if available_langs else self.default_lang
        
        processed_image_path = preprocess(
            image=pil_image,
            resize_factor=resize_factor,
            padding=padding_size
        )
        
        tess_args = TessArgs(
            tessdata_path=self.tessdata_path,
            lang=lang,
            oem=oem,
            psm=psm
        )
        
        ocr_result_data = perform_ocr(
            tesseract_bin_path=self.tesseract_path,
            image_path=processed_image_path,
            args=tess_args.as_list()
        )
        
        result = OcrResult(tess_args=tess_args, words=ocr_result_data)
        return result.text
    
    def recognize_detailed(self,
                          image: Union[str, Path, 'PILImage.Image'],
                          lang: Optional[str] = None,
                          resize_factor: Optional[float] = None,
                          padding_size: int = 80,
                          psm: PSM = PSM.AUTO,
                          oem: OEM = OEM.DEFAULT) -> OcrResult:
        """Recognize text with detailed metadata."""
        pil_image = self._prepare_image(image)
        
        if lang is None:
            lang = self.default_lang
        elif lang == "auto_fast":
            lang = self._detect_language_fast(pil_image)
        elif lang == "auto" or lang == "auto_high":
            lang = self._detect_language_precise(pil_image)
        elif lang == "all":
            # Use all available languages
            available_langs = self.get_available_languages()
            lang = '+'.join(available_langs) if available_langs else self.default_lang
        
        processed_image_path = preprocess(
            image=pil_image,
            resize_factor=resize_factor,
            padding=padding_size
        )
        
        tess_args = TessArgs(
            tessdata_path=self.tessdata_path,
            lang=lang,
            oem=oem,
            psm=psm
        )
        
        ocr_result_data = perform_ocr(
            tesseract_bin_path=self.tesseract_path,
            image_path=processed_image_path,
            args=tess_args.as_list()
        )
        
        return OcrResult(tess_args=tess_args, words=ocr_result_data)
    
    def get_available_languages(self) -> list[str]:
        try:
            return get_languages(self.tesseract_path, self.tessdata_path)
        except Exception as e:
            logger.error(f"Error getting languages: {e}")
            return []
    
    def set_default_language(self, lang: str):
        """Set the default language for OCR recognition."""
        self.default_lang = lang
    
    def set_auto_languages(self, languages: list[str]):
        """Set the list of languages to consider during auto-detection."""
        self.auto_languages = languages or []
    
    def get_version(self) -> str:
        """Get the library version."""
        from . import __version__
        return __version__


_global_ocr = None


def get_ocr_instance(**kwargs) -> YomitoOCR:
    global _global_ocr
    if _global_ocr is None:
        _global_ocr = YomitoOCR(**kwargs)
    return _global_ocr


def recognize_text(image: Union[str, Path, 'PILImage.Image'], 
                  lang: str = "auto", 
                  **kwargs) -> str:
    """Quick text recognition with auto-optimization.
    
    Args:
        image: Input image (path or PIL Image)
        lang: Language mode - 'auto'/'auto_high' (precise), 'auto_fast' (fast), 
              'all' (all languages), specific language ('eng'), or combined ('eng+rus+jpn')
        **kwargs: Additional OCR parameters
    
    Returns:
        Recognized text string
    """
    ocr = get_ocr_instance()
    return ocr.recognize(image, lang=lang, **kwargs)