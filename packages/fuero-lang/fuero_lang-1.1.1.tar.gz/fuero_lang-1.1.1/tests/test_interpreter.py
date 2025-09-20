"""
tests for the interpreter module
"""

import pytest
from fuero.core.lexer import Lexer
from fuero.core.parser import Parser
from fuero.core.interpreter import Interpreter


class TestInterpreter:
    
    def test_variable_assignment(self):
        """test variable assignment and retrieval"""
        source = """
        let x = 5
        let y = x + 3
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
        assert interpreter.environment.get("x") == 5.0
        assert interpreter.environment.get("y") == 8.0
    
    def test_arithmetic_operations(self):
        """test basic arithmetic operations"""
        source = """
        let a = 10 + 5
        let b = 20 - 8
        let c = 6 * 7
        let d = 15 / 3
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
        assert interpreter.environment.get("a") == 15.0
        assert interpreter.environment.get("b") == 12.0
        assert interpreter.environment.get("c") == 42.0
        assert interpreter.environment.get("d") == 5.0
    
    def test_string_operations(self):
        """test string concatenation"""
        source = """
        let greeting = "hello"
        let name = "world"
        let message = greeting + " " + name
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
        assert interpreter.environment.get("greeting") == "hello"
        assert interpreter.environment.get("name") == "world"
        assert interpreter.environment.get("message") == "hello world"
    
    def test_function_definition_and_call(self):
        """test function definition and calling"""
        source = """
        func add(a, b) {
            return a + b
        }
        let result = add(5, 3)
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
        assert interpreter.environment.get("result") == 8.0
    
    def test_conditional_statements(self):
        """test if/else statements"""
        source = """
        let x = 10
        let result = ""
        if (x > 5) {
            result = "big"
        } else {
            result = "small"
        }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
        assert interpreter.environment.get("result") == "big"
    
    def test_while_loop(self):
        """test while loop execution"""
        source = """
        let i = 0
        let sum = 0
        while (i < 5) {
            sum = sum + i
            i = i + 1
        }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
        assert interpreter.environment.get("i") == 5.0
        assert interpreter.environment.get("sum") == 10.0  # 0+1+2+3+4
    
    def test_comparison_operators(self):
        """test comparison operators"""
        source = """
        let a = 5 == 5
        let b = 3 != 4
        let c = 7 > 3
        let d = 2 < 8
        let e = 5 >= 5
        let f = 4 <= 6
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
        assert interpreter.environment.get("a") == True
        assert interpreter.environment.get("b") == True
        assert interpreter.environment.get("c") == True
        assert interpreter.environment.get("d") == True
        assert interpreter.environment.get("e") == True
        assert interpreter.environment.get("f") == True
