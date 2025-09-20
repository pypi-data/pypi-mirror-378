"""
fuero programming language v1.1.1 (experimental)
a modern programming language with comprehensive utilities

created by: ogcae
"""

__version__     = "1.1.1"
__author__      = "ogcae"
__description__ = "a modern programming language with comprehensive utilities"

from .core.interpreter import Interpreter
from .core.lexer import Lexer
from .core.parser import Parser

__all__ = ['Interpreter', 'Lexer', 'Parser']
