"""Hashing and hash analysis utilities."""

import hashlib
from ..exceptions import CryptoError


class HashUtils:
    """Hash utility class for various hashing operations."""
    
    @staticmethod
    def md5(data: str) -> str:
        """
        Generate MD5 hash of data.
        
        Args:
            data: Data to hash
            
        Returns:
            MD5 hash as hex string
            
        Example:
            >>> HashUtils.md5("Hello World")
            'b10a8db164e0754105b7a99be72e3fe5'
        """
        if not isinstance(data, str):
            raise CryptoError("Data must be a string")
        
        return hashlib.md5(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def sha1(data: str) -> str:
        """
        Generate SHA1 hash of data.
        
        Args:
            data: Data to hash
            
        Returns:
            SHA1 hash as hex string
        """
        if not isinstance(data, str):
            raise CryptoError("Data must be a string")
        
        return hashlib.sha1(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def sha256(data: str) -> str:
        """
        Generate SHA256 hash of data.
        
        Args:
            data: Data to hash
            
        Returns:
            SHA256 hash as hex string
        """
        if not isinstance(data, str):
            raise CryptoError("Data must be a string")
        
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def sha512(data: str) -> str:
        """
        Generate SHA512 hash of data.
        
        Args:
            data: Data to hash
            
        Returns:
            SHA512 hash as hex string
        """
        if not isinstance(data, str):
            raise CryptoError("Data must be a string")
        
        return hashlib.sha512(data.encode('utf-8')).hexdigest()


class HashAnalyzer:
    """Hash analysis utilities."""
    
    @staticmethod
    def identify_hash_type(hash_string: str) -> str:
        """
        Try to identify hash type based on length.
        
        Args:
            hash_string: Hash to identify
            
        Returns:
            Possible hash type
        """
        hash_length = len(hash_string)
        
        if hash_length == 32:
            return "MD5"
        elif hash_length == 40:
            return "SHA1"
        elif hash_length == 64:
            return "SHA256"
        elif hash_length == 128:
            return "SHA512"
        else:
            return "Unknown"
    
    @staticmethod
    def verify_hash(data: str, hash_value: str, hash_type: str = "md5") -> bool:
        """
        Verify if data matches the given hash.
        
        Args:
            data: Original data
            hash_value: Hash to verify against
            hash_type: Type of hash (md5, sha1, sha256, sha512)
            
        Returns:
            True if hash matches
        """
        hash_functions = {
            'md5': HashUtils.md5,
            'sha1': HashUtils.sha1,
            'sha256': HashUtils.sha256,
            'sha512': HashUtils.sha512
        }
        
        if hash_type.lower() not in hash_functions:
            raise CryptoError(f"Unsupported hash type: {hash_type}")
        
        computed_hash = hash_functions[hash_type.lower()](data)
        return computed_hash.lower() == hash_value.lower()
    
    @staticmethod
    def hash_all_types(data: str) -> dict:
        """
        Generate all supported hash types for data.
        
        Args:
            data: Data to hash
            
        Returns:
            Dictionary with all hash types
        """
        return {
            'md5': HashUtils.md5(data),
            'sha1': HashUtils.sha1(data),
            'sha256': HashUtils.sha256(data),
            'sha512': HashUtils.sha512(data)
        }


# Backward compatibility functions
def md5_hash(data: str) -> str:
    """Backward compatibility function for MD5 hashing."""
    return HashUtils.md5(data)


def sha1_hash(data: str) -> str:
    """Backward compatibility function for SHA1 hashing."""
    return HashUtils.sha1(data)


def sha256_hash(data: str) -> str:
    """Backward compatibility function for SHA256 hashing."""
    return HashUtils.sha256(data)


def identify_hash(hash_string: str) -> str:
    """Backward compatibility function for hash identification."""
    return HashAnalyzer.identify_hash_type(hash_string)


def verify_hash(data: str, hash_value: str, hash_type: str = "md5") -> bool:
    """Backward compatibility function for hash verification."""
    return HashAnalyzer.verify_hash(data, hash_value, hash_type)