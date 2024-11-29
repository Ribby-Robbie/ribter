from r_token import Token
import r_utils as utils


class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        # enclosing allows for nesting environments, i.e., scopes
        self.enclosing = enclosing

    def inner(self):
        return Environment(self)

    def define(self, name, value):
        self.values[name] = value

    def get(self, name: Token):
        lexeme = name.lexeme

        if lexeme in self.values.keys():
            return self.values[lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise utils.RunTimeError(name, f"Undefined variable '{lexeme}'.")

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

        raise utils.RunTimeError(name, f"Undefined variable '{lexeme}'.")
