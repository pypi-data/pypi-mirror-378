"""Forensics utilities for CTF challenges."""

# Import classes (new OOP approach)
from .files import FileAnalyzer
from .network import NetworkAnalyzer
from .memory import MemoryAnalyzer

# Import backward compatibility functions
from .files import extract_strings, file_signature, metadata_extract
from .network import parse_pcap_basic, extract_http_data
from .memory import find_patterns, extract_processes

__all__ = [
    # Classes
    'FileAnalyzer', 'NetworkAnalyzer', 'MemoryAnalyzer',
    # Backward compatibility functions
    'extract_strings', 'file_signature', 'metadata_extract',
    'parse_pcap_basic', 'extract_http_data',
    'find_patterns', 'extract_processes'
]