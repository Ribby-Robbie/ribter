from r_class import RibClass
from r_token import Token
from r_environment import RunTimeError


class RibInstance:
    def __init__(self, class_: RibClass):
        self.class_ = class_
        self.fields = dict()

    def __str__(self):
        return self.class_.name + " instance"

    def get(self, name: Token):
        # If the instance has that field, cool, return it
        if name.lexeme in self.fields.keys():
            return self.fields[name.lexeme]

        # Otherwise, it is a runtime error to let the user know something funky is happening
        raise RunTimeError(name, f"Undefined property {name.lexeme}.")
