from __future__ import annotations

import ast
import operator


ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression such as '12 * (4 + 3)'."""
    try:
        result = _eval_math(ast.parse(expression, mode="eval").body)
    except Exception as exc:
        return f"Could not calculate that expression: {exc}"

    return str(result)


def _eval_math(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        left = _eval_math(node.left)
        right = _eval_math(node.right)
        return ALLOWED_OPERATORS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[type(node.op)](_eval_math(node.operand))

    raise ValueError("only basic arithmetic is allowed")

