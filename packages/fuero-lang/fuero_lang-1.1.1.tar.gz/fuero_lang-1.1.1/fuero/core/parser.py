"""
parser for fuero language
parses tokens into an abstract syntax tree (ast)
"""

from typing import List, Optional, Union
from .lexer import Token, TokenType, Lexer
from .ast_nodes import *


class ParseError(Exception):
    """Exception raised when parsing fails"""
    pass


class Parser:
    """parser for the fuero programming language"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> Program:
        """Parse tokens into an AST"""
        statements = []
        
        while not self._is_at_end():
            if self._peek().type == TokenType.NEWLINE:
                self._advance()
                continue
            
            stmt = self._statement()
            if stmt:
                statements.append(stmt)
        
        return Program(statements)
    
    def _statement(self) -> Optional[Statement]:
        """Parse a statement"""
        try:
            if self._match(TokenType.KEYWORD):
                keyword = self._previous().value
                
                if keyword == 'let' or keyword == 'var':
                    return self._variable_declaration(False)
                elif keyword == 'const':
                    return self._variable_declaration(True)
                elif keyword == 'func':
                    return self._function_declaration()
                elif keyword == 'return':
                    return self._return_statement()
                elif keyword == 'if':
                    return self._if_statement()
                elif keyword == 'while':
                    return self._while_statement()
                elif keyword == 'for':
                    return self._for_statement()
                elif keyword == 'break':
                    return BreakStatement()
                elif keyword == 'continue':
                    return ContinueStatement()
                elif keyword == 'import':
                    return self._import_statement()
                elif keyword == 'try':
                    return self._try_statement()
                elif keyword == 'throw':
                    return self._throw_statement()
                elif keyword == 'class':
                    return self._class_declaration()
            
            # Expression statement or assignment
            expr = self._expression()
            
            # Check for assignment
            if self._match(TokenType.ASSIGN):
                value = self._expression()
                return Assignment(expr, value)
            
            return ExpressionStatement(expr)
        
        except ParseError:
            self._synchronize()
            return None
    
    def _variable_declaration(self, is_const: bool) -> VariableDeclaration:
        """Parse variable declaration"""
        name = self._consume(TokenType.IDENTIFIER, "Expected variable name").value
        
        value = None
        if self._match(TokenType.ASSIGN):
            value = self._expression()
        
        return VariableDeclaration(name, value, is_const)
    
    def _function_declaration(self) -> FunctionDeclaration:
        """Parse function declaration"""
        name = self._consume(TokenType.IDENTIFIER, "Expected function name").value
        
        self._consume(TokenType.LPAREN, "Expected '(' after function name")
        
        parameters = []
        if not self._check(TokenType.RPAREN):
            parameters.append(self._consume(TokenType.IDENTIFIER, "Expected parameter name").value)
            while self._match(TokenType.COMMA):
                parameters.append(self._consume(TokenType.IDENTIFIER, "Expected parameter name").value)
        
        self._consume(TokenType.RPAREN, "Expected ')' after parameters")
        self._consume(TokenType.LBRACE, "Expected '{' before function body")
        
        body = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            if self._peek().type == TokenType.NEWLINE:
                self._advance()
                continue
            stmt = self._statement()
            if stmt:
                body.append(stmt)
        
        self._consume(TokenType.RBRACE, "Expected '}' after function body")
        
        return FunctionDeclaration(name, parameters, body)
    
    def _return_statement(self) -> ReturnStatement:
        """Parse return statement"""
        value = None
        if not self._check(TokenType.NEWLINE) and not self._is_at_end():
            value = self._expression()
        return ReturnStatement(value)
    
    def _if_statement(self) -> IfStatement:
        """Parse if statement"""
        self._consume(TokenType.LPAREN, "Expected '(' after 'if'")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "Expected ')' after if condition")
        
        self._consume(TokenType.LBRACE, "Expected '{' after if condition")
        then_branch = self._block()
        self._consume(TokenType.RBRACE, "Expected '}' after if body")
        
        else_branch = None
        if self._match(TokenType.KEYWORD) and self._previous().value == 'else':
            self._consume(TokenType.LBRACE, "Expected '{' after 'else'")
            else_branch = self._block()
            self._consume(TokenType.RBRACE, "Expected '}' after else body")
        
        return IfStatement(condition, then_branch, else_branch)
    
    def _while_statement(self) -> WhileStatement:
        """Parse while statement"""
        self._consume(TokenType.LPAREN, "Expected '(' after 'while'")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "Expected ')' after while condition")
        
        self._consume(TokenType.LBRACE, "Expected '{' after while condition")
        body = self._block()
        self._consume(TokenType.RBRACE, "Expected '}' after while body")
        
        return WhileStatement(condition, body)
    
    def _for_statement(self) -> ForStatement:
        """Parse for statement"""
        self._consume(TokenType.LPAREN, "Expected '(' after 'for'")
        variable = self._consume(TokenType.IDENTIFIER, "Expected variable name").value
        self._consume(TokenType.KEYWORD, "Expected 'in'")
        iterable = self._expression()
        self._consume(TokenType.RPAREN, "Expected ')' after for clause")
        
        self._consume(TokenType.LBRACE, "Expected '{' after for clause")
        body = self._block()
        self._consume(TokenType.RBRACE, "Expected '}' after for body")
        
        return ForStatement(variable, iterable, body)
    
    def _import_statement(self) -> ImportStatement:
        """Parse import statement"""
        module = self._consume(TokenType.IDENTIFIER, "Expected module name").value
        
        alias = None
        items = None
        
        if self._match(TokenType.KEYWORD) and self._previous().value == 'as':
            alias = self._consume(TokenType.IDENTIFIER, "Expected alias name").value
        
        return ImportStatement(module, alias, items)
    
    def _try_statement(self) -> TryStatement:
        """Parse try statement"""
        self._consume(TokenType.LBRACE, "Expected '{' after 'try'")
        try_block = self._block()
        self._consume(TokenType.RBRACE, "Expected '}' after try block")
        
        catch_variable = None
        catch_block = None
        finally_block = None
        
        if self._match(TokenType.KEYWORD) and self._previous().value == 'catch':
            self._consume(TokenType.LPAREN, "Expected '(' after 'catch'")
            catch_variable = self._consume(TokenType.IDENTIFIER, "Expected variable name").value
            self._consume(TokenType.RPAREN, "Expected ')' after catch variable")
            self._consume(TokenType.LBRACE, "Expected '{' after catch clause")
            catch_block = self._block()
            self._consume(TokenType.RBRACE, "Expected '}' after catch block")
        
        if self._match(TokenType.KEYWORD) and self._previous().value == 'finally':
            self._consume(TokenType.LBRACE, "Expected '{' after 'finally'")
            finally_block = self._block()
            self._consume(TokenType.RBRACE, "Expected '}' after finally block")
        
        return TryStatement(try_block, catch_variable, catch_block, finally_block)
    
    def _throw_statement(self) -> ThrowStatement:
        """Parse throw statement"""
        value = self._expression()
        return ThrowStatement(value)
    
    def _class_declaration(self) -> ClassDeclaration:
        """Parse class declaration"""
        name = self._consume(TokenType.IDENTIFIER, "Expected class name").value
        
        superclass = None
        if self._match(TokenType.KEYWORD) and self._previous().value == 'extends':
            superclass = self._consume(TokenType.IDENTIFIER, "Expected superclass name").value
        
        self._consume(TokenType.LBRACE, "Expected '{' after class name")
        
        methods = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            if self._peek().type == TokenType.NEWLINE:
                self._advance()
                continue
            if self._match(TokenType.KEYWORD) and self._previous().value == 'func':
                methods.append(self._function_declaration())
        
        self._consume(TokenType.RBRACE, "Expected '}' after class body")
        
        return ClassDeclaration(name, superclass, methods)
    
    def _block(self) -> List[Statement]:
        """Parse a block of statements"""
        statements = []
        
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            if self._peek().type == TokenType.NEWLINE:
                self._advance()
                continue
            stmt = self._statement()
            if stmt:
                statements.append(stmt)
        
        return statements
    
    def _expression(self) -> Expression:
        """Parse an expression"""
        return self._logical_or()
    
    def _logical_or(self) -> Expression:
        """Parse logical OR expression"""
        expr = self._logical_and()
        
        while self._match(TokenType.OR):
            operator = self._previous().value
            right = self._logical_and()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _logical_and(self) -> Expression:
        """Parse logical AND expression"""
        expr = self._equality()
        
        while self._match(TokenType.AND):
            operator = self._previous().value
            right = self._equality()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _equality(self) -> Expression:
        """Parse equality expression"""
        expr = self._comparison()
        
        while self._match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self._previous().value
            right = self._comparison()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _comparison(self) -> Expression:
        """Parse comparison expression"""
        expr = self._term()
        
        while self._match(TokenType.GREATER_THAN, TokenType.GREATER_EQUAL, 
                          TokenType.LESS_THAN, TokenType.LESS_EQUAL):
            operator = self._previous().value
            right = self._term()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _term(self) -> Expression:
        """Parse addition and subtraction"""
        expr = self._factor()
        
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous().value
            right = self._factor()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _factor(self) -> Expression:
        """Parse multiplication, division, and modulo"""
        expr = self._power()
        
        while self._match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self._previous().value
            right = self._power()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _power(self) -> Expression:
        """Parse power expression"""
        expr = self._unary()
        
        if self._match(TokenType.POWER):
            operator = self._previous().value
            right = self._power()  # Right associative
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def _unary(self) -> Expression:
        """Parse unary expression"""
        if self._match(TokenType.NOT, TokenType.MINUS):
            operator = self._previous().value
            right = self._unary()
            return UnaryOperation(operator, right)
        
        return self._call()
    
    def _call(self) -> Expression:
        """Parse function calls and member access"""
        expr = self._primary()
        
        while True:
            if self._match(TokenType.LPAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                name = self._consume(TokenType.IDENTIFIER, "Expected property name after '.'").value
                expr = MemberAccess(expr, name)
            elif self._match(TokenType.LBRACKET):
                index = self._expression()
                self._consume(TokenType.RBRACKET, "Expected ']' after index")
                expr = IndexAccess(expr, index)
            else:
                break
        
        return expr
    
    def _finish_call(self, callee: Expression) -> FunctionCall:
        """Parse function call arguments"""
        arguments = []
        
        if not self._check(TokenType.RPAREN):
            arguments.append(self._expression())
            while self._match(TokenType.COMMA):
                arguments.append(self._expression())
        
        self._consume(TokenType.RPAREN, "Expected ')' after arguments")
        return FunctionCall(callee, arguments)
    
    def _primary(self) -> Expression:
        """Parse primary expressions"""
        if self._match(TokenType.BOOLEAN):
            return BooleanLiteral(self._previous().value == 'true')
        
        if self._match(TokenType.NULL):
            return NullLiteral()
        
        if self._match(TokenType.NUMBER):
            value = self._previous().value
            return NumberLiteral(float(value))
        
        if self._match(TokenType.STRING):
            value = self._previous().value[1:-1]  # Remove quotes
            return StringLiteral(value)
        
        if self._match(TokenType.IDENTIFIER):
            return Identifier(self._previous().value)
        
        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        if self._match(TokenType.LBRACKET):
            elements = []
            if not self._check(TokenType.RBRACKET):
                elements.append(self._expression())
                while self._match(TokenType.COMMA):
                    elements.append(self._expression())
            self._consume(TokenType.RBRACKET, "Expected ']' after array elements")
            return ArrayLiteral(elements)
        
        if self._match(TokenType.LBRACE):
            properties = {}
            if not self._check(TokenType.RBRACE):
                key = self._consume(TokenType.IDENTIFIER, "Expected property name").value
                self._consume(TokenType.COLON, "Expected ':' after property name")
                value = self._expression()
                properties[key] = value
                
                while self._match(TokenType.COMMA):
                    key = self._consume(TokenType.IDENTIFIER, "Expected property name").value
                    self._consume(TokenType.COLON, "Expected ':' after property name")
                    value = self._expression()
                    properties[key] = value
            
            self._consume(TokenType.RBRACE, "Expected '}' after object properties")
            return ObjectLiteral(properties)
        
        raise ParseError(f"Unexpected token: {self._peek().value}")
    
    # Helper methods
    def _match(self, *types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _check(self, token_type: TokenType) -> bool:
        """Check if current token is of given type"""
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _advance(self) -> Token:
        """Consume current token and return it"""
        if not self._is_at_end():
            self.current += 1
        return self._previous()
    
    def _is_at_end(self) -> bool:
        """Check if we're at the end of tokens"""
        return self._peek().type == TokenType.EOF
    
    def _peek(self) -> Token:
        """Return current token without advancing"""
        return self.tokens[self.current]
    
    def _previous(self) -> Token:
        """Return previous token"""
        return self.tokens[self.current - 1]
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """Consume token of expected type or raise error"""
        if self._check(token_type):
            return self._advance()
        
        current_token = self._peek()
        raise ParseError(f"{message}. Got {current_token.type.value} at line {current_token.line}")
    
    def _synchronize(self):
        """Recover from parse error"""
        self._advance()
        
        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return
            
            if self._peek().type == TokenType.KEYWORD:
                keyword = self._peek().value
                if keyword in ('class', 'func', 'var', 'for', 'if', 'while', 'return'):
                    return
            
            self._advance()
