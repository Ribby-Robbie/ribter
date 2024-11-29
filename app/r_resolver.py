from r_token import Token
from r_expression import ExpressionVisitor, Expression, Variable, Assign, Binary, Call, Grouping, Literal, Logical, \
    Unary
from r_statement import (StatementVisitor, BlockStatement, Statement, VarStatement, FunctionStatement,
                         ExpressionStatement, IfStatement, PrintStatement, ReturnStatement, WhileStatement)
from r_environment import error
from collections import deque


class Resolver(ExpressionVisitor, StatementVisitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = deque()

    def resolve(self, statements: list[Statement]):
        """
        For each statement, it applies the visitor to the given syntax tree node
        """
        for statement in statements:
            self.resolveStatement(statement)

    def visitBlockStatement(self, block: BlockStatement):
        self.beginScope()
        self.resolve(block.block)
        self.endScope()
        return None

    def visitExpressionStatement(self, expression: ExpressionStatement):
        self.resolveExpression(expression.expression)
        return None

    def visitFunctionStatement(self, function: FunctionStatement):
        """
        Declares and defines the function under the function name, and then visits the function
        """
        self.declare(function.name)
        self.define(function.name)

        self.resolveFunction(function)
        return None

    def visitIfStatement(self, if_statement: IfStatement):
        self.resolveExpression(if_statement.condition)
        self.resolve([if_statement.then_branch])
        if if_statement.else_branch is not None:
            self.resolve([if_statement.else_branch])

        return None

    def visitPrintStatement(self, print_statement: PrintStatement):
        self.resolveExpression(print_statement.expression)
        return None

    def visitReturnStatement(self, return_statement: ReturnStatement):
        if return_statement.value is not None:
            self.resolveExpression(return_statement.value)

        return None

    def visitVarStatement(self, variable: VarStatement):
        self.declare(variable.name)
        if variable.initializer is not None:
            self.resolve([variable.initializer])

        self.define(variable.name)
        return None

    def visitWhileStatement(self, while_statement: WhileStatement):
        self.resolveExpression(while_statement.condition)
        self.resolve([while_statement.body])
        return None

    def visitAssign(self, assign: Assign):
        self.resolveExpression(assign.value)
        self.resolveLocal(assign, assign.name)
        return None

    def visitBinary(self, binary: Binary):
        """
        Resolves the left and right terms of a binary expression
        """
        self.resolveExpression(binary.left)
        self.resolveExpression(binary.right)
        return None

    def visitCall(self, call: Call):
        self.resolveExpression(call.callee)

        for argument in call.arguments:
            self.resolveExpression(argument)

    def visitGrouping(self, grouping: Grouping):
        self.resolveExpression(grouping.expression)
        return None

    def visitLiteral(self, literal: Literal):
        return None

    def visitLogical(self, logical: Logical):
        self.resolveExpression(logical.left)
        self.resolveExpression(logical.right)
        return None

    def visitUnary(self, unary: Unary):
        self.resolveExpression(unary.right)
        return None

    def visitVariable(self, variable: Variable):
        if (len(self.scopes) != 0) and (self.scopes[-1].get(variable.name.lexeme) is False):
            raise error(variable.name, "Can't read variable in its own initializer.")

        self.resolveLocal(variable, variable.name)
        return None

    def beginScope(self):
        self.scopes.append(dict())

    def endScope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if len(self.scopes) == 0:
            return

        scope = self.scopes[-1]
        if name.lexeme in scope.keys():
            raise error(name, "Already a variable with this name in this scope.")

        scope[name.lexeme] = False

    def define(self, name: Token):
        if len(self.scopes) == 0:
            return

        scope = self.scopes[-1]
        scope[name.lexeme] = True

    def resolveLocal(self, expression: Expression, name: Token):
        index = len(self.scopes) - 1
        while index >= 0:
            if name.lexeme in self.scopes[index].keys():
                self.interpreter.resolve(expression, len(self.scopes) - 1 - index)
                return

            index -= 1

    def resolveFunction(self, function: FunctionStatement):
        self.beginScope()
        for param in function.params:
            self.declare(param)
            self.define(param)

        self.resolve(function.body)
        self.endScope()

    def resolveStatement(self, statement: Statement):
        statement.visit(self)

    def resolveExpression(self, expression: Expression):
        expression.visit(self)
