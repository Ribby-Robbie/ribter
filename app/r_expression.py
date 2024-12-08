import abc
from r_token import Token


class Expression(abc.ABC):
    """
    Our abstract class of what an expression is
    """
    @abc.abstractmethod
    def visit(self, visit: "ExpressionVisitor"):
        """
        An abstract method of what it means to visit
        """
        pass


class Assign(Expression):
    def __init__(self, name: Token, value: Expression):
        self.name = name
        self.value = value

    def visit(self, visitor: "ExpressionVisitor"):
        return visitor.visitAssign(self)


class Literal(Expression):
    def __init__(self, value):
        self.value = value

    def visit(self, visitor: "ExpressionVisitor"):
        """
        Overrides the visit function to show what it means to visit a literal
        """
        return visitor.visitLiteral(self)


class Logical(Expression):
    def __init__(self, left: Expression, operator: Token, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def visit(self, visitor: "ExpressionVisitor"):
        return visitor.visitLogical(self)


class Unary(Expression):
    def __init__(self, operator: Token, right: Expression):
        self.operator = operator
        self.right = right

    def visit(self, visitor: "ExpressionVisitor"):
        """
        Overrides the visit function to show what it means to visit a unary
        """
        return visitor.visitUnary(self)


class Binary(Expression):
    def __init__(self, left: Expression, operator: Token, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def visit(self, visitor: "ExpressionVisitor"):
        """
        Overrides the visit function to show what it means to visit a binary
        """
        return visitor.visitBinary(self)


class Call(Expression):
    def __init__(self, callee: Expression, paren: Token, arguments: list[Expression]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def visit(self, visitor: "ExpressionVisitor"):
        return visitor.visitCall(self)


class Get(Expression):
    def __init__(self, obj: Expression, name: Token):
        self.obj = obj
        self.name = name

    def visit(self, visitor: "ExpressionVisitor"):
        return visitor.visitGet(self)


class Grouping(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def visit(self, visitor: "ExpressionVisitor"):
        """
        Overrides the visit function to show what it means to visit a grouping
        """
        return visitor.visitGrouping(self)


class Variable(Expression):
    def __init__(self, name: Token):
        self.name = name

    def visit(self, visitor: "ExpressionVisitor"):
        """
        Overrides the visit function to show what it means to visit a variable
        """
        return visitor.visitVariable(self)


class ExpressionVisitor:
    """
    An abstract class showing what it means each extension of an Expression
    """

    def visitAssign(self, assign: Assign):
        pass

    def visitLiteral(self, literal: Literal):
        pass

    def visitLogical(self, logical: Logical):
        pass

    def visitUnary(self, unary: Unary):
        pass

    def visitBinary(self, binary: Binary):
        pass

    def visitCall(self, call: Call):
        pass

    def visitGet(self, get: Get):
        pass

    def visitGrouping(self, grouping: Grouping):
        pass

    def visitVariable(self, variable: Variable):
        pass


class AstPrint(ExpressionVisitor):
    """
    Declares the extension of each Expression, as well as some helper functions to make it user readable
    """
    def parenthesize(self, name, *expressions: Expression):
        builder = f"({name}"

        for expression in expressions:
            builder += " "
            # Visits whatever type of expression it is
            builder += expression.visit(self)

        return builder + ")"

    def visitLiteral(self, literal: Literal):
        value = literal.value

        if value is None:
            return "nil"
        elif isinstance(value, bool):
            return str(value).lower()
        else:
            return str(value)

    def visitGrouping(self, grouping: Grouping):
        return self.parenthesize("group", grouping.expression)

    def visitUnary(self, unary: Unary):
        return self.parenthesize(unary.operator.lexeme, unary.right)

    def visitBinary(self, binary: Binary):
        return self.parenthesize(binary.operator.lexeme, binary.left, binary.right)

    def print(self, expression: Expression):
        return expression.visit(self)
