"""
MaskInfo - Sensitive Information Masking Library

A Python library that can read various file types and mask sensitive information
with asterisks or other placeholders, while providing the ability to restore
the original content.
"""

__version__ = "0.1.1"
__author__ = "Hayashi Kunita"
__email__ = "hayashi.kunita@example.com"

from .detector import SensitiveDetector
from .file_handler import FileHandler
from .masker import SensitiveMasker

__all__ = ["SensitiveMasker", "SensitiveDetector", "FileHandler"]
