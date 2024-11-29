from r_token import Token
from r_expression import ExpressionVisitor, Expression, Variable, Assign
from r_statement import (StatementVisitor, BlockStatement, Statement, VarStatement, FunctionStatement,
                         ExpressionStatement, IfStatement, PrintStatement)
from r_parser import Parser
from collections import deque


class Resolver(ExpressionVisitor, StatementVisitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = deque()

    def resolve(self, statements: list[Statement | Expression]):
        """
        For each statement, it applies the visitor to the given syntax tree node
        """
        for statement in statements:
            statement.visit(self)

    def visitBlockStatement(self, block: BlockStatement):
        self.beginScope()
        self.resolve(block.block)
        self.endScope()
        return None

    def visitExpressionStatement(self, expression: ExpressionStatement):
        self.resolve([expression.expression])
        return None

    def visitFunctionStatement(self, function: FunctionStatement):
        self.declare(function.name)
        self.define(function.name)

        self.resolveFunction(function)
        return None

    def visitIfStatement(self, if_statement: IfStatement):
        self.resolve([if_statement.condition])
        self.resolve([if_statement.then_branch])
        if if_statement.else_branch is not None:
            self.resolve([if_statement.else_branch])

        return None

    def visitPrintStatement(self, print_statement: PrintStatement):
        self.resolve([print_statement.expression])
        return None

    def visitVarStatement(self, variable: VarStatement):
        self.declare(variable.name)
        if variable.initializer is not None:
            self.resolve(variable.initializer)

        self.define(variable.name)
        return None

    def visitAssign(self, assign: Assign):
        self.resolve([assign.value])
        self.resolveLocal(assign, assign.name)
        return None

    def visitVariable(self, variable: Variable):
        if (len(self.scopes) != 0) and (self.scopes[-1][variable.name.lexeme] is False):
            Parser.error(variable.name, "Can't read variable in its own initializer.")

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
