"""Cryptography utilities for CTF challenges."""

# Import classes (new OOP approach)
from .classical import CaesarCipher, VigenereCipher
from .modern import Base64Encoder, XORCipher
from .hashing import HashUtils, HashAnalyzer

# Import backward compatibility functions
from .classical import caesar_encrypt, caesar_decrypt, vigenere_encrypt, vigenere_decrypt
from .modern import base64_encode, base64_decode, xor_encrypt
from .hashing import md5_hash, sha256_hash

__all__ = [
    # Classes
    'CaesarCipher', 'VigenereCipher',
    'Base64Encoder', 'XORCipher', 
    'HashUtils', 'HashAnalyzer',
    # Backward compatibility functions
    'caesar_encrypt', 'caesar_decrypt', 
    'vigenere_encrypt', 'vigenere_decrypt',
    'base64_encode', 'base64_decode', 'xor_encrypt',
    'md5_hash', 'sha256_hash'
]