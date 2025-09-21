from math import gcd

class Fraction:
    """
    A human-friendly Fraction class that supports basic arithmetic
    and works with string-style inputs like '4/5' or '2'.
    """

    def __init__(self, numerator, denominator=1):
        # Allow initialization from strings like "3/4"
        if isinstance(numerator, str):
            if "/" in numerator:
                num, den = numerator.split("/")
                numerator, denominator = int(num.strip()), int(den.strip())
            else:
                numerator, denominator = int(numerator.strip()), 1

        # Ensure integers
        if not isinstance(numerator, int) or not isinstance(denominator, int):
            raise TypeError("Numerator and denominator must be integers")

        if denominator == 0:
            raise ValueError("Denominator cannot be zero")

        # Normalize signs: keep denominator positive
        if denominator < 0:
            numerator, denominator = -numerator, -denominator

        # Simplify fraction
        g = gcd(numerator, denominator)
        self.n = numerator // g
        self.d = denominator // g

    # String representation
    def __str__(self):
        return f"{self.n}/{self.d}"

    def __repr__(self):
        return f"Fraction({self.n}, {self.d})"

    # Basic operations
    def __add__(self, other):
        other = self._ensure_fraction(other)
        return Fraction(self.n * other.d + other.n * self.d, self.d * other.d)

    def __sub__(self, other):
        other = self._ensure_fraction(other)
        return Fraction(self.n * other.d - other.n * self.d, self.d * other.d)

    def __mul__(self, other):
        other = self._ensure_fraction(other)
        return Fraction(self.n * other.n, self.d * other.d)

    def __truediv__(self, other):
        other = self._ensure_fraction(other)
        if other.n == 0:
            raise ZeroDivisionError("Cannot divide by zero fraction")
        return Fraction(self.n * other.d, self.d * other.n)

    # Comparison
    def __eq__(self, other):
        other = self._ensure_fraction(other)
        return self.n == other.n and self.d == other.d

    def __lt__(self, other):
        other = self._ensure_fraction(other)
        return self.n * other.d < other.n * self.d

    def __le__(self, other):
        return self == other or self < other

    # Helper: convert input to Fraction
    @staticmethod
    def _ensure_fraction(value):
        if isinstance(value, Fraction):
            return value
        if isinstance(value, str):
            return Fraction(value)
        if isinstance(value, int):
            return Fraction(value, 1)
        raise TypeError("Unsupported type for Fraction operation")

    # Allow humanized evaluation of strings like "4/5 - 3/5"
    @staticmethod
    def evaluate(expression: str):
        """
        Evaluate a string expression with fractions.
        Example: "4/5 - 3/5" -> Fraction(1,5)
        """
        # Replace fractions with Fraction("x/y") calls
        tokens = expression.replace("*", " * ").replace("/", " / ").replace("+", " + ").replace("-", " - ").split()
        processed = []
        for t in tokens:
            if "/" in t or t.isdigit():  # looks like a fraction or integer
                processed.append(f'Fraction("{t}")')
            else:
                processed.append(t)

        python_expr = " ".join(processed)
        return eval(python_expr, {"Fraction": Fraction})
