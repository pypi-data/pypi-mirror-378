"""
lexer for fuero language
tokenizes source code into tokens for parsing
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Iterator


class TokenType(Enum):
    # Literals
    NUMBER = "NUMBER"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"
    
    # Identifiers and Keywords
    IDENTIFIER = "IDENTIFIER"
    KEYWORD = "KEYWORD"
    
    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"
    POWER = "POWER"
    
    # Comparison
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS_THAN = "LESS_THAN"
    GREATER_THAN = "GREATER_THAN"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER_EQUAL = "GREATER_EQUAL"
    
    # Logical
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    
    # Assignment
    ASSIGN = "ASSIGN"
    
    # Delimiters
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    COMMA = "COMMA"
    DOT = "DOT"
    SEMICOLON = "SEMICOLON"
    COLON = "COLON"
    
    # Special
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    WHITESPACE = "WHITESPACE"
    COMMENT = "COMMENT"


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int


class Lexer:
    """lexical analyzer for the fuero programming language"""
    
    KEYWORDS = {
        'let', 'const', 'var', 'func', 'return', 'if', 'else', 'elif',
        'while', 'for', 'in', 'break', 'continue', 'true', 'false',
        'null', 'import', 'from', 'as', 'class', 'extends', 'try',
        'catch', 'finally', 'throw', 'async', 'await'
    }
    
    TOKEN_PATTERNS = [
        # Comments
        (r'#.*', TokenType.COMMENT),
        
        # Numbers (integers and floats)
        (r'\d+\.\d+', TokenType.NUMBER),
        (r'\d+', TokenType.NUMBER),
        
        # Strings
        (r'"([^"\\]|\\.)*"', TokenType.STRING),
        (r"'([^'\\]|\\.)*'", TokenType.STRING),
        
        # Two-character operators
        (r'==', TokenType.EQUAL),
        (r'!=', TokenType.NOT_EQUAL),
        (r'<=', TokenType.LESS_EQUAL),
        (r'>=', TokenType.GREATER_EQUAL),
        (r'&&', TokenType.AND),
        (r'\|\|', TokenType.OR),
        (r'\*\*', TokenType.POWER),
        
        # Single-character operators
        (r'\+', TokenType.PLUS),
        (r'-', TokenType.MINUS),
        (r'\*', TokenType.MULTIPLY),
        (r'/', TokenType.DIVIDE),
        (r'%', TokenType.MODULO),
        (r'<', TokenType.LESS_THAN),
        (r'>', TokenType.GREATER_THAN),
        (r'!', TokenType.NOT),
        (r'=', TokenType.ASSIGN),
        
        # Delimiters
        (r'\(', TokenType.LPAREN),
        (r'\)', TokenType.RPAREN),
        (r'\{', TokenType.LBRACE),
        (r'\}', TokenType.RBRACE),
        (r'\[', TokenType.LBRACKET),
        (r'\]', TokenType.RBRACKET),
        (r',', TokenType.COMMA),
        (r'\.', TokenType.DOT),
        (r';', TokenType.SEMICOLON),
        (r':', TokenType.COLON),
        
        # Identifiers (must come after keywords)
        (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),
        
        # Whitespace and newlines
        (r'\n', TokenType.NEWLINE),
        (r'[ \t]+', TokenType.WHITESPACE),
    ]
    
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code"""
        while self.position < len(self.source):
            self._next_token()
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
    
    def _next_token(self) -> Optional[Token]:
        """Get the next token from the source"""
        if self.position >= len(self.source):
            return None
        
        # Try to match each pattern
        for pattern, token_type in self.TOKEN_PATTERNS:
            regex = re.compile(pattern)
            match = regex.match(self.source, self.position)
            
            if match:
                value = match.group(0)
                token = Token(token_type, value, self.line, self.column)
                
                # Handle special cases
                if token_type == TokenType.IDENTIFIER and value in self.KEYWORDS:
                    token.type = TokenType.KEYWORD
                elif token_type == TokenType.KEYWORD:
                    if value in ('true', 'false'):
                        token.type = TokenType.BOOLEAN
                    elif value == 'null':
                        token.type = TokenType.NULL
                
                # Update position
                self.position = match.end()
                
                # Update line and column
                if token_type == TokenType.NEWLINE:
                    self.line += 1
                    self.column = 1
                else:
                    self.column += len(value)
                
                # Skip whitespace and comments in the token list
                if token_type not in (TokenType.WHITESPACE, TokenType.COMMENT):
                    self.tokens.append(token)
                
                return token
        
        # If no pattern matches, raise an error
        char = self.source[self.position]
        raise SyntaxError(f"Unexpected character '{char}' at line {self.line}, column {self.column}")
    
    def peek_token(self, offset: int = 0) -> Optional[Token]:
        """Peek at a token without consuming it"""
        index = len(self.tokens) + offset
        if 0 <= index < len(self.tokens):
            return self.tokens[index]
        return None
