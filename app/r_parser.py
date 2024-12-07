from r_token import Token
from r_expression import Literal, Unary, Grouping, Binary, Variable, Assign, Logical, Expression, Call
from r_statement import (PrintStatement, ExpressionStatement, VarStatement, BlockStatement, IfStatement,
                         WhileStatement, FunctionStatement, ReturnStatement, ClassStatement)
from r_environment import ParserError, error


class Parser:

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parseExpression(self):
        """
        Parsing used for expressions
        """
        try:
            return self.expression()
        except ParserError:
            return None

    def parseStatement(self):
        """
        Parsing used for statements
        """
        try:
            statements = []
            while not self.isAtEnd():
                statements.append(self.declaration())

            return statements
        except ParserError:
            return None

    def declaration(self):
        """
        Declaring that something is a function or variable, as well as what its statement is
        """
        try:
            if self.match("CLASS"):
                return self.classDeclaration()
            elif self.match("FUN"):
                return self.function("function")
            elif self.match("VAR"):
                return self.varDeclaration()

            return self.statement()
        except ParserError:
            self.synchronize()
            return None

    def classDeclaration(self):
        name = self.consume("IDENTIFIER", "Expect class name.")
        self.consume("LEFT_BRACE", "Expect '{' before class body.")

        methods = []
        while (not self.check("RIGHT_BRACE")) and (not self.isAtEnd()):
            methods.append(self.function("method"))

        self.consume("RIGHT_BRACE", "Expect '}' after class body.")

        return ClassStatement(name, methods)

    def varDeclaration(self):
        """
        Declares a variable to have whatever the initializer is set to, if it isn't set to anything it stays as None
        """
        name = self.consume("IDENTIFIER", "Expect variable name")

        initializer = None
        if self.match("EQUAL"):
            initializer = self.expression()

        self.consume("SEMICOLON", "Expect ';' after variable declaration.")
        return VarStatement(name, initializer)

    def whileStatement(self):
        """
        Gets the condition of the while statement, and then the body that it is supposed to execute while in the while
        statement.
        """
        self.consume("LEFT_PAREN", "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume("RIGHT_PAREN", "Expect ')' after condition.")
        body = self.statement()

        return WhileStatement(condition, body)

    def statement(self):
        """
        Checks what kind of statement it is, and calls the corresponding function
        :return:
        """
        if self.match("FOR"):
            return self.forStatement()
        elif self.match("IF"):
            return self.ifStatement()
        elif self.match("PRINT"):
            return self.printStatement()
        elif self.match("RETURN"):
            return self.returnStatement()
        elif self.match("WHILE"):
            return self.whileStatement()
        elif self.match("LEFT_BRACE"):
            return BlockStatement(self.blockStatement())
        else:
            return self.expressionStatement()

    def forStatement(self):
        self.consume("LEFT_PAREN", "Expect '(' after 'for'.")

        if self.match("SEMICOLON"):
            initializer = None
        elif self.match("VAR"):
            initializer = self.varDeclaration()
        else:
            initializer = self.expressionStatement()

        condition = None
        if not self.match("SEMICOLON"):
            condition = self.expression()

        self.consume("SEMICOLON", "Expect ';' after loop condition.")

        increment = None
        if not self.check("RIGHT_PAREN"):
            increment = self.expression()

        self.consume("RIGHT_PAREN", "Expect ')' after for conditions.")
        body = self.statement()

        if increment is not None:
            body = BlockStatement([body, ExpressionStatement(increment)])

        # If the condition is omitted, we shove in a true to make it run continuously
        if condition is None:
            condition = Literal(True)

        body = WhileStatement(condition, body)

        # initializer runs once before the entire loop
        # We do that again by replacing the whole statement with a block that runs the initializer,
        # and then runs the body
        if initializer is not None:
            body = BlockStatement([initializer, body])

        return body

    def ifStatement(self):
        self.consume("LEFT_PAREN", "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume("RIGHT_PAREN", "Expect ')' after if condition.")

        then_branch = self.statement()
        else_branch = None

        if self.match("ELSE"):
            else_branch = self.statement()

        return IfStatement(condition, then_branch, else_branch)

    def printStatement(self):
        """
        Module for if there is a print statement
        :return:
        """
        value = self.expression()
        self.consume("SEMICOLON", "Expect ';' after value.")
        return PrintStatement(value)

    def returnStatement(self):
        keyword = self.previous()
        value = None
        if not self.check("SEMICOLON"):
            value = self.expression()

        self.consume("SEMICOLON", "Expect ';' after return value.")
        return ReturnStatement(keyword, value)

    def expressionStatement(self):
        """
        Module for if there is a general expression
        :return:
        """
        expression = self.expression()
        self.consume("SEMICOLON", "Expect ';' after value.")
        return ExpressionStatement(expression)

    def function(self, kind: str):
        name = self.consume("IDENTIFIER", f"Expect {kind} name.")
        self.consume("LEFT_PAREN", f"Expect '(' after {kind} name.")

        parameters = []
        if not self.check("RIGHT_PAREN"):
            while True:
                if len(parameters) >= 255:
                    raise error(self.peek(), "Can't have more than 255 parameters.")

                parameters.append(self.consume("IDENTIFIER", "Expect parameter name."))

                if not self.match("COMMA"):
                    break

        self.consume("RIGHT_PAREN", "Expect ')' right after parameters.")
        self.consume("LEFT_BRACE", f"Expect '{{' before {kind} body.")
        body = self.blockStatement()

        return FunctionStatement(name, parameters, body)

    def blockStatement(self):
        statements = []

        while (not self.check("RIGHT_BRACE")) and (not self.isAtEnd()):
            statements.append(self.declaration())

        self.consume("RIGHT_BRACE", "Expect '}' after block.")
        return statements

    def assignment(self):
        expression = self.or_()

        if self.match("EQUAL"):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expression, Variable):
                name = expression.name
                return Assign(name, value)

            raise error(equals, "Invalid assignment target.")

        return expression

    def or_(self):
        expression = self.and_()

        while self.match("OR"):
            operator = self.previous()
            right = self.and_()
            expression = Logical(expression, operator, right)

        return expression

    def and_(self):
        expression = self.equality()

        while self.match("AND"):
            operator = self.previous()
            right = self.equality()
            expression = Logical(expression, operator, right)

        return expression

    def peek(self) -> Token:
        """
        It looks at the next value to see what it is

        Returns
        -------
        :return token_next: the next token in the token list
        """
        return self.tokens[self.current]

    def isAtEnd(self):
        """
        It looks at the next value to see if it is an EOF token

        Returns
        -------
        :return eof_bool: A bool saying if it is the EOF
        """
        return self.peek().token_type == "EOF"

    def previous(self):
        """
        Goes back to the previous token

        Returns
        -------
        :return prev_token: the previous token in the list of tokens
        """
        return self.tokens[self.current - 1]

    def advance(self):
        """
        Advances the current index by 1
        """
        if not self.isAtEnd():
            self.current += 1

        return self.previous()

    def check(self, token_type):
        """
        Checks to see if the next token is the token type we are expecting

        Parameters
        ----------
        :param token_type: the next token type we are expecting

        Returns
        -------
        :return check_bool: if it matches the next token type we are expecting
        """
        if self.isAtEnd():
            # Nothing matches the EOF token
            return False

        return self.peek().token_type == token_type

    def match(self, *token_types) -> bool:
        """
        Checks to see if the next token is within our list of tokens

        Returns
        -------
        :return match_bool: a bool saying if the next token matches a token we have
        """
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True

        else:
            # If we get through our whole list of tokens, then it isn't in there
            return False

    def consume(self, token_type, message: str):
        """
        Consumes the next token from the parsing
        If it isn't as expected, we throw an error

        Parameters
        ----------
        :param token_type: The next token we expect
        :param message: The message we give if there is an error
        """
        if self.check(token_type):
            return self.advance()

        raise error(self.peek(), message)

    def primary(self):
        """
        Checks to see if the next token is one of the major expressions

        Returns
        -------
        :return literal | variable | grouping:
        """
        if self.match("FALSE"):
            return Literal(False)
        elif self.match("TRUE"):
            return Literal(True)
        elif self.match("NIL"):
            return Literal(None)
        elif self.match("PRINT"):
            return Literal("print")
        # Gets the literal of the token, which is the number or the expression in the string itself
        elif self.match("NUMBER", "STRING"):
            return Literal(self.previous().literal)
        elif self.match("IDENTIFIER"):
            # Gives the variable a token which serves as the variable
            return Variable(self.previous())
        elif self.match("LEFT_PAREN"):
            expression = self.expression()
            # Need to check that they included the right ) as well
            self.consume("RIGHT_PAREN", "Expect ')' after expression.")
            return Grouping(expression)
        else:
            raise error(self.peek(), "Expect expression.")

    def unary(self):
        """
        Module used to check if there is a unary operator
        Is a recursive function to get all tokens
        :return:
        """
        # We want to check for unary symbols that do negation
        if self.match("BANG", "MINUS"):
            # match advances if it finds one of these operators, so then the operator is now the previous
            operator = self.previous()
            # keep advancing until we get something that is one of the major expressions
            right = self.unary()
            return Unary(operator, right)

        # If it isn't a unary symbol, then it is one of the major symbols
        return self.call()

    def finishCall(self, callee: Expression):
        arguments = []

        if not self.check("RIGHT_PAREN"):
            while True:
                arguments.append(self.expression())

                if len(arguments) >= 255:
                    (self.peek(), "Can't have more than 255 arguments.")

                if not self.match("COMMA"):
                    break

        paren = self.consume("RIGHT_PAREN", "Expect ')' after arguments.")
        return Call(callee, paren, arguments)

    def call(self):
        """
        Used to call a native function
        """
        expression = self.primary()

        while True:
            if self.match("LEFT_PAREN"):
                expression = self.finishCall(expression)
            else:
                break

        return expression

    def factor(self):
        """
        Module used to check if there is a factor operator
        Inherits from unary operator
        :return:
        """
        # Need to check if there is a unary symbol, if there isn't then we just get the major
        expression = self.unary()
        # Goes through the process of checking if we are multiplying or dividing
        while self.match("SLASH", "STAR"):
            operator = self.previous()
            right = self.unary()
            # Need to nest that if there are multiple things all grouped together
            expression = Binary(expression, operator, right)

        return expression

    def term(self):
        """
        Module used to check if there is a term operator
        Inherits from factor module
        :return:
        """
        # Need to check if the previous stuff had to do with multiplication and division
        expression = self.factor()
        # Goes through the process of checking if we are adding or subtracting stuff
        while self.match("PLUS", "MINUS"):
            operator = self.previous()
            right = self.factor()
            # Need to nest that if there are multiple things all grouped together
            expression = Binary(expression, operator, right)

        return expression

    def comparison(self):
        """
        Module used to check if there is a comparison operator
        Inherits from term module
        :return:
        """
        expression = self.term()

        while self.match("GREATER", "LESS", "GREATER_EQUAL", "LESS_EQUAL"):
            operator = self.previous()
            right = self.term()
            expression = Binary(expression, operator, right)

        return expression

    def equality(self):
        """
        Module used to check if there is an equality operator
        Inherits from comparison
        :return:
        """
        expression = self.comparison()

        while self.match("BANG_EQUAL", "EQUAL_EQUAL"):
            operator = self.previous()
            right = self.comparison()
            expression = Binary(expression, operator, right)

        return expression

    def expression(self):
        """
        A module that returns the final expression
        :return:
        """
        return self.assignment()

    def synchronize(self):
        """
        Need to synchronize the tokens and discard them until we are at the beginning of the next statement.
        This occurs after a semicolon

        Returns
        -------
        :return EOS: return 0 if we are at the end of a statement
        """
        self.advance()

        while not self.isAtEnd():
            if self.previous().token_type == "SEMICOLON":
                return

            if self.peek().token_type == "CLASS":
                return
            elif self.peek().token_type == "FUN":
                return
            elif self.peek().token_type == "VAR":
                return
            elif self.peek().token_type == "FOR":
                return
            elif self.peek().token_type == "IF":
                return
            elif self.peek().token_type == "WHILE":
                return
            elif self.peek().token_type == "PRINT":
                return
            elif self.peek().token_type == "RETURN":
                return

            self.advance()
