from r_function import Callable
from r_instance import RibInstance


# Needs to use the interpreter and arguments from Callable
class RibClass(Callable):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def call(self, interpreter, arguments):
        instance = RibInstance(self)
        return instance

    def arity(self) -> int:
        return 0
