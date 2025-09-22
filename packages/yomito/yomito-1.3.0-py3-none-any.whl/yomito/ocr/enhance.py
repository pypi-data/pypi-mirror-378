"""Image preprocessing with intelligent optimization."""

import logging
import tempfile
from typing import Optional

try:
    from PIL import Image
except ImportError:
    raise ImportError("Pillow required: pip install Pillow")

logger = logging.getLogger(__name__)


def _get_edge_colors(image: Image.Image) -> list[tuple[int, int, int]]:
    width, height = image.size
    edge_pixels = []
    
    for x in range(0, width, max(1, width // 50)):
        edge_pixels.append(image.getpixel((x, 0)))
        edge_pixels.append(image.getpixel((x, height - 1)))
    
    for y in range(0, height, max(1, height // 50)):
        edge_pixels.append(image.getpixel((0, y)))
        edge_pixels.append(image.getpixel((width - 1, y)))
    
    return edge_pixels


def _get_most_frequent_color(pixels: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    from collections import Counter
    return Counter(pixels).most_common(1)[0][0]


def add_padding(image: Image.Image, padding: int = 80) -> Image.Image:
    width, height = image.size
    new_width = width + padding * 2
    new_height = height + padding * 2
    
    edge_colors = _get_edge_colors(image)
    bg_color = _get_most_frequent_color(edge_colors)
    
    padded_image = Image.new('RGB', (new_width, new_height), bg_color)
    padded_image.paste(image, (padding, padding))
    
    return padded_image


def resize_image(image: Image.Image, factor: float) -> Image.Image:
    width, height = image.size
    new_width = int(width * factor)
    new_height = int(height * factor)
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


def calculate_optimal_resize_factor(image: Image.Image) -> float:
    width, height = image.size
    min_dimension = min(width, height)
    max_dimension = max(width, height)
    total_pixels = width * height
    aspect_ratio = max_dimension / min_dimension
    
    gray_image = image.convert('L')
    
    try:
        import numpy as np
        img_array = np.array(gray_image)
        brightness = np.mean(img_array)
        contrast = np.std(img_array)
        
        edges_h = np.abs(np.diff(img_array, axis=0)).mean()
        edges_v = np.abs(np.diff(img_array, axis=1)).mean()
        edge_density = (edges_h + edges_v) / 2
        text_density = (contrast * edge_density) / (brightness + 1)
        
        binary = img_array > (brightness + contrast * 0.5)
        text_regions = np.sum(binary) / total_pixels
        
    except ImportError:
        pixels = list(gray_image.getdata())
        brightness = sum(pixels) / len(pixels)
        variance = sum((p - brightness) ** 2 for p in pixels) / len(pixels)
        contrast = variance ** 0.5
        text_density = contrast / (brightness + 1)
        text_regions = 0.5
    
    if total_pixels < 3000:
        base_factor = 8.0
    elif total_pixels < 8000 and min_dimension < 40:
        base_factor = 7.0
    elif min_dimension < 50:
        base_factor = 6.0
    elif min_dimension < 80:
        base_factor = 5.0 if aspect_ratio > 6 else 4.5
    elif min_dimension < 120:
        base_factor = 3.5 if aspect_ratio > 4 else 3.0
    elif min_dimension < 180:
        base_factor = 2.2 if aspect_ratio > 3 else 1.8
    elif min_dimension < 300:
        base_factor = 1.5
    elif min_dimension < 500:
        base_factor = 1.3
    else:
        base_factor = 1.0
    
    if 'text_regions' in locals():
        if text_regions > 0.7:
            base_factor *= 1.1
        elif text_regions < 0.2:
            base_factor *= 0.95
    
    if contrast < 25:
        base_factor *= 1.2
    elif contrast < 40:
        base_factor *= 1.1
    elif contrast > 80:
        base_factor *= 0.95
    
    if brightness < 40:
        base_factor *= 1.15
    elif brightness > 220:
        base_factor *= 1.1
    elif 80 <= brightness <= 180:
        base_factor *= 0.98
    
    if 'text_density' in locals():
        if text_density > 60:
            base_factor *= 1.05
        elif text_density < 15:
            base_factor *= 0.92
    
    factor = max(1.0, min(8.0, base_factor))
    
    if factor >= 4.0:
        return round(factor * 2) / 2
    else:
        return round(factor * 10) / 10


def save_image_for_tesseract(image: Image.Image) -> str:
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(tmp_file.name, 'PNG')
        return tmp_file.name


def preprocess(
    image: Image.Image, 
    resize_factor: Optional[float] = None, 
    padding: Optional[int] = None
) -> str:
    """Preprocess image with intelligent optimization."""
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    if resize_factor is None:
        resize_factor = calculate_optimal_resize_factor(image)
        logger.debug(f"Auto-resize: {resize_factor}x for {image.size}")
    
    if resize_factor and resize_factor != 1.0:
        image = resize_image(image, factor=resize_factor)
    
    if padding:
        image = add_padding(image, padding=padding)
    
    return save_image_for_tesseract(image)
