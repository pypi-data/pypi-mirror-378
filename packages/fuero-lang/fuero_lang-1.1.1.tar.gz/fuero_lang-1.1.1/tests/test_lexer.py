"""
tests for the lexer module
"""

import pytest
from fuero.core.lexer import Lexer, Token, TokenType


class TestLexer:
    
    def test_basic_tokens(self):
        """test basic token recognition"""
        source = "let x = 5"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected = [
            Token(TokenType.KEYWORD, "let", 1, 1),
            Token(TokenType.IDENTIFIER, "x", 1, 5),
            Token(TokenType.ASSIGN, "=", 1, 7),
            Token(TokenType.NUMBER, "5", 1, 9),
            Token(TokenType.EOF, "", 1, 10)
        ]
        
        assert len(tokens) == len(expected)
        for i, token in enumerate(tokens):
            assert token.type == expected[i].type
            assert token.value == expected[i].value
    
    def test_string_literals(self):
        """test string literal tokenization"""
        source = 'let name = "hello world"'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        string_token = tokens[3]
        assert string_token.type == TokenType.STRING
        assert string_token.value == '"hello world"'
    
    def test_numbers(self):
        """test number tokenization"""
        source = "42 3.14 0.5"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "42"
        assert tokens[1].type == TokenType.NUMBER
        assert tokens[1].value == "3.14"
        assert tokens[2].type == TokenType.NUMBER
        assert tokens[2].value == "0.5"
    
    def test_operators(self):
        """test operator tokenization"""
        source = "+ - * / == != < > <= >="
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,
            TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS_THAN, 
            TokenType.GREATER_THAN, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL
        ]
        
        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type
    
    def test_keywords(self):
        """test keyword recognition"""
        source = "func if else while for return class import"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # All keywords should be TokenType.KEYWORD
        for i in range(8):  # 8 keywords
            assert tokens[i].type == TokenType.KEYWORD
    
    def test_comments(self):
        """test comment handling"""
        source = """
        let x = 5  # this is a comment
        # another comment
        let y = 10
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # comments should be ignored, but newlines are kept
        non_eof_tokens = [t for t in tokens if t.type not in (TokenType.EOF, TokenType.NEWLINE)]
        assert len(non_eof_tokens) == 8  # let x = 5 let y = 10 (8 tokens total)
    
    def test_whitespace_handling(self):
        """test whitespace is properly ignored"""
        source = "   let    x   =   5   "
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected = [
            Token(TokenType.KEYWORD, "let", 1, 1),
            Token(TokenType.IDENTIFIER, "x", 1, 5),
            Token(TokenType.ASSIGN, "=", 1, 7),
            Token(TokenType.NUMBER, "5", 1, 9),
            Token(TokenType.EOF, "", 1, 10)
        ]
        
        assert len(tokens) == len(expected)
        for i, token in enumerate(tokens):
            assert token.type == expected[i].type
