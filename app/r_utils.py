from r_token import Token
import sys
import builtins


class RunTimeError(builtins.RuntimeError):
    def __init__(self, token: Token, *args):
        super().__init__(*args)
        self.token = token


def isDigit(character: str) -> bool:
    """
    Determines if a character is a digit or not

    Returns
    -------
    :return digit: a bool saying if the character is a digit
    """
    if character is None:
        return False
    else:
        return "0" <= character <= "9"


def isAlpha(character: str) -> bool:
    """
    Determines if a character is a letter or an underscore, or not

    Parameters
    ----------
    :param character: a character

    Returns
    -------
    :return alpha: a bool if the character is a letter or underscore
    """
    if character is None:
        return False
    else:
        return ("a" <= character <= "z") or ("A" <= character <= "Z") or (character == "_")


def isAlphaNumeric(character: str) -> bool:
    return isAlpha(character) or isDigit(character)


def isTruthy(value):
    if value is None:
        return False
    elif isinstance(value, bool):
        return value
    else:
        return True


def isEqual(object_a, object_b):
    if (object_a and object_b) is None:
        return True
    elif object_a is None:
        return False
    elif object_b is None:
        return False
    else:
        return object_a == object_b


def checkNumberOperand(token, operand):
    if isinstance(operand, float):
        return
    else:
        raise RunTimeError(token, "Operand must be a number")


def checkMultipleNumberOperands(token, operand_left, operand_right):
    if isinstance(operand_left, float) and isinstance(operand_right, float):
        return
    else:
        raise RunTimeError(token, "Operands must be numbers")


def stringify(object_to_string):
    if object_to_string is None:
        return "nil"
    elif isinstance(object_to_string, float):
        text = str(object_to_string)
        if text.endswith(".0"):
            text = text[:len(text) - 2]

        return text
    elif isinstance(object_to_string, bool):
        if object_to_string:
            return "true"
        else:
            return "false"
    else:
        return str(object_to_string)


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
