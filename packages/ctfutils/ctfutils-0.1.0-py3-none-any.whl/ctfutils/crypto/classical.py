"""Classical cryptography algorithms."""

from ..exceptions import CryptoError


class CaesarCipher:
    """Caesar cipher implementation."""
    
    def __init__(self, shift: int = 0):
        """
        Initialize Caesar cipher with default shift.
        
        Args:
            shift: Default shift value
        """
        self.shift = shift
    
    def encrypt(self, text: str, shift: int = None) -> str:
        """
        Encrypt text using Caesar cipher.
        
        Args:
            text: Text to encrypt
            shift: Number of positions to shift (uses default if None)
            
        Returns:
            Encrypted text
            
        Example:
            >>> cipher = CaesarCipher(3)
            >>> cipher.encrypt("HELLO")
            'KHOOR'
        """
        if not isinstance(text, str):
            raise CryptoError("Text must be a string")
        
        shift = shift if shift is not None else self.shift
        
        result = ""
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result += chr((ord(char) - base + shift) % 26 + base)
            else:
                result += char
        return result
    
    def decrypt(self, text: str, shift: int = None) -> str:
        """
        Decrypt Caesar cipher.
        
        Args:
            text: Text to decrypt
            shift: Number of positions to shift (uses default if None)
            
        Returns:
            Decrypted text
        """
        shift = shift if shift is not None else self.shift
        return self.encrypt(text, -shift)
    
    def brute_force(self, text: str) -> dict:
        """
        Try all possible shifts for Caesar cipher.
        
        Args:
            text: Encrypted text
            
        Returns:
            Dictionary with shift values and results
        """
        results = {}
        for shift in range(26):
            results[shift] = self.decrypt(text, shift)
        return results


class VigenereCipher:
    """Vigenère cipher implementation."""
    
    def __init__(self, key: str = ""):
        """
        Initialize Vigenère cipher with default key.
        
        Args:
            key: Default encryption key
        """
        self.key = key.upper()
    
    def encrypt(self, text: str, key: str = None) -> str:
        """
        Encrypt text using Vigenère cipher.
        
        Args:
            text: Text to encrypt
            key: Encryption key (uses default if None)
            
        Returns:
            Encrypted text
        """
        key = (key or self.key).upper()
        
        if not text or not key:
            raise CryptoError("Text and key cannot be empty")
        
        result = ""
        key_index = 0
        
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shift = ord(key[key_index % len(key)]) - ord('A')
                result += chr((ord(char) - base + shift) % 26 + base)
                key_index += 1
            else:
                result += char
        
        return result
    
    def decrypt(self, text: str, key: str = None) -> str:
        """
        Decrypt Vigenère cipher.
        
        Args:
            text: Text to decrypt
            key: Decryption key (uses default if None)
            
        Returns:
            Decrypted text
        """
        key = (key or self.key).upper()
        
        if not text or not key:
            raise CryptoError("Text and key cannot be empty")
        
        result = ""
        key_index = 0
        
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shift = ord(key[key_index % len(key)]) - ord('A')
                result += chr((ord(char) - base - shift) % 26 + base)
                key_index += 1
            else:
                result += char
        
        return result


# Backward compatibility functions
def caesar_encrypt(text: str, shift: int) -> str:
    """Backward compatibility function for caesar encryption."""
    cipher = CaesarCipher(shift)
    return cipher.encrypt(text)


def caesar_decrypt(text: str, shift: int) -> str:
    """Backward compatibility function for caesar decryption."""
    cipher = CaesarCipher(shift)
    return cipher.decrypt(text)


def vigenere_encrypt(text: str, key: str) -> str:
    """Backward compatibility function for vigenere encryption."""
    cipher = VigenereCipher(key)
    return cipher.encrypt(text)


def vigenere_decrypt(text: str, key: str) -> str:
    """Backward compatibility function for vigenere decryption."""
    cipher = VigenereCipher(key)
    return cipher.decrypt(text)