"""Steganography utilities for CTF challenges."""

# Import classes (new OOP approach)
from .text import TextSteganography, ZeroWidthSteganography
from .image import ImageSteganography
from .audio import AudioSteganography

# Import backward compatibility functions
from .text import hide_text_whitespace, extract_text_whitespace
from .image import hide_text_lsb, extract_text_lsb

__all__ = [
    # Classes
    'TextSteganography', 'ZeroWidthSteganography', 
    'ImageSteganography', 'AudioSteganography',
    
    # Backward compatibility functions
    'hide_text_whitespace', 'extract_text_whitespace',
    'hide_text_lsb', 'extract_text_lsb'
]