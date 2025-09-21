"""Miscellaneous utilities for CTF challenges."""

# Import classes (new OOP approach)
from .converters import NumberConverter, TextConverter, StringManipulator
from .utils import WordlistGenerator, MathUtils, ValidationUtils, StringDistance

# Import backward compatibility functions
from .encodings import *
from .converters import *
from .utils import *

__all__ = [
    # Classes
    'NumberConverter', 'TextConverter', 'StringManipulator',
    'WordlistGenerator', 'MathUtils', 'ValidationUtils', 'StringDistance',
    
    # Encodings
    'hex_encode', 'hex_decode', 'binary_encode', 'binary_decode',
    'base32_encode', 'base32_decode', 'url_encode', 'url_decode',
    'html_encode', 'html_decode', 'morse_encode', 'morse_decode',
    
    # Converters  
    'ascii_to_hex', 'hex_to_ascii', 'decimal_to_binary', 'binary_to_decimal',
    'text_to_ascii_values', 'ascii_values_to_text', 'reverse_string',
    
    # Utils
    'generate_wordlist', 'bruteforce_pattern', 'calculate_entropy',
    'find_common_factors', 'gcd', 'lcm'
]