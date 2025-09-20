"""
interpreter for fuero language
executes the abstract syntax tree (ast)
"""

import sys
from typing import Any, Dict, List, Optional, Callable
from .ast_nodes import *
from ..stdlib import *


class RuntimeError(Exception):
    """runtime error in fuero execution"""
    pass


class Environment:
    """environment for variable and function storage"""
    
    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}
    
    def define(self, name: str, value: Any):
        """Define a variable in this environment"""
        self.variables[name] = value
    
    def get(self, name: str) -> Any:
        """Get a variable value"""
        if name in self.variables:
            return self.variables[name]
        
        if self.parent:
            return self.parent.get(name)
        
        raise RuntimeError(f"undefined variable '{name}'")
    
    def set(self, name: str, value: Any):
        """Set a variable value"""
        if name in self.variables:
            self.variables[name] = value
            return
        
        if self.parent:
            self.parent.set(name, value)
            return
        
        raise RuntimeError(f"undefined variable '{name}'")


class Function:
    """represents a fuero function"""
    
    def __init__(self, declaration: FunctionDeclaration, closure: Environment):
        self.declaration = declaration
        self.closure = closure
    
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        """Call the function"""
        if len(arguments) != len(self.declaration.parameters):
            raise RuntimeError(
                f"expected {len(self.declaration.parameters)} arguments but got {len(arguments)}"
            )
        
        # Create new environment for function execution
        environment = Environment(self.closure)
        
        # Bind parameters
        for i, param in enumerate(self.declaration.parameters):
            environment.define(param, arguments[i])
        
        try:
            interpreter._execute_block(self.declaration.body, environment)
        except ReturnValue as return_value:
            return return_value.value
        
        return None


class ReturnValue(Exception):
    """exception used to implement return statements"""
    
    def __init__(self, value: Any):
        self.value = value


class Interpreter:
    """interpreter for the fuero programming language"""
    
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.output = []
        
        # Define built-in functions
        self._define_builtins()
    
    def interpret(self, program: Program) -> Any:
        """Interpret a program"""
        try:
            for statement in program.statements:
                self._execute(statement)
        except RuntimeError as error:
            print(f"runtime error: {error}", file=sys.stderr)
            return None
        
        return self.output
    
    def _define_builtins(self):
        """define built-in functions and modules"""
        # built-in functions
        self.globals.define("print", self._builtin_print)
        self.globals.define("input", self._builtin_input)
        self.globals.define("len", self._builtin_len)
        self.globals.define("type", self._builtin_type)
        self.globals.define("str", self._builtin_str)
        self.globals.define("int", self._builtin_int)
        self.globals.define("float", self._builtin_float)
        self.globals.define("bool", self._builtin_bool)
        
        # standard library modules
        self.globals.define("math", Math())
        self.globals.define("string", String())
        self.globals.define("json", Json())
        self.globals.define("http", Http())
        self.globals.define("database", Database())
        self.globals.define("crypto", Crypto())
        self.globals.define("ai", Ai())
    
    def _execute(self, statement: Statement):
        """Execute a statement"""
        if isinstance(statement, ExpressionStatement):
            self._evaluate(statement.expression)
        
        elif isinstance(statement, VariableDeclaration):
            value = None
            if statement.value:
                value = self._evaluate(statement.value)
            self.environment.define(statement.name, value)
        
        elif isinstance(statement, Assignment):
            value = self._evaluate(statement.value)
            if isinstance(statement.target, Identifier):
                self.environment.set(statement.target.name, value)
            else:
                raise RuntimeError("invalid assignment target")
        
        elif isinstance(statement, FunctionDeclaration):
            function = Function(statement, self.environment)
            self.environment.define(statement.name, function)
        
        elif isinstance(statement, ReturnStatement):
            value = None
            if statement.value:
                value = self._evaluate(statement.value)
            raise ReturnValue(value)
        
        elif isinstance(statement, IfStatement):
            condition = self._evaluate(statement.condition)
            if self._is_truthy(condition):
                self._execute_block(statement.then_branch, Environment(self.environment))
            elif statement.else_branch:
                self._execute_block(statement.else_branch, Environment(self.environment))
        
        elif isinstance(statement, WhileStatement):
            while self._is_truthy(self._evaluate(statement.condition)):
                try:
                    self._execute_block(statement.body, Environment(self.environment))
                except BreakException:
                    break
                except ContinueException:
                    continue
        
        elif isinstance(statement, ForStatement):
            iterable = self._evaluate(statement.iterable)
            if not hasattr(iterable, '__iter__'):
                raise RuntimeError("object is not iterable")
            
            for item in iterable:
                try:
                    loop_env = Environment(self.environment)
                    loop_env.define(statement.variable, item)
                    self._execute_block(statement.body, loop_env)
                except BreakException:
                    break
                except ContinueException:
                    continue
        
        elif isinstance(statement, BreakStatement):
            raise BreakException()
        
        elif isinstance(statement, ContinueStatement):
            raise ContinueException()
        
        elif isinstance(statement, ImportStatement):
            # Simple import handling - in a real implementation, this would load modules
            pass
        
        else:
            raise RuntimeError(f"unknown statement type: {type(statement)}")
    
    def _execute_block(self, statements: List[Statement], environment: Environment):
        """Execute a block of statements in a new environment"""
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self._execute(statement)
        finally:
            self.environment = previous
    
    def _evaluate(self, expression: Expression) -> Any:
        """Evaluate an expression"""
        if isinstance(expression, NumberLiteral):
            return expression.value
        
        elif isinstance(expression, StringLiteral):
            return expression.value
        
        elif isinstance(expression, BooleanLiteral):
            return expression.value
        
        elif isinstance(expression, NullLiteral):
            return None
        
        elif isinstance(expression, Identifier):
            return self.environment.get(expression.name)
        
        elif isinstance(expression, BinaryOperation):
            left = self._evaluate(expression.left)
            right = self._evaluate(expression.right)
            return self._apply_binary_operator(expression.operator, left, right)
        
        elif isinstance(expression, UnaryOperation):
            operand = self._evaluate(expression.operand)
            return self._apply_unary_operator(expression.operator, operand)
        
        elif isinstance(expression, FunctionCall):
            function = self._evaluate(expression.function)
            arguments = [self._evaluate(arg) for arg in expression.arguments]
            
            if isinstance(function, Function):
                return function.call(self, arguments)
            elif callable(function):
                return function(*arguments)
            else:
                raise RuntimeError("object is not callable")
        
        elif isinstance(expression, MemberAccess):
            obj = self._evaluate(expression.object)
            if hasattr(obj, expression.member):
                return getattr(obj, expression.member)
            else:
                raise RuntimeError(f"object has no member '{expression.member}'")
        
        elif isinstance(expression, IndexAccess):
            obj = self._evaluate(expression.object)
            index = self._evaluate(expression.index)
            try:
                return obj[index]
            except (KeyError, IndexError, TypeError):
                raise RuntimeError("invalid index access")
        
        elif isinstance(expression, ArrayLiteral):
            return [self._evaluate(element) for element in expression.elements]
        
        elif isinstance(expression, ObjectLiteral):
            obj = {}
            for key, value in expression.properties.items():
                obj[key] = self._evaluate(value)
            return obj
        
        else:
            raise RuntimeError(f"unknown expression type: {type(expression)}")
    
    def _apply_binary_operator(self, operator: str, left: Any, right: Any) -> Any:
        """Apply binary operator"""
        if operator == '+':
            return left + right
        elif operator == '-':
            return left - right
        elif operator == '*':
            return left * right
        elif operator == '/':
            if right == 0:
                raise RuntimeError("division by zero")
            return left / right
        elif operator == '%':
            return left % right
        elif operator == '**':
            return left ** right
        elif operator == '==':
            return left == right
        elif operator == '!=':
            return left != right
        elif operator == '<':
            return left < right
        elif operator == '>':
            return left > right
        elif operator == '<=':
            return left <= right
        elif operator == '>=':
            return left >= right
        elif operator == '&&':
            return self._is_truthy(left) and self._is_truthy(right)
        elif operator == '||':
            return self._is_truthy(left) or self._is_truthy(right)
        else:
            raise RuntimeError(f"unknown binary operator: {operator}")
    
    def _apply_unary_operator(self, operator: str, operand: Any) -> Any:
        """Apply unary operator"""
        if operator == '-':
            return -operand
        elif operator == '!':
            return not self._is_truthy(operand)
        else:
            raise RuntimeError(f"unknown unary operator: {operator}")
    
    def _is_truthy(self, value: Any) -> bool:
        """Determine if a value is truthy"""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True
    
    # Built-in functions
    def _builtin_print(self, *args):
        """built-in print function"""
        output = ' '.join(str(arg) for arg in args)
        print(output)
        self.output.append(output)
        return None
    
    def _builtin_input(self, prompt=""):
        """built-in input function"""
        return input(prompt)
    
    def _builtin_len(self, obj):
        """built-in len function"""
        return len(obj)
    
    def _builtin_type(self, obj):
        """built-in type function"""
        return type(obj).__name__
    
    def _builtin_str(self, obj):
        """built-in str function"""
        return str(obj)
    
    def _builtin_int(self, obj):
        """built-in int function"""
        return int(obj)
    
    def _builtin_float(self, obj):
        """built-in float function"""
        return float(obj)
    
    def _builtin_bool(self, obj):
        """built-in bool function"""
        return bool(obj)


class BreakException(Exception):
    """exception for break statements"""
    pass


class ContinueException(Exception):
    """exception for continue statements"""
    pass
