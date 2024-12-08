import abc
from r_expression import Expression
from r_token import Token


class Statement(abc.ABC):
    @abc.abstractmethod
    def visit(self, visit: "StatementVisitor"):
        """
        An abstract class method of what it means to visit a statement
        """
        pass


class ExpressionStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def visit(self, visitor: "StatementVisitor"):
        return visitor.visitExpressionStatement(self)


class FunctionStatement(Statement):
    def __init__(self, name: Token, parameters: list[Token], body: list[Statement]):
        self.name = name
        self.params = parameters
        self.body = body

    def visit(self, visitor: "StatementVisitor"):
        return visitor.visitFunctionStatement(self)


class IfStatement(Statement):
    def __init__(self, condition: Expression, then_branch: Statement, else_branch: Statement):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def visit(self, visitor: "StatementVisitor"):
        return visitor.visitIfStatement(self)


class PrintStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def visit(self, visitor: "StatementVisitor"):
        return visitor.visitPrintStatement(self)


class ReturnStatement(Statement):
    def __init__(self, keyword: Token, value: Expression):
        self.keyword = keyword
        self.value = value

    def visit(self, visitor: "StatementVisitor"):
        return visitor.visitReturnStatement(self)


class VarStatement(Statement):
    def __init__(self, name: Token, initializer):
        self.name = name
        self.initializer = initializer

    def visit(self, visitor: "StatementVisitor"):
        return visitor.visitVarStatement(self)


class WhileStatement(Statement):
    def __init__(self, condition: Expression, body: Statement):
        self.condition = condition
        self.body = body

    def visit(self, visitor: "StatementVisitor"):
        return visitor.visitWhileStatement(self)


class BlockStatement(Statement):
    def __init__(self, block: list[Statement]):
        self.block = block

    def visit(self, visitor: "StatementVisitor"):
        return visitor.visitBlockStatement(self)


class ClassStatement(Statement):
    def __init__(self, name: Token, methods: list[FunctionStatement]):
        self.name = name
        self.methods = methods

    def visit(self, visitor: "StatementVisitor"):
        return visitor.visitClassStatement(self)


class StatementVisitor:
    def visitExpressionStatement(self, expression: ExpressionStatement):
        pass

    def visitFunctionStatement(self, function: FunctionStatement):
        pass

    def visitIfStatement(self, expression: IfStatement):
        pass

    def visitPrintStatement(self, expression: PrintStatement):
        pass

    def visitReturnStatement(self, expression: ReturnStatement):
        pass

    def visitVarStatement(self, expression: VarStatement):
        pass

    def visitWhileStatement(self, expression: WhileStatement):
        pass

    def visitBlockStatement(self, block: BlockStatement):
        pass

    def visitClassStatement(self, class_: ClassStatement):
        pass
