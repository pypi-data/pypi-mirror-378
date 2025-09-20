"""
string utilities for fuero
provides string manipulation and processing functions
"""

import re
import string
import unicodedata
from typing import List, Optional, Dict, Union


class String:
    """string manipulation and processing utilities"""
    
    def __init__(self):
        # String constants
        self.ASCII_LETTERS = string.ascii_letters
        self.ASCII_LOWERCASE = string.ascii_lowercase
        self.ASCII_UPPERCASE = string.ascii_uppercase
        self.DIGITS = string.digits
        self.HEXDIGITS = string.hexdigits
        self.OCTDIGITS = string.octdigits
        self.PUNCTUATION = string.punctuation
        self.PRINTABLE = string.printable
        self.WHITESPACE = string.whitespace
    
    # Basic string operations
    def length(self, s: str) -> int:
        """Return length of string"""
        return len(s)
    
    def upper(self, s: str) -> str:
        """Convert to uppercase"""
        return s.upper()
    
    def lower(self, s: str) -> str:
        """Convert to lowercase"""
        return s.lower()
    
    def capitalize(self, s: str) -> str:
        """Capitalize first character"""
        return s.capitalize()
    
    def title(self, s: str) -> str:
        """Convert to title case"""
        return s.title()
    
    def swapcase(self, s: str) -> str:
        """Swap case of all characters"""
        return s.swapcase()
    
    def casefold(self, s: str) -> str:
        """Return casefolded string for caseless comparisons"""
        return s.casefold()
    
    # String testing
    def is_alpha(self, s: str) -> bool:
        """Check if all characters are alphabetic"""
        return s.isalpha()
    
    def is_digit(self, s: str) -> bool:
        """Check if all characters are digits"""
        return s.isdigit()
    
    def is_alnum(self, s: str) -> bool:
        """Check if all characters are alphanumeric"""
        return s.isalnum()
    
    def is_lower(self, s: str) -> bool:
        """Check if all characters are lowercase"""
        return s.islower()
    
    def is_upper(self, s: str) -> bool:
        """Check if all characters are uppercase"""
        return s.isupper()
    
    def is_space(self, s: str) -> bool:
        """Check if all characters are whitespace"""
        return s.isspace()
    
    def is_title(self, s: str) -> bool:
        """Check if string is in title case"""
        return s.istitle()
    
    def is_ascii(self, s: str) -> bool:
        """Check if all characters are ASCII"""
        return s.isascii()
    
    def is_decimal(self, s: str) -> bool:
        """Check if all characters are decimal"""
        return s.isdecimal()
    
    def is_numeric(self, s: str) -> bool:
        """Check if all characters are numeric"""
        return s.isnumeric()
    
    def is_printable(self, s: str) -> bool:
        """Check if all characters are printable"""
        return s.isprintable()
    
    # String searching and matching
    def find(self, s: str, sub: str, start: int = 0, end: Optional[int] = None) -> int:
        """Find substring, return index or -1"""
        return s.find(sub, start, end)
    
    def rfind(self, s: str, sub: str, start: int = 0, end: Optional[int] = None) -> int:
        """Find substring from right, return index or -1"""
        return s.rfind(sub, start, end)
    
    def index(self, s: str, sub: str, start: int = 0, end: Optional[int] = None) -> int:
        """Find substring, return index or raise ValueError"""
        return s.index(sub, start, end)
    
    def rindex(self, s: str, sub: str, start: int = 0, end: Optional[int] = None) -> int:
        """Find substring from right, return index or raise ValueError"""
        return s.rindex(sub, start, end)
    
    def count(self, s: str, sub: str, start: int = 0, end: Optional[int] = None) -> int:
        """Count non-overlapping occurrences of substring"""
        return s.count(sub, start, end)
    
    def startswith(self, s: str, prefix: Union[str, tuple], start: int = 0, end: Optional[int] = None) -> bool:
        """Check if string starts with prefix"""
        return s.startswith(prefix, start, end)
    
    def endswith(self, s: str, suffix: Union[str, tuple], start: int = 0, end: Optional[int] = None) -> bool:
        """Check if string ends with suffix"""
        return s.endswith(suffix, start, end)
    
    # String modification
    def replace(self, s: str, old: str, new: str, count: int = -1) -> str:
        """Replace occurrences of old with new"""
        return s.replace(old, new, count)
    
    def strip(self, s: str, chars: Optional[str] = None) -> str:
        """Remove leading and trailing characters"""
        return s.strip(chars)
    
    def lstrip(self, s: str, chars: Optional[str] = None) -> str:
        """Remove leading characters"""
        return s.lstrip(chars)
    
    def rstrip(self, s: str, chars: Optional[str] = None) -> str:
        """Remove trailing characters"""
        return s.rstrip(chars)
    
    def removeprefix(self, s: str, prefix: str) -> str:
        """Remove prefix if present"""
        if s.startswith(prefix):
            return s[len(prefix):]
        return s
    
    def removesuffix(self, s: str, suffix: str) -> str:
        """Remove suffix if present"""
        if s.endswith(suffix):
            return s[:-len(suffix)]
        return s
    
    # String splitting and joining
    def split(self, s: str, sep: Optional[str] = None, maxsplit: int = -1) -> List[str]:
        """Split string into list"""
        return s.split(sep, maxsplit)
    
    def rsplit(self, s: str, sep: Optional[str] = None, maxsplit: int = -1) -> List[str]:
        """Split string from right into list"""
        return s.rsplit(sep, maxsplit)
    
    def splitlines(self, s: str, keepends: bool = False) -> List[str]:
        """Split string at line boundaries"""
        return s.splitlines(keepends)
    
    def partition(self, s: str, sep: str) -> tuple:
        """Partition string into three parts"""
        return s.partition(sep)
    
    def rpartition(self, s: str, sep: str) -> tuple:
        """Partition string from right into three parts"""
        return s.rpartition(sep)
    
    def join(self, separator: str, iterable) -> str:
        """Join iterable with separator"""
        return separator.join(str(x) for x in iterable)
    
    # String formatting and alignment
    def center(self, s: str, width: int, fillchar: str = ' ') -> str:
        """Center string in field of given width"""
        return s.center(width, fillchar)
    
    def ljust(self, s: str, width: int, fillchar: str = ' ') -> str:
        """Left-justify string in field of given width"""
        return s.ljust(width, fillchar)
    
    def rjust(self, s: str, width: int, fillchar: str = ' ') -> str:
        """Right-justify string in field of given width"""
        return s.rjust(width, fillchar)
    
    def zfill(self, s: str, width: int) -> str:
        """Pad string with zeros on left"""
        return s.zfill(width)
    
    def expandtabs(self, s: str, tabsize: int = 8) -> str:
        """Expand tabs to spaces"""
        return s.expandtabs(tabsize)
    
    # Advanced string operations
    def reverse(self, s: str) -> str:
        """Reverse string"""
        return s[::-1]
    
    def slice(self, s: str, start: int, end: Optional[int] = None, step: int = 1) -> str:
        """Slice string"""
        return s[start:end:step]
    
    def repeat(self, s: str, count: int) -> str:
        """Repeat string count times"""
        return s * count
    
    def insert(self, s: str, index: int, substring: str) -> str:
        """Insert substring at index"""
        return s[:index] + substring + s[index:]
    
    def delete(self, s: str, start: int, end: Optional[int] = None) -> str:
        """Delete characters from start to end"""
        if end is None:
            end = start + 1
        return s[:start] + s[end:]
    
    # Regular expressions
    def match(self, pattern: str, string: str, flags: int = 0) -> Optional[re.Match]:
        """Match pattern at beginning of string"""
        return re.match(pattern, string, flags)
    
    def search(self, pattern: str, string: str, flags: int = 0) -> Optional[re.Match]:
        """Search for pattern in string"""
        return re.search(pattern, string, flags)
    
    def findall(self, pattern: str, string: str, flags: int = 0) -> List[str]:
        """Find all occurrences of pattern"""
        return re.findall(pattern, string, flags)
    
    def finditer(self, pattern: str, string: str, flags: int = 0):
        """Return iterator of match objects"""
        return re.finditer(pattern, string, flags)
    
    def sub(self, pattern: str, repl: str, string: str, count: int = 0, flags: int = 0) -> str:
        """Replace occurrences of pattern with replacement"""
        return re.sub(pattern, repl, string, count, flags)
    
    def subn(self, pattern: str, repl: str, string: str, count: int = 0, flags: int = 0) -> tuple:
        """Replace occurrences and return (new_string, number_of_subs)"""
        return re.subn(pattern, repl, string, count, flags)
    
    def split_regex(self, pattern: str, string: str, maxsplit: int = 0, flags: int = 0) -> List[str]:
        """Split string by regex pattern"""
        return re.split(pattern, string, maxsplit, flags)
    
    # Unicode operations
    def normalize(self, s: str, form: str = 'NFC') -> str:
        """Normalize Unicode string"""
        return unicodedata.normalize(form, s)
    
    def encode(self, s: str, encoding: str = 'utf-8', errors: str = 'strict') -> bytes:
        """Encode string to bytes"""
        return s.encode(encoding, errors)
    
    def decode(self, b: bytes, encoding: str = 'utf-8', errors: str = 'strict') -> str:
        """Decode bytes to string"""
        return b.decode(encoding, errors)
    
    # String analysis
    def word_count(self, s: str) -> int:
        """Count words in string"""
        return len(s.split())
    
    def char_frequency(self, s: str) -> Dict[str, int]:
        """Return character frequency dictionary"""
        freq = {}
        for char in s:
            freq[char] = freq.get(char, 0) + 1
        return freq
    
    def is_palindrome(self, s: str, ignore_case: bool = True, ignore_spaces: bool = True) -> bool:
        """Check if string is palindrome"""
        if ignore_spaces:
            s = ''.join(s.split())
        if ignore_case:
            s = s.lower()
        return s == s[::-1]
    
    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity ratio between two strings (0.0 to 1.0)"""
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0
        distance = self.levenshtein_distance(s1, s2)
        return 1.0 - (distance / max_len)
