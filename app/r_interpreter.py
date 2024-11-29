from r_statement import PrintStatement, VarStatement
from r_expression import Expression, ExpressionVisitor
from r_statement import (Statement, StatementVisitor, ExpressionStatement, BlockStatement, IfStatement,
                          WhileStatement, FunctionStatement, ReturnStatement)
from r_environment import Environment
from r_function import Callable, RibCallable, RibFunction, Return
import r_utils as utils
import time


class Interpreter(ExpressionVisitor, StatementVisitor):
    def __init__(self):
        # Holds a fixed pov on the outermost global perspective
        self.globals = Environment()
        # Holds the local scope environment
        self.environment = self.globals

        # Defining the clock function to the name clock
        self.globals.define("clock", RibCallable("clock", 0, lambda: float(time.time())))

    def interpret_expression(self, expression: Expression):
        try:
            value = self.evaluate(expression)
            print(utils.stringify(value))
        except utils.RunTimeError as error:
            utils.Rib.runtimeError(error.token.line, str(error))

    def interpret_statement(self, statements: list[Statement]):
        try:
            for statement in statements:
                self.execute(statement)
        except utils.RunTimeError as error:
            utils.Rib.runtimeError(error.token.line, str(error))

    # Analog to evaluate, but for statements
    def execute(self, statement: Statement):
        statement.visit(self)

    def executeBlock(self, statements, environment):
        previous = self.environment

        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visitBlockStatement(self, block: BlockStatement):
        self.executeBlock(block.block, self.environment.inner())
        return None

    # Sends the expression back into the interpreter’s visitor implementation
    def evaluate(self, expression: Expression):
        return expression.visit(self)

    def visitExpressionStatement(self, statement: ExpressionStatement):
        self.evaluate(statement.expression)
        return None

    def visitFunctionStatement(self, function_statement: FunctionStatement):
        """
        Takes the function name, and defines it to the function that the user made
        """
        function = RibFunction(function_statement, self.environment)
        self.environment.define(function_statement.name.lexeme, function)
        return None

    def visitIfStatement(self, statement: IfStatement):
        if utils.isTruthy(self.evaluate(statement.condition)):
            self.execute(statement.then_branch)
        elif statement.else_branch is not None:
            self.execute(statement.else_branch)

        return None

    def visitPrintStatement(self, statement: PrintStatement):
        value = self.evaluate(statement.expression)
        print(utils.stringify(value))
        return None

    def visitReturnStatement(self, return_statement: ReturnStatement):
        value = None
        if return_statement.value is not None:
            value = self.evaluate(return_statement.value)

        raise Return(value)

    # What the variable is actually set to
    def visitVarStatement(self, variable: VarStatement):
        value = None
        if variable.initializer is not None:
            value = self.evaluate(variable.initializer)

        # Defining to dictionary what the variable name means (i.e., the value)
        self.environment.define(variable.name.lexeme, value)
        return

    def visitWhileStatement(self, while_statement: WhileStatement):
        while utils.isTruthy(self.evaluate(while_statement.condition)):
            self.execute(while_statement.body)

        return None

    # Visiting the variable to call what it is set to
    def visitVariable(self, variable):
        # This gets the variable value from the dictionary of variables
        return self.environment.get(variable.name)

    def visitAssign(self, assign):
        """
        Assigns something to a variable
        """
        value = self.evaluate(assign.value)
        self.environment.assign(assign.name, value)
        return value

    # Convert the literal tree node into a runtime value
    def visitLiteral(self, literal):
        return literal.value

    def visitLogical(self, logical):
        """
        Visits a logical statement, tells us what to do based off of the left, right, and operator
        """
        left = self.evaluate(logical.left)

        if logical.operator.token_type == "OR":
            if utils.isTruthy(left):
                return left
        else:
            if not utils.isTruthy(left):
                return left

        # If the left-hand side is nonsensical, then it goes to the right-hand side
        return self.evaluate(logical.right)

    # Recursively evaluate that subexpression and return it.
    def visitGrouping(self, grouping):
        """
        Evaluates a grouping (shown by parentheses)
        """
        return self.evaluate(grouping.expression)

    # Evaluate subexpression first
    # Apply operator after
    # Return the result
    def visitUnary(self, unary):
        """
        Evaluates a unary expression, needs the type of unary and the expression it is applying to
        """
        right = self.evaluate(unary.right)
        operator = unary.operator.token_type

        if operator == "MINUS":
            # Ensures that right is a number
            utils.checkNumberOperand(unary.operator, right)
            return -right
        elif operator == "BANG":
            return not utils.isTruthy(right)
        else:
            return None

    def visitBinary(self, binary):
        """
        Evaluates a binary expression: addition, subtraction, division, multiplication, as well as equalities
        """
        left = self.evaluate(binary.left)
        right = self.evaluate(binary.right)
        operator = binary.operator.token_type

        if operator == "MINUS":
            utils.checkMultipleNumberOperands(binary.operator, left, right)
            return left - right
        elif operator == "STAR":
            utils.checkMultipleNumberOperands(binary.operator, left, right)
            return left * right
        elif operator == "SLASH":
            utils.checkMultipleNumberOperands(binary.operator, left, right)
            return left / right
        elif operator == "PLUS":
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            elif isinstance(left, float) and isinstance(right, float):
                return left + right
            else:
                raise utils.RunTimeError(binary.operator, "Operands must be two numbers or two strings.")
        elif operator == "GREATER":
            utils.checkMultipleNumberOperands(binary.operator, left, right)
            return left > right
        elif operator == "GREATER_EQUAL":
            utils.checkMultipleNumberOperands(binary.operator, left, right)
            return left >= right
        elif operator == "LESS":
            utils.checkMultipleNumberOperands(binary.operator, left, right)
            return left < right
        elif operator == "LESS_EQUAL":
            utils.checkMultipleNumberOperands(binary.operator, left, right)
            return left <= right
        elif operator == "BANG_EQUAL":
            return not utils.isEqual(left, right)
        elif operator == "EQUAL_EQUAL":
            return utils.isEqual(left, right)

    def visitCall(self, call):
        callee = self.evaluate(call.callee)

        arguments = [self.evaluate(argument) for argument in call.arguments]

        if not isinstance(callee, Callable):
            raise utils.RunTimeError(call.paren, "Can only call functions and classes")

        function = callee

        if len(arguments) != function.arity():
            raise utils.RunTimeError(call.paren, f"Expected "
                                                 f"{function.arity()} arguments but got {len(arguments)}.")

        return function.call(self, arguments)