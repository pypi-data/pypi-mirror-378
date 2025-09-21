"""General utilities for CTF challenges."""

import math
import itertools
import string
from typing import List, Generator, Union
from ..exceptions import CTFUtilsError


class WordlistGenerator:
    """Wordlist and pattern generation utilities."""
    
    @staticmethod
    def generate_wordlist(charset: str, min_length: int, max_length: int) -> Generator[str, None, None]:
        """
        Generate wordlist with specified charset and length range.
        
        Args:
            charset: Characters to use
            min_length: Minimum word length
            max_length: Maximum word length
            
        Yields:
            Generated words
            
        Example:
            >>> words = list(WordlistGenerator.generate_wordlist("abc", 2, 3))
            >>> len(words)
            39
        """
        for length in range(min_length, max_length + 1):
            for word in itertools.product(charset, repeat=length):
                yield ''.join(word)

    @staticmethod
    def bruteforce_pattern(pattern: str, charset: str = string.ascii_lowercase) -> Generator[str, None, None]:
        """
        Generate strings matching a pattern.
        Use '?' for variable characters.
        
        Args:
            pattern: Pattern with '?' for variable chars
            charset: Characters to substitute
            
        Yields:
            Generated strings
            
        Example:
            >>> list(WordlistGenerator.bruteforce_pattern("a?c", "xyz"))
            ['axc', 'ayc', 'azc']
        """
        variable_positions = [i for i, char in enumerate(pattern) if char == '?']
        
        if not variable_positions:
            yield pattern
            return
        
        for combination in itertools.product(charset, repeat=len(variable_positions)):
            result = list(pattern)
            for pos, char in zip(variable_positions, combination):
                result[pos] = char
            yield ''.join(result)


class MathUtils:
    """Mathematical utilities for CTF challenges."""
    
    @staticmethod
    def calculate_entropy(text: str) -> float:
        """
        Calculate Shannon entropy of text.
        
        Args:
            text: Input text
            
        Returns:
            Entropy value
        """
        if not text:
            return 0.0
        
        # Count character frequencies
        frequencies = {}
        for char in text:
            frequencies[char] = frequencies.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        text_length = len(text)
        
        for count in frequencies.values():
            probability = count / text_length
            entropy -= probability * math.log2(probability)
        
        return entropy

    @staticmethod
    def find_common_factors(numbers: List[int]) -> List[int]:
        """
        Find common factors of a list of numbers.
        
        Args:
            numbers: List of integers
            
        Returns:
            List of common factors
        """
        if not numbers:
            return []
        
        # Start with factors of first number
        first_num = abs(numbers[0])
        factors = set()
        
        for i in range(1, int(math.sqrt(first_num)) + 1):
            if first_num % i == 0:
                factors.add(i)
                factors.add(first_num // i)
        
        # Filter factors that divide all numbers
        common_factors = []
        for factor in factors:
            if all(num % factor == 0 for num in numbers):
                common_factors.append(factor)
        
        return sorted(common_factors)

    @staticmethod
    def gcd(a: int, b: int) -> int:
        """
        Calculate Greatest Common Divisor.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            GCD of a and b
        """
        while b:
            a, b = b, a % b
        return abs(a)

    @staticmethod
    def gcd_list(numbers: List[int]) -> int:
        """
        Calculate GCD of a list of numbers.
        
        Args:
            numbers: List of integers
            
        Returns:
            GCD of all numbers
        """
        if not numbers:
            return 0
        
        result = abs(numbers[0])
        for num in numbers[1:]:
            result = MathUtils.gcd(result, abs(num))
        
        return result

    @staticmethod
    def lcm(a: int, b: int) -> int:
        """
        Calculate Least Common Multiple.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            LCM of a and b
        """
        return abs(a * b) // MathUtils.gcd(a, b) if a and b else 0

    @staticmethod
    def is_prime(n: int) -> bool:
        """
        Check if a number is prime.
        
        Args:
            n: Number to check
            
        Returns:
            True if prime, False otherwise
        """
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        
        return True

    @staticmethod
    def prime_factors(n: int) -> List[int]:
        """
        Find prime factors of a number.
        
        Args:
            n: Number to factorize
            
        Returns:
            List of prime factors
        """
        factors = []
        d = 2
        
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        
        if n > 1:
            factors.append(n)
        
        return factors


class ValidationUtils:
    """Input validation and safety utilities."""
    
    @staticmethod
    def validate_input(value: any, expected_type: type, param_name: str = "parameter") -> None:
        """
        Validate input parameter type.
        
        Args:
            value: Value to validate
            expected_type: Expected type
            param_name: Parameter name for error message
            
        Raises:
            CTFUtilsError: If validation fails
        """
        if not isinstance(value, expected_type):
            raise CTFUtilsError(f"{param_name} must be of type {expected_type.__name__}, got {type(value).__name__}")

    @staticmethod
    def safe_divide(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Safe division that handles division by zero.
        
        Args:
            a: Dividend
            b: Divisor
            
        Returns:
            Division result
            
        Raises:
            CTFUtilsError: If division by zero
        """
        if b == 0:
            raise CTFUtilsError("Division by zero")
        return a / b


class StringDistance:
    """String distance calculation utilities."""
    
    @staticmethod
    def hamming_distance(str1: str, str2: str) -> int:
        """
        Calculate Hamming distance between two strings.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Hamming distance
        """
        if len(str1) != len(str2):
            raise CTFUtilsError("Strings must have equal length for Hamming distance")
        
        return sum(c1 != c2 for c1, c2 in zip(str1, str2))

    @staticmethod
    def levenshtein_distance(str1: str, str2: str) -> int:
        """
        Calculate Levenshtein distance between two strings.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Levenshtein distance
        """
        if len(str1) < len(str2):
            return StringDistance.levenshtein_distance(str2, str1)
        
        if len(str2) == 0:
            return len(str1)
        
        previous_row = range(len(str2) + 1)
        for i, c1 in enumerate(str1):
            current_row = [i + 1]
            for j, c2 in enumerate(str2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]


# Backward compatibility functions
def generate_wordlist(charset: str, min_length: int, max_length: int) -> Generator[str, None, None]:
    """Backward compatibility function."""
    return WordlistGenerator.generate_wordlist(charset, min_length, max_length)


def bruteforce_pattern(pattern: str, charset: str = string.ascii_lowercase) -> Generator[str, None, None]:
    """Backward compatibility function."""
    return WordlistGenerator.bruteforce_pattern(pattern, charset)


def calculate_entropy(text: str) -> float:
    """Backward compatibility function."""
    return MathUtils.calculate_entropy(text)


def find_common_factors(numbers: List[int]) -> List[int]:
    """Backward compatibility function."""
    return MathUtils.find_common_factors(numbers)


def gcd(a: int, b: int) -> int:
    """Backward compatibility function."""
    return MathUtils.gcd(a, b)


def gcd_list(numbers: List[int]) -> int:
    """Backward compatibility function."""
    return MathUtils.gcd_list(numbers)


def lcm(a: int, b: int) -> int:
    """Backward compatibility function."""
    return MathUtils.lcm(a, b)


def is_prime(n: int) -> bool:
    """Backward compatibility function."""
    return MathUtils.is_prime(n)


def prime_factors(n: int) -> List[int]:
    """Backward compatibility function."""
    return MathUtils.prime_factors(n)


def validate_input(value: any, expected_type: type, param_name: str = "parameter") -> None:
    """Backward compatibility function."""
    return ValidationUtils.validate_input(value, expected_type, param_name)


def safe_divide(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Backward compatibility function."""
    return ValidationUtils.safe_divide(a, b)


def hamming_distance(str1: str, str2: str) -> int:
    """Backward compatibility function."""
    return StringDistance.hamming_distance(str1, str2)


def levenshtein_distance(str1: str, str2: str) -> int:
    """Backward compatibility function."""
    return StringDistance.levenshtein_distance(str1, str2)
    """
    Calculate Least Common Multiple.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        LCM of a and b
    """
    return abs(a * b) // gcd(a, b) if a and b else 0

def is_prime(n: int) -> bool:
    """
    Check if a number is prime.
    
    Args:
        n: Number to check
        
    Returns:
        True if prime, False otherwise
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    
    return True

def prime_factors(n: int) -> List[int]:
    """
    Find prime factors of a number.
    
    Args:
        n: Number to factorize
        
    Returns:
        List of prime factors
    """
    factors = []
    d = 2
    
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    
    if n > 1:
        factors.append(n)
    
    return factors

def validate_input(value: any, expected_type: type, param_name: str = "parameter") -> None:
    """
    Validate input parameter type.
    
    Args:
        value: Value to validate
        expected_type: Expected type
        param_name: Parameter name for error message
        
    Raises:
        CTFUtilsError: If validation fails
    """
    if not isinstance(value, expected_type):
        raise CTFUtilsError(f"{param_name} must be of type {expected_type.__name__}, got {type(value).__name__}")

def safe_divide(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Safe division that handles division by zero.
    
    Args:
        a: Dividend
        b: Divisor
        
    Returns:
        Division result
        
    Raises:
        CTFUtilsError: If division by zero
    """
    if b == 0:
        raise CTFUtilsError("Division by zero")
    return a / b

def hamming_distance(str1: str, str2: str) -> int:
    """
    Calculate Hamming distance between two strings.
    
    Args:
        str1: First string
        str2: Second string
        
    Returns:
        Hamming distance
    """
    if len(str1) != len(str2):
        raise CTFUtilsError("Strings must have equal length for Hamming distance")
    
    return sum(c1 != c2 for c1, c2 in zip(str1, str2))

def levenshtein_distance(str1: str, str2: str) -> int:
    """
    Calculate Levenshtein distance between two strings.
    
    Args:
        str1: First string
        str2: Second string
        
    Returns:
        Levenshtein distance
    """
    if len(str1) < len(str2):
        return levenshtein_distance(str2, str1)
    
    if len(str2) == 0:
        return len(str1)
    
    previous_row = range(len(str2) + 1)
    for i, c1 in enumerate(str1):
        current_row = [i + 1]
        for j, c2 in enumerate(str2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]