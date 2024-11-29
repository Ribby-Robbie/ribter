import abc
from r_statement import FunctionStatement
from r_environment import Environment
import typing
import builtins

if typing.TYPE_CHECKING:
    from .r_interpreter import Interpreter


class Callable(abc.ABC):
    @abc.abstractmethod
    def call(self, interpreter: "Interpreter", arguments):
        pass

    @abc.abstractmethod
    def arity(self) -> int:
        pass


class Return(builtins.RuntimeError):
    def __init__(self, value):
        self.value = value


class RibCallable(Callable):
    def __init__(self, name: str, arity: int, called):
        self.name = name
        # variable naming like this because for some reason Python doesn't like variables with the same names as functs
        self._arity = arity
        self.called = called

    def arity(self) -> int:
        return self._arity

    def call(self, interpreter, arguments):
        return self.called(*arguments)

    def __str__(self):
        return f"<native fn {self.name}>"


class RibFunction(Callable):
    def __init__(self, declaration: FunctionStatement, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, arguments):
        environment = self.closure.inner()

        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        # When it finds the return keyword, it calls the Return "error" and makes it return the value from the call
        try:
            interpreter.executeBlock(self.declaration.body, environment)
        except Return as return_value:
            return return_value.value

        return None

    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
