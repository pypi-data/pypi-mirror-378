"""
abstract syntax tree (ast) nodes for the fuero programming language
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict
from dataclasses import dataclass


class ASTNode(ABC):
    """base class for all ast nodes"""
    pass


class Expression(ASTNode):
    """base class for all expressions"""
    pass


class Statement(ASTNode):
    """base class for all statements"""
    pass


# Literals
@dataclass
class NumberLiteral(Expression):
    value: float


@dataclass
class StringLiteral(Expression):
    value: str


@dataclass
class BooleanLiteral(Expression):
    value: bool


@dataclass
class NullLiteral(Expression):
    pass


@dataclass
class Identifier(Expression):
    name: str


# Binary Operations
@dataclass
class BinaryOperation(Expression):
    left: Expression
    operator: str
    right: Expression


# Unary Operations
@dataclass
class UnaryOperation(Expression):
    operator: str
    operand: Expression


# Function Call
@dataclass
class FunctionCall(Expression):
    function: Expression
    arguments: List[Expression]


# Member Access
@dataclass
class MemberAccess(Expression):
    object: Expression
    member: str


# Array/Object Access
@dataclass
class IndexAccess(Expression):
    object: Expression
    index: Expression


# Array Literal
@dataclass
class ArrayLiteral(Expression):
    elements: List[Expression]


# Object Literal
@dataclass
class ObjectLiteral(Expression):
    properties: Dict[str, Expression]


# Statements
@dataclass
class ExpressionStatement(Statement):
    expression: Expression


@dataclass
class VariableDeclaration(Statement):
    name: str
    value: Optional[Expression]
    is_const: bool = False


@dataclass
class Assignment(Statement):
    target: Expression
    value: Expression


@dataclass
class FunctionDeclaration(Statement):
    name: str
    parameters: List[str]
    body: List[Statement]


@dataclass
class ReturnStatement(Statement):
    value: Optional[Expression]


@dataclass
class IfStatement(Statement):
    condition: Expression
    then_branch: List[Statement]
    else_branch: Optional[List[Statement]] = None


@dataclass
class WhileStatement(Statement):
    condition: Expression
    body: List[Statement]


@dataclass
class ForStatement(Statement):
    variable: str
    iterable: Expression
    body: List[Statement]


@dataclass
class BreakStatement(Statement):
    pass


@dataclass
class ContinueStatement(Statement):
    pass


@dataclass
class ImportStatement(Statement):
    module: str
    alias: Optional[str] = None
    items: Optional[List[str]] = None


@dataclass
class TryStatement(Statement):
    try_block: List[Statement]
    catch_variable: Optional[str]
    catch_block: Optional[List[Statement]]
    finally_block: Optional[List[Statement]]


@dataclass
class ThrowStatement(Statement):
    value: Expression


@dataclass
class ClassDeclaration(Statement):
    name: str
    superclass: Optional[str]
    methods: List[FunctionDeclaration]


# Program (root node)
@dataclass
class Program(ASTNode):
    statements: List[Statement]
