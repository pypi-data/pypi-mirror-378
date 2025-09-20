"""
tests for the parser module
"""

import pytest
from fuero.core.lexer import Lexer
from fuero.core.parser import Parser
from fuero.core.ast_nodes import (
    Program, VariableDeclaration, FunctionDeclaration, BinaryOperation,
    IfStatement, WhileStatement, ExpressionStatement, FunctionCall,
    NumberLiteral, StringLiteral, Identifier
)


class TestParser:
    
    def test_variable_declaration(self):
        """test variable declaration parsing"""
        source = "let x = 5"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, VariableDeclaration)
        assert stmt.name == "x"
        assert isinstance(stmt.value, NumberLiteral)
        assert stmt.value.value == 5.0
    
    def test_function_declaration(self):
        """test function declaration parsing"""
        source = """
        func add(a, b) {
            return a + b
        }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, FunctionDeclaration)
        assert stmt.name == "add"
        assert len(stmt.parameters) == 2
        assert stmt.parameters[0] == "a"
        assert stmt.parameters[1] == "b"
    
    def test_binary_expression(self):
        """test binary expression parsing"""
        source = "let result = 5 + 3"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        stmt = ast.statements[0]
        assert isinstance(stmt, VariableDeclaration)
        assert isinstance(stmt.value, BinaryOperation)
        assert stmt.value.operator == "+"
        assert isinstance(stmt.value.left, NumberLiteral)
        assert isinstance(stmt.value.right, NumberLiteral)
    
    def test_if_statement(self):
        """test if statement parsing"""
        source = """
        if (x > 5) {
            print("big")
        } else {
            print("small")
        }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        stmt = ast.statements[0]
        assert isinstance(stmt, IfStatement)
        assert isinstance(stmt.condition, BinaryOperation)
        assert len(stmt.then_branch) == 1
        assert len(stmt.else_branch) == 1
    
    def test_while_loop(self):
        """test while loop parsing"""
        source = """
        while (i < 10) {
            i = i + 1
        }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        stmt = ast.statements[0]
        assert isinstance(stmt, WhileStatement)
        assert isinstance(stmt.condition, BinaryOperation)
        assert len(stmt.body) == 1
    
    def test_function_call(self):
        """test function call parsing"""
        source = "print(hello)"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        stmt = ast.statements[0]
        assert isinstance(stmt, ExpressionStatement)
        assert isinstance(stmt.expression, FunctionCall)
        assert stmt.expression.function.name == "print"
        assert len(stmt.expression.arguments) == 1
