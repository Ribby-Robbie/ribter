from r_token import Token
import sys
import builtins


class RunTimeError(builtins.RuntimeError):
    def __init__(self, token: Token, *args):
        super().__init__(*args)
        self.token = token


class ParserError(Exception):
    pass


def error(token, message):
    if token.token_type == "EOF":
        Rib.report(token.line - 1, " at end", message)
    else:
        Rib.report(token.line, f" at '{token.lexeme}'", message)

    return ParserError


class Rib:
    had_error = False
    had_runtime_error = False

    def __init__(self):
        pass

    @staticmethod
    def runtimeError(error_line, error_message):
        Rib.had_runtime_error = True
        print(f"{error_message} \n[line {error_line}]", file=sys.stderr)

    @staticmethod
    def report(line, where, message):
        Rib.had_error = True
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)


class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        # enclosing allows for nesting environments, i.e., scopes
        self.enclosing = enclosing

    def inner(self):
        return Environment(self)

    def define(self, name, value):
        self.values[name] = value

    def ancestor(self, distance: int):
        """
        Walks a fixed number of spaces up the parent chain and returns the environment there
        """
        environment = self
        i = 0
        while i < distance:
            environment = environment.enclosing
            i += 1

        return environment

    def getAt(self, distance: int, name: str):
        """
        Returns the value of a variable in that specific environment's map
        """
        return self.ancestor(distance).values.get(name)

    def assignAt(self, distance: int, name: Token, value):
        self.ancestor(distance).values[name.lexeme] = value

    def get(self, name: Token):
        lexeme = name.lexeme

        if lexeme in self.values.keys():
            return self.values[lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RunTimeError(name, f"Undefined variable '{lexeme}'.")

    def assign(self, name: Token, value):
        """
        This doesn't define a new value, so if it doesn't already exist, it throws a RunTimeError

        Parameters
        ----------
        :param name: The variable name (that already exists) that value is being assigned to
        :param value: The value of the variable
        """
        lexeme = name.lexeme
        if lexeme in self.values.keys():
            self.values[lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise RunTimeError(name, f"Undefined variable '{lexeme}'.")
