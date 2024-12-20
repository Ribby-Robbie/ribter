from r_token import Token
from r_expression import ExpressionVisitor, Expression, Variable, Assign, Binary, Call, Grouping, Literal, Logical, \
    Unary, Get
from r_statement import (StatementVisitor, BlockStatement, Statement, VarStatement, FunctionStatement,
                         ExpressionStatement, IfStatement, PrintStatement, ReturnStatement, WhileStatement,
                         ClassStatement)
from r_environment import error
from collections import deque
from enum import Enum


class FunctionType(Enum):
    NONE = 0,
    FUNCTION = 1


class Resolver(ExpressionVisitor, StatementVisitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = deque()
        self.current_function = FunctionType.NONE

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

    def visitClassStatement(self, class_: ClassStatement):
        self.declare(class_.name)
        self.define(class_.name)
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

        self.resolveFunction(function, FunctionType.FUNCTION)
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
        if self.current_function == FunctionType.NONE:
            error(return_statement.keyword, "Can't return from top-level code.")

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

    def visitGet(self, get: Get):
        """
        We want to visit the get's object expression.
        Properties are looked up dynamically, so they don't really get 'resolved'.
        Property access happens in the interpreter.
        """
        self.resolveExpression(get.obj)
        return None

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
        """
        Within a certain scope, allows a specific identifier to be defined
        :param name:
        :return:
        """
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

    def resolveFunction(self, function: FunctionStatement, func_type: FunctionType):
        """
        Goes through the steps of declaring the scope of the function, declaring and defining the parameters for the
        function, and then resolving the body of the function.
        This can be nested, hence the check for where we are in enclosing vs. current functions.
        """
        # The enclosing function we are in is the current function
        enclosing_function = self.current_function
        # If there is anything else in this function, we deem if it is a function or not
        self.current_function = func_type

        self.beginScope()
        for param in function.params:
            self.declare(param)
            self.define(param)

        self.resolve(function.body)
        self.endScope()

        # Now we are out of this enclosing function, and we are back up top
        self.current_function = enclosing_function

    def resolveStatement(self, statement: Statement):
        """
        Used to visit a statement to 'resolve' it.
        Being used to figure out what kind of statement it is, and what it needs to do.
        """
        statement.visit(self)

    def resolveExpression(self, expression: Expression):
        """
        Used to visit an expression to 'resolve' it. This is basically being used to figure out what kind of expression
        it is, and what it needs to do.
        """
        expression.visit(self)
