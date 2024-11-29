import sys
from r_scanner import Scanner
from r_parser import Parser
from r_interpreter import Interpreter
from r_expression import AstPrint
from r_utils import Rib


def tokenize(contents):
    file_scanner = Scanner(contents)
    tokens, errors = file_scanner.scanTokens()

    for token in tokens:
        print(token)

    for error in errors:
        print(error, file=sys.stderr)


def parse(contents):
    file_scanner = Scanner(contents)
    tokens, errors = file_scanner.scanTokens()

    if Rib.had_error:
        return

    parser = Parser(tokens)
    expression = parser.parseExpression()

    if Rib.had_error:
        return
    else:
        print(AstPrint().print(expression))


def evaluate(contents):
    file_scanner = Scanner(contents)
    tokens, errors = file_scanner.scanTokens()

    if Rib.had_error:
        return

    parser = Parser(tokens)
    expression = parser.parseExpression()

    if Rib.had_error:
        return

    interpreter = Interpreter()
    interpreter.interpret_expression(expression)


def run(contents):
    file_scanner = Scanner(contents)
    tokens, errors = file_scanner.scanTokens()

    if Rib.had_error:
        return

    parser = Parser(tokens)
    statements = parser.parseStatement()

    if Rib.had_error:
        return

    interpreter = Interpreter()
    interpreter.interpret_statement(statements)


def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    with open(filename) as file:
        file_contents = file.read()

    if command == "tokenize":
        tokenize(file_contents)
    elif command == "parse":
        parse(file_contents)
    elif command == "evaluate":
        evaluate(file_contents)
    elif command == "run":
        run(file_contents)
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    if Rib.had_error:
        # Exit code 65 for lexical errors
        exit(65)
    elif Rib.had_runtime_error:
        # Exit 70 for actual runtime errors
        exit(70)


if __name__ == "__main__":
    main()
