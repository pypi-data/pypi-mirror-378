"""
math utilities for fuero
provides mathematical functions and constants
"""

import math
import random
import statistics
from typing import List, Union


class Math:
    """mathematical utilities and functions"""
    
    def __init__(self):
        # Mathematical constants
        self.PI = math.pi
        self.E = math.e
        self.TAU = math.tau
        self.INF = math.inf
        self.NAN = math.nan
    
    # Basic operations
    def abs(self, x: Union[int, float]) -> Union[int, float]:
        """Return absolute value"""
        return abs(x)
    
    def ceil(self, x: float) -> int:
        """Return ceiling of x"""
        return math.ceil(x)
    
    def floor(self, x: float) -> int:
        """Return floor of x"""
        return math.floor(x)
    
    def round(self, x: float, digits: int = 0) -> float:
        """Round to given number of digits"""
        return round(x, digits)
    
    def trunc(self, x: float) -> int:
        """Return truncated integer part"""
        return math.trunc(x)
    
    # Power and logarithmic functions
    def pow(self, x: float, y: float) -> float:
        """Return x raised to power y"""
        return math.pow(x, y)
    
    def sqrt(self, x: float) -> float:
        """Return square root"""
        return math.sqrt(x)
    
    def cbrt(self, x: float) -> float:
        """Return cube root"""
        return x ** (1/3)
    
    def exp(self, x: float) -> float:
        """Return e raised to power x"""
        return math.exp(x)
    
    def log(self, x: float, base: float = math.e) -> float:
        """Return logarithm of x to given base"""
        return math.log(x, base)
    
    def log10(self, x: float) -> float:
        """Return base-10 logarithm"""
        return math.log10(x)
    
    def log2(self, x: float) -> float:
        """Return base-2 logarithm"""
        return math.log2(x)
    
    # Trigonometric functions
    def sin(self, x: float) -> float:
        """Return sine of x (in radians)"""
        return math.sin(x)
    
    def cos(self, x: float) -> float:
        """Return cosine of x (in radians)"""
        return math.cos(x)
    
    def tan(self, x: float) -> float:
        """Return tangent of x (in radians)"""
        return math.tan(x)
    
    def asin(self, x: float) -> float:
        """Return arc sine of x"""
        return math.asin(x)
    
    def acos(self, x: float) -> float:
        """Return arc cosine of x"""
        return math.acos(x)
    
    def atan(self, x: float) -> float:
        """Return arc tangent of x"""
        return math.atan(x)
    
    def atan2(self, y: float, x: float) -> float:
        """Return atan(y/x) in correct quadrant"""
        return math.atan2(y, x)
    
    # Hyperbolic functions
    def sinh(self, x: float) -> float:
        """Return hyperbolic sine"""
        return math.sinh(x)
    
    def cosh(self, x: float) -> float:
        """Return hyperbolic cosine"""
        return math.cosh(x)
    
    def tanh(self, x: float) -> float:
        """Return hyperbolic tangent"""
        return math.tanh(x)
    
    # Angle conversion
    def degrees(self, x: float) -> float:
        """Convert radians to degrees"""
        return math.degrees(x)
    
    def radians(self, x: float) -> float:
        """Convert degrees to radians"""
        return math.radians(x)
    
    # Utility functions
    def gcd(self, a: int, b: int) -> int:
        """Return greatest common divisor"""
        return math.gcd(a, b)
    
    def lcm(self, a: int, b: int) -> int:
        """Return least common multiple"""
        return abs(a * b) // math.gcd(a, b)
    
    def factorial(self, n: int) -> int:
        """Return factorial of n"""
        return math.factorial(n)
    
    def is_prime(self, n: int) -> bool:
        """Check if number is prime"""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    def fibonacci(self, n: int) -> int:
        """Return nth Fibonacci number"""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    
    # Random number generation
    def random(self) -> float:
        """Return random float between 0 and 1"""
        return random.random()
    
    def randint(self, a: int, b: int) -> int:
        """Return random integer between a and b (inclusive)"""
        return random.randint(a, b)
    
    def uniform(self, a: float, b: float) -> float:
        """Return random float between a and b"""
        return random.uniform(a, b)
    
    def choice(self, seq: List) -> any:
        """Return random element from sequence"""
        return random.choice(seq)
    
    def shuffle(self, seq: List) -> List:
        """Shuffle sequence in place and return it"""
        random.shuffle(seq)
        return seq
    
    def sample(self, population: List, k: int) -> List:
        """Return k random elements from population"""
        return random.sample(population, k)
    
    # Statistical functions
    def mean(self, data: List[Union[int, float]]) -> float:
        """Return arithmetic mean"""
        return statistics.mean(data)
    
    def median(self, data: List[Union[int, float]]) -> float:
        """Return median value"""
        return statistics.median(data)
    
    def mode(self, data: List) -> any:
        """Return most common value"""
        return statistics.mode(data)
    
    def stdev(self, data: List[Union[int, float]]) -> float:
        """Return standard deviation"""
        return statistics.stdev(data)
    
    def variance(self, data: List[Union[int, float]]) -> float:
        """Return variance"""
        return statistics.variance(data)
    
    def min(self, *args) -> Union[int, float]:
        """Return minimum value"""
        if len(args) == 1 and hasattr(args[0], '__iter__'):
            return min(args[0])
        return min(args)
    
    def max(self, *args) -> Union[int, float]:
        """Return maximum value"""
        if len(args) == 1 and hasattr(args[0], '__iter__'):
            return max(args[0])
        return max(args)
    
    def sum(self, iterable) -> Union[int, float]:
        """Return sum of all elements"""
        return sum(iterable)
    
    # Advanced mathematical functions
    def gamma(self, x: float) -> float:
        """Return gamma function"""
        return math.gamma(x)
    
    def lgamma(self, x: float) -> float:
        """Return natural log of gamma function"""
        return math.lgamma(x)
    
    def erf(self, x: float) -> float:
        """Return error function"""
        return math.erf(x)
    
    def erfc(self, x: float) -> float:
        """Return complementary error function"""
        return math.erfc(x)
