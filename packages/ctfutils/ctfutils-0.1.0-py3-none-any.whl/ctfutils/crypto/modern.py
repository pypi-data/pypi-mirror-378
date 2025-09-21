"""Modern cryptography utilities."""

import base64
from ..exceptions import CryptoError


class Base64Encoder:
    """Base64 encoding and decoding utilities."""
    
    @staticmethod
    def encode(data: str) -> str:
        """
        Encode string to base64.
        
        Args:
            data: String to encode
            
        Returns:
            Base64 encoded string
            
        Example:
            >>> Base64Encoder.encode("Hello World")
            'SGVsbG8gV29ybGQ='
        """
        if not isinstance(data, str):
            raise CryptoError("Data must be a string")
        
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')
    
    @staticmethod
    def decode(data: str) -> str:
        """
        Decode base64 string.
        
        Args:
            data: Base64 encoded string
            
        Returns:
            Decoded string
        """
        try:
            return base64.b64decode(data).decode('utf-8')
        except Exception as e:
            raise CryptoError(f"Invalid base64 data: {e}")
    
    @staticmethod
    def is_base64(data: str) -> bool:
        """
        Check if string is valid base64.
        
        Args:
            data: String to check
            
        Returns:
            True if valid base64
        """
        try:
            if isinstance(data, str):
                sb_bytes = bytes(data, 'ascii')
            elif isinstance(data, bytes):
                sb_bytes = data
            else:
                raise ValueError("Argument must be string or bytes")
            return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
        except ValueError:
            return False


class XORCipher:
    """XOR encryption and decryption utilities."""
    
    def __init__(self, key: str = ""):
        """
        Initialize XOR cipher with default key.
        
        Args:
            key: Default XOR key
        """
        self.key = key
    
    def encrypt(self, data: str, key: str = None) -> str:
        """
        XOR encrypt data with key.
        
        Args:
            data: Data to encrypt
            key: XOR key (uses default if None)
            
        Returns:
            XOR result as hex string
            
        Example:
            >>> cipher = XORCipher("key")
            >>> cipher.encrypt("Hello")
            '03010d0c1b'
        """
        key = key or self.key
        
        if not data or not key:
            raise CryptoError("Data and key cannot be empty")
        
        result = []
        for i, char in enumerate(data):
            key_char = key[i % len(key)]
            result.append(format(ord(char) ^ ord(key_char), '02x'))
        
        return ''.join(result)
    
    def decrypt_hex(self, hex_data: str, key: str = None) -> str:
        """
        Decrypt hex XOR data.
        
        Args:
            hex_data: Hex encoded XOR data
            key: XOR key (uses default if None)
            
        Returns:
            Decrypted string
        """
        key = key or self.key
        
        try:
            # Convert hex to bytes
            data_bytes = bytes.fromhex(hex_data)
            result = []
            
            for i, byte in enumerate(data_bytes):
                key_char = key[i % len(key)]
                result.append(chr(byte ^ ord(key_char)))
            
            return ''.join(result)
        except Exception as e:
            raise CryptoError(f"Invalid hex data: {e}")
    
    def brute_force_single_byte(self, hex_data: str) -> dict:
        """
        Brute force single-byte XOR key.
        
        Args:
            hex_data: Hex encoded XOR data
            
        Returns:
            Dictionary with possible keys and results
        """
        results = {}
        
        try:
            data_bytes = bytes.fromhex(hex_data)
            
            for key_byte in range(256):
                try:
                    decrypted = ''.join([chr(byte ^ key_byte) for byte in data_bytes])
                    # Only include printable results
                    if all(32 <= ord(c) <= 126 or c in '\n\t' for c in decrypted):
                        results[key_byte] = decrypted
                except:
                    continue
                    
            return results
        except Exception as e:
            raise CryptoError(f"Invalid hex data: {e}")


# Backward compatibility functions
def base64_encode(data: str) -> str:
    """Backward compatibility function for base64 encoding."""
    return Base64Encoder.encode(data)


def base64_decode(data: str) -> str:
    """Backward compatibility function for base64 decoding."""
    return Base64Encoder.decode(data)


def xor_encrypt(data: str, key: str) -> str:
    """Backward compatibility function for XOR encryption."""
    cipher = XORCipher(key)
    return cipher.encrypt(data)


def xor_decrypt_hex(hex_data: str, key: str) -> str:
    """Backward compatibility function for XOR decryption."""
    cipher = XORCipher(key)
    return cipher.decrypt_hex(hex_data)