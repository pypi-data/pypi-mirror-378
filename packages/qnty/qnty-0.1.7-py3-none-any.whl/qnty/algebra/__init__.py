from .equation import Equation
from .functions import abs_expr, cond_expr, cos, exp, ln, log10, max_expr, min_expr, sin, sqrt, tan
from .nodes import BinaryOperation, ConditionalExpression, Constant, Expression, UnaryFunction, VariableReference, wrap_operand
from .system import EquationSystem


def equation(lhs, rhs, name: str | None = None) -> Equation:
    """
    Create an equation: lhs = rhs

    This is the preferred way to create equations for Problem classes.

    Args:
        lhs: The left-hand side quantity (the variable being defined)
        rhs: The right-hand side expression
        name: Optional name for the equation

    Returns:
        Equation object that can be used in Problem classes

    Examples:
        >>> from qnty import Length
        >>> from qnty.algebra import equation
        >>> T = Length("T")
        >>> T_bar = Length("T_bar").set(0.147).inch
        >>> U_m = Dimensionless("U_m").set(0.125).dimensionless
        >>> T_eq = equation(T, T_bar * (1 - U_m))
    """
    eq_name = name or f"{lhs.name}_equation"

    # Handle DelayedExpression objects from Problem class
    if hasattr(rhs, "resolve"):
        # This is a DelayedExpression - store it as-is for later resolution
        # during problem initialization when proper context is available
        rhs_expr = rhs
    else:
        # Convert RHS to Expression if needed using wrap_operand
        rhs_expr = wrap_operand(rhs)

    return Equation(eq_name, lhs, rhs_expr)


def geq(lhs, rhs) -> BinaryOperation:
    """Create a greater-than-or-equal comparison: lhs >= rhs"""
    return BinaryOperation(">=", wrap_operand(lhs), wrap_operand(rhs))


def gt(lhs, rhs) -> BinaryOperation:
    """Create a greater-than comparison: lhs > rhs"""
    return BinaryOperation(">", wrap_operand(lhs), wrap_operand(rhs))


def leq(lhs, rhs) -> BinaryOperation:
    """Create a less-than-or-equal comparison: lhs <= rhs"""
    return BinaryOperation("<=", wrap_operand(lhs), wrap_operand(rhs))


def lt(lhs, rhs) -> BinaryOperation:
    """Create a less-than comparison: lhs < rhs"""
    return BinaryOperation("<", wrap_operand(lhs), wrap_operand(rhs))


def eq(lhs, rhs) -> BinaryOperation:
    """Create an equality comparison: lhs == rhs"""
    return BinaryOperation("==", wrap_operand(lhs), wrap_operand(rhs))


def solve(quantity, expression) -> bool:
    """
    Solve an expression for a quantity.

    This is the preferred way to solve equations - it matches the natural
    mathematical thinking: "solve this expression for this variable".

    Args:
        quantity: The Quantity to solve for (Length, Acceleration, etc.)
        expression: The expression to solve (Expression, Quantity, or numeric value)

    Returns:
        True if solving succeeded, False otherwise

    Examples:
        >>> from qnty.core import Length, Q
        >>> from qnty.algebra import solve
        >>> x = Length("x")  # Unknown length
        >>> expr = x + Q(5, "m")  # x + 5 meters
        >>> solve(x, Q(10, "m"))  # Solve for x: x + 5m = 10m, so x = 5m
        True
        >>> print(x)  # Should show "x = 5 m"
    """
    # Handle direct assignment cases
    if hasattr(expression, "value") and hasattr(expression, "dim"):
        # Expression is another Quantity
        if expression.value is not None:
            # Check dimension compatibility
            if hasattr(quantity, "dim") and quantity.dim != expression.dim:
                raise TypeError(f"Dimension mismatch: cannot assign {expression.dim} to {quantity.dim}")

            # Direct assignment
            if hasattr(quantity, "value"):
                quantity.value = expression.value
                if hasattr(quantity, "preferred") and hasattr(expression, "preferred"):
                    quantity.preferred = expression.preferred or quantity.preferred
                return True
        return False

    # Handle numeric values
    if isinstance(expression, int | float):
        if hasattr(quantity, "dim") and hasattr(quantity, "value"):
            if quantity.dim.is_dimensionless():
                quantity.value = float(expression)
                return True
            else:
                # For dimensional quantities, treat as SI units
                quantity.value = float(expression)
                return True
        return False

    # Handle Expression objects
    if isinstance(expression, Expression):
        return expression.solve_for(quantity)

    return False


# Define public API
__all__ = [
    # Core AST classes
    "Expression",
    "VariableReference",
    "Constant",
    "BinaryOperation",
    "UnaryFunction",
    "ConditionalExpression",
    # Helper functions
    "sin",
    "cos",
    "tan",
    "sqrt",
    "abs_expr",
    "ln",
    "log10",
    "exp",
    "cond_expr",
    "min_expr",
    "max_expr",
    # Utilities
    "wrap_operand",
    # Solving
    "solve",
    "equation",
    # Comparisons
    "geq",
    "gt",
    "leq",
    "lt",
    "eq",
    "Equation",
    "EquationSystem",
]
